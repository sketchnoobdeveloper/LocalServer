"""কামপণ্ডিত বটের ডেটাবেজ স্তর।

ডিফল্ট backend = JSON। MongoDB ও Firebase optional।
সব backend একই API expose করে যাতে handler কোডে কোনো backend-specific
কোড না লিখতে হয়।

ডেটা মডেল (top-level keys):
    users        : {user_id: {...}}
    vip_orders   : {order_id: {...}}      # পেন্ডিং বা processed VIP order
    ebook_orders : {order_id: {...}}
    ebooks       : {ebook_id: {...}}
    settings     : {key: value}           # সব global config
    ai_channels  : {channel_id: {...}}    # টেলিগ্রাম চ্যানেল কনফিগ
    ai_fb_pages  : {page_id: {...}}       # ফেসবুক পেজ কনফিগ
    promos       : {promo_id: {...}}
    ui_texts     : {key: text}            # custom UI overrides
    menu_buttons : {key: label}
    payment      : [{method, number, ...}]
    public_links : {channel: ..., group: ...}
    help_items   : [...]
"""

from __future__ import annotations

import copy
import json
import logging
import os
import threading
import time
import uuid
from typing import Any

log = logging.getLogger(__name__)


DEFAULT_DOC: dict[str, Any] = {
    "users": {},
    "vip_orders": {},
    "ebook_orders": {},
    "ebooks": {},
    "settings": {
        "vip_plans": {
            "lifetime": {"name": "লাইফটাইম", "price": 249, "days": 36500},
            "yearly": {"name": "বার্ষিক", "price": 149, "days": 365},
            "monthly": {"name": "মাসিক", "price": 99, "days": 30},
        },
        "vip_links": {"lifetime": "", "yearly": "", "monthly": ""},
        "kick_targets": [],
        "auto_kick": True,
        "auto_post": False,
        "auto_react": False,
        "group_mode": False,
        "bot_enabled": True,
        "auto_promo": False,
        "promo_interval_min": 60,
        "post_interval_min": 30,
        "ai_role": "একজন অভিজ্ঞ বাংলা কনটেন্ট রাইটার",
        "text_ai_provider": "google",
        "text_ai_model": "gemini-2.5-flash",
        "image_ai_provider": "pollinations",
        "demo": "",
        "extra_admins": [],
    },
    "ai_channels": {},
    "ai_fb_pages": {},
    "promos": {},
    "ui_texts": {},
    "menu_buttons": {},
    "payment": [],
    "public_links": {"channel": "", "group": ""},
    "help_items": [],
    "prompt_history": {"current": "", "stack": [], "redo": []},
    "scheduled_messages": [],
}


def _now() -> int:
    return int(time.time())


def _new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def _deep_merge(base: dict, override: dict) -> dict:
    """`base` কে `override` দিয়ে recursive merge করে। `base` এ no-op."""
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Backend ইন্টারফেস
# ---------------------------------------------------------------------------


class _Backend:
    """Backend interface — সম্পূর্ণ doc load/save করতে হয়।"""

    def load(self) -> dict[str, Any]:  # pragma: no cover - abstract
        raise NotImplementedError

    def save(self, doc: dict[str, Any]) -> None:  # pragma: no cover - abstract
        raise NotImplementedError


class JsonBackend(_Backend):
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        if not os.path.exists(self.path):
            self.save(copy.deepcopy(DEFAULT_DOC))

    def load(self) -> dict[str, Any]:
        with self._lock:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return copy.deepcopy(DEFAULT_DOC)

    def save(self, doc: dict[str, Any]) -> None:
        with self._lock:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)


