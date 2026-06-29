# Bug Report — User Management API

This document will be used as a list of all the defects (bugs) founds while the project is building and running the automated test suite against the document sdet_challenge_api.yml
Each bug represent cases where the API's behavior do not match as sdet_challenge_api.yml say.

## BUG-001 — POST /users returns 500 instead of 409 on duplicate email
When creating a user with an email that already exists, the API returns
`500 Internal Server Error` instead of the `409 Conflict` defined in the sdet_challenge_api.yml.

**Steps to reproduce:**
1- create a random user successfully or you can get one if there are users created.
2- get email created
3- Try to create a new user using the same email

**Expected:** `409 Conflict` with an `ErrorResponse` body.
**Actual:** `500 Internal Server Error` with `{"error": "Internal server error"}`.

**Evidence:** Automated test `test_valid_duplicate_email_user` + manual reproduction in Postman.

![Postman 500 on duplicate email](evidence/SSEvidence001.png)
![Terminal result test case executed](evidence/SSEvidence002.png)

## BUG-002 — POST /users accept invalid email format
When creating a user with malformed email format, the API documentation say should be
rejected with `400 Validation error`. Instead, the API accepts an email without
an `@` symbol and creates the user, returning `201 Created`.

**Steps to reproduce:**
1- Send `POST /users` with body `{"name": "manuel test", "age": 4, "email": "email2test.com"}`.

**Expected:** `400 Validation error` with an `ErrorResponse` body.
**Actual:** `201 Created` user created with an invalid email.

**Evidence:** Automated test `test_create_user_invalid_return_400` + manual reproduction in Postman.

![Postman 201 on malformed email format](evidence/SSEvidence003.png)
![Postman get all users and there is user with not email format](evidence/SSEvidence004.png)

## BUG-003 — GET /users/{email} returns 500 instead of 404 according API documentation for non-existent users
According API documentation difne when endpoint `GET /users/{email}` is executed with an email that does not exist, 
should return `404 Not Found`with an `ErrorResponse` body. Instead, the API returns
`500 Internal Server Error`.

**Steps to reproduce:**
1- Send `GET /users/{email}` with email does not exist. (example. definitely_does_not_exist_12345@nowhere.com)

**Expected:** `404 Not Found` with an `ErrorResponse` body.
**Actual:** `500 Internal Server Error` with `{"error": "Internal server error"}`.

**Evidence:** Automated test `test_get_user_not_found` + manual reproduction in Postman.

![Postman get 500](evidence/SSEvidence005.png)



