import os
import requests
import pytest
import logging

from tests.schemasAPI import USER_ARRAY_SCHEMA, USER_CREATE_USER, ERROR_RESPONSE_SCHEMA
from jsonschema  import validate

logger = logging.getLogger(__name__)

@pytest.mark.skip
def test_get_all_users(base_url,environment):
    response = requests.get(f"{base_url}/{environment}/users")
    dataJSON = response.json()
    assert response.status_code == 200
    validate(dataJSON, schema=USER_ARRAY_SCHEMA)

@pytest.mark.skip
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

@pytest.mark.xfail(reason="BUG: API returns 500 instead of 409 on duplicate email (violates contract), schema documentation says should return 409 when email is duplicated.")
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