class MongoBackend(_Backend):
    """MongoDB backend। কেবল একটি ডকুমেন্ট ব্যবহার করে যাতে JSON এর সাথে সামঞ্জস্য থাকে।"""

    def __init__(self, uri: str, db_name: str):
        from pymongo import MongoClient  # type: ignore

        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.coll = self.client[db_name]["bot_state"]
        if not self.coll.find_one({"_id": "main"}):
            doc = copy.deepcopy(DEFAULT_DOC)
            doc["_id"] = "main"
            self.coll.insert_one(doc)

    def load(self) -> dict[str, Any]:
        doc = self.coll.find_one({"_id": "main"}) or copy.deepcopy(DEFAULT_DOC)
        doc.pop("_id", None)
        return doc

    def save(self, doc: dict[str, Any]) -> None:
        clean = {k: v for k, v in doc.items() if k != "_id"}
        self.coll.replace_one({"_id": "main"}, {"_id": "main", **clean}, upsert=True)


class FirebaseBackend(_Backend):
    def __init__(self, url: str, credentials_path: str | None = None):
        import firebase_admin  # type: ignore
        from firebase_admin import credentials, db  # type: ignore

        opts = {"databaseURL": url}
        if credentials_path and os.path.exists(credentials_path):
            cred = credentials.Certificate(credentials_path)
        else:
            cred = credentials.ApplicationDefault()
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, opts)
        self._db = db
        self._ref = db.reference("/bot_state")
        if not self._ref.get():
            self._ref.set(copy.deepcopy(DEFAULT_DOC))

    def load(self) -> dict[str, Any]:
        data = self._ref.get()
        if not data:
            return copy.deepcopy(DEFAULT_DOC)
        return data

    def save(self, doc: dict[str, Any]) -> None:
        self._ref.set(doc)


# ---------------------------------------------------------------------------
# Database — High level API
# ---------------------------------------------------------------------------


