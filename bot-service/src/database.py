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
    
    def get_total_by_category(
        self, 
        user_id: int, 
        category: Optional[str] = None, 
        days: int = 30
    ) -> float:
        """
        Get total amount spent in a category in the last N days.
        
        Args:
            user_id: User ID
            category: Category name (None for all categories)
            days: Number of days to look back
            
        Returns:
            Total amount spent
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if category:
                    cursor.execute(
                        """
                        SELECT COALESCE(SUM(CAST(amount AS NUMERIC)), 0) as total
                        FROM expenses
                        WHERE user_id = %s 
                          AND category = %s
                          AND added_at >= NOW() - INTERVAL '%s days'
                        """,
                        (user_id, category, days)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT COALESCE(SUM(CAST(amount AS NUMERIC)), 0) as total
                        FROM expenses
                        WHERE user_id = %s 
                          AND added_at >= NOW() - INTERVAL '%s days'
                        """,
                        (user_id, days)
                    )
                result = cursor.fetchone()
                return float(result[0]) if result else 0.0
    
    def get_category_breakdown(self, user_id: int, days: int = 30) -> List[Dict]:
        """
        Get spending breakdown by category.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of {category, total, count} dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT 
                        category,
                        COUNT(*) as count,
                        SUM(CAST(amount AS NUMERIC)) as total
                    FROM expenses
                    WHERE user_id = %s 
                      AND added_at >= NOW() - INTERVAL '%s days'
                    GROUP BY category
                    ORDER BY total DESC
                    """,
                    (user_id, days)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_expenses(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get recent expenses for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of expenses to return
            
        Returns:
            List of expense dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT description, amount, category, added_at
                    FROM expenses
                    WHERE user_id = %s
                    ORDER BY added_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def search_expenses(self, user_id: int, keyword: str) -> List[Dict]:
        """
        Search expenses by description keyword.
        
        Args:
            user_id: User ID
            keyword: Keyword to search in description
            
        Returns:
            List of matching expense dicts
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT description, amount, category, added_at
                    FROM expenses
                    WHERE user_id = %s 
                      AND LOWER(description) LIKE LOWER(%s)
                    ORDER BY added_at DESC
                    """,
                    (user_id, f"%{keyword}%")
                )
                return [dict(row) for row in cursor.fetchall()]
    
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

