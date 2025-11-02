from typing import Optional, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from src.config import get_settings


class ExpenseInfo(BaseModel):
    """Structured expense information extracted from user message."""
    is_expense: bool = Field(description="Whether the message is about an expense")
    description: str = Field(description="Brief description of the expense")
    amount: float = Field(description="Amount of money spent")
    category: str = Field(
        description="Expense category: Housing, Transportation, Food, Utilities, "
        "Insurance, Medical/Healthcare, Savings, Debt, Education, Entertainment, or Other"
    )


class ExpenseParser:
    """Parse user messages to extract expense information using LLM."""
    
    VALID_CATEGORIES = [
        "Housing",
        "Transportation",
        "Food",
        "Utilities",
        "Insurance",
        "Medical/Healthcare",
        "Savings",
        "Debt",
        "Education",
        "Entertainment",
        "Other"
    ]
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        self.parser = PydanticOutputParser(pydantic_object=ExpenseInfo)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expense tracking assistant. Analyze user messages to determine if they describe an expense.

If the message is about an expense, extract:
1. A brief description of what was purchased
2. The amount spent (convert any currency words like "bucks", "dollars" to numbers)
3. The most appropriate category from: {categories}

If the message is NOT about an expense (e.g., greetings, questions, random text), set is_expense to false.

{format_instructions}

Examples:
- "Pizza 20 bucks" → is_expense: true, description: "Pizza", amount: 20, category: "Food"
- "Uber to work 15.50" → is_expense: true, description: "Uber to work", amount: 15.50, category: "Transportation"
- "Paid rent 800 dollars" → is_expense: true, description: "Rent payment", amount: 800, category: "Housing"
- "Hello!" → is_expense: false
- "How are you?" → is_expense: false
"""),
            ("user", "{message}")
        ])
    
    def parse_message(self, message: str) -> Optional[ExpenseInfo]:
        """
        Parse a user message to extract expense information.
        
        Returns:
            ExpenseInfo if the message is about an expense, None otherwise
        """
        try:
            chain = self.prompt | self.llm | self.parser
            
            result = chain.invoke({
                "message": message,
                "categories": ", ".join(self.VALID_CATEGORIES),
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Only return if it's actually an expense
            if result.is_expense:
                # Validate category
                if result.category not in self.VALID_CATEGORIES:
                    result.category = "Other"
                return result
            
            return None
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None


# Singleton instance
expense_parser = ExpenseParser()

