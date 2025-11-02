import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import List, Dict, Optional
from src.config import get_settings


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.settings = get_settings()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = psycopg2.connect(
            host=self.settings.database_host,
            port=self.settings.database_port,
            database=self.settings.database_name,
            user=self.settings.database_user,
            password=self.settings.database_password
        )
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def is_user_whitelisted(self, telegram_id: str) -> bool:
        """Check if a user is in the whitelist."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE telegram_id = %s",
                    (telegram_id,)
                )
                return cursor.fetchone() is not None
    
    def get_user_id(self, telegram_id: str) -> Optional[int]:
        """Get user ID from telegram_id."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE telegram_id = %s",
                    (telegram_id,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
    
    def add_expense(
        self, 
        user_id: int, 
        description: str, 
        amount: float, 
        category: str
    ) -> bool:
        """Add an expense to the database."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO expenses (user_id, description, amount, category)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (user_id, description, amount, category)
                    )
            return True
        except Exception as e:
            print(f"Error adding expense: {e}")
            return False
    
    def get_user_expenses(self, user_id: int) -> List[Dict]:
        """Get all expenses for a user."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, description, amount, category, added_at
                    FROM expenses
                    WHERE user_id = %s
                    ORDER BY added_at DESC
                    """,
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]


# Singleton instance
db = Database()

