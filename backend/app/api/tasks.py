"""Task API endpoints"""
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.task_tool import get_task_tool

logger = logging.getLogger(__name__)
router = APIRouter()


class CreateTaskRequest(BaseModel):
    """Request for creating a new task"""
    title: str
    status: str = "pending"
    due_date: str | None = None  # ISO format datetime string


class TaskResponse(BaseModel):
    """Response model for task data"""
    id: str
    title: str
    status: str
    due_date: str | None
    created_at: str
    updated_at: str


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(request: CreateTaskRequest):
    """
    Create a new task.
    
    Args:
        request: Task creation request
        
    Returns:
        Created task data with auto-generated ID
    """
    try:
        task_tool = get_task_tool()
        
        # Parse due_date if provided
        due_date = None
        if request.due_date:
            try:
                due_date = datetime.fromisoformat(request.due_date)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
        
        # Create task
        task = task_tool.add_task(
            title=request.title,
            status=request.status,
            due_date=due_date
        )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.get("", response_model=list[TaskResponse])
async def list_tasks(status: str | None = Query(None, description="Filter by status (pending, completed, cancelled)")):
    """
    List all tasks, optionally filtered by status.
    
    Args:
        status: Optional status filter
        
    Returns:
        List of tasks
    """
    try:
        task_tool = get_task_tool()
        tasks = task_tool.list_tasks(status_filter=status)
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tasks")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Get a single task by ID.
    
    Args:
        task_id: Firestore document ID
        
    Returns:
        Task data
    """
    try:
        task_tool = get_task_tool()
        task = task_tool.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task")
