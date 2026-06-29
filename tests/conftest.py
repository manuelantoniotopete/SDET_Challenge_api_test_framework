import os
import pytest
import requests

import random
from faker import Faker
fake = Faker()

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3000")
VALID_ENVS = ("dev", "prod")


@pytest.fixture(params=VALID_ENVS)
def environment(request):
    env = request.param
    if env not in VALID_ENVS:
        pytest.fail(f"Invalid environment: '{env}'. Please choose: {VALID_ENVS}")
    return env
    
@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def generate_random_data_user():
    random_data_user = {
         "name": fake.name(),
        "email": fake.unique.email(),
        "age": random.randint(1, 150),
    }
    return random_data_user

@pytest.fixture
def create_random_user_via_api(base_url, environment, generate_random_data_user):
    url = f"{base_url}/{environment}/users"
    response = requests.post(url, json=generate_random_data_user)
    assert response.status_code == 201
    return generate_random_data_user

@pytest.fixture
def auth_headers():
    return {"Authentication": "mysecrettoken"}
