"""
contact.py
----------
お問い合わせ内容の保存を担当するモジュール。
現時点では JSONL ファイルへ追記保存する（SMTP 等は未使用）。
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
INQUIRIES_FILE = DATA_DIR / "inquiries.jsonl"

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """メールアドレスの簡易チェック（入力がある場合のみ使用）"""
    return bool(EMAIL_PATTERN.match(email))


def save_inquiry(name: str, email: str, message: str, lang: str) -> None:
    """問い合わせを1件ファイルに追記する"""
    DATA_DIR.mkdir(exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "name": name.strip(),
        "email": email.strip(),
        "message": message.strip(),
        "lang": lang,
    }
    with open(INQUIRIES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
