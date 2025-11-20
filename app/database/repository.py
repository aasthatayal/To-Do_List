"""
Database operations for tasks table.
All CRUD operations using raw SQL queries.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import date
from app.database.connection import db

logger = logging.getLogger(__name__)


class TaskRepository:
    """Repository for task CRUD operations using raw SQL."""
    
    @staticmethod
    def create_task(title: str, description: Optional[str], due_date: Optional[date], 
                   status: str = 'pending') -> Optional[Dict[str, Any]]:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            due_date: Task due date
            status: Task status (pending, in_progress, completed)
        
        Returns:
            Created task as dictionary
        """
        try:
            query = """
                INSERT INTO tasks (title, description, due_date, status)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title, description, due_date, status, created_at, updated_at
            """
            result = db.execute_one(query, (title, description, due_date, status))
            logger.info(f"Task created successfully with ID: {result['id']}")
            return dict(result)
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    @staticmethod
    def get_all_tasks(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks, optionally filtered by status.
        
        Args:
            status: Optional status filter
        
        Returns:
            List of tasks
        """
        try:
            if status:
                query = """
                    SELECT id, title, description, due_date, status, created_at, updated_at
                    FROM tasks
                    WHERE status = %s
                    ORDER BY created_at DESC
                """
                results = db.execute_query(query, (status,))
            else:
                query = """
                    SELECT id, title, description, due_date, status, created_at, updated_at
                    FROM tasks
                    ORDER BY created_at DESC
                """
                results = db.execute_query(query)
            
            logger.info(f"Retrieved {len(results)} tasks")
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve tasks: {str(e)}")
            raise
    
    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task dictionary or None if not found
        """
        try:
            query = """
                SELECT id, title, description, due_date, status, created_at, updated_at
                FROM tasks
                WHERE id = %s
            """
            result = db.execute_one(query, (task_id,))
            if result:
                logger.info(f"Retrieved task with ID: {task_id}")
                return dict(result)
            else:
                logger.warning(f"Task with ID {task_id} not found")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve task {task_id}: {str(e)}")
            raise
    
    @staticmethod
    def update_task(task_id: int, title: Optional[str] = None, 
                   description: Optional[str] = None, due_date: Optional[date] = None,
                   status: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a task.
        
        Args:
            task_id: Task ID
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            status: New status (optional)
        
        Returns:
            Updated task dictionary or None if not found
        """
        try:
            # Build dynamic update query
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = %s")
                params.append(title)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if due_date is not None:
                updates.append("due_date = %s")
                params.append(due_date)
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            
            if not updates:
                logger.warning(f"No fields to update for task {task_id}")
                return TaskRepository.get_task_by_id(task_id)
            
            params.append(task_id)
            query = f"""
                UPDATE tasks
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, title, description, due_date, status, created_at, updated_at
            """
            
            result = db.execute_one(query, tuple(params))
            if result:
                logger.info(f"Task {task_id} updated successfully")
                return dict(result)
            else:
                logger.warning(f"Task {task_id} not found for update")
                return None
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            query = "DELETE FROM tasks WHERE id = %s"
            rows_affected = db.execute_query(query, (task_id,), fetch=False)
            
            if rows_affected > 0:
                logger.info(f"Task {task_id} deleted successfully")
                return True
            else:
                logger.warning(f"Task {task_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_tasks_count() -> int:
        """Get total count of tasks."""
        try:
            query = "SELECT COUNT(*) as count FROM tasks"
            result = db.execute_one(query)
            count = result['count'] if result else 0
            logger.info(f"Total tasks count: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to get tasks count: {str(e)}")
            raise


# Global repository instance
task_repo = TaskRepository()
