"""ইউজার-ফেসিং সব handler।"""

from __future__ import annotations

import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import is_admin, settings
from keyboards import (
    back_kb,
    ebook_list_kb,
    main_menu_kb,
    vip_plans_kb,
)
from strings_bn import b, t
from utils import fmt_remaining, fmt_ts

log = logging.getLogger(__name__)


def _user_extra_admins(db) -> list[int]:
    return [int(x) for x in db.get_setting("extra_admins", []) if str(x).isdigit() or isinstance(x, int)]


async def _bot_blocked_for_user(update: Update, db) -> bool:
    user = update.effective_user
    if user is None:
        return True
    if not db.get_setting("bot_enabled", True):
        if is_admin(user.id, _user_extra_admins(db)):
            return False
        await _send(update, t("bot_disabled", db))
        return True
    if db.is_banned(user.id):
        await _send(update, t("banned_user", db))
        return True
    return False


async def _send(update: Update, text: str, **kwargs) -> None:
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=text, parse_mode=ParseMode.HTML, **kwargs
            )
            return
        except Exception:  # noqa: BLE001
            pass
    if update.effective_message:
        await update.effective_message.reply_text(
            text=text, parse_mode=ParseMode.HTML, **kwargs
        )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    user = update.effective_user
    if user is None:
        return
    db.upsert_user(
        user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        last_seen=int(__import__("time").time()),
    )
    if await _bot_blocked_for_user(update, db):
        return
    await _send(
        update,
        t("welcome", db),
        reply_markup=main_menu_kb(db),
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await cmd_start(update, context)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    items = db.list_help_items()
    if not items:
        text = (
            "ℹ️ সাহায্য\n\n"
            "/start — মেনু খুলুন\n"
            "/account — আপনার অ্যাকাউন্ট দেখুন\n"
            "/admin — অ্যাডমিন প্যানেল (শুধু অ্যাডমিনদের জন্য)\n"
        )
    else:
        text = "ℹ️ <b>সাহায্য</b>\n\n" + "\n\n".join(
            f"<b>{i.get('title', '')}</b>\n{i.get('text', '')}" for i in items
        )
    await _send(update, text)


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    text = (
        f"🆔 আপনার ID: <code>{user.id if user else '—'}</code>\n"
        f"💬 চ্যাট ID: <code>{chat.id if chat else '—'}</code>"
    )
    await _send(update, text)


async def on_user_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    db = context.bot_data["db"]
    query = update.callback_query
    if query is None:
        return
    await query.answer()
    if await _bot_blocked_for_user(update, db):
        return
    data = query.data or ""
    if data == "user:menu":
        await _send(update, t("welcome", db), reply_markup=main_menu_kb(db))
    elif data == "user:vip":
        await _send(update, t("vip_intro", db), reply_markup=vip_plans_kb(db))
    elif data.startswith("user:vip:plan:"):
        plan_key = data.rsplit(":", 1)[1]
        await _show_payment(update, context, plan_key)
    elif data == "user:ebooks":
        await _show_ebooks(update, context)
    elif data.startswith("user:eb:"):
        eid = data.split(":", 2)[2]
        await _handle_ebook(update, context, eid)
    elif data == "user:support":
        context.user_data["awaiting_support"] = True
        await _send(update, t("support_text", db), reply_markup=back_kb(db))
    elif data == "user:demo":
        demo = db.get_setting("demo", "") or t("demo_default", db)
        await _send(update, demo, reply_markup=back_kb(db))
    elif data == "user:public":
        links = db.get_public_links()
        parts = []
        if links.get("channel"):
            parts.append(f"📢 চ্যানেল: {links['channel']}")
        if links.get("group"):
            parts.append(f"👥 গ্রুপ: {links['group']}")
        text = "\n".join(parts) if parts else t("public_links_default", db)
        await _send(update, text, reply_markup=back_kb(db))
    elif data == "user:account":
        await _show_account(update, context)


async def _show_payment(
    update: Update, context: ContextTypes.DEFAULT_TYPE, plan_key: str
) -> None:
    db = context.bot_data["db"]
    plans = db.get_setting("vip_plans", {})
    plan = plans.get(plan_key)
    if not plan:
        await _send(update, "⚠️ অজানা প্ল্যান", reply_markup=back_kb(db, "user:vip"))
        return
    methods = db.list_payment_methods()
    if not methods:
        await _send(
            update, t("no_payment_methods", db), reply_markup=back_kb(db, "user:vip")
        )
        return
    method_lines = []
    for m in methods:
        line = f"• <b>{m.get('method', '?')}</b>: <code>{m.get('number', '')}</code>"
        if m.get("hint"):
            line += f"  <i>{m['hint']}</i>"
        method_lines.append(line)
    msg = t(
        "payment_guide",
        db,
        amount=plan.get("price", 0),
        methods="\n".join(method_lines),
    )
    context.user_data["pending_payment"] = {"type": "vip", "plan": plan_key}
    await _send(update, msg, reply_markup=back_kb(db, "user:vip"))


async def _show_ebooks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    ebooks = db.list_ebooks(active_only=True)
    if not ebooks:
        await _send(update, t("no_ebooks", db), reply_markup=back_kb(db))
        return
    await _send(update, t("ebooks_intro", db), reply_markup=ebook_list_kb(db, ebooks))


async def _handle_ebook(
    update: Update, context: ContextTypes.DEFAULT_TYPE, ebook_id: str
) -> None:
    db = context.bot_data["db"]
    eb = db.get_ebook(ebook_id)
    if not eb:
        await _send(update, "⚠️ ই-বুকটি খুঁজে পাওয়া যায়নি", reply_markup=back_kb(db, "user:ebooks"))
        return

    title = eb.get("title", "ই-বুক")
    desc = eb.get("description", "")
    info = f"📖 <b>{title}</b>\n\n{desc}\n"
    if eb.get("is_free"):
        info += "\n🆓 <b>ফ্রি</b> — নিচের চ্যানেলে যোগ দিলেই ডাউনলোড করতে পারবেন।"
        kb_rows = []
        ch = db.get_public_links().get("channel")
        if ch:
            kb_rows.append([InlineKeyboardButton("📢 চ্যানেলে যোগ দিন", url=ch)])
        kb_rows.append([
            InlineKeyboardButton("⬇️ ডাউনলোড", callback_data=f"user:eb:dl:{ebook_id}")
        ])
        kb_rows.append([InlineKeyboardButton(b("back", db), callback_data="user:ebooks")])
        await _send(update, info, reply_markup=InlineKeyboardMarkup(kb_rows))
        return

    # paid
    price = eb.get("price", 0)
    info += f"\n💰 <b>মূল্য:</b> ৳{price}"
    methods = db.list_payment_methods()
    method_lines = []
    for m in methods:
        method_lines.append(
            f"• <b>{m.get('method')}</b>: <code>{m.get('number')}</code>"
        )
    if method_lines:
        info += "\n\n" + t("payment_guide", db, amount=price, methods="\n".join(method_lines))
    context.user_data["pending_payment"] = {"type": "ebook", "ebook_id": ebook_id}
    await _send(update, info, reply_markup=back_kb(db, "user:ebooks"))


async def _show_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    user = update.effective_user
    if user is None:
        return
    rec = db.get_user(user.id) or {}
    vip_active = rec.get("vip_active")
    plan = rec.get("vip_plan", "—")
    if vip_active and rec.get("trial"):
        status = t("vip_trial", db) + f" ({plan})"
    elif vip_active:
        status = t("vip_active", db) + f" ({plan})"
    elif rec.get("vip_expiry"):
        status = t("vip_expired", db)
    else:
        status = t("vip_inactive", db)
    expiry_ts = rec.get("vip_expiry")
    expiry_text = (
        f"{fmt_ts(expiry_ts)} — বাকি {fmt_remaining(expiry_ts)}"
        if expiry_ts
        else "—"
    )
    orders = sum(
        1 for o in db.list_vip_orders() if o.get("user_id") == user.id
    ) + sum(
        1 for o in db.list_ebook_orders() if o.get("user_id") == user.id
    )
    text = t(
        "account_template",
        db,
        user_id=user.id,
        name=user.full_name or "—",
        vip_status=status,
        expiry=expiry_text,
        orders=orders,
    )
    await _send(update, text, reply_markup=back_kb(db))


async def on_user_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """ইউজারের ফ্রি-টেক্সট, ছবি (পেমেন্ট স্ক্রিনশট), ইত্যাদি।"""
    db = context.bot_data["db"]
    user = update.effective_user
    msg = update.effective_message
    if user is None or msg is None:
        return
    if await _bot_blocked_for_user(update, db):
        return

    # সাপোর্ট মোড
    if context.user_data.get("awaiting_support"):
        context.user_data.pop("awaiting_support", None)
        admin_ids = list(settings.admin_ids) + _user_extra_admins(db)
        forwarded = False
        for aid in admin_ids:
            try:
                await context.bot.forward_message(
                    chat_id=aid, from_chat_id=user.id, message_id=msg.message_id
                )
                forwarded = True
            except Exception:  # noqa: BLE001
                continue
        if forwarded:
            await msg.reply_text(t("support_sent", db))
        return

    # পেমেন্ট স্ক্রিনশট
    pending = context.user_data.get("pending_payment")
    if pending and (msg.photo or msg.document):
        photo_id = ""
        if msg.photo:
            photo_id = msg.photo[-1].file_id
        elif msg.document:
            photo_id = msg.document.file_id
        if pending["type"] == "vip":
            oid = db.add_vip_order(
                user.id, pending["plan"], screenshot=photo_id
            )
            await _notify_admins_vip(context, db, oid)
        elif pending["type"] == "ebook":
            oid = db.add_ebook_order(
                user.id, pending["ebook_id"], screenshot=photo_id
            )
            await _notify_admins_ebook(context, db, oid)
        context.user_data.pop("pending_payment", None)
        await msg.reply_text(t("screenshot_received", db))
        return

    # গ্রুপে @mention এ AI জবাব
    chat = update.effective_chat
    if chat and chat.type in {"group", "supergroup"}:
        if not db.get_setting("group_mode", False):
            return
        bot_user = await context.bot.get_me()
        text = msg.text or ""
        if f"@{bot_user.username}".lower() not in text.lower():
            return
        prompt = text.replace(f"@{bot_user.username}", "").strip()
        if not prompt:
            return
        from ai_providers import generate_text

        try:
            reply = await generate_text(prompt, settings=settings, db=db)
        except Exception as e:  # noqa: BLE001
            reply = f"⚠️ AI ত্রুটি: {e}"
        await msg.reply_text(reply, parse_mode=ParseMode.HTML)
        return


async def _notify_admins_vip(
    context: ContextTypes.DEFAULT_TYPE, db, order_id: str
) -> None:
    from keyboards import approve_reject_kb

    order = db.get_vip_order(order_id)
    if not order:
        return
    plan = db.get_setting("vip_plans", {}).get(order["plan"], {})
    text = (
        f"⏳ <b>নতুন VIP অর্ডার</b>\n\n"
        f"👤 ইউজার: <code>{order['user_id']}</code>\n"
        f"💎 প্ল্যান: {plan.get('name', order['plan'])} (৳{plan.get('price', '?')})\n"
        f"🆔 অর্ডার: <code>{order_id}</code>"
    )
    admin_ids = list(settings.admin_ids) + _user_extra_admins(db)
    screenshot = order.get("screenshot")
    for aid in admin_ids:
        try:
            if screenshot:
                await context.bot.send_photo(
                    chat_id=aid,
                    photo=screenshot,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=approve_reject_kb("adm:vip", order_id),
                )
            else:
                await context.bot.send_message(
                    chat_id=aid,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=approve_reject_kb("adm:vip", order_id),
                )
        except Exception:  # noqa: BLE001
            continue


async def _notify_admins_ebook(
    context: ContextTypes.DEFAULT_TYPE, db, order_id: str
) -> None:
    from keyboards import approve_reject_kb

    orders = db.list_ebook_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        return
    eb = db.get_ebook(order["ebook_id"]) or {}
    text = (
        f"⏳ <b>নতুন ই-বুক অর্ডার</b>\n\n"
        f"👤 ইউজার: <code>{order['user_id']}</code>\n"
        f"📖 ই-বুক: {eb.get('title', '?')} (৳{eb.get('price', '?')})\n"
        f"🆔 অর্ডার: <code>{order_id}</code>"
    )
    admin_ids = list(settings.admin_ids) + _user_extra_admins(db)
    screenshot = order.get("screenshot")
    for aid in admin_ids:
        try:
            if screenshot:
                await context.bot.send_photo(
                    chat_id=aid,
                    photo=screenshot,
                    caption=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=approve_reject_kb("adm:ebooks", order_id),
                )
            else:
                await context.bot.send_message(
                    chat_id=aid,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=approve_reject_kb("adm:ebooks", order_id),
                )
        except Exception:  # noqa: BLE001
            continue
