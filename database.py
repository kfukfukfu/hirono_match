"""
database.py
-----------
SQLite データベースへの接続を管理するモジュール。
Flask アプリ全体から共通で使う DB 接続関数を提供する。
"""

import sqlite3
from pathlib import Path

# プロジェクト直下の hirono_match.db を使う
DB_PATH = Path(__file__).parent / "hirono_match.db"


def get_db():
    """データベース接続を取得する。行は辞書形式で返る。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
