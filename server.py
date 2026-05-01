"""aiohttp ভিত্তিক হেলথ ও Telegram webhook server।

Render এ deploy করার জন্য `/`, `/ping`, `/health`, `/status` endpoint
এবং একটি Telegram webhook endpoint expose করে। Webhook URL টোকেন-suffixed,
যাতে কেউ guess করতে না পারে।
"""

from __future__ import annotations

import json
import logging
from typing import Awaitable, Callable

from aiohttp import web
from telegram import Update

log = logging.getLogger(__name__)


def build_app(
    *,
    application,
    bot_token: str,
    webhook_handler: Callable[[Update], Awaitable[None]] | None = None,
) -> web.Application:
    app = web.Application()

    async def root(_request: web.Request) -> web.Response:
        return web.Response(text="OK")

    async def ping(_request: web.Request) -> web.Response:
        return web.Response(text="OK")

    async def status(_request: web.Request) -> web.Response:
        bot_info = "bot"
        try:
            me = await application.bot.get_me()
            bot_info = f"@{me.username}"
        except Exception:  # noqa: BLE001
            pass
        body = {
            "status": "OK",
            "bot": bot_info,
            "running": True,
        }
        return web.Response(text=json.dumps(body), content_type="application/json")

    async def telegram_webhook(request: web.Request) -> web.Response:
        try:
            data = await request.json()
        except Exception:  # noqa: BLE001
            return web.Response(status=400, text="bad request")
        update = Update.de_json(data, application.bot)
        if update is None:
            return web.Response(status=400, text="bad update")
        await application.process_update(update)
        return web.Response(text="OK")

    app.router.add_get("/", root)
    app.router.add_get("/ping", ping)
    app.router.add_get("/health", ping)
    app.router.add_get("/status", status)
    app.router.add_post(f"/telegram/{bot_token}", telegram_webhook)
    return app
