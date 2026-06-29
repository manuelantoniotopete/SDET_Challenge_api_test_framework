import os
import requests
import pytest
import logging

from tests.schemasAPI import USER_ARRAY_SCHEMA, USER_CREATE_USER, ERROR_RESPONSE_SCHEMA
from jsonschema  import validate

from faker import Faker
fake = Faker()

logger = logging.getLogger(__name__)

def test_get_all_users(base_url,environment):
    response = requests.get(f"{base_url}/{environment}/users")
    dataJSON = response.json()
    assert response.status_code == 200
    validate(dataJSON, schema=USER_ARRAY_SCHEMA)

def test_create_a_new_user(base_url,environment,generate_random_data_user):
    url = f"{base_url}/{environment}/users"
    response = requests.post(url,json=generate_random_data_user) 
    assert response.status_code == 201
    logger.info(f"User created: {generate_random_data_user}")
    dataJSON = response.json()   
    #valid user returned created is the same than we send to be created
    assert dataJSON["name"] == generate_random_data_user["name"]
    assert dataJSON["email"] == generate_random_data_user["email"]
    assert dataJSON["age"] == generate_random_data_user["age"]
    # validate the return schema is the same than we spected
    validate(dataJSON, schema=USER_CREATE_USER)

@pytest.mark.xfail(reason="BUG-001: API returns 500 instead of 409 on duplicate email (violates contract), schema documentation says should return 409 when email is duplicated.")
def test_valid_duplicate_email_user(base_url, environment, create_random_user_via_api):
    logger.info(f"User created: {create_random_user_via_api}")
    email_duplicate = create_random_user_via_api["email"]
    jsonUserDuplicate = {
        "name": "User Duplicated",
        "email": email_duplicate,
        "age": 5,
    }
    url = f"{base_url}/{environment}/users"
    response = requests.post(url,json=jsonUserDuplicate) 
    assert response.status_code == 409
    dataJSON = response.json()
    validate(dataJSON, schema=ERROR_RESPONSE_SCHEMA)

@pytest.mark.parametrize("invalid_payload, description, expected_msg", [
    ({"email": "test@test.com", "age": 30}, "missing name", "name is required"),
    ({"name": "Test", "age": 30}, "missing email", "email is required"),
    ({"name": "Test", "email": "test@test.com"}, "missing age", "age is required"),
    ({"name": "Test", "email": "test@test.com", "age": 0}, "age below minimum", "age must be between 1 and 150"),
    ({"name": "Test", "email": "test@test.com", "age": 200}, "age above maximum", "age must be between 1 and 150"),
    pytest.param(
        {"name": "Test", "email": "not-an-email", "age": 30}, "invalid email format", "email",
        marks=pytest.mark.xfail(reason="BUG-002: API accepts invalid email format, returns 201 instead of 400")
    ),
])
def test_create_user_invalid_return_400(base_url, environment, invalid_payload, description, expected_msg):
    url = f"{base_url}/{environment}/users"
    response = requests.post(url, json=invalid_payload)

    assert response.status_code == 400, f"Failed case: {description}"
    dataJSON = response.json()
    validate(dataJSON, schema=ERROR_RESPONSE_SCHEMA)
    assert expected_msg in dataJSON["error"].lower(), \
        f"Failed case: {description}. Expected '{expected_msg}' in '{dataJSON['error']}'"

def test_get_user_by_email(base_url,environment, create_random_user_via_api):
    email = create_random_user_via_api["email"]
    url = f"{base_url}/{environment}/users/{email}"
    response = requests.get(url)
    assert response.status_code == 200
    dataJSON = response.json()
    validate(dataJSON, schema=USER_CREATE_USER)
    assert dataJSON["email"] == create_random_user_via_api["email"]
    assert dataJSON["name"] == create_random_user_via_api["name"]
    assert dataJSON["age"] == create_random_user_via_api["age"]

@pytest.mark.xfail(reason="BUG-003: API returns 500 instead of 404 for non-existent users (violates contract)")
def test_get_user_not_found(base_url, environment, generate_random_data_user):
    email = generate_random_data_user["email"]
    url = f"{base_url}/{environment}/users/{email}"
    response = requests.get(url)
    assert response.status_code == 404
    dataJSON = response.json()
    validate(dataJSON, schema=ERROR_RESPONSE_SCHEMA)

