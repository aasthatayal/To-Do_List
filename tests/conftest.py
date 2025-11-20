"""
Pytest configuration file.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db, task_repo


@pytest.fixture(scope="module")
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def sample_task():
    """Create a sample task for testing."""
    task = task_repo.create_task(
        title="Test Task",
        description="This is a test task",
        due_date=None,
        status="pending"
    )
    yield task
    # Cleanup
    try:
        task_repo.delete_task(task['id'])
    except:
        pass


@pytest.fixture(scope="module")
def test_db():
    """Test database connection."""
    assert db.test_connection(), "Database connection failed"
    return db
