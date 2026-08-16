import os
from base64 import b64encode

from app import app


def _auth_header(username: str, password: str) -> dict:
    token = b64encode(f"{username}:{password}".encode()).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_basic_auth_disabled_without_password():
    app.config["TESTING"] = True
    env = os.environ.pop("BASIC_AUTH_PASS", None)
    try:
        with app.test_client() as client:
            assert client.get("/").status_code == 200
    finally:
        if env is not None:
            os.environ["BASIC_AUTH_PASS"] = env


def test_basic_auth_requires_credentials():
    app.config["TESTING"] = True
    os.environ["BASIC_AUTH_USER"] = "admin"
    os.environ["BASIC_AUTH_PASS"] = "test-secret"
    try:
        with app.test_client() as client:
            assert client.get("/").status_code == 401
            assert client.get("/", headers=_auth_header("admin", "wrong")).status_code == 401
            assert client.get("/", headers=_auth_header("admin", "test-secret")).status_code == 200
            assert client.get("/health").status_code == 200
    finally:
        os.environ.pop("BASIC_AUTH_USER", None)
        os.environ.pop("BASIC_AUTH_PASS", None)
