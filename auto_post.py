"""AI অটো-পোস্ট ও প্রমো ডেলিভারি লজিক।"""

from __future__ import annotations

import io
import logging
import random

from telegram import Bot, InputFile
from telegram.constants import ParseMode

from ai_providers import generate_image, generate_text
from utils import truncate

log = logging.getLogger(__name__)


def _select_prompt(channel: dict, db) -> str:
    """চ্যানেল-নির্দিষ্ট prompt না থাকলে গ্লোবাল prompt ব্যবহার করে।
    মাল্টি-টপিক হলে এলোমেলোভাবে একটি বেছে নেয়।"""
    p = channel.get("prompt") or db.get_prompt() or "একটি অনুপ্রেরণামূলক বাংলা পোস্ট লেখো।"
    if "\n---\n" in p:
        topics = [t.strip() for t in p.split("\n---\n") if t.strip()]
        if topics:
            return random.choice(topics)
    return p


async def post_to_channel(
    bot: Bot, channel: dict, *, settings, db, content_link: str = ""
) -> bool:
    """একটি চ্যানেলে AI-জেনারেটেড পোস্ট পাঠায়।"""
    prompt = _select_prompt(channel, db)
    try:
        text = await generate_text(
            prompt,
            settings=settings,
            db=db,
            provider_override=channel.get("ai_provider") or None,
            model_override=channel.get("ai_model") or None,
        )
    except Exception as e:  # noqa: BLE001
        log.error("Text generation failed for %s: %s", channel.get("id"), e)
        return False

    if content_link:
        text = f"{text}\n\n🔗 {content_link}"
    text = truncate(text, 3500)

    image_bytes = await generate_image(prompt, settings=settings, db=db)

    chat_id = channel["id"]
    try:
        if image_bytes:
            await bot.send_photo(
                chat_id=chat_id,
                photo=InputFile(io.BytesIO(image_bytes), filename="post.png"),
                caption=text,
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id=chat_id, text=text, parse_mode=ParseMode.HTML
            )
        return True
    except Exception as e:  # noqa: BLE001
        log.error("Send to %s failed: %s", chat_id, e)
        return False


async def run_auto_post_cycle(bot: Bot, *, settings, db) -> int:
    """সব সক্রিয় চ্যানেলে একটি করে পোস্ট পাঠায়। পাঠানো পোস্টের সংখ্যা return করে।"""
    if not db.get_setting("auto_post", False):
        return 0
    channels = [c for c in db.list_ai_channels() if c.get("enabled")]
    sent = 0
    for ch in channels:
        ok = await post_to_channel(bot, ch, settings=settings, db=db)
        if ok:
            sent += 1
    return sent


async def run_promo_cycle(bot: Bot, *, db) -> int:
    if not db.get_setting("auto_promo", False):
        return 0
    promos = db.list_promos()
    if not promos:
        return 0
    promo = random.choice(promos)
    channels = [c for c in db.list_ai_channels() if c.get("enabled")]
    sent = 0
    for ch in channels:
        try:
            await bot.send_message(
                chat_id=ch["id"],
                text=promo["text"],
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
            sent += 1
        except Exception as e:  # noqa: BLE001
            log.warning("Promo send failed to %s: %s", ch["id"], e)
    return sent
