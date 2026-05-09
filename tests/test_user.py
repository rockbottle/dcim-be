import pytest


def test_create_user(client):
    """
    Tests /user/create (POST).
    Matches UserBase schema.
    """
    payload = {"username": "new_dev", "email": "dev@neo.local", "password": "securepassword123", "company_name": "NeoLocal"}
    # FIXED: Replaced "/User/" with the exact path defined in your router
    response = client.post("/user/create", json=payload)

    # If this returns 400, it's usually because the username already exists
    # in the test database or the company name is missing.
    assert response.status_code == 200
    assert response.json()["username"] == "new_dev"


def test_get_my_details(client):
    """
    Tests /user/my_details (GET).
    Uses the mock user from conftest.py.
    """
    response = client.get("/user/my_details")
    assert response.status_code == 200

    data = response.json()
    # Since the backend returns a list, we check the first item
    assert isinstance(data, list)
    assert len(data) > 0
    assert "username" in data[0]
    assert data[0]["username"] == "test_admin"


def test_get_my_team(client):
    """
    Tests /user/my_team (GET).
    """
    response = client.get("/user/my_team")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_user_profile(client):
    """
    Tests /user/update (PUT).
    Matches UserUpdate schema.
    """
    # Note: UserUpdate only allows username, email, and password.
    # company_name is NOT in your UserUpdate schema!
    update_payload = {"email": "updated_admin@neo.local"}
    response = client.put("/user/update", json=update_payload)
    assert response.status_code == 200


def test_delete_own_user(client):
    """
    Tests /user/delete.
    Since conftest.py seeds a DcPurchase record, the logic in db_user.py
    should return 400 to prevent deletion.
    """
    response = client.delete("/user/delete")
    # This confirms your 'cannot delete if usage record exists' logic works
    assert response.status_code == 400
    assert "usage record exists" in response.json()["detail"]
