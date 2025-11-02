from typing import Optional, Dict
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from src.config import get_settings


class ExpenseInfo(BaseModel):
    """Structured expense information extracted from user message."""
    is_expense: bool
    description: str
    amount: float
    category: str
    confirmation_message: str


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
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expense tracking assistant. Analyze user messages to determine if they describe an expense.

Your response must be a valid JSON object with the following structure:

If the message IS about an expense:
{{
  "is_expense": true,
  "description": "brief description",
  "amount": <number>,
  "category": "category name",
  "confirmation_message": "confirmation in the SAME language as the user input"
}}

If the message is NOT about an expense (greetings, questions, random text):
{{
  "is_expense": false
}}

Valid categories: {categories}

Examples:
- "Pizza 20 bucks" → {{"is_expense": true, "description": "Pizza", "amount": 20, "category": "Food", "confirmation_message": "Food expense added ✅"}}
- "Pizza 20 dólares" → {{"is_expense": true, "description": "Pizza", "amount": 20, "category": "Food", "confirmation_message": "Gasto de comida agregado ✅"}}
- "Uber to work 15.50" → {{"is_expense": true, "description": "Uber to work", "amount": 15.50, "category": "Transportation", "confirmation_message": "Transportation expense added ✅"}}
- "Uber al trabajo $15" → {{"is_expense": true, "description": "Uber al trabajo", "amount": 15, "category": "Transportation", "confirmation_message": "Gasto de transporte agregado ✅"}}
- "Paid rent 800 dollars" → {{"is_expense": true, "description": "Rent payment", "amount": 800, "category": "Housing", "confirmation_message": "Housing expense added ✅"}}
- "Pagué el alquiler 800 dólares" → {{"is_expense": true, "description": "Pago de alquiler", "amount": 800, "category": "Housing", "confirmation_message": "Gasto de vivienda agregado ✅"}}
- "Hello!" → {{"is_expense": false}}
- "Hola!" → {{"is_expense": false}}

IMPORTANT: 
1. Return ONLY the JSON object, no additional text.
2. The confirmation_message MUST be in the SAME language as the user's input message.
3. Keep confirmation messages short and friendly.
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
            # Create chain with string output parser
            chain = self.prompt | self.llm | StrOutputParser()
            
            response_str = chain.invoke({
                "message": message,
                "categories": ", ".join(self.VALID_CATEGORIES)
            })

            response_data = json.loads(response_str.strip())
            
            if not response_data.get("is_expense", False):
                return None
            
            expense_info = ExpenseInfo(
                is_expense=True,
                description=response_data.get("description", "Unknown expense"),
                amount=float(response_data.get("amount", 0)),
                category=response_data.get("category", "Other"),
                confirmation_message=response_data.get("confirmation_message", "Expense added ✅")
            )
            
            if expense_info.category not in self.VALID_CATEGORIES:
                expense_info.category = "Other"
            
            return expense_info
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM: {e}")
            print(f"LLM response: {response_str if 'response_str' in locals() else 'N/A'}")
            return None
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None


expense_parser = ExpenseParser()

