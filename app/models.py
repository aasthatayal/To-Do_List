"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskCreate(BaseModel):
    """Model for creating a task."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Validate that title is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete FastAPI tutorial",
                "description": "Learn FastAPI basics and advanced features",
                "due_date": "2025-11-25",
                "status": "in_progress"
            }
        }


class TaskUpdate(BaseModel):
    """Model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Validate that title is not empty or whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated task title",
                "status": "completed"
            }
        }


class TaskResponse(BaseModel):
    """Model for task response."""
    id: int = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[date] = Field(None, description="Task due date")
    status: str = Field(..., description="Task status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete FastAPI tutorial",
                "description": "Learn FastAPI basics and advanced features",
                "due_date": "2025-11-25",
                "status": "in_progress",
                "created_at": "2025-11-20T10:30:00",
                "updated_at": "2025-11-20T15:45:00"
            }
        }


class TaskListResponse(BaseModel):
    """Model for list of tasks response."""
    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    count: int = Field(..., description="Total number of tasks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "title": "Complete FastAPI tutorial",
                        "description": "Learn FastAPI basics",
                        "due_date": "2025-11-25",
                        "status": "in_progress",
                        "created_at": "2025-11-20T10:30:00",
                        "updated_at": "2025-11-20T15:45:00"
                    }
                ],
                "count": 1
            }
        }


class ErrorResponse(BaseModel):
    """Model for error responses."""
    detail: str = Field(..., description="Error detail message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Task not found"
            }
        }
