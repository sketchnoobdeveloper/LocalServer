"""APScheduler-based পর্যায়কালীন কাজ।

জব:
  - trial_check (প্রতি 1 মিনিটে): ট্রায়াল মেয়াদ শেষ হলে kick + notify
  - vip_check (প্রতি 30 মিনিটে): VIP মেয়াদ শেষ হলে kick + notify
  - auto_post (post_interval_min মিনিট পর পর): AI পোস্ট
  - auto_promo (promo_interval_min মিনিট পর পর): প্রমো বার্তা
  - scheduled_messages (প্রতি মিনিটে): scheduled broadcast deliver
"""

from __future__ import annotations

import asyncio
import logging
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.constants import ParseMode

from auto_post import run_auto_post_cycle, run_promo_cycle
from strings_bn import t

log = logging.getLogger(__name__)


async def _kick_user(bot: Bot, chat_id: str | int, user_id: int) -> bool:
    """চ্যানেল/গ্রুপ থেকে kick = ban + unban (immediate)।"""
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await asyncio.sleep(1)
        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except Exception as e:  # noqa: BLE001
        log.warning("Kick failed user=%s chat=%s err=%s", user_id, chat_id, e)
        return False


async def _expire_user(bot: Bot, db, user: dict, *, is_trial: bool) -> None:
    user_id = user["id"]
    db.revoke_vip(user_id)
    if db.get_setting("auto_kick", True):
        targets = db.get_setting("kick_targets", [])
        # যদি configured না থাকে, VIP লিংক থেকে guess করার চেষ্টা না করে স্কিপ
        for target in targets:
            await _kick_user(bot, target, user_id)
    msg = t("vip_expired_msg", db)
    try:
        await bot.send_message(chat_id=user_id, text=msg, parse_mode=ParseMode.HTML)
    except Exception:  # noqa: BLE001
        pass


async def trial_check_job(bot: Bot, db) -> None:
    now = int(time.time())
    for user in db.list_active_vips():
        if not user.get("trial"):
            continue
        if user.get("vip_expiry", 0) <= now:
            log.info("Expiring trial user %s", user.get("id"))
            await _expire_user(bot, db, user, is_trial=True)


async def vip_check_job(bot: Bot, db) -> None:
    now = int(time.time())
    for user in db.list_active_vips():
        if user.get("trial"):
            continue
        expiry = user.get("vip_expiry", 0)
        if expiry <= now:
            log.info("Expiring VIP user %s", user.get("id"))
            await _expire_user(bot, db, user, is_trial=False)
        elif expiry - now <= 86400 * 2 and not user.get("expiry_warned"):
            try:
                await bot.send_message(
                    chat_id=user["id"],
                    text=t("vip_expiring_soon", db, days=2),
                    parse_mode=ParseMode.HTML,
                )
                db.set_user_field(user["id"], "expiry_warned", True)
            except Exception:  # noqa: BLE001
                pass


async def auto_post_job(bot: Bot, settings, db) -> None:
    try:
        sent = await run_auto_post_cycle(bot, settings=settings, db=db)
        if sent:
            log.info("Auto-posted to %d channels", sent)
    except Exception as e:  # noqa: BLE001
        log.error("auto_post_job error: %s", e)


async def promo_job(bot: Bot, db) -> None:
    try:
        sent = await run_promo_cycle(bot, db=db)
        if sent:
            log.info("Promo sent to %d channels", sent)
    except Exception as e:  # noqa: BLE001
        log.error("promo_job error: %s", e)


async def scheduled_messages_job(bot: Bot, db) -> None:
    due = db.pop_due_scheduled_messages()
    if not due:
        return
    for msg in due:
        audience = msg.get("audience", "all")
        text = msg.get("text", "")
        users = db.list_users()
        if audience == "vip":
            users = [u for u in users if u.get("vip_active")]
        elif audience.startswith("user:"):
            try:
                uid = int(audience.split(":", 1)[1])
                users = [u for u in users if u.get("id") == uid]
            except (ValueError, IndexError):
                users = []
        for u in users:
            try:
                await bot.send_message(
                    chat_id=u["id"], text=text, parse_mode=ParseMode.HTML
                )
            except Exception:  # noqa: BLE001
                continue


def start_scheduler(bot: Bot, settings, db) -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone="Asia/Dhaka")
    sched.add_job(trial_check_job, "interval", minutes=1, args=[bot, db], id="trial")
    sched.add_job(vip_check_job, "interval", minutes=30, args=[bot, db], id="vip")
    sched.add_job(
        scheduled_messages_job, "interval", minutes=1, args=[bot, db], id="sched_msgs"
    )
    post_interval = max(int(db.get_setting("post_interval_min", 30) or 30), 1)
    sched.add_job(
        auto_post_job,
        "interval",
        minutes=post_interval,
        args=[bot, settings, db],
        id="ai_post",
    )
    promo_interval = max(int(db.get_setting("promo_interval_min", 60) or 60), 1)
    sched.add_job(
        promo_job, "interval", minutes=promo_interval, args=[bot, db], id="promo"
    )
    sched.start()
    log.info(
        "Scheduler started (post=%dm, promo=%dm)", post_interval, promo_interval
    )
    return sched