class Database:
    def __init__(self, backend: _Backend):
        self.backend = backend
        self._lock = threading.RLock()
        self._cache: dict[str, Any] | None = None

    # ---- core ----
    def _read(self) -> dict[str, Any]:
        if self._cache is None:
            raw = self.backend.load()
            self._cache = _deep_merge(DEFAULT_DOC, raw)
        return self._cache

    def _flush(self) -> None:
        if self._cache is not None:
            self.backend.save(self._cache)

    def reload(self) -> None:
        with self._lock:
            self._cache = None
            self._read()

    def export_all(self) -> dict[str, Any]:
        with self._lock:
            return copy.deepcopy(self._read())

    def import_all(self, doc: dict[str, Any]) -> None:
        with self._lock:
            self._cache = _deep_merge(DEFAULT_DOC, doc)
            self._flush()

    # ---- users ----
    def upsert_user(self, user_id: int, **fields) -> dict:
        with self._lock:
            d = self._read()
            uid = str(user_id)
            user = d["users"].get(uid, {"id": user_id, "joined": _now()})
            user.update(fields)
            d["users"][uid] = user
            self._flush()
            return user

    def get_user(self, user_id: int) -> dict | None:
        with self._lock:
            return self._read()["users"].get(str(user_id))

    def list_users(self) -> list[dict]:
        with self._lock:
            return list(self._read()["users"].values())

    def delete_user(self, user_id: int) -> bool:
        with self._lock:
            d = self._read()
            uid = str(user_id)
            if uid in d["users"]:
                del d["users"][uid]
                self._flush()
                return True
            return False

    def set_user_field(self, user_id: int, field: str, value: Any) -> None:
        with self._lock:
            d = self._read()
            uid = str(user_id)
            user = d["users"].setdefault(uid, {"id": user_id, "joined": _now()})
            user[field] = value
            self._flush()

    def is_banned(self, user_id: int) -> bool:
        u = self.get_user(user_id)
        return bool(u and u.get("banned"))

    # ---- vip ----
    def add_vip_order(self, user_id: int, plan_key: str, **extra) -> str:
        with self._lock:
            d = self._read()
            oid = _new_id("vip_")
            d["vip_orders"][oid] = {
                "id": oid,
                "user_id": user_id,
                "plan": plan_key,
                "status": "pending",
                "created": _now(),
                **extra,
            }
            self._flush()
            return oid

    def list_vip_orders(self, status: str | None = None) -> list[dict]:
        with self._lock:
            orders = list(self._read()["vip_orders"].values())
            if status:
                orders = [o for o in orders if o.get("status") == status]
            return orders

    def get_vip_order(self, order_id: str) -> dict | None:
        with self._lock:
            return self._read()["vip_orders"].get(order_id)

    def update_vip_order(self, order_id: str, **fields) -> dict | None:
        with self._lock:
            d = self._read()
            order = d["vip_orders"].get(order_id)
            if not order:
                return None
            order.update(fields)
            self._flush()
            return order

    def grant_vip(self, user_id: int, plan_key: str, days: int) -> dict:
        with self._lock:
            expiry = _now() + days * 86400
            return self.upsert_user(
                user_id,
                vip_plan=plan_key,
                vip_expiry=expiry,
                vip_started=_now(),
                vip_active=True,
                trial=False,
            )

    def grant_trial(self, user_id: int, seconds: int) -> dict:
        with self._lock:
            expiry = _now() + seconds
            return self.upsert_user(
                user_id,
                vip_plan="trial",
                vip_expiry=expiry,
                vip_started=_now(),
                vip_active=True,
                trial=True,
            )

    def revoke_vip(self, user_id: int) -> None:
        with self._lock:
            self.upsert_user(
                user_id, vip_active=False, trial=False, vip_plan=None
            )

    def list_active_vips(self) -> list[dict]:
        with self._lock:
            return [u for u in self.list_users() if u.get("vip_active")]

    # ---- ebooks ----
    def add_ebook(
        self,
        title: str,
        description: str,
        price: int,
        is_free: bool,
        file_id: str | None = None,
        link: str | None = None,
    ) -> str:
        with self._lock:
            d = self._read()
            eid = _new_id("eb_")
            d["ebooks"][eid] = {
                "id": eid,
                "title": title,
                "description": description,
                "price": price,
                "is_free": is_free,
                "file_id": file_id,
                "link": link,
                "active": True,
                "created": _now(),
                "downloads": 0,
            }
            self._flush()
            return eid

    def list_ebooks(self, active_only: bool = True) -> list[dict]:
        with self._lock:
            ebs = list(self._read()["ebooks"].values())
            if active_only:
                ebs = [e for e in ebs if e.get("active")]
            return ebs

    def get_ebook(self, eid: str) -> dict | None:
        with self._lock:
            return self._read()["ebooks"].get(eid)

    def update_ebook(self, eid: str, **fields) -> dict | None:
        with self._lock:
            d = self._read()
            eb = d["ebooks"].get(eid)
            if not eb:
                return None
            eb.update(fields)
            self._flush()
            return eb

    def delete_ebook(self, eid: str) -> bool:
        with self._lock:
            d = self._read()
            if eid in d["ebooks"]:
                del d["ebooks"][eid]
                self._flush()
                return True
            return False

    def add_ebook_order(self, user_id: int, ebook_id: str, **extra) -> str:
        with self._lock:
            d = self._read()
            oid = _new_id("ebo_")
            d["ebook_orders"][oid] = {
                "id": oid,
                "user_id": user_id,
                "ebook_id": ebook_id,
                "status": "pending",
                "created": _now(),
                **extra,
            }
            self._flush()
            return oid

    def list_ebook_orders(self, status: str | None = None) -> list[dict]:
        with self._lock:
            orders = list(self._read()["ebook_orders"].values())
            if status:
                orders = [o for o in orders if o.get("status") == status]
            return orders

    def update_ebook_order(self, order_id: str, **fields) -> dict | None:
        with self._lock:
            d = self._read()
            order = d["ebook_orders"].get(order_id)
            if not order:
                return None
            order.update(fields)
            self._flush()
            return order

    # ---- settings ----
    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._read()["settings"].get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        with self._lock:
            self._read()["settings"][key] = value
            self._flush()

    def update_settings(self, mapping: dict[str, Any]) -> None:
        with self._lock:
            self._read()["settings"].update(mapping)
            self._flush()

    # ---- ai channels & fb pages ----
    def add_ai_channel(
        self,
        chat_id: str,
        title: str = "",
        prompt: str = "",
        ai_provider: str = "",
        ai_model: str = "",
    ) -> str:
        with self._lock:
            d = self._read()
            d["ai_channels"][str(chat_id)] = {
                "id": str(chat_id),
                "title": title,
                "prompt": prompt,
                "ai_provider": ai_provider,
                "ai_model": ai_model,
                "enabled": True,
                "added": _now(),
            }
            self._flush()
            return str(chat_id)

    def list_ai_channels(self) -> list[dict]:
        with self._lock:
            return list(self._read()["ai_channels"].values())

    def update_ai_channel(self, chat_id: str, **fields) -> dict | None:
        with self._lock:
            d = self._read()
            ch = d["ai_channels"].get(str(chat_id))
            if not ch:
                return None
            ch.update(fields)
            self._flush()
            return ch

    def delete_ai_channel(self, chat_id: str) -> bool:
        with self._lock:
            d = self._read()
            if str(chat_id) in d["ai_channels"]:
                del d["ai_channels"][str(chat_id)]
                self._flush()
                return True
            return False

    def add_fb_page(
        self,
        page_id: str,
        title: str = "",
        prompt: str = "",
        access_token: str = "",
    ) -> str:
        with self._lock:
            d = self._read()
            d["ai_fb_pages"][str(page_id)] = {
                "id": str(page_id),
                "title": title,
                "prompt": prompt,
                "access_token": access_token,
                "enabled": True,
                "added": _now(),
            }
            self._flush()
            return str(page_id)

    def list_fb_pages(self) -> list[dict]:
        with self._lock:
            return list(self._read()["ai_fb_pages"].values())

    def delete_fb_page(self, page_id: str) -> bool:
        with self._lock:
            d = self._read()
            if str(page_id) in d["ai_fb_pages"]:
                del d["ai_fb_pages"][str(page_id)]
                self._flush()
                return True
            return False

    # ---- promos ----
    def add_promo(self, text: str, parse_mode: str = "HTML") -> str:
        with self._lock:
            d = self._read()
            pid = _new_id("pr_")
            d["promos"][pid] = {
                "id": pid,
                "text": text,
                "parse_mode": parse_mode,
                "created": _now(),
            }
            self._flush()
            return pid

    def list_promos(self) -> list[dict]:
        with self._lock:
            return list(self._read()["promos"].values())

    def delete_promo(self, pid: str) -> bool:
        with self._lock:
            d = self._read()
            if pid in d["promos"]:
                del d["promos"][pid]
                self._flush()
                return True
            return False

    # ---- ui texts / menu buttons ----
    def get_ui_text(self, key: str) -> str | None:
        with self._lock:
            v = self._read()["ui_texts"].get(key)
            return v if isinstance(v, str) else None

    def set_ui_text(self, key: str, text: str) -> None:
        with self._lock:
            self._read()["ui_texts"][key] = text
            self._flush()

    def get_menu_button(self, key: str) -> str | None:
        with self._lock:
            v = self._read()["menu_buttons"].get(key)
            return v if isinstance(v, str) else None

    def set_menu_button(self, key: str, label: str) -> None:
        with self._lock:
            self._read()["menu_buttons"][key] = label
            self._flush()

    # ---- payment ----
    def list_payment_methods(self) -> list[dict]:
        with self._lock:
            return list(self._read()["payment"])

    def add_payment_method(self, method: str, number: str, hint: str = "") -> None:
        with self._lock:
            d = self._read()
            d["payment"].append({"method": method, "number": number, "hint": hint})
            self._flush()

    def remove_payment_method(self, idx: int) -> bool:
        with self._lock:
            d = self._read()
            if 0 <= idx < len(d["payment"]):
                d["payment"].pop(idx)
                self._flush()
                return True
            return False

    # ---- public links ----
    def get_public_links(self) -> dict:
        with self._lock:
            return dict(self._read()["public_links"])

    def set_public_link(self, key: str, value: str) -> None:
        with self._lock:
            self._read()["public_links"][key] = value
            self._flush()

    # ---- help items ----
    def list_help_items(self) -> list[dict]:
        with self._lock:
            return list(self._read()["help_items"])

    def set_help_items(self, items: list[dict]) -> None:
        with self._lock:
            self._read()["help_items"] = items
            self._flush()

    # ---- prompt history ----
    def push_prompt(self, prompt: str) -> None:
        with self._lock:
            d = self._read()
            ph = d["prompt_history"]
            current = ph.get("current", "")
            stack = ph.setdefault("stack", [])
            if current:
                stack.append(current)
                # ১০ স্তর সীমা
                if len(stack) > 10:
                    stack.pop(0)
            ph["current"] = prompt
            ph["redo"] = []
            self._flush()

    def get_prompt(self) -> str:
        with self._lock:
            return self._read()["prompt_history"].get("current", "")

    def undo_prompt(self) -> str:
        with self._lock:
            d = self._read()
            ph = d["prompt_history"]
            stack = ph.setdefault("stack", [])
            if not stack:
                return ph.get("current", "")
            prev = stack.pop()
            redo = ph.setdefault("redo", [])
            if ph.get("current"):
                redo.append(ph["current"])
            ph["current"] = prev
            self._flush()
            return prev

    def redo_prompt(self) -> str:
        with self._lock:
            d = self._read()
            ph = d["prompt_history"]
            redo = ph.setdefault("redo", [])
            if not redo:
                return ph.get("current", "")
            nxt = redo.pop()
            stack = ph.setdefault("stack", [])
            if ph.get("current"):
                stack.append(ph["current"])
            ph["current"] = nxt
            self._flush()
            return nxt

    # ---- scheduled messages ----
    def add_scheduled_message(self, send_at: int, audience: str, text: str) -> str:
        with self._lock:
            d = self._read()
            mid = _new_id("sm_")
            d["scheduled_messages"].append(
                {"id": mid, "send_at": send_at, "audience": audience, "text": text}
            )
            self._flush()
            return mid

    def pop_due_scheduled_messages(self) -> list[dict]:
        with self._lock:
            d = self._read()
            now = _now()
            due = [m for m in d["scheduled_messages"] if m["send_at"] <= now]
            d["scheduled_messages"] = [
                m for m in d["scheduled_messages"] if m["send_at"] > now
            ]
            if due:
                self._flush()
            return due

    def list_scheduled_messages(self) -> list[dict]:
        with self._lock:
            return list(self._read()["scheduled_messages"])


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_database(settings) -> Database:
    kind = (settings.db_kind or "json").lower()
    log.info("Initializing database backend: %s", kind)
    if kind == "mongo" or kind == "mongodb":
        if not settings.mongo_uri:
            log.warning("MONGO_URI not set, falling back to JSON")
            return Database(JsonBackend(settings.json_path))
        try:
            return Database(
                MongoBackend(settings.mongo_uri, settings.mongo_db_name)
            )
        except Exception as e:  # pragma: no cover - depends on env
            log.error("Mongo init failed: %s — falling back to JSON", e)
            return Database(JsonBackend(settings.json_path))
    if kind == "firebase":
        if not settings.firebase_url:
            log.warning("FIREBASE_URL not set, falling back to JSON")
            return Database(JsonBackend(settings.json_path))
        try:
            return Database(
                FirebaseBackend(
                    settings.firebase_url, settings.firebase_credentials or None
                )
            )
        except Exception as e:  # pragma: no cover
            log.error("Firebase init failed: %s — falling back to JSON", e)
            return Database(JsonBackend(settings.json_path))
    return Database(JsonBackend(settings.json_path))
