"""সাধারণ helper ফাংশন।"""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone, timedelta

DHAKA = timezone(timedelta(hours=6))


def now_ts() -> int:
    return int(time.time())


def fmt_ts(ts: int | None) -> str:
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(ts, DHAKA).strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return "—"


def fmt_remaining(ts: int | None) -> str:
    if not ts:
        return "—"
    remaining = ts - now_ts()
    if remaining <= 0:
        return "মেয়াদ শেষ"
    days, rem = divmod(remaining, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days:
        return f"{days} দিন {hours} ঘণ্টা"
    if hours:
        return f"{hours} ঘণ্টা {minutes} মিনিট"
    return f"{minutes} মিনিট"


_HTML_ALLOWED = re.compile(
    r"</?(b|i|u|s|code|pre|blockquote|tg-spoiler|a)(\s[^>]*)?>", re.I
)


def sanitize_html(text: str) -> str:
    """নিষিদ্ধ ক্যারেক্টার (#, **, _ as decorative dash) সরিয়ে দেয়।"""
    if not text:
        return ""
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = text.replace("**", "")
    text = re.sub(r"(?<![a-zA-Z0-9])_(?![a-zA-Z0-9])", "", text)
    return text


def parse_duration(s: str) -> int | None:
    """`5m`, `7d`, `2h`, `30s` ইত্যাদি -> সেকেন্ড।"""
    if not s:
        return None
    s = s.strip().lower()
    m = re.match(r"^(\d+)\s*([smhd]?)$", s)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2) or "m"
    return n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]


def safe_int(value, default: int | None = None) -> int | None:
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return default


def chunked(items, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
