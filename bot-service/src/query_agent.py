"""Query agent for answering expense-related questions using tools."""
from typing import Optional
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from src.database import Database
from src.config import get_settings


def parse_money(value) -> float:
    """Parse PostgreSQL MONEY type to float."""
    if isinstance(value, (int, float)):
        return float(value)
    # Remove $ and commas, then convert to float
    return float(str(value).replace('$', '').replace(',', ''))


def create_expense_tools(db: Database, user_id: int):
    """Create tools for the expense query agent."""
    
    @tool
    def get_total_spending(category: Optional[str] = None, days: int = 30) -> str:
        """
        Get the total amount spent in a specific category or overall.
        
        Args:
            category: Category name (Food, Transportation, Housing, etc.). 
                     If None, returns total for all categories.
            days: Number of days to look back (default 30)
        
        Returns:
            A string describing the total spending
        """
        total = db.get_total_by_category(user_id, category, days)
        total = parse_money(total)
        
        if category:
            return f"Total spent on {category} in the last {days} days: ${total:.2f}"
        else:
            return f"Total spent across all categories in the last {days} days: ${total:.2f}"
    
    @tool
    def get_spending_breakdown(days: int = 30) -> str:
        """
        Get a breakdown of spending by category.
        
        Args:
            days: Number of days to look back (default 30)
        
        Returns:
            A formatted string showing spending per category
        """
        breakdown = db.get_category_breakdown(user_id, days)
        
        if not breakdown:
            return f"No expenses found in the last {days} days."
        
        lines = [f"Spending breakdown for the last {days} days:\n"]
        for item in breakdown:
            category = item['category']
            total = parse_money(item['total'])
            count = item['count']
            lines.append(f"- {category}: ${total:.2f} ({count} expenses)")
        
        return "\n".join(lines)
    
    @tool
    def get_recent_expenses_list(limit: int = 10) -> str:
        """
        Get a list of recent expenses.
        
        Args:
            limit: Maximum number of expenses to return (default 10)
        
        Returns:
            A formatted string listing recent expenses
        """
        expenses = db.get_recent_expenses(user_id, limit)
        
        if not expenses:
            return "No expenses found."
        
        lines = [f"Your {len(expenses)} most recent expenses:\n"]
        for exp in expenses:
            desc = exp['description']
            amount = parse_money(exp['amount'])
            category = exp['category']
            date = exp['added_at'].strftime('%Y-%m-%d')
            lines.append(f"- {desc}: ${amount:.2f} ({category}) on {date}")
        
        return "\n".join(lines)
    
    @tool
    def search_expenses_by_keyword(keyword: str) -> str:
        """
        Search for expenses containing a specific keyword in the description.
        
        Args:
            keyword: The keyword to search for
        
        Returns:
            A formatted string listing matching expenses
        """
        expenses = db.search_expenses(user_id, keyword)
        
        if not expenses:
            return f"No expenses found matching '{keyword}'."
        
        lines = [f"Found {len(expenses)} expenses matching '{keyword}':\n"]
        for exp in expenses:
            desc = exp['description']
            amount = parse_money(exp['amount'])
            category = exp['category']
            date = exp['added_at'].strftime('%Y-%m-%d')
            lines.append(f"- {desc}: ${amount:.2f} ({category}) on {date}")
        
        return "\n".join(lines)
    
    return [
        get_total_spending,
        get_spending_breakdown,
        get_recent_expenses_list,
        search_expenses_by_keyword
    ]


class QueryAgent:
    """Agent for answering expense-related queries."""
    
    def __init__(self, database: Database):
        """
        Initialize the query agent.
        
        Args:
            database: Database instance for data operations
        """
        settings = get_settings()
        self.db = database
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
    
    def query(self, user_id: int, message: str) -> str:
        """
        Process a query from a user.
        
        Args:
            user_id: The user's database ID
            message: The query message
            
        Returns:
            The agent's response as a string
        """
        # Create tools for this specific user
        tools = create_expense_tools(self.db, user_id)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful expense tracking assistant. 
            
You have access to tools that can query the user's expense data. Use these tools to answer their questions accurately.

When the user asks about spending, categories, or expenses:
1. Use the appropriate tool(s) to get the data
2. Provide a clear, natural language response
3. Include specific numbers and details from the tools

Valid expense categories are: Housing, Transportation, Food, Utilities, Insurance, Medical/Healthcare, Savings, Debt, Education, Entertainment, Other

Be concise but informative. Format currency as $XX.XX."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Execute query
        try:
            result = agent_executor.invoke({"input": message})
            return result["output"]
        except Exception as e:
            print(f"Error executing query agent: {e}")
            return "Sorry, I encountered an error processing your query. Please try again."


# Singleton instance
from src.database import db
query_agent = QueryAgent(db)

