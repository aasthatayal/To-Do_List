"""
Main FastAPI application.
Integrates API endpoints and web templates.
"""
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import logging
from datetime import date
from typing import Optional

from app.config import settings
from app.api import tasks_router
from app.database import db, task_repo

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting application...")
    
    # Test database connection
    if db.test_connection():
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="To-Do List API",
    description="""
    A comprehensive To-Do List application with RESTful APIs.
    
    ## Features
    
    * **Create Tasks**: Add new tasks with title, description, due date, and status
    * **Read Tasks**: Retrieve all tasks or filter by status
    * **Update Tasks**: Modify existing tasks
    * **Delete Tasks**: Remove tasks from the list
    * **Web Interface**: User-friendly HTML templates for task management
    
    ## Status Options
    
    * `pending` - Task is not yet started
    * `in_progress` - Task is currently being worked on
    * `completed` - Task is finished
    
    ## Database
    
    Uses PostgreSQL with raw SQL queries (no ORM).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Mount static files
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(tasks_router)


# Web Interface Routes

@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
async def index(request: Request, status: Optional[str] = None):
    """
    Display all tasks in a web interface.
    Optionally filter by status.
    """
    try:
        # Get all tasks
        all_tasks = task_repo.get_all_tasks()
        
        # Filter if status provided
        if status:
            tasks = task_repo.get_all_tasks(status=status)
        else:
            tasks = all_tasks
        
        # Calculate statistics
        total_count = len(all_tasks)
        pending_count = len([t for t in all_tasks if t['status'] == 'pending'])
        in_progress_count = len([t for t in all_tasks if t['status'] == 'in_progress'])
        completed_count = len([t for t in all_tasks if t['status'] == 'completed'])
        
        logger.info(f"Rendering index page with {len(tasks)} tasks")
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "tasks": tasks,
                "status_filter": status,
                "total_count": total_count,
                "pending_count": pending_count,
                "in_progress_count": in_progress_count,
                "completed_count": completed_count
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "tasks": [],
                "message": f"Error loading tasks: {str(e)}",
                "message_type": "error",
                "total_count": 0,
                "pending_count": 0,
                "in_progress_count": 0,
                "completed_count": 0
            }
        )


@app.get("/add", response_class=HTMLResponse, tags=["Web Interface"])
async def add_task_form(request: Request):
    """Display the add task form."""
    logger.info("Rendering add task form")
    return templates.TemplateResponse("add_task.html", {"request": request})


@app.post("/tasks/create", response_class=HTMLResponse, tags=["Web Interface"])
async def create_task_web(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    status: str = Form("pending")
):
    """Create a new task from web form."""
    try:
        # Parse due date
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = date.fromisoformat(due_date)
            except ValueError:
                logger.warning(f"Invalid due date format: {due_date}")
        
        # Create task
        task = task_repo.create_task(
            title=title.strip(),
            description=description.strip() if description else None,
            due_date=parsed_due_date,
            status=status
        )
        
        logger.info(f"Task created via web form: {task['id']}")
        
        # Redirect to home page with success message
        return RedirectResponse(url="/?message=Task created successfully", status_code=303)
    
    except Exception as e:
        logger.error(f"Error creating task via web form: {str(e)}")
        return templates.TemplateResponse(
            "add_task.html",
            {
                "request": request,
                "message": f"Error creating task: {str(e)}",
                "message_type": "error"
            }
        )


@app.post("/tasks/{task_id}/update-status", response_class=HTMLResponse, tags=["Web Interface"])
async def update_task_status(task_id: int, status: str = Form(...)):
    """Update task status from web interface."""
    try:
        task_repo.update_task(task_id=task_id, status=status)
        logger.info(f"Task {task_id} status updated to {status} via web")
        return RedirectResponse(url="/?message=Task updated successfully", status_code=303)
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return RedirectResponse(url=f"/?message=Error updating task: {str(e)}", status_code=303)


@app.post("/tasks/{task_id}/delete", response_class=HTMLResponse, tags=["Web Interface"])
async def delete_task_web(task_id: int):
    """Delete a task from web interface."""
    try:
        deleted = task_repo.delete_task(task_id)
        if deleted:
            logger.info(f"Task {task_id} deleted via web")
            return RedirectResponse(url="/?message=Task deleted successfully", status_code=303)
        else:
            return RedirectResponse(url="/?message=Task not found", status_code=303)
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return RedirectResponse(url=f"/?message=Error deleting task: {str(e)}", status_code=303)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    db_healthy = db.test_connection()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
