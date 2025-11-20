"""
Database connection and configuration module.
Handles PostgreSQL connections without ORM.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging
from typing import Generator
from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager using raw SQL queries."""
    
    def __init__(self):
        self.connection_params = {
            'host': settings.POSTGRES_HOST,
            'port': settings.POSTGRES_PORT,
            'database': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD
        }
        logger.info(f"Database configured for {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager for database connections.
        Automatically handles connection lifecycle and error handling.
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params, cursor_factory=RealDictCursor)
            logger.debug("Database connection established")
            yield conn
            conn.commit()
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """
        Execute a SQL query with parameters.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            fetch: Whether to fetch results (True for SELECT, False for INSERT/UPDATE/DELETE)
        
        Returns:
            Query results if fetch=True, otherwise None
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, params)
                    if fetch:
                        result = cursor.fetchall()
                        logger.debug(f"Query executed successfully, fetched {len(result)} rows")
                        return result
                    else:
                        logger.debug(f"Query executed successfully, {cursor.rowcount} rows affected")
                        return cursor.rowcount
                except psycopg2.Error as e:
                    logger.error(f"Query execution failed: {str(e)}")
                    raise
    
    def execute_one(self, query: str, params: tuple = None):
        """
        Execute a query and return a single row.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
        
        Returns:
            Single row result or None
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    logger.debug("Query executed successfully, fetched one row")
                    return result
                except psycopg2.Error as e:
                    logger.error(f"Query execution failed: {str(e)}")
                    raise
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    logger.info("Database connection test successful")
                    return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False


# Global database instance
db = Database()
