"""
Tests for incident endpoints.
"""
import pytest
import os
import tempfile
from io import BytesIO
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Setup and teardown test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_auth_token():
    """Helper function to register and login a user, returning access token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    return login_response.json()["access_token"]


def test_report_incident_success():
    """Test successful incident report with video upload."""
    token = get_auth_token()
    
    # Create a fake video file
    video_content = b"fake video content" * 100
    video_file = BytesIO(video_content)
    
    # Create temporary directory for videos
    temp_dir = tempfile.mkdtemp()
    original_video_path = settings.VIDEO_STORAGE_PATH
    settings.VIDEO_STORAGE_PATH = temp_dir
    
    try:
        response = client.post(
            "/api/v1/incidents/report",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "type": "crash",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "timestamp": "2024-01-13T12:00:00Z",
                "speed": "65.5",
                "heading": "90.0",
                "description": "Test incident"
            },
            files={"video": ("test.mp4", video_file, "video/mp4")}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "incident_id" in data
        assert data["type"] == "crash"
        assert data["latitude"] == 37.7749
        assert data["longitude"] == -122.4194
        assert data["processing_status"] == "pending"
    finally:
        # Restore original settings
        settings.VIDEO_STORAGE_PATH = original_video_path
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_report_incident_missing_fields():
    """Test incident report with missing required fields."""
    token = get_auth_token()
    
    video_file = BytesIO(b"fake video content")
    
    response = client.post(
        "/api/v1/incidents/report",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "type": "crash",
            "latitude": "37.7749"
            # Missing longitude and timestamp
        },
        files={"video": ("test.mp4", video_file, "video/mp4")}
    )
    
    assert response.status_code == 422


def test_report_incident_invalid_coordinates():
    """Test incident report with invalid coordinates."""
    token = get_auth_token()
    
    video_file = BytesIO(b"fake video content")
    
    response = client.post(
        "/api/v1/incidents/report",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "type": "crash",
            "latitude": "999.0",  # Invalid latitude
            "longitude": "-122.4194",
            "timestamp": "2024-01-13T12:00:00Z"
        },
        files={"video": ("test.mp4", video_file, "video/mp4")}
    )
    
    # Should fail validation
    assert response.status_code in [400, 422]


def test_get_incident_success():
    """Test retrieving incident details."""
    token = get_auth_token()
    
    # Create an incident first
    video_file = BytesIO(b"fake video content" * 100)
    temp_dir = tempfile.mkdtemp()
    original_video_path = settings.VIDEO_STORAGE_PATH
    settings.VIDEO_STORAGE_PATH = temp_dir
    
    try:
        create_response = client.post(
            "/api/v1/incidents/report",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "type": "crash",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "timestamp": "2024-01-13T12:00:00Z"
            },
            files={"video": ("test.mp4", video_file, "video/mp4")}
        )
        incident_id = create_response.json()["incident_id"]
        
        # Get incident details
        response = client.get(
            f"/api/v1/incidents/{incident_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["incident_id"] == incident_id
        assert data["type"] == "crash"
    finally:
        settings.VIDEO_STORAGE_PATH = original_video_path
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_incident_not_found():
    """Test retrieving non-existent incident."""
    token = get_auth_token()
    
    response = client.get(
        "/api/v1/incidents/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404


def test_get_nearby_incidents_with_results():
    """Test getting nearby incidents."""
    token = get_auth_token()
    
    # Create a few incidents
    video_file = BytesIO(b"fake video content" * 100)
    temp_dir = tempfile.mkdtemp()
    original_video_path = settings.VIDEO_STORAGE_PATH
    settings.VIDEO_STORAGE_PATH = temp_dir
    
    try:
        # Create incident 1
        client.post(
            "/api/v1/incidents/report",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "type": "crash",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "timestamp": "2024-01-13T12:00:00Z"
            },
            files={"video": ("test1.mp4", BytesIO(b"fake1" * 100), "video/mp4")}
        )
        
        # Query nearby incidents
        response = client.get(
            "/api/v1/incidents/nearby",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "latitude": 37.7749,
                "longitude": -122.4194,
                "radius_km": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        if len(data) > 0:
            assert "incident_id" in data[0]
            assert "distance_km" in data[0]
    finally:
        settings.VIDEO_STORAGE_PATH = original_video_path
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_nearby_incidents_no_results():
    """Test getting nearby incidents with no results."""
    token = get_auth_token()
    
    response = client.get(
        "/api/v1/incidents/nearby",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "latitude": 0.0,
            "longitude": 0.0,
            "radius_km": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_delete_incident_success():
    """Test deleting own incident."""
    token = get_auth_token()
    
    # Create an incident
    video_file = BytesIO(b"fake video content" * 100)
    temp_dir = tempfile.mkdtemp()
    original_video_path = settings.VIDEO_STORAGE_PATH
    settings.VIDEO_STORAGE_PATH = temp_dir
    
    try:
        create_response = client.post(
            "/api/v1/incidents/report",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "type": "crash",
                "latitude": "37.7749",
                "longitude": "-122.4194",
                "timestamp": "2024-01-13T12:00:00Z"
            },
            files={"video": ("test.mp4", video_file, "video/mp4")}
        )
        incident_id = create_response.json()["incident_id"]
        
        # Delete incident
        response = client.delete(
            f"/api/v1/incidents/{incident_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify incident is deleted
        get_response = client.get(
            f"/api/v1/incidents/{incident_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
    finally:
        settings.VIDEO_STORAGE_PATH = original_video_path
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_delete_incident_not_found():
    """Test deleting non-existent incident."""
    token = get_auth_token()
    
    response = client.delete(
        "/api/v1/incidents/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
