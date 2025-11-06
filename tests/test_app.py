import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    assert "index.html" in str(response.url)

def test_get_activities(client):
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Test structure of an activity
    activity = list(activities.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    activity_name = list(activities.keys())[0]  # Get first activity
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    # Verify participant was added
    assert email in activities[activity_name]["participants"]

def test_signup_for_activity_already_registered(client):
    """Test signup fails when student is already registered"""
    activity_name = list(activities.keys())[0]  # Get first activity
    email = "already@mergington.edu"
    # First signup
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Try to signup again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_for_nonexistent_activity(client):
    """Test signup fails for non-existent activity"""
    response = client.post("/activities/NonExistentActivity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_from_activity_success(client):
    """Test successful unregistration from an activity"""
    activity_name = list(activities.keys())[0]
    email = "unregister@mergington.edu"
    # First sign up
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Then unregister
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    # Verify participant was removed
    assert email not in activities[activity_name]["participants"]

def test_unregister_when_not_registered(client):
    """Test unregistration fails when student is not registered"""
    activity_name = list(activities.keys())[0]
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_from_nonexistent_activity(client):
    """Test unregistration fails for non-existent activity"""
    response = client.post("/activities/NonExistentActivity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]