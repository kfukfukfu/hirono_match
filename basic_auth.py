"""
basic_auth.py
-------------
Render 等の公開環境向け HTTP Basic 認証。
BASIC_AUTH_PASS が未設定のときは認証を無効化する（ローカル開発用）。
"""

import os
import secrets

from flask import Response

PUBLIC_PATHS = frozenset({"/health"})


def _credentials():
    password = os.environ.get("BASIC_AUTH_PASS")
    if not password:
        return None
    username = os.environ.get("BASIC_AUTH_USER", "admin")
    return username, password


def _unauthorized() -> Response:
    return Response(
        "Authentication required.\n",
        401,
        {"WWW-Authenticate": 'Basic realm="Hirono Match", charset="UTF-8"'},
    )


def _is_authorized(auth, username: str, password: str) -> bool:
    if auth is None or not auth.username or not auth.password:
        return False
    return secrets.compare_digest(auth.username, username) and secrets.compare_digest(
        auth.password, password
    )


def init_basic_auth(app) -> None:
    """Flask アプリに Basic 認証の before_request を登録する。"""

    @app.before_request
    def require_basic_auth():
        from flask import request

        if request.path in PUBLIC_PATHS:
            return None

        creds = _credentials()
        if creds is None:
            return None

        username, password = creds
        if _is_authorized(request.authorization, username, password):
            return None
        return _unauthorized()
