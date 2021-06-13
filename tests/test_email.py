import os

import flask_login

import lada.email
import tests.utils

from functools import partial

from tests.fixtures import *

TEST_EMAIL_FLAG_NAME = "TEST_EMAIL"

TEST_EMAIL = os.getenv(TEST_EMAIL_FLAG_NAME, None)
TEST_EMAIL_SKIP_REASON = f"To test email set {TEST_EMAIL_FLAG_NAME} environment variable"

skip_if_test_email_not_set = partial(pytest.mark.skipif, TEST_EMAIL is None, reason=TEST_EMAIL_SKIP_REASON)


def test_recipient_processing(admin):
    assert lada.email.process_recipient(admin) == (f"{admin.email}", admin.email)
    assert lada.email.process_recipient("test@example.com") == "test@example.com"


@skip_if_test_email_not_set()
def test_registration_email(client, feature_flags):
    feature_flags.enable(FEATURE_EMAIL_VERIFICATION)
    feature_flags.disable(FEATURE_MULTITHREADING)

    password = "password"

    data = {
        "email": TEST_EMAIL,
        "password": password,
        "repassword": password,
    }

    client.post("/fellow/register", data=data)

    tests.utils.web_login(client, email=TEST_EMAIL, password=password)

    current_user = flask_login.current_user
    assert current_user.email == TEST_EMAIL
    assert not current_user.verified
