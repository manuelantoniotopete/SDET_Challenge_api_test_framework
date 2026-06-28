import os
import requests
import pytest


def test_get_all_users(base_url,environment):
    response = requests.get(f"{base_url}/{environment}/users")
    assert response.status_code == 200
