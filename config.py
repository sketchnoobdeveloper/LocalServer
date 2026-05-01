"""কামপণ্ডিত বট - কনফিগারেশন লোডার

পরিবেশ ভেরিয়েবল থেকে সেটিংস লোড করে। সংবেদনশীল কোনো ডিফল্ট মান নেই।
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _parse_ids(raw: str | None) -> list[int]:
    if not raw:
        return []
    out: list[int] = []
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            out.append(int(chunk))
        except ValueError:
            continue
    return out


@dataclass
class Settings:
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    admin_ids: list[int] = field(
        default_factory=lambda: _parse_ids(os.getenv("ADMIN_IDS"))
    )
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "10000")))
    external_url: str = field(
        default_factory=lambda: os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
    )

    db_kind: str = field(default_factory=lambda: os.getenv("DB_KIND", "json").lower())
    json_path: str = field(default_factory=lambda: os.getenv("JSON_PATH", "data.json"))
    mongo_uri: str = field(default_factory=lambda: os.getenv("MONGO_URI", ""))
    mongo_db_name: str = field(
        default_factory=lambda: os.getenv("MONGO_DB_NAME", "kamponditbot")
    )
    firebase_url: str = field(default_factory=lambda: os.getenv("FIREBASE_URL", ""))
    firebase_credentials: str = field(
        default_factory=lambda: os.getenv("FIREBASE_CREDENTIALS", "")
    )

    google_ai_key: str = field(default_factory=lambda: os.getenv("GOOGLE_AI_KEY", ""))
    openrouter_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_KEY", ""))
    custom_ai_url: str = field(default_factory=lambda: os.getenv("CUSTOM_AI_URL", ""))
    custom_ai_key: str = field(default_factory=lambda: os.getenv("CUSTOM_AI_KEY", ""))
    custom_ai_model: str = field(
        default_factory=lambda: os.getenv("CUSTOM_AI_MODEL", "")
    )

    ghostweb_key: str = field(default_factory=lambda: os.getenv("GHOSTWEB_KEY", ""))

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @property
    def has_external_url(self) -> bool:
        return self.external_url.startswith("http")

    @property
    def webhook_url(self) -> str:
        if not self.has_external_url:
            return ""
        return f"{self.external_url}/telegram/{self.bot_token}"


settings = Settings()


def is_admin(user_id: int, extra_admins: list[int] | None = None) -> bool:
    if user_id in settings.admin_ids:
        return True
    if extra_admins and user_id in extra_admins:
        return True
    return False