def test_update_user(base_url, environment, create_random_user_via_api):
    email = create_random_user_via_api["email"]
    url = f"{base_url}/{environment}/users/{email}"

    updated_data = {
        "name": "Updated Name",
        "email": email,         
        "age": 99,
    }
    response = requests.put(url, json=updated_data)
    assert response.status_code == 200
    dataJSON = response.json()
    validate(dataJSON, schema=USER_CREATE_USER)
    assert dataJSON["name"] == updated_data["name"]
    assert dataJSON["age"] == updated_data["age"]
    assert dataJSON["email"] == email

@pytest.mark.parametrize("invalid_payload, description, expected_msg", [
    ({"email": "test@test.com", "age": 30}, "missing name", "name is required"),
    ({"name": "Test", "age": 30}, "missing email", "email is required"),
    ({"name": "Test", "email": "test@test.com"}, "missing age", "age is required"),
    ({"name": "Test", "email": "test@test.com", "age": 0}, "age below minimum", "age must be between 1 and 150"),
    ({"name": "Test", "email": "test@test.com", "age": 200}, "age above maximum", "age must be between 1 and 150"),
])
def test_update_user_invalid_return_400(base_url, environment, create_random_user_via_api, invalid_payload, description, expected_msg):
    email = create_random_user_via_api["email"]   
    url = f"{base_url}/{environment}/users/{email}"

    response = requests.put(url, json=invalid_payload)

    assert response.status_code == 400, f"Failed case: {description}"
    dataJSON = response.json()
    validate(dataJSON, schema=ERROR_RESPONSE_SCHEMA)
    assert expected_msg in dataJSON["error"].lower(), \
        f"Failed case: {description}. Expected '{expected_msg}' in '{dataJSON['error']}'"

def test_update_user_not_found(base_url,environment,generate_random_data_user):
    email = generate_random_data_user["email"]
    url = f"{base_url}/{environment}/users/{email}"

    updated_data = {
        "name": "edited",
        "email": email,
        "age": 30,
    }
    response = requests.put(url, json=updated_data)

    assert response.status_code == 404
    dataJSON = response.json()
    validate(dataJSON, schema=ERROR_RESPONSE_SCHEMA)
    assert "not found" in dataJSON["error"].lower()

def test_update_user_duplicate_email(base_url, environment, generate_random_data_user):
    url_base = f"{base_url}/{environment}/users"

    user_a = generate_random_data_user
    requests.post(url_base, json=user_a)

    user_b = {
        "name": "User B",
        "email": fake.unique.email(),
        "age": 40,
    }
    requests.post(url_base, json=user_b)

    update_b = {
        "name": "User B Edited",
        "email": user_a["email"],  
        "age": 40,
    }

    url_b = f"{url_base}/{user_b['email']}"
    response = requests.put(url_b, json=update_b)

    assert response.status_code == 409
    dataJSON = response.json()
    validate(dataJSON, schema=ERROR_RESPONSE_SCHEMA)
    assert "already exists" in dataJSON["error"].lower()

def test_delete_user(base_url, environment, create_random_user_via_api, request):
    if environment == "prod":
        request.node.add_marker(
            pytest.mark.xfail(reason="BUG-004: DELETE auth broken in prod, returns 401 regardless of token")
        )

    email = create_random_user_via_api["email"]
    url = f"{base_url}/{environment}/users/{email}"
    headers = {"Authentication": "validtoken"}

    response = requests.delete(url, headers=headers)
    assert response.status_code == 204

def test_delete_user_unauthorized(base_url, environment, create_random_user_via_api, request):
    if environment == "dev":
        request.node.add_marker(
            pytest.mark.xfail(reason="BUG-004: dev does not enforce auth, DELETE succeeds without valid token")
        )

    email = create_random_user_via_api["email"]
    url = f"{base_url}/{environment}/users/{email}"

    response = requests.delete(url)   
    assert response.status_code == 401
    validate(response.json(), schema=ERROR_RESPONSE_SCHEMA)

def test_delete_user_not_found(base_url, environment, generate_random_data_user, request):
    if environment == "prod":
        request.node.add_marker(
            pytest.mark.xfail(
                reason="BUG-004: prod auth always returns 401, blocking the 404 not-found path")
        )

    email = generate_random_data_user["email"]   
    url = f"{base_url}/{environment}/users/{email}"
    headers = {"Authentication": "validtoken"}

    response = requests.delete(url, headers=headers)
    assert response.status_code == 404
    validate(response.json(), schema=ERROR_RESPONSE_SCHEMA)