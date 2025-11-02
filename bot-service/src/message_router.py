"""Message router to classify incoming messages."""
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from src.config import get_settings


MessageType = Literal["expense", "query", "other"]


class MessageRouter:
    """Routes messages to appropriate handlers based on content."""
    
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a message classifier for an expense tracking bot.

Classify the message into ONE of these categories:

1. "expense" - User is reporting an expense
   Examples: "Pizza 20 bucks", "Uber to work 15.50", "Paid rent 800 dollars"

2. "query" - User is asking about their expenses
   Examples: "How much did I spend on food?", "Show my expenses", "What's my total spending?"

3. "other" - Greetings, questions, or unrelated messages
   Examples: "Hello", "How are you?", "What can you do?"

Respond with ONLY a JSON object: {{"message_type": "expense|query|other"}}

IMPORTANT: Return ONLY the JSON object, no additional text."""),
            ("user", "{message}")
        ])
    
    def classify(self, message: str) -> MessageType:
        """
        Classify a message into expense, query, or other.
        
        Args:
            message: The message text to classify
            
        Returns:
            MessageType: "expense", "query", or "other"
        """
        try:
            chain = self.prompt | self.llm | StrOutputParser()
            response_str = chain.invoke({"message": message})
            response_data = json.loads(response_str.strip())
            
            message_type = response_data.get("message_type", "other")
            
            # Validate response
            if message_type not in ["expense", "query", "other"]:
                print(f"Invalid message_type from LLM: {message_type}, defaulting to 'other'")
                return "other"
            
            return message_type
            
        except Exception as e:
            print(f"Error classifying message: {e}")
            # Default to "other" on error to fail gracefully
            return "other"


# Singleton instance
message_router = MessageRouter()

