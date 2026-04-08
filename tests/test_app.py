from fastapi.testclient import TestClient
from src.app import app
import uuid

client = TestClient(app)


def test_get_activities_returns_available_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert expected_activity in activities
    assert "description" in activities[expected_activity]
    assert "schedule" in activities[expected_activity]
    assert "participants" in activities[expected_activity]
    assert "max_participants" in activities[expected_activity]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Soccer Team"
    new_email = f"test_user_{uuid.uuid4().hex}@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={new_email}"

    # Act
    response = client.post(signup_url)
    get_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert f"Signed up {new_email} for {activity_name}" in response.json()["message"]
    activities = get_response.json()
    assert new_email in activities[activity_name]["participants"]


def test_delete_participant_removes_participant_from_activity():
    # Arrange
    activity_name = "Basketball Team"
    participant_email = f"remove_test_{uuid.uuid4().hex}@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={participant_email}"
    delete_url = f"/activities/{activity_name}/participants?email={participant_email}"

    client.post(signup_url)

    # Act
    delete_response = client.delete(delete_url)
    activities_response = client.get("/activities")

    # Assert
    assert delete_response.status_code == 200
    assert f"Unregistered {participant_email} from {activity_name}" in delete_response.json()["message"]
    activities = activities_response.json()
    assert participant_email not in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Drama Club"
    duplicate_email = f"duplicate_test_{uuid.uuid4().hex}@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={duplicate_email}"

    client.post(signup_url)

    # Act
    second_response = client.post(signup_url)

    # Assert
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up for this activity"


def test_delete_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    missing_email = f"missing_test_{uuid.uuid4().hex}@mergington.edu"
    delete_url = f"/activities/{activity_name}/participants?email={missing_email}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_invalid_activity_returns_404_for_signup_and_delete():
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = f"invalid_test_{uuid.uuid4().hex}@mergington.edu"
    signup_url = f"/activities/{invalid_activity}/signup?email={email}"
    delete_url = f"/activities/{invalid_activity}/participants?email={email}"

    # Act
    signup_response = client.post(signup_url)
    delete_response = client.delete(delete_url)

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
