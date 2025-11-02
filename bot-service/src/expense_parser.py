from typing import Optional, Dict
import os
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
        
        # Configure LangSmith for tracing (optional)
        if settings.langchain_tracing_v2 == "true" and settings.langchain_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
            os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        
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
  "category": "category name"
}}

If the message is NOT about an expense (greetings, questions, random text):
{{
  "is_expense": false
}}

Valid categories: {categories}

Examples:
- "Pizza 20 bucks" → {{"is_expense": true, "description": "Pizza", "amount": 20, "category": "Food"}}
- "Uber to work 15.50" → {{"is_expense": true, "description": "Uber to work", "amount": 15.50, "category": "Transportation"}}
- "Paid rent 800 dollars" → {{"is_expense": true, "description": "Rent payment", "amount": 800, "category": "Housing"}}
- "Hello!" → {{"is_expense": false}}
- "How are you?" → {{"is_expense": false}}

IMPORTANT: Return ONLY the JSON object, no additional text.
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
            
            # Get LLM response as string
            response_str = chain.invoke({
                "message": message,
                "categories": ", ".join(self.VALID_CATEGORIES)
            })
            
            # Parse JSON response
            response_data = json.loads(response_str.strip())
            
            # Check if it's an expense
            if not response_data.get("is_expense", False):
                return None
            
            # Validate and create ExpenseInfo
            expense_info = ExpenseInfo(
                is_expense=True,
                description=response_data.get("description", "Unknown expense"),
                amount=float(response_data.get("amount", 0)),
                category=response_data.get("category", "Other")
            )
            
            # Validate category
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


# Singleton instance
expense_parser = ExpenseParser()

