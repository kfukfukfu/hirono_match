"""
i18n.py
-------
翻訳データ（JSON）の読み込みと、表示言語の判定を担当する。

・translations/ja.json … 日本語のUI文言
・translations/en.json … 英語のUI文言

テンプレートからは _( "nav.diagnosis" ) のようにドット区切りのキーで参照する。
"""

import json
from pathlib import Path

from flask import session

TRANSLATIONS_DIR = Path(__file__).parent / "translations"
DEFAULT_LANG = "ja"
SUPPORTED_LANGS = ("ja", "en")

_cache: dict[str, dict] = {}


def load_translations(lang: str) -> dict:
    """指定言語の JSON を読み込む（2回目以降はメモリから返す）"""
    if lang not in _cache:
        path = TRANSLATIONS_DIR / f"{lang}.json"
        with open(path, encoding="utf-8") as f:
            _cache[lang] = json.load(f)
    return _cache[lang]


def get_lang() -> str:
    """現在の表示言語を返す。未設定なら日本語。"""
    try:
        lang = session.get("lang", DEFAULT_LANG)
    except RuntimeError:
        return DEFAULT_LANG
    if lang not in SUPPORTED_LANGS:
        return DEFAULT_LANG
    return lang


def localize_row(row, fields: tuple[str, ...], lang: str | None = None) -> dict:
    """
    DBの1行を、表示言語に合わせた辞書に変換する。
    英語のときは name_en があれば name の代わりに使う。

    例: localize_row(spot, ("name", "description"))
    """
    lang = lang or get_lang()
    data = dict(row)
    if lang == "en":
        for field in fields:
            en_field = f"{field}_en"
            if data.get(en_field):
                data[field] = data[en_field]
    return data


def translate_value(key: str, lang: str | None = None):
    """
    翻訳キーから任意の値（文字列・リスト・辞書）を取得する。
    例: translate_value("index.empathy.items") → ["旅行先を探している", ...]
    """
    lang = lang or get_lang()
    data = load_translations(lang)
    value = data
    try:
        for part in key.split("."):
            value = value[part]
        return value
    except (KeyError, TypeError):
        return None


def translate(key: str, lang: str | None = None) -> str:
    """
    翻訳キーから文言を取得する。
    例: translate("nav.diagnosis") → "診断" または "Diagnosis"
    """
    lang = lang or get_lang()
    data = load_translations(lang)
    value = data
    try:
        for part in key.split("."):
            value = value[part]
        if not isinstance(value, str):
            return key
        return value
    except (KeyError, TypeError):
        return key
