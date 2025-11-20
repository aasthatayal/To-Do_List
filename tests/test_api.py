"""
Tests for Task API endpoints.
"""
import pytest
from datetime import date


class TestTaskAPI:
    """Test suite for task API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
    
    def test_create_task(self, client):
        """Test creating a new task."""
        task_data = {
            "title": "Test Task Create",
            "description": "This is a test task",
            "due_date": "2025-12-31",
            "status": "pending"
        }
        
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Cleanup
        task_id = data["id"]
        client.delete(f"/api/tasks/{task_id}")
    
    def test_create_task_minimal(self, client):
        """Test creating a task with only required fields."""
        task_data = {
            "title": "Minimal Task"
        }
        
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["status"] == "pending"  # Default status
        
        # Cleanup
        client.delete(f"/api/tasks/{data['id']}")
    
    def test_create_task_invalid_title(self, client):
        """Test creating a task with empty title."""
        task_data = {
            "title": ""
        }
        
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_all_tasks(self, client, sample_task):
        """Test retrieving all tasks."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert isinstance(data["tasks"], list)
        assert data["count"] >= 1
    
    def test_get_tasks_by_status(self, client, sample_task):
        """Test retrieving tasks filtered by status."""
        response = client.get("/api/tasks?status=pending")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        
        # All returned tasks should have pending status
        for task in data["tasks"]:
            assert task["status"] == "pending"
    
    def test_get_tasks_invalid_status(self, client):
        """Test retrieving tasks with invalid status filter."""
        response = client.get("/api/tasks?status=invalid_status")
        assert response.status_code == 400
    
    def test_get_task_by_id(self, client, sample_task):
        """Test retrieving a specific task by ID."""
        task_id = sample_task["id"]
        
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task["title"]
    
    def test_get_task_not_found(self, client):
        """Test retrieving a non-existent task."""
        response = client.get("/api/tasks/999999")
        assert response.status_code == 404
    
    def test_update_task(self, client, sample_task):
        """Test updating a task."""
        task_id = sample_task["id"]
        
        update_data = {
            "title": "Updated Task Title",
            "status": "in_progress"
        }
        
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]
    
    def test_update_task_not_found(self, client):
        """Test updating a non-existent task."""
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.put("/api/tasks/999999", json=update_data)
        assert response.status_code == 404
    
    def test_update_task_partial(self, client, sample_task):
        """Test partially updating a task."""
        task_id = sample_task["id"]
        
        # Update only status
        update_data = {
            "status": "completed"
        }
        
        response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
        assert data["title"] == sample_task["title"]  # Title unchanged
    
    def test_delete_task(self, client):
        """Test deleting a task."""
        # Create a task to delete
        task_data = {
            "title": "Task to Delete"
        }
        create_response = client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_delete_task_not_found(self, client):
        """Test deleting a non-existent task."""
        response = client.delete("/api/tasks/999999")
        assert response.status_code == 404
    
    def test_task_lifecycle(self, client):
        """Test complete task lifecycle: create, read, update, delete."""
        # Create
        create_data = {
            "title": "Lifecycle Test Task",
            "description": "Testing complete lifecycle",
            "status": "pending"
        }
        create_response = client.post("/api/tasks", json=create_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Read
        read_response = client.get(f"/api/tasks/{task_id}")
        assert read_response.status_code == 200
        assert read_response.json()["title"] == create_data["title"]
        
        # Update
        update_data = {
            "status": "in_progress"
        }
        update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "in_progress"
        
        # Delete
        delete_response = client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        verify_response = client.get(f"/api/tasks/{task_id}")
        assert verify_response.status_code == 404
