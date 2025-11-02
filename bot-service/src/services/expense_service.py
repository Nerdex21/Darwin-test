"""Business logic for expense processing."""
from typing import Tuple, Optional
from src.database import Database
from src.expense_parser import ExpenseParser, ExpenseInfo


class ExpenseService:
    """Service for handling expense-related business logic."""
    
    def __init__(self, database: Database, parser: ExpenseParser):
        """
        Initialize the expense service.
        
        Args:
            database: Database instance for data operations
            parser: ExpenseParser instance for message parsing
        """
        self.db = database
        self.parser = parser
    
    def process_message(
        self, 
        telegram_id: str, 
        message: str
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Process a message from a Telegram user.
        
        This method:
        1. Verifies the user is whitelisted
        2. Parses the message to extract expense information
        3. Stores the expense in the database
        
        Args:
            telegram_id: The Telegram user ID
            message: The message text to process
        
        Returns:
            Tuple of (success, message, http_status_code)
            - success: Whether the operation succeeded
            - message: Response message
            - http_status_code: HTTP status code to return (403, 500, or None for 200)
        """
        # 1. Check if user is whitelisted
        user_id = self.db.get_user_id(telegram_id)
        if not user_id:
            return False, "User not authorized", 403
        
        # 2. Parse the message
        expense_info = self.parser.parse_message(message)
        
        if not expense_info:
            # Not an expense message - this is OK, just return success=false
            return False, "Not an expense message", None
        
        # 3. Save to database
        try:
            success = self.db.add_expense(
                user_id=user_id,
                description=expense_info.description,
                amount=expense_info.amount,
                category=expense_info.category
            )
            
            if success:
                return True, f"{expense_info.category} expense added ✅", None
            else:
                return False, "Failed to save expense", 500
        
        except Exception as e:
            print(f"Error saving expense: {e}")
            return False, "Failed to save expense", 500


# Singleton instance
from src.database import db
from src.expense_parser import expense_parser

expense_service = ExpenseService(db, expense_parser)

