from datetime import timedelta

from fastapi_app.models import UserDB
from fastapi_app.security import create_access_token


test_data = {
    "email" : "testuser@example.com",
    "password" : "TestPassword123!"
}

def test_register_user(client):

    register_response = client.post(
        "/auth/register",
        json = test_data
    )

    # Check if the test account register successfully
    assert register_response.status_code == 201

    # check tha response contient the email
    assert register_response.json()["email"] == "testuser@example.com"

    # check that passwort does not expose in response
    assert "password" not in register_response.json()

    # check that hashed password does not expose in response
    assert "hashed_password" not in register_response.json()

login_test_data = {
    "username" : "testuser@example.com",
    "password" : "TestPassword123!"
}

def test_login_returns_jwt(client, jwt_secret):

    # register a temporary account
    register_response = client.post(
        "/auth/register",
        json = test_data
    )

    # Check if the test account register successfully
    assert register_response.status_code == 201

    # logint to created account
    login_response = client.post(
        "/auth/login",
        data = login_test_data
    )

    # check if successafly login to account created
    assert login_response.status_code == 200

    # check of token type is bearer
    assert login_response.json()["token_type"] == "bearer"

    # check if theres is a access token in response
    assert "access_token" in login_response.json()

    # extract the jwt
    access_token = login_response.json()["access_token"]

    # check if the access token is a string
    assert isinstance(access_token, str)

    # check if the access token is not empty
    assert len(access_token) > 0

    # test token is valid
    profile_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # check that success have access to protected endpoint
    assert profile_response.status_code == 200

    # check that email is the same in our test_data
    assert profile_response.json()["email"] == test_data["email"]


wrong_login_test_data = {
    "username" : "testuser@example.com",
    "password" : "TestPassword12"
}

def test_login_wrong_password(client):

    # register a temporary account
    register_response = client.post(
        "/auth/register",
        json = test_data
    )

    # Check if the test account register successfully
    assert register_response.status_code == 201

    # try to login to created account with wrong password
    login_response = client.post(
        "/auth/login",
        data = wrong_login_test_data
    )

    # check if login fail with wrong password
    assert login_response.status_code == 401

    # check if message appear
    assert login_response.json()["detail"] == "Incorrect email or password"

    # check if no token generated
    assert "access_token" not in login_response.json()

#Test Missing JWT
def test_profile_requires_authentication(client):

    # try to access to profile without login
    profile_response = client.get(
        "/auth/me"
    )

    # check if the acces faild
    assert profile_response.status_code == 401

    # check if response have not authenticated message
    assert profile_response.json()["detail"] == "Not authenticated"

#invalid token
invalid_token = "jdnvojnvancakzencad,cnazjenfzenfcjkzadncjzdncjazkenckd,nckjazdncjkazdnckjdncqzncdc"
# TEst invalid JWT
def test_profile_rejects_invalid_token(client, jwt_secret):

    # try to access to profile with invalid token
    profile_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    # check if the acces faild
    assert profile_response.status_code == 401

    # check if response have right error message
    assert profile_response.json()["detail"] == "Could not validate credentials"


# Testing an expired JWT
def test_profile_rejects_expired_token(client, jwt_secret):

    expired_token = create_access_token(
        data={"sub":"1"},
        expires_delta= timedelta(seconds=-5)
    )

    # try to access to profile with expired
    profile_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )

    # check if the accessfaild
    assert profile_response.status_code == 401

    # check if response have right error message
    assert profile_response.json()["detail"] == "Could not validate credentials"

# Test for valid JWT, Nonexistant user
def test_token_for_nonexistent_user(client, jwt_secret):

    nonexistent_user_token = create_access_token(
            data={"sub":"9999999"},
            expires_delta= timedelta(seconds=100)
    )

    # try to access to profile with nonexistent user token
    profile_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {nonexistent_user_token}"}
    )

    # check if the accessfaild
    assert profile_response.status_code == 401

    # check if response have right error message
    assert profile_response.json()["detail"] == "Could not validate credentials"


# Test real JWT role-based authorization
def test_real_teacher_cannot_delete_student(client, jwt_secret):

    # register a temporary account
    register_response = client.post(
        "/auth/register",
        json = test_data
    )

    # Check if the test account register successfully
    assert register_response.status_code == 201

    # logint to created account
    login_response = client.post(
        "/auth/login",
        data = login_test_data
    )

    # check if successafly login to account created
    assert login_response.status_code == 200

    # extract the jwt
    access_token = login_response.json()["access_token"]

    # try to delete a student
    delete_response = client.delete(
        "/students/1",
         headers={"Authorization": f"Bearer {access_token}"}
    )

    # check if the request rejected
    assert delete_response.status_code == 403

# Test an authenticated administrator successfully delete a student
def test_real_admin_can_delete_student(
        client,
        jwt_secret,
        db_session
):

    # register a temporary account
    register_response = client.post(
        "/auth/register",
        json = test_data
    )

    # Check if the test account register successfully
    assert register_response.status_code == 201

    registered_user_id = register_response.json()["id"]

    # retrive user
    user = db_session.get(UserDB, registered_user_id )

    # check if the user not null
    assert user is not None

    # change role to admin
    user.role = "admin"
    db_session.commit()

    # logint to created account
    login_response = client.post(
        "/auth/login",
        data = login_test_data
    )

    # check if successafly login to account created
    assert login_response.status_code == 200

    # extract the jwt
    access_token = login_response.json()["access_token"]

    # Create a temporary student
    student_create_response = client.post(
        "/students",
        json={
            "name": "Test Student",
            "age": 17,
            "grade": "2Bac"
        },
         headers={"Authorization": f"Bearer {access_token}"}
    )

    # check if the student create successfily
    assert student_create_response.status_code == 201

    # Retrive student id
    student_id = student_create_response.json()["id"]

    #check if the student_id not null
    assert student_id is not None

    # Try to delete the student using administrator's JWT
    delete_response = client.delete(
        f"/students/{student_id}",
         headers={"Authorization": f"Bearer {access_token}"}
    )

    # check if the request accepted
    assert delete_response.status_code == 200

    # test if the student is deleted
    test_delete_response = client.get(
        f"/students/{student_id}",
         headers={"Authorization": f"Bearer {access_token}"}
    )

    # check if the student not found
    assert test_delete_response.status_code == 404

# Test inactive user cannot access to profile
def test_inactive_user_cannot_access_profile(
        client,
        jwt_secret,
        db_session
):

    # register a temporary account
    register_response = client.post(
        "/auth/register",
        json = test_data
    )

    # Check if the test account register successfully
    assert register_response.status_code == 201

    registered_user_id = register_response.json()["id"]

    # logint to created account
    login_response = client.post(
        "/auth/login",
        data = login_test_data
    )

    # check if successafly login to account created
    assert login_response.status_code == 200

    # extract the jwt
    access_token = login_response.json()["access_token"]

    # retrive user
    user = db_session.get(UserDB, registered_user_id )

    # check if the user not null
    assert user is not None

    # inactive the user
    user.is_active = False
    db_session.commit()

    # try to access to profile non active user
    profile_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # check if the request is rejected
    assert profile_response.status_code == 401