import pytest


class TestActivityWorkflow:
    """Integration tests for complete activity workflows"""
    
    def test_full_signup_and_unregister_workflow(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"
        
        # Act & Assert - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant appears in activity list
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Act & Assert - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify participant removed from activity list
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]
    
    def test_multiple_participants(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        emails = ["bob@mergington.edu", "carol@mergington.edu", "dave@mergington.edu"]
        
        # Act - Sign up multiple participants
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert - Verify all participants are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        
        for email in emails:
            assert email in participants
        
        assert len(participants) == len(emails)
    
    def test_cannot_signup_twice(self, client, reset_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "frank@mergington.edu"
        
        # Act - First signup succeeds
        first_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert first_response.status_code == 200
        
        # Second signup should fail
        second_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"]
    
    def test_signup_then_unregister_then_signup_again(self, client, reset_activities):
        # Arrange
        activity_name = "Gym Class"
        email = "grace@mergington.edu"
        
        # Act & Assert - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Sign up again should succeed
        response3 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response3.status_code == 200
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
    
    def test_concurrent_activities_independent(self, client, reset_activities):
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        email = "hannah@mergington.edu"
        
        # Act - Sign up for both activities
        signup1 = client.post(
            f"/activities/{activity1}/signup?email={email}"
        )
        signup2 = client.post(
            f"/activities/{activity2}/signup?email={email}"
        )
        
        # Assert
        assert signup1.status_code == 200
        assert signup2.status_code == 200
        
        # Verify in both activities
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
        
        # Act - Unregister from one activity
        unregister = client.delete(
            f"/activities/{activity1}/unregister?email={email}"
        )
        
        # Assert - Still in activity2
        assert unregister.status_code == 200
        activities = client.get("/activities").json()
        assert email not in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
