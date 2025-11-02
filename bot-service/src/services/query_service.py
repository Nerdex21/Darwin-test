"""Business logic for query processing."""
from typing import Tuple, Optional
from src.database import Database
from src.query_agent import QueryAgent


class QueryService:
    """Service for handling query-related business logic."""
    
    def __init__(self, database: Database, agent: QueryAgent):
        """
        Initialize the query service.
        
        Args:
            database: Database instance for data operations
            agent: QueryAgent instance for processing queries
        """
        self.db = database
        self.agent = agent
    
    def process_query(
        self, 
        telegram_id: str, 
        message: str
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Process a query from a Telegram user.
        
        Args:
            telegram_id: The Telegram user ID
            message: The query message
        
        Returns:
            Tuple of (success, response_message, http_status_code)
        """
        # 1. Check if user is whitelisted
        user_id = self.db.get_user_id(telegram_id)
        if not user_id:
            return False, "User not authorized", 403
        
        # 2. Process query with agent
        try:
            response = self.agent.query(user_id, message)
            return True, response, None
        
        except Exception as e:
            print(f"Error processing query: {e}")
            return False, "Sorry, I encountered an error processing your query.", 500


# Singleton instance
from src.database import db
from src.query_agent import query_agent

query_service = QueryService(db, query_agent)

