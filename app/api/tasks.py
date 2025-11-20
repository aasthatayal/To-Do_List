"""
Task API endpoints.
RESTful API for CRUD operations on tasks.
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
import logging
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, ErrorResponse
from app.database import task_repo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task with title, description, due date, and status.",
    responses={
        201: {"description": "Task created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_task(task: TaskCreate):
    """
    Create a new task.
    
    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **due_date**: Task due date (optional)
    - **status**: Task status - pending, in_progress, or completed (default: pending)
    """
    try:
        logger.info(f"Creating task: {task.title}")
        created_task = task_repo.create_task(
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status.value
        )
        
        if not created_task:
            logger.error("Failed to create task")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )
        
        logger.info(f"Task created successfully with ID: {created_task['id']}")
        return TaskResponse(**created_task)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Get all tasks",
    description="Retrieve all tasks, optionally filtered by status.",
    responses={
        200: {"description": "Tasks retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_tasks(
    task_status: Optional[str] = Query(
        None,
        alias="status",
        description="Filter tasks by status (pending, in_progress, completed)"
    )
):
    """
    Retrieve all tasks.
    
    - **status**: Optional status filter (pending, in_progress, completed)
    """
    try:
        logger.info(f"Retrieving tasks with status filter: {task_status}")
        
        if task_status and task_status not in ['pending', 'in_progress', 'completed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be one of: pending, in_progress, completed"
            )
        
        tasks = task_repo.get_all_tasks(status=task_status)
        logger.info(f"Retrieved {len(tasks)} tasks")
        
        return TaskListResponse(
            tasks=[TaskResponse(**task) for task in tasks],
            count=len(tasks)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    description="Retrieve a specific task by its ID.",
    responses={
        200: {"description": "Task retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_task(task_id: int):
    """
    Retrieve a task by ID.
    
    - **task_id**: Task ID
    """
    try:
        logger.info(f"Retrieving task with ID: {task_id}")
        task = task_repo.get_task_by_id(task_id)
        
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        logger.info(f"Task {task_id} retrieved successfully")
        return TaskResponse(**task)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update an existing task by ID.",
    responses={
        200: {"description": "Task updated successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_task(task_id: int, task_update: TaskUpdate):
    """
    Update a task.
    
    - **task_id**: Task ID
    - **title**: New task title (optional)
    - **description**: New task description (optional)
    - **due_date**: New due date (optional)
    - **status**: New status (optional)
    """
    try:
        logger.info(f"Updating task with ID: {task_id}")
        
        # Check if task exists
        existing_task = task_repo.get_task_by_id(task_id)
        if not existing_task:
            logger.warning(f"Task with ID {task_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Update task
        updated_task = task_repo.update_task(
            task_id=task_id,
            title=task_update.title,
            description=task_update.description,
            due_date=task_update.due_date,
            status=task_update.status.value if task_update.status else None
        )
        
        if not updated_task:
            logger.error(f"Failed to update task {task_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )
        
        logger.info(f"Task {task_id} updated successfully")
        return TaskResponse(**updated_task)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by ID.",
    responses={
        204: {"description": "Task deleted successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def delete_task(task_id: int):
    """
    Delete a task.
    
    - **task_id**: Task ID
    """
    try:
        logger.info(f"Deleting task with ID: {task_id}")
        
        deleted = task_repo.delete_task(task_id)
        
        if not deleted:
            logger.warning(f"Task with ID {task_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        logger.info(f"Task {task_id} deleted successfully")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
