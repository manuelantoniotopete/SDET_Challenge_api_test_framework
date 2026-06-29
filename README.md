# SDET Challenge — User Management API Test Framework

End-to-end API test suite for the User Management API, built with Python and pytest.
The suite runs against both dev and prod environments and is automated through
GitHub Actions.

The API under test is a RESTful service for managing users, scoped by environment.
All requests are prefixed with the environment name (/dev/users, /prod/users).
The authoritative source for expected behavior is the OpenAPI spec
(sdet_challenge_api.yml).

## Tech Stack
* Language: Python 3.12
* Test runner: pytest
* HTTP client: requests
* Schema validation: jsonschema
* Test data: Faker
* Reporting: pytest-html
* CI/CD: GitHub Actions

## Prerequisites
* Docker installed and running
* Python 3.12+

## Running the API

The API is provided as a Docker image. Start it with:
```bash
docker run -p 3000:3000 ghcr.io/danielsilva-loanpro/sdet-interview-challenge:latest
```
The application will be available at http://localhost:3000.

## Verify it is running:

```bash
curl http://localhost:3000/dev/users
```
You should get a JSON array (empty if no users have been created yet).

## Setup

Clone the repo and install dependencies:
```bash
git clone https://github.com/manuelantoniotopete/SDET_Challenge_api_test_framework.git
cd SDET_Challenge_api_test_framework
```
```bash
python -m venv .venv
```
## Windows
```bash
.\.venv\Scripts\Activate.ps1
```
## macOS / Linux
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```
## Running the Tests

Make sure the API container is running first.

Run the full suite (both environments):
```bash
pytest
```
Run only one environment:
```bash
pytest -k "dev"
pytest -k "prod"
```
Generate an HTML report:
```bash
pytest --html=report.html --self-contained-html
```
The base URL can be overridden with the API_BASE_URL environment variable
(defaults to http://localhost:3000). This is what the CI pipeline uses.

## Project Structure
```
.
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions pipeline (dev + prod)
├── evidence/                  # Screenshots backing the bug report
├── tests/
│   ├── api/
│   │   └── users/
│   │       └── test_users.py  # Test suite for the users endpoints
│   ├── conftest.py            # Fixtures (base_url, environment, data, auth)
│   └── schemasAPI.py          # JSON schemas used for contract validation
├── BUGS.md                    # Documented defects
├── README.md
├── pytest.ini                 # pytest config (pythonpath, logging, xfail_strict)
└── requirements.txt
```
## Test Coverage

The suite covers every endpoint in the spec, across both environments:
```
Endpoint                       Cases covered
GET /users200                   (list users)
POST /users201                  (create), 400 (validation), 409 (duplicate email)
GET /users/{email}200           (found), 404 (not found)PUT /users/{email}200 (update), 400 (validation), 404 (not found), 409 (duplicate email)
DELETE /users/{email}204        (deleted), 401 (unauthorized), 404 (not found)
```
Each test validates the response status code, the response body against a JSON
schema, and the relevant business rules (e.g. that a created/updated user matches
the data sent).

The environment fixture is parametrized over dev and prod, so every test
runs once per environment.

## CI/CD Pipeline

The pipeline (.github/workflows/tests.yml) runs on every push and pull request
to master. It:

* Spins up the API container from GHCR as a service on localhost:3000.
* Waits for the API to be ready before running anything.
* Runs the suite against dev and prod as two separate jobs in parallel.
* Uploads an HTML report per environment as a build artifact.

The two environments run independently (fail-fast: false), so a failure in one
does not block the other, as required by the challenge.

## Where to find the reports

Each pipeline run uploads report-dev and report-prod as artifacts. To view them:
Actions tab → select the run → Artifacts section (bottom of the page) → download
and open the HTML.

## Bugs Found

While building the suite I found several cases where the API does not match the
spec. They are documented in detail in BUGS.md.

Tests that expose known bugs are marked as xfail (with xfail_strict = true),
so the suite stays green while still documenting the defects. If a bug ever gets
fixed, the strict xfail turns the test red to flag that it should be updated.

A short summary:
```
ID                    Endpoint                    Issue
BUG-001             POST/users              Returns 500 instead of 409 on duplicate email
BUG-002             POST/users              Accepts invalid email format (201 instead of 400)
BUG-003             GET/users/{email}       Returns 500 instead of 404 for a non-existent user
BUG-004             DELETE/users/{email}    Authentication not enforced in dev (succeeds without a valid token), unlike prod
```
## Notes / patterns

A couple of observations beyond the individual bugs:

Inconsistent behavior between endpoints. PUT /users/{email} handles invalid
email, non-existent users, and duplicate emails correctly (400 / 404 / 409),
while POST and GET fail on the equivalent cases. The correct handling exists
in the system but is not applied at the same apis.
Inconsistent behavior between environments. The spec states dev and prod
behave identically, but DELETE authentication is enforced in prod and not in
dev