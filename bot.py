"""কামপণ্ডিত বট — entry point।

Render-friendly: webhook + aiohttp health server একসাথে চালায়। Local এ
RENDER_EXTERNAL_URL সেট না থাকলে polling মোডে fallback করে এবং তখনও
aiohttp server চালু থাকে।

ENV ভেরিয়েবল:
    BOT_TOKEN          (required)
    ADMIN_IDS          কমা-সেপারেটেড অ্যাডমিন ইউজার ID
    PORT               default 10000
    RENDER_EXTERNAL_URL Render এ deploy এর সময় public URL
    DB_KIND            json | mongo | firebase  (default json)
    GOOGLE_AI_KEY      Gemini এর জন্য
    OPENROUTER_KEY     OpenRouter এর জন্য
    GHOSTWEB_KEY       GhostWeb image API key
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys

from aiohttp import web
from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import settings
from database import build_database
from handlers_admin import (
    cmd_addadmin,
    cmd_addchannel,
    cmd_addebook,
    cmd_addfb,
    cmd_addhelp,
    cmd_addkick,
    cmd_addpay,
    cmd_addpromo,
    cmd_admin,
    cmd_clearhelp,
    cmd_delchannel,
    cmd_deladmin,
    cmd_delebook,
    cmd_delfb,
    cmd_delkick,
    cmd_delpay,
    cmd_delpromo,
    cmd_editebook,
    cmd_promointv,
    cmd_sendpromo,
    cmd_setbtn,
    cmd_setchprompt,
    cmd_setpublic,
    cmd_setplan,
    cmd_setui,
    cmd_setviplink,
    on_admin_callback,
    on_admin_document,
    on_admin_ebook_file,
    on_admin_message,
    on_manual_vip_callback,
)
from handlers_user import (
    cmd_help,
    cmd_id,
    cmd_menu,
    cmd_start,
    on_user_callback,
    on_user_message,
)
from scheduler import start_scheduler
from server import build_app


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)


log = logging.getLogger("kampondit")


# ---------------------------------------------------------------------------
# Combined message dispatcher (admin states win over user states)
# ---------------------------------------------------------------------------


async def _on_any_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if await on_admin_ebook_file(update, context):
        return
    if await on_admin_document(update, context):
        return
    if await on_admin_message(update, context):
        return
    await on_user_message(update, context)


async def _on_any_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    data = (update.callback_query.data if update.callback_query else "") or ""
    if data.startswith("adm:vip:manual_plan:"):
        await on_manual_vip_callback(update, context)
        return
    if data.startswith("adm:"):
        await on_admin_callback(update, context)
        return
    if data.startswith("user:"):
        await on_user_callback(update, context)


# ---------------------------------------------------------------------------
# Auto-react on new channel posts
# ---------------------------------------------------------------------------


REACT_EMOJIS = ["👍", "🔥", "❤️", "💯", "🤩", "🥰", "👏"]


async def _on_channel_post(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    db = context.bot_data.get("db")
    if not db or not db.get_setting("auto_react", False):
        return
    msg = update.channel_post
    if not msg:
        return
    import random

    emoji = random.choice(REACT_EMOJIS)
    try:
        # PTB v21 supports set_message_reaction
        await context.bot.set_message_reaction(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            reaction=[{"type": "emoji", "emoji": emoji}],
        )
    except Exception as e:  # noqa: BLE001
        log.debug("auto-react failed: %s", e)


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("menu", cmd_menu))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("id", cmd_id))
    application.add_handler(CommandHandler("admin", cmd_admin))

    # Admin commands
    for name, fn in [
        ("setviplink", cmd_setviplink),
        ("setplan", cmd_setplan),
        ("setpublic", cmd_setpublic),
        ("addpay", cmd_addpay),
        ("delpay", cmd_delpay),
        ("addadmin", cmd_addadmin),
        ("deladmin", cmd_deladmin),
        ("addchannel", cmd_addchannel),
        ("delchannel", cmd_delchannel),
        ("setchprompt", cmd_setchprompt),
        ("addfb", cmd_addfb),
        ("delfb", cmd_delfb),
        ("addpromo", cmd_addpromo),
        ("delpromo", cmd_delpromo),
        ("sendpromo", cmd_sendpromo),
        ("promointv", cmd_promointv),
        ("addkick", cmd_addkick),
        ("delkick", cmd_delkick),
        ("setui", cmd_setui),
        ("setbtn", cmd_setbtn),
        ("addhelp", cmd_addhelp),
        ("clearhelp", cmd_clearhelp),
        ("addebook", cmd_addebook),
        ("editebook", cmd_editebook),
        ("delebook", cmd_delebook),
    ]:
        application.add_handler(CommandHandler(name, fn))

    application.add_handler(CallbackQueryHandler(_on_any_callback))
    application.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.Document.ALL | filters.VIDEO)
            & ~filters.COMMAND,
            _on_any_message,
        )
    )
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, _on_channel_post))


# ---------------------------------------------------------------------------
# Run modes
# ---------------------------------------------------------------------------


async def _run_webhook(application: Application, db) -> None:
    app = build_app(application=application, bot_token=settings.bot_token)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.port)
    await site.start()
    log.info("aiohttp server listening on :%d", settings.port)

    if settings.has_external_url:
        url = settings.webhook_url
        log.info("Setting Telegram webhook: %s", url)
        try:
            await application.bot.set_webhook(
                url=url, allowed_updates=Update.ALL_TYPES, drop_pending_updates=True
            )
        except Exception as e:  # noqa: BLE001
            log.error("set_webhook failed: %s", e)

    sched = start_scheduler(application.bot, settings, db)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _signal_handler(*_):
        log.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    try:
        await stop_event.wait()
    finally:
        log.info("Stopping...")
        try:
            sched.shutdown(wait=False)
        except Exception:  # noqa: BLE001
            pass
        try:
            await application.bot.delete_webhook()
        except Exception:  # noqa: BLE001
            pass
        await runner.cleanup()


async def _run_polling(application: Application, db) -> None:
    """Local দেব / Render এ external URL সেট না থাকলে।"""
    app = build_app(application=application, bot_token=settings.bot_token)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", settings.port)
    await site.start()
    log.info("aiohttp server listening on :%d (polling mode)", settings.port)

    sched = start_scheduler(application.bot, settings, db)
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
    except Exception:  # noqa: BLE001
        pass
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _signal_handler(*_):
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass
    try:
        await stop_event.wait()
    finally:
        try:
            sched.shutdown(wait=False)
        except Exception:  # noqa: BLE001
            pass
        await application.updater.stop()
        await runner.cleanup()


async def main() -> None:
    _setup_logging(settings.log_level)
    if not settings.bot_token:
        log.error("BOT_TOKEN env var অনুপস্থিত")
        sys.exit(1)
    if not settings.admin_ids:
        log.warning(
            "ADMIN_IDS সেট নেই — কোনো অ্যাডমিন কমান্ড কাজ করবে না যতক্ষণ"
            " ADMIN_IDS env var দেওয়া হবে।"
        )

    db = build_database(settings)

    application = (
        Application.builder()
        .token(settings.bot_token)
        .rate_limiter(AIORateLimiter())
        .build()
    )
    application.bot_data["db"] = db
    register_handlers(application)

    await application.initialize()
    await application.start()

    try:
        if settings.has_external_url:
            await _run_webhook(application, db)
        else:
            await _run_polling(application, db)
    finally:
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
