from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.security import get_current_user, require_admin
from fastapi_app.models import UserDB



client = TestClient(app)

# create fake teacher
def fake_teacher ():
    user = UserDB()

    user.id = 1
    user.email = "faketecher@gmail.com"
    user.is_active = True
    user.role = "teacher"

    return user

# Test that teacher cannot delete student
def  test_teacher_cannot_delete_student():

    app.dependency_overrides[get_current_user]= fake_teacher
    try:
        response = client.delete("/students/1")

        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_students_requires_login(client):

    # 1. Send Get request without a token
    response = client.get("/students/")

    # 2. Verify the HTTP status code
    assert response.status_code == 401

#Verify Fastapi endpoints use the in-memory testing database
def test_teacher_sees_empty_test_database(client):

    app.dependency_overrides[get_current_user]= fake_teacher

    try:
       response = client.get("/students/")

       assert response.status_code == 200
       assert response.json() == [] 
    finally:
       app.dependency_overrides.pop(get_current_user, None)


# define fake admin
def fake_admin():
    admin = UserDB()
    
    admin.id = 2
    admin.email = "fakeadmin@gmail.com"
    admin.is_active = True
    admin.role = "admin"

    return admin

# Test that admin can delete a student
def test_admin_can_delete_student(client):
    app.dependency_overrides[get_current_user] = fake_admin

    try:
        create_response = client.post(
            "/students",
            json={
                "name": "Test Student",
                "age": 17,
                "grade": "2Bac"   
            }
        )

        # test that admin can post a student
        assert create_response.status_code == 201

        # retrive the id of the created student
        student_id = create_response.json()["id"]

        delete_response = client.delete(f"/students/{student_id}")

        # check that admin can delete student
        assert delete_response.status_code == 200

        get_response = client.get(f"/students/{student_id}")

        # check that student succsafilly deleted
        assert get_response.status_code == 404

    finally : 
        app.dependency_overrides.pop(get_current_user, None)

def test_teacher_delete_does_not_remove_student(client):

    app.dependency_overrides[get_current_user] = fake_admin

    try:
        # Create temporary student as admin
        create_response = client.post(
            "/students",
            json={
                "name": "Test Student",
                "age": 17,
                "grade": "2Bac"   
            }
        )

        assert create_response.status_code == 201
        # retrive the temporary student id
        student_id = create_response.json()["id"]    

        # Switch from admin to teacher
        app.dependency_overrides[get_current_user] = fake_teacher

        # try to delete student as teacher
        delete_response = client.delete(f"/students/{student_id}")

        # check that teacher forbiden from deleting students
        assert delete_response.status_code == 403

        # check if student still in exists
        get_response = client.get(f"/students/{student_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == student_id

    finally:

        app.dependency_overrides.pop(get_current_user, None)

