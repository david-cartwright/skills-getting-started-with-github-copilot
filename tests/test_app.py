"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """Test retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify structure of an activity
        for name, activity in data.items():
            assert isinstance(name, str)
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)

    def test_activities_have_known_names(self, client):
        """Test that expected activities exist."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity_name in expected_activities:
            assert activity_name in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup is rejected."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_invalid_activity(self, client):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_updates_participant_list(self, client):
        """Test that signup adds participant to the activity."""
        email = "testupdate@mergington.edu"
        
        # Get initial activity state
        response = client.get("/activities")
        activity_before = response.json()["Art Club"]
        count_before = len(activity_before["participants"])
        
        # Sign up
        client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        
        # Get updated activity state
        response = client.get("/activities")
        activity_after = response.json()["Art Club"]
        count_after = len(activity_after["participants"])
        
        assert count_after == count_before + 1
        assert email in activity_after["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client):
        """Test successful removal of a participant."""
        email = "removetest@mergington.edu"
        activity_name = "Drama%20Society"
        
        # Sign up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify removal
        response = client.get("/activities")
        assert email not in response.json()["Drama Society"]["participants"]

    def test_remove_nonexistent_participant(self, client):
        """Test removal of participant not in activity."""
        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "nobody@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity(self, client):
        """Test removal from non-existent activity."""
        response = client.delete(
            "/activities/Fake%20Club/participants",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_participant_decreases_count(self, client):
        """Test that removal decreases participant count."""
        email = "counttest@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Debate%20Team/signup",
            params={"email": email}
        )
        
        # Get count before removal
        response = client.get("/activities")
        count_before = len(response.json()["Debate Team"]["participants"])
        
        # Remove participant
        client.delete(
            "/activities/Debate%20Team/participants",
            params={"email": email}
        )
        
        # Get count after removal
        response = client.get("/activities")
        count_after = len(response.json()["Debate Team"]["participants"])
        
        assert count_after == count_before - 1


class TestRootRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        """Test that root path redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
