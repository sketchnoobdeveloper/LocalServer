"""অ্যাডমিন প্যানেলের সব handler।

ক্যালব্যাক ডেটা ফরম্যাট: `adm:<section>:<sub>:...`
টেক্সট ইনপুটের জন্য `context.user_data["adm_state"]` ব্যবহার করা হয়।
"""

from __future__ import annotations

import io
import json
import logging
import time

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ai_providers import chat_test
from config import is_admin, settings
from keyboards import (
    admin_ai_kb,
    admin_ebooks_kb,
    admin_members_kb,
    admin_root_kb,
    admin_settings_kb,
    admin_system_kb,
    admin_vip_kb,
    back_kb,
    trial_duration_kb,
)
from strings_bn import b, t
from utils import (
    fmt_remaining,
    fmt_ts,
    parse_duration,
    safe_int,
    truncate,
)

log = logging.getLogger(__name__)


def _admins(db) -> list[int]:
    extras = db.get_setting("extra_admins", []) or []
    out = list(settings.admin_ids)
    for x in extras:
        if isinstance(x, int):
            out.append(x)
        else:
            n = safe_int(x)
            if n is not None:
                out.append(n)
    return out


def _is_admin(user_id: int, db) -> bool:
    return is_admin(user_id, _admins(db))


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


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    user = update.effective_user
    if user is None or not _is_admin(user.id, db):
        await _send(update, t("admin_only", db))
        return
    await _send(update, t("admin_panel", db), reply_markup=admin_root_kb(db))


async def on_admin_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    db = context.bot_data["db"]
    query = update.callback_query
    if query is None or update.effective_user is None:
        return
    if not _is_admin(update.effective_user.id, db):
        await query.answer(t("admin_only", db), show_alert=True)
        return
    await query.answer()
    data = query.data or ""
    parts = data.split(":")
    # parts[0] = "adm"
    section = parts[1] if len(parts) > 1 else ""
    sub = parts[2] if len(parts) > 2 else ""
    arg = ":".join(parts[3:]) if len(parts) > 3 else ""

    if section == "root":
        await _send(update, t("admin_panel", db), reply_markup=admin_root_kb(db))
        return
    if section == "members":
        await _members_dispatch(update, context, sub, arg)
    elif section == "vip":
        await _vip_dispatch(update, context, sub, arg)
    elif section == "trial":
        await _trial_dispatch(update, context, sub, arg)
    elif section == "ebooks":
        await _ebooks_dispatch(update, context, sub, arg)
    elif section == "ai":
        await _ai_dispatch(update, context, sub, arg)
    elif section == "set":
        await _settings_dispatch(update, context, sub, arg)
    elif section == "sys":
        await _system_dispatch(update, context, sub, arg)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------


async def _members_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "":
        await _send(
            update,
            "👥 <b>সদস্য ব্যবস্থাপনা</b>\nনিচের অপশনগুলো থেকে বেছে নিন।",
            reply_markup=admin_members_kb(db),
        )
    elif sub == "list":
        users = db.list_users()
        total = len(users)
        vip = sum(1 for u in users if u.get("vip_active"))
        banned = sum(1 for u in users if u.get("banned"))
        rows = [
            f"মোট: <b>{total}</b> | VIP: <b>{vip}</b> | ব্যান: <b>{banned}</b>",
            "",
        ]
        for u in users[:30]:
            tag = "💎" if u.get("vip_active") else ("🚫" if u.get("banned") else "👤")
            name = u.get("username") or u.get("first_name") or "—"
            rows.append(f"{tag} <code>{u.get('id')}</code> — {name}")
        if total > 30:
            rows.append(f"\n<i>...আরও {total - 30} জন</i>")
        await _send(update, "\n".join(rows), reply_markup=admin_members_kb(db))
    elif sub == "msg":
        if not arg:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 সবাইকে", callback_data="adm:members:msg:all")],
                [InlineKeyboardButton("💎 শুধু VIP", callback_data="adm:members:msg:vip")],
                [InlineKeyboardButton("👤 নির্দিষ্ট ID", callback_data="adm:members:msg:user")],
                [InlineKeyboardButton("⏰ শিডিউল", callback_data="adm:members:msg:sched")],
                [InlineKeyboardButton(b("back", db), callback_data="adm:members")],
            ])
            await _send(update, "📨 কাকে বার্তা পাঠাবেন?", reply_markup=kb)
        elif arg == "all":
            context.user_data["adm_state"] = "broadcast_all"
            await _send(update, "📢 সবাইকে পাঠানোর বার্তা লিখুন:", reply_markup=back_kb(db, "adm:members"))
        elif arg == "vip":
            context.user_data["adm_state"] = "broadcast_vip"
            await _send(update, "💎 VIP দের পাঠানোর বার্তা লিখুন:", reply_markup=back_kb(db, "adm:members"))
        elif arg == "user":
            context.user_data["adm_state"] = "broadcast_user_id"
            await _send(update, "👤 ইউজার ID পাঠান:", reply_markup=back_kb(db, "adm:members"))
        elif arg == "sched":
            context.user_data["adm_state"] = "broadcast_sched_when"
            await _send(update, "⏰ কত সময় পরে পাঠাবেন? (যেমন: 30m, 2h, 1d)", reply_markup=back_kb(db, "adm:members"))
    elif sub == "ban":
        context.user_data["adm_state"] = "ban_user"
        await _send(update, "🚫 যে ইউজারকে ব্যান করতে চান তার <b>ID</b> পাঠান:", reply_markup=back_kb(db, "adm:members"))
    elif sub == "unban":
        context.user_data["adm_state"] = "unban_user"
        await _send(update, "✅ যে ইউজারের ব্যান তুলবেন তার <b>ID</b> পাঠান:", reply_markup=back_kb(db, "adm:members"))
    elif sub == "del":
        context.user_data["adm_state"] = "delete_user"
        await _send(update, "🗑️ যে ইউজার মুছবেন তার <b>ID</b> পাঠান:", reply_markup=back_kb(db, "adm:members"))


# ---------------------------------------------------------------------------
# VIP
# ---------------------------------------------------------------------------


async def _vip_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "":
        await _send(update, "💎 <b>VIP ব্যবস্থাপনা</b>", reply_markup=admin_vip_kb(db))
    elif sub == "pending":
        orders = db.list_vip_orders(status="pending")
        if not orders:
            await _send(update, "📭 কোনো পেন্ডিং VIP অর্ডার নেই", reply_markup=admin_vip_kb(db))
            return
        await _send(update, f"⏳ <b>{len(orders)}</b> টি পেন্ডিং VIP অর্ডার:", reply_markup=admin_vip_kb(db))
        for o in orders[:10]:
            plan = db.get_setting("vip_plans", {}).get(o["plan"], {})
            text = (
                f"🆔 <code>{o['id']}</code>\n"
                f"👤 ইউজার: <code>{o['user_id']}</code>\n"
                f"💎 প্ল্যান: {plan.get('name', o['plan'])} — ৳{plan.get('price', '?')}\n"
                f"🕒 {fmt_ts(o.get('created'))}"
            )
            from keyboards import approve_reject_kb

            screenshot = o.get("screenshot")
            try:
                if screenshot:
                    await context.bot.send_photo(
                        chat_id=update.effective_user.id,
                        photo=screenshot,
                        caption=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=approve_reject_kb("adm:vip", o["id"]),
                    )
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_user.id,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=approve_reject_kb("adm:vip", o["id"]),
                    )
            except Exception:  # noqa: BLE001
                pass
    elif sub == "approve" and arg:
        await _approve_vip(update, context, arg)
    elif sub == "reject" and arg:
        await _reject_vip(update, context, arg)
    elif sub == "list":
        users = db.list_active_vips()
        rows = [f"💎 সক্রিয় VIP: <b>{len(users)}</b>", ""]
        for u in users[:30]:
            rows.append(
                f"<code>{u.get('id')}</code> — {u.get('vip_plan', '—')}"
                f" — মেয়াদ: {fmt_remaining(u.get('vip_expiry'))}"
            )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ম্যানুয়াল VIP যোগ", callback_data="adm:vip:manual")],
            [InlineKeyboardButton(b("back", db), callback_data="adm:vip")],
        ])
        await _send(update, "\n".join(rows), reply_markup=kb)
    elif sub == "manual":
        context.user_data["adm_state"] = "manual_vip_id"
        await _send(update, "👤 ম্যানুয়াল VIP দিতে যে ইউজারের ID পাঠাবেন:", reply_markup=back_kb(db, "adm:vip"))
    elif sub == "trial":
        await _send(update, "🎫 ট্রায়াল সময়কাল বেছে নিন:", reply_markup=trial_duration_kb())
    elif sub == "links":
        plans = db.get_setting("vip_plans", {})
        links = db.get_setting("vip_links", {})
        rows = ["🔗 <b>VIP লিংক সেটিংস</b>", ""]
        for k, plan in plans.items():
            rows.append(f"<b>{plan.get('name', k)}:</b> {links.get(k) or '—'}")
        rows.append("")
        rows.append("লিংক সেট করতে: <code>/setviplink &lt;plan&gt; &lt;url&gt;</code>")
        rows.append("যেমন: <code>/setviplink monthly https://t.me/+abc</code>")
        await _send(update, "\n".join(rows), reply_markup=admin_vip_kb(db))
    elif sub == "autokick":
        cur = db.get_setting("auto_kick", True)
        db.set_setting("auto_kick", not cur)
        await _send(update, f"অটো-কিক এখন: <b>{'চালু' if not cur else 'বন্ধ'}</b>", reply_markup=admin_vip_kb(db))
    elif sub == "kicks":
        targets = db.get_setting("kick_targets", [])
        rows = ["⚙️ <b>কিক টার্গেট</b>", ""]
        if not targets:
            rows.append("<i>কোনো টার্গেট সেট নেই</i>")
        for tgt in targets:
            rows.append(f"• <code>{tgt}</code>")
        rows.append("")
        rows.append("যোগ: <code>/addkick &lt;chat_id&gt;</code>")
        rows.append("সরান: <code>/delkick &lt;chat_id&gt;</code>")
        await _send(update, "\n".join(rows), reply_markup=admin_vip_kb(db))


async def _approve_vip(
    update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str
) -> None:
    db = context.bot_data["db"]
    order = db.get_vip_order(order_id)
    if not order:
        await _send(update, "⚠️ অর্ডার পাওয়া যায়নি")
        return
    if order.get("status") != "pending":
        await _send(update, f"⚠️ এই অর্ডার ইতোমধ্যে {order.get('status')}")
        return
    plan_key = order["plan"]
    plan = db.get_setting("vip_plans", {}).get(plan_key, {})
    days = plan.get("days", 30)
    db.update_vip_order(order_id, status="approved", processed=int(time.time()))
    db.grant_vip(order["user_id"], plan_key, days)
    link = db.get_setting("vip_links", {}).get(plan_key, "") or ""
    msg = t(
        "vip_approved",
        db,
        plan=plan.get("name", plan_key),
        expiry=fmt_ts(int(time.time()) + days * 86400),
        links=(f"🔗 {link}" if link else "<i>লিংক শীঘ্রই পাঠানো হবে।</i>"),
    )
    try:
        await context.bot.send_message(
            chat_id=order["user_id"], text=msg, parse_mode=ParseMode.HTML
        )
    except Exception:  # noqa: BLE001
        pass
    await _send(update, f"✅ <code>{order_id}</code> অর্ডার approve করা হয়েছে")


async def _reject_vip(
    update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str
) -> None:
    db = context.bot_data["db"]
    order = db.get_vip_order(order_id)
    if not order:
        await _send(update, "⚠️ অর্ডার পাওয়া যায়নি")
        return
    db.update_vip_order(order_id, status="rejected", processed=int(time.time()))
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=t("vip_rejected", db, reason="পেমেন্ট যাচাই করা যায়নি"),
            parse_mode=ParseMode.HTML,
        )
    except Exception:  # noqa: BLE001
        pass
    await _send(update, f"❌ <code>{order_id}</code> reject করা হয়েছে")


# ---------------------------------------------------------------------------
# Trial
# ---------------------------------------------------------------------------


async def _trial_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "dur":
        if arg == "custom":
            context.user_data["adm_state"] = "trial_custom_duration"
            await _send(update, "⌨️ কাস্টম সময়কাল লিখুন (যেমন: 5m, 7d, 2h):", reply_markup=back_kb(db, "adm:vip"))
        else:
            seconds = parse_duration(arg)
            if seconds is None:
                await _send(update, "⚠️ অবৈধ সময়কাল")
                return
            context.user_data["adm_state"] = "trial_user_id"
            context.user_data["trial_seconds"] = seconds
            await _send(update, "👤 যে ইউজারকে ট্রায়াল দিতে চান তার ID পাঠান:", reply_markup=back_kb(db, "adm:vip"))


# ---------------------------------------------------------------------------
# E-books
# ---------------------------------------------------------------------------


async def _ebooks_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "":
        await _send(update, "📚 <b>ই-বুক ব্যবস্থাপনা</b>", reply_markup=admin_ebooks_kb(db))
    elif sub == "pending":
        orders = db.list_ebook_orders(status="pending")
        if not orders:
            await _send(update, "📭 পেন্ডিং নেই", reply_markup=admin_ebooks_kb(db))
            return
        await _send(update, f"⏳ <b>{len(orders)}</b> টি পেন্ডিং ই-বুক অর্ডার", reply_markup=admin_ebooks_kb(db))
        for o in orders[:10]:
            eb = db.get_ebook(o["ebook_id"]) or {}
            text = (
                f"🆔 <code>{o['id']}</code>\n"
                f"👤 ইউজার: <code>{o['user_id']}</code>\n"
                f"📖 ই-বুক: {eb.get('title', '?')} — ৳{eb.get('price', '?')}\n"
                f"🕒 {fmt_ts(o.get('created'))}"
            )
            from keyboards import approve_reject_kb

            kb = approve_reject_kb("adm:ebooks", o["id"])
            screenshot = o.get("screenshot")
            try:
                if screenshot:
                    await context.bot.send_photo(
                        chat_id=update.effective_user.id,
                        photo=screenshot,
                        caption=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=kb,
                    )
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_user.id,
                        text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=kb,
                    )
            except Exception:  # noqa: BLE001
                pass
    elif sub == "approve" and arg:
        await _approve_ebook(update, context, arg)
    elif sub == "reject" and arg:
        await _reject_ebook(update, context, arg)
    elif sub == "manage":
        ebooks = db.list_ebooks(active_only=False)
        rows = [f"📖 মোট ই-বুক: <b>{len(ebooks)}</b>", ""]
        for eb in ebooks[:30]:
            tag = "🆓" if eb.get("is_free") else f"৳{eb.get('price', 0)}"
            status = "✅" if eb.get("active") else "🚫"
            rows.append(
                f"{status} <code>{eb['id']}</code> {tag} — {eb.get('title', '?')}"
            )
        rows += [
            "",
            "➕ যোগ: <code>/addebook &lt;title&gt; | &lt;desc&gt; | &lt;price&gt;</code>",
            "  মূল্য 0 = ফ্রি",
            "  তারপর ফাইল reply দিয়ে পাঠান",
            "✏️ এডিট: <code>/editebook &lt;id&gt; field=value ...</code>",
            "🗑️ মুছুন: <code>/delebook &lt;id&gt;</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_ebooks_kb(db))


async def _approve_ebook(
    update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str
) -> None:
    db = context.bot_data["db"]
    orders = db.list_ebook_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        await _send(update, "⚠️ অর্ডার পাওয়া যায়নি")
        return
    eb = db.get_ebook(order["ebook_id"])
    if not eb:
        await _send(update, "⚠️ ই-বুক পাওয়া যায়নি")
        return
    db.update_ebook_order(order_id, status="approved", processed=int(time.time()))
    db.update_ebook(eb["id"], downloads=int(eb.get("downloads", 0)) + 1)
    try:
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=t("ebook_approved", db, title=eb.get("title", "ই-বুক")),
            parse_mode=ParseMode.HTML,
        )
        if eb.get("file_id"):
            await context.bot.send_document(
                chat_id=order["user_id"], document=eb["file_id"]
            )
        elif eb.get("link"):
            await context.bot.send_message(
                chat_id=order["user_id"], text=f"🔗 {eb['link']}"
            )
    except Exception:  # noqa: BLE001
        pass
    await _send(update, f"✅ <code>{order_id}</code> approve")


async def _reject_ebook(
    update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str
) -> None:
    db = context.bot_data["db"]
    db.update_ebook_order(order_id, status="rejected", processed=int(time.time()))
    orders = db.list_ebook_orders()
    order = next((o for o in orders if o["id"] == order_id), None)
    if order:
        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text="❌ আপনার ই-বুক অর্ডার বাতিল হয়েছে।",
            )
        except Exception:  # noqa: BLE001
            pass
    await _send(update, f"❌ <code>{order_id}</code> reject")


# ---------------------------------------------------------------------------
# AI auto-post
# ---------------------------------------------------------------------------


async def _ai_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "":
        await _send(update, "🤖 <b>এআই অটো-পোস্ট</b>", reply_markup=admin_ai_kb(db))
    elif sub == "channels":
        channels = db.list_ai_channels()
        rows = [f"📢 চ্যানেল সংখ্যা: <b>{len(channels)}</b>", ""]
        for c in channels[:30]:
            tag = "🟢" if c.get("enabled") else "🔴"
            rows.append(
                f"{tag} <code>{c['id']}</code> — {c.get('title') or '—'}"
            )
        rows += [
            "",
            "➕ যোগ: <code>/addchannel &lt;chat_id&gt; [শিরোনাম]</code>",
            "📝 চ্যানেল-প্রম্পট: <code>/setchprompt &lt;chat_id&gt; &lt;prompt&gt;</code>",
            "🗑️ মুছুন: <code>/delchannel &lt;chat_id&gt;</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_ai_kb(db))
    elif sub == "fb":
        pages = db.list_fb_pages()
        rows = [f"📘 ফেসবুক পেজ: <b>{len(pages)}</b>", ""]
        for p in pages[:30]:
            rows.append(f"• <code>{p['id']}</code> — {p.get('title') or '—'}")
        rows += [
            "",
            "➕ যোগ: <code>/addfb &lt;page_id&gt; &lt;access_token&gt;</code>",
            "🗑️ মুছুন: <code>/delfb &lt;page_id&gt;</code>",
            "<i>(Facebook API integration optional — কোর ফোকাস টেলিগ্রাম)</i>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_ai_kb(db))
    elif sub == "prompt":
        cur = db.get_prompt()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ সেট", callback_data="adm:ai:prompt_set")],
            [InlineKeyboardButton("↩️ Undo", callback_data="adm:ai:prompt_undo"),
             InlineKeyboardButton("↪️ Redo", callback_data="adm:ai:prompt_redo")],
            [InlineKeyboardButton("🗑️ মুছুন", callback_data="adm:ai:prompt_clear")],
            [InlineKeyboardButton(b("back", db), callback_data="adm:ai")],
        ])
        text = (
            "📝 <b>প্রম্পট</b>\n\n"
            f"<b>বর্তমান:</b>\n<code>{(cur or '—')[:1000]}</code>\n\n"
            "মাল্টি-টপিকের জন্য প্রতিটি টপিক <code>\\n---\\n</code> দিয়ে আলাদা করুন।"
        )
        await _send(update, text, reply_markup=kb)
    elif sub == "prompt_set":
        context.user_data["adm_state"] = "set_prompt"
        await _send(update, "✏️ নতুন প্রম্পট পাঠান:", reply_markup=back_kb(db, "adm:ai"))
    elif sub == "prompt_undo":
        new = db.undo_prompt()
        await _send(update, f"↩️ Undo সম্পন্ন।\nবর্তমান:\n<code>{(new or '—')[:500]}</code>", reply_markup=admin_ai_kb(db))
    elif sub == "prompt_redo":
        new = db.redo_prompt()
        await _send(update, f"↪️ Redo সম্পন্ন।\nবর্তমান:\n<code>{(new or '—')[:500]}</code>", reply_markup=admin_ai_kb(db))
    elif sub == "prompt_clear":
        db.push_prompt("")
        await _send(update, "🗑️ প্রম্পট মুছে দেওয়া হয়েছে", reply_markup=admin_ai_kb(db))
    elif sub == "role":
        context.user_data["adm_state"] = "set_ai_role"
        cur = db.get_setting("ai_role", "")
        await _send(update, f"🎭 <b>এআই রোল</b>\n\nবর্তমান: <code>{cur or '—'}</code>\n\nনতুন রোল পাঠান:", reply_markup=back_kb(db, "adm:ai"))
    elif sub == "text":
        prov = db.get_setting("text_ai_provider", "google")
        model = db.get_setting("text_ai_model", "")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Google AI Studio", callback_data="adm:ai:text_set:google")],
            [InlineKeyboardButton("🛣️ OpenRouter", callback_data="adm:ai:text_set:openrouter")],
            [InlineKeyboardButton("⚙️ কাস্টম", callback_data="adm:ai:text_set:custom")],
            [InlineKeyboardButton("✏️ মডেল পরিবর্তন", callback_data="adm:ai:text_model")],
            [InlineKeyboardButton(b("back", db), callback_data="adm:ai")],
        ])
        await _send(
            update,
            f"🧠 <b>টেক্সট AI</b>\n\nপ্রোভাইডার: <b>{prov}</b>\nমডেল: <code>{model or '—'}</code>",
            reply_markup=kb,
        )
    elif sub == "text_set" and arg:
        db.set_setting("text_ai_provider", arg)
        await _send(update, f"✅ প্রোভাইডার সেট: <b>{arg}</b>", reply_markup=admin_ai_kb(db))
    elif sub == "text_model":
        context.user_data["adm_state"] = "set_text_model"
        await _send(update, "✏️ মডেল নাম পাঠান (যেমন: gemini-2.5-flash, llama-3.3-8b):", reply_markup=back_kb(db, "adm:ai"))
    elif sub == "image":
        prov = db.get_setting("image_ai_provider", "pollinations")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👻 GhostWeb", callback_data="adm:ai:img_set:ghostweb")],
            [InlineKeyboardButton("🌸 Pollinations", callback_data="adm:ai:img_set:pollinations")],
            [InlineKeyboardButton("❌ ছাড়া", callback_data="adm:ai:img_set:none")],
            [InlineKeyboardButton(b("back", db), callback_data="adm:ai")],
        ])
        await _send(update, f"🖼️ <b>ইমেজ AI</b>\n\nপ্রোভাইডার: <b>{prov}</b>", reply_markup=kb)
    elif sub == "img_set" and arg:
        db.set_setting("image_ai_provider", arg)
        await _send(update, f"✅ ইমেজ AI সেট: <b>{arg}</b>", reply_markup=admin_ai_kb(db))
    elif sub == "schedule":
        cur = db.get_setting("post_interval_min", 30)
        context.user_data["adm_state"] = "set_post_interval"
        await _send(update, f"⏰ <b>শিডিউল</b>\n\nবর্তমান: প্রতি <b>{cur}</b> মিনিট\n\nনতুন interval (মিনিট) পাঠান:", reply_markup=back_kb(db, "adm:ai"))
    elif sub == "toggle":
        cur = db.get_setting("auto_post", False)
        db.set_setting("auto_post", not cur)
        await _send(update, f"অটো-পোস্ট এখন: <b>{'চালু' if not cur else 'বন্ধ'}</b>", reply_markup=admin_ai_kb(db))
    elif sub == "promo":
        promos = db.list_promos()
        rows = [f"📣 প্রমো: <b>{len(promos)}</b>", ""]
        for p in promos[:10]:
            rows.append(f"• <code>{p['id']}</code> — {truncate(p['text'], 80)}")
        rows += [
            "",
            "➕ যোগ: <code>/addpromo &lt;text&gt;</code>",
            "🗑️ মুছুন: <code>/delpromo &lt;id&gt;</code>",
            "📤 পাঠান: <code>/sendpromo &lt;id&gt;</code>",
            "⏰ interval: <code>/promointv &lt;minutes&gt;</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_ai_kb(db))
    elif sub == "promo_toggle":
        cur = db.get_setting("auto_promo", False)
        db.set_setting("auto_promo", not cur)
        await _send(update, f"অটো-প্রমো এখন: <b>{'চালু' if not cur else 'বন্ধ'}</b>", reply_markup=admin_ai_kb(db))
    elif sub == "now":
        from auto_post import run_auto_post_cycle

        await _send(update, "✍️ এখনই পোস্ট তৈরি হচ্ছে...")
        try:
            n = await run_auto_post_cycle(context.bot, settings=settings, db=db)
            await _send(update, f"✅ {n} টি চ্যানেলে পোস্ট হয়েছে", reply_markup=admin_ai_kb(db))
        except Exception as e:  # noqa: BLE001
            await _send(update, f"⚠️ ত্রুটি: {e}", reply_markup=admin_ai_kb(db))
    elif sub == "push":
        context.user_data["adm_state"] = "ai_push_message"
        await _send(update, "🚀 যা চ্যানেলে পাঠাতে চান লিখুন (HTML ok):", reply_markup=back_kb(db, "adm:ai"))


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


async def _settings_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "":
        await _send(update, "⚙️ <b>সেটিংস</b>", reply_markup=admin_settings_kb(db))
    elif sub == "react":
        cur = db.get_setting("auto_react", False)
        db.set_setting("auto_react", not cur)
        await _send(update, f"অটো-রিয়েক্ট: <b>{'চালু' if not cur else 'বন্ধ'}</b>", reply_markup=admin_settings_kb(db))
    elif sub == "group":
        cur = db.get_setting("group_mode", False)
        db.set_setting("group_mode", not cur)
        await _send(update, f"গ্রুপ মোড: <b>{'চালু' if not cur else 'বন্ধ'}</b>", reply_markup=admin_settings_kb(db))
    elif sub == "bot":
        cur = db.get_setting("bot_enabled", True)
        db.set_setting("bot_enabled", not cur)
        await _send(update, f"বট: <b>{'চালু' if not cur else 'বন্ধ'}</b>", reply_markup=admin_settings_kb(db))
    elif sub == "ui":
        from strings_bn import DEFAULT_UI_TEXTS

        keys = list(DEFAULT_UI_TEXTS.keys())
        rows = ["✍️ <b>ইউআই টেক্সট</b>\n\nকাস্টমাইজ করার জন্য:", ""]
        rows.append("<code>/setui &lt;key&gt; &lt;text&gt;</code>")
        rows.append("\nKey list:")
        for k in keys[:40]:
            cur = db.get_ui_text(k) or ""
            mark = "✏️" if cur else " "
            rows.append(f"{mark} <code>{k}</code>")
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))
    elif sub == "menu":
        from strings_bn import DEFAULT_MENU_BUTTONS

        rows = ["🔲 <b>মেনু বাটন</b>\n\nকাস্টমাইজ:", ""]
        rows.append("<code>/setbtn &lt;key&gt; &lt;label&gt;</code>")
        rows.append("\nKey list:")
        for k in list(DEFAULT_MENU_BUTTONS.keys())[:40]:
            cur = db.get_menu_button(k) or ""
            mark = "✏️" if cur else " "
            rows.append(f"{mark} <code>{k}</code>")
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))
    elif sub == "vip":
        plans = db.get_setting("vip_plans", {})
        rows = ["💎 <b>VIP সেটিংস</b>", ""]
        for k, p in plans.items():
            rows.append(
                f"<b>{p.get('name', k)}</b> — ৳{p.get('price')} ({p.get('days')} দিন) [<code>{k}</code>]"
            )
        rows += [
            "",
            "✏️ পরিবর্তন: <code>/setplan &lt;key&gt; name=... price=... days=...</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))
    elif sub == "viplinks":
        await _vip_dispatch(update, context, "links", "")
    elif sub == "help":
        items = db.list_help_items()
        rows = ["ℹ️ <b>সাহায্য আইটেম</b>", ""]
        for it in items:
            rows.append(f"<b>{it.get('title', '')}</b> — {truncate(it.get('text', ''), 80)}")
        rows += [
            "",
            "➕ যোগ: <code>/addhelp &lt;title&gt; | &lt;text&gt;</code>",
            "🗑️ Clear: <code>/clearhelp</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))
    elif sub == "public":
        links = db.get_public_links()
        rows = [
            "📢 <b>পাবলিক লিংক</b>",
            f"চ্যানেল: {links.get('channel') or '—'}",
            f"গ্রুপ: {links.get('group') or '—'}",
            "",
            "✏️ সেট: <code>/setpublic channel &lt;url&gt;</code>",
            "✏️ সেট: <code>/setpublic group &lt;url&gt;</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))
    elif sub == "demo":
        cur = db.get_setting("demo", "")
        context.user_data["adm_state"] = "set_demo"
        await _send(update, f"🎬 <b>ডেমো সেটিংস</b>\n\nবর্তমান: {cur or '—'}\n\nনতুন ডেমো টেক্সট/লিংক পাঠান:", reply_markup=back_kb(db, "adm:settings"))
    elif sub == "payment":
        methods = db.list_payment_methods()
        rows = ["💳 <b>পেমেন্ট পদ্ধতি</b>", ""]
        for i, m in enumerate(methods):
            rows.append(f"{i+1}. <b>{m.get('method')}</b>: <code>{m.get('number')}</code>")
        rows += [
            "",
            "➕ যোগ: <code>/addpay bKash 01XXXXXX [hint]</code>",
            "🗑️ মুছুন: <code>/delpay &lt;index&gt;</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))
    elif sub == "admins":
        admins = _admins(db)
        rows = ["🔑 <b>অ্যাডমিন তালিকা</b>", ""]
        for a in admins:
            tag = "🌟" if a in settings.admin_ids else "👤"
            rows.append(f"{tag} <code>{a}</code>")
        rows += [
            "",
            "<i>🌟 = environment-level (BOT_TOKEN owner)</i>",
            "➕ যোগ: <code>/addadmin &lt;user_id&gt;</code>",
            "🗑️ সরান: <code>/deladmin &lt;user_id&gt;</code>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_settings_kb(db))


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------


async def _system_dispatch(
    update: Update, context: ContextTypes.DEFAULT_TYPE, sub: str, arg: str
) -> None:
    db = context.bot_data["db"]
    if sub == "":
        await _send(update, "🗄️ <b>সিস্টেম ও ডেটাবেজ</b>", reply_markup=admin_system_kb(db))
    elif sub == "backup":
        doc = db.export_all()
        raw = json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")
        try:
            await context.bot.send_document(
                chat_id=update.effective_user.id,
                document=InputFile(io.BytesIO(raw), filename="kampondit_backup.json"),
                caption="💾 ডেটাবেজ ব্যাকআপ",
            )
        except Exception as e:  # noqa: BLE001
            await _send(update, f"⚠️ ব্যাকআপ পাঠাতে ব্যর্থ: {e}")
        await _send(update, "✅ ব্যাকআপ পাঠানো হয়েছে", reply_markup=admin_system_kb(db))
    elif sub == "restore":
        context.user_data["adm_state"] = "restore_db"
        await _send(update, "📥 ব্যাকআপ JSON ফাইলটি reply দিয়ে পাঠান:", reply_markup=back_kb(db, "adm:system"))
    elif sub == "db":
        kind = settings.db_kind
        rows = [
            "🗄️ <b>ডেটাবেজ</b>",
            f"বর্তমান: <b>{kind}</b>",
            f"JSON path: <code>{settings.json_path}</code>",
            f"Mongo configured: <b>{'হ্যাঁ' if settings.mongo_uri else 'না'}</b>",
            f"Firebase configured: <b>{'হ্যাঁ' if settings.firebase_url else 'না'}</b>",
            "",
            "<i>পরিবর্তন করতে DB_KIND env vars সেট করে restart করুন।</i>",
        ]
        await _send(update, "\n".join(rows), reply_markup=admin_system_kb(db))
    elif sub == "chat":
        context.user_data["adm_state"] = "chatbot_test"
        await _send(update, "🤖 <b>চ্যাটবট পরীক্ষা</b>\n\nএখন যা লিখবেন AI সেটার উত্তর দেবে।\nবেরোতে: /cancel", reply_markup=back_kb(db, "adm:system"))


# ---------------------------------------------------------------------------
# অ্যাডমিন টেক্সট ইনপুট স্টেট মেশিন
# ---------------------------------------------------------------------------


async def on_admin_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    """অ্যাডমিনের free-text প্রসেস করে। `True` রিটার্ন = handled।"""
    db = context.bot_data["db"]
    user = update.effective_user
    msg = update.effective_message
    if user is None or msg is None or not _is_admin(user.id, db):
        return False
    state = context.user_data.get("adm_state")
    if not state:
        return False
    text = (msg.text or "").strip()

    if text in {"/cancel", "❌ বাতিল"}:
        context.user_data.pop("adm_state", None)
        await msg.reply_text("✅ বাতিল করা হয়েছে")
        return True

    handled = True

    if state == "ban_user":
        uid = safe_int(text)
        if uid is None:
            await msg.reply_text("⚠️ অবৈধ ID")
        else:
            db.upsert_user(uid, banned=True)
            await msg.reply_text(f"🚫 <code>{uid}</code> ব্যান করা হয়েছে", parse_mode=ParseMode.HTML)
    elif state == "unban_user":
        uid = safe_int(text)
        if uid is None:
            await msg.reply_text("⚠️ অবৈধ ID")
        else:
            db.upsert_user(uid, banned=False)
            await msg.reply_text(f"✅ <code>{uid}</code> আনব্যান করা হয়েছে", parse_mode=ParseMode.HTML)
    elif state == "delete_user":
        uid = safe_int(text)
        if uid is None:
            await msg.reply_text("⚠️ অবৈধ ID")
        else:
            ok = db.delete_user(uid)
            await msg.reply_text(("🗑️ মুছে ফেলা হয়েছে" if ok else "⚠️ পাওয়া যায়নি"))
    elif state == "broadcast_all":
        await _broadcast(context, db, audience="all", text=text)
        await msg.reply_text("📢 ব্রডকাস্ট পাঠানো হয়েছে")
    elif state == "broadcast_vip":
        await _broadcast(context, db, audience="vip", text=text)
        await msg.reply_text("💎 VIP দের পাঠানো হয়েছে")
    elif state == "broadcast_user_id":
        uid = safe_int(text)
        if uid is None:
            await msg.reply_text("⚠️ অবৈধ ID")
        else:
            context.user_data["adm_state"] = "broadcast_user_text"
            context.user_data["broadcast_user"] = uid
            await msg.reply_text("✏️ এখন বার্তা পাঠান:")
            return True
    elif state == "broadcast_user_text":
        uid = context.user_data.pop("broadcast_user", None)
        if uid:
            try:
                await context.bot.send_message(chat_id=uid, text=text, parse_mode=ParseMode.HTML)
                await msg.reply_text("✅ পাঠানো হয়েছে")
            except Exception as e:  # noqa: BLE001
                await msg.reply_text(f"⚠️ ব্যর্থ: {e}")
    elif state == "broadcast_sched_when":
        secs = parse_duration(text)
        if secs is None:
            await msg.reply_text("⚠️ অবৈধ সময়। যেমন: 30m, 2h, 1d")
        else:
            context.user_data["adm_state"] = "broadcast_sched_text"
            context.user_data["sched_when"] = secs
            await msg.reply_text("✏️ এখন বার্তাটি পাঠান:")
            return True
    elif state == "broadcast_sched_text":
        secs = context.user_data.pop("sched_when", 60)
        send_at = int(time.time()) + secs
        db.add_scheduled_message(send_at, "all", text)
        await msg.reply_text(f"⏰ {fmt_ts(send_at)} এ পাঠানো হবে")
    elif state == "manual_vip_id":
        uid = safe_int(text)
        if uid is None:
            await msg.reply_text("⚠️ অবৈধ ID")
        else:
            plans = db.get_setting("vip_plans", {})
            kb_rows = [
                [InlineKeyboardButton(p.get("name", k), callback_data=f"adm:vip:manual_plan:{uid}:{k}")]
                for k, p in plans.items()
            ]
            await msg.reply_text(
                "💎 কোন প্ল্যান দেবেন?",
                reply_markup=InlineKeyboardMarkup(kb_rows),
            )
            context.user_data.pop("adm_state", None)
            return True
    elif state == "trial_user_id":
        uid = safe_int(text)
        if uid is None:
            await msg.reply_text("⚠️ অবৈধ ID")
        else:
            secs = context.user_data.pop("trial_seconds", 0)
            db.grant_trial(uid, secs)
            try:
                links = db.get_setting("vip_links", {})
                link_text = "\n".join(f"🔗 {v}" for v in links.values() if v) or "<i>(লিংক সেট নেই)</i>"
                await context.bot.send_message(
                    chat_id=uid,
                    text=t(
                        "trial_welcome",
                        db,
                        duration=fmt_remaining(int(time.time()) + secs),
                        links=link_text,
                    ),
                    parse_mode=ParseMode.HTML,
                )
            except Exception:  # noqa: BLE001
                pass
            await msg.reply_text(f"🎫 <code>{uid}</code> কে ট্রায়াল দেওয়া হয়েছে", parse_mode=ParseMode.HTML)
    elif state == "trial_custom_duration":
        secs = parse_duration(text)
        if secs is None:
            await msg.reply_text("⚠️ যেমন: 5m, 7d, 2h")
        else:
            context.user_data["adm_state"] = "trial_user_id"
            context.user_data["trial_seconds"] = secs
            await msg.reply_text("👤 এখন ইউজার ID পাঠান:")
    elif state == "set_prompt":
        db.push_prompt(text)
        await msg.reply_text("✅ প্রম্পট সেট হয়েছে")
    elif state == "set_ai_role":
        db.set_setting("ai_role", text)
        await msg.reply_text("✅ AI রোল সেট হয়েছে")
    elif state == "set_text_model":
        db.set_setting("text_ai_model", text)
        await msg.reply_text(f"✅ মডেল সেট: <code>{text}</code>", parse_mode=ParseMode.HTML)
    elif state == "set_post_interval":
        n = safe_int(text)
        if n is None or n < 1:
            await msg.reply_text("⚠️ মিনিট সংখ্যা পাঠান (≥1)")
        else:
            db.set_setting("post_interval_min", n)
            await msg.reply_text(f"⏰ interval সেট: {n} মিনিট\n<i>পরিবর্তনের পর restart দরকার পড়তে পারে।</i>", parse_mode=ParseMode.HTML)
    elif state == "ai_push_message":
        await _push_to_channels(context, db, text)
        await msg.reply_text("🚀 পাঠানো হয়েছে")
    elif state == "set_demo":
        db.set_setting("demo", text)
        await msg.reply_text("✅ ডেমো সেট হয়েছে")
    elif state == "restore_db":
        await msg.reply_text("📥 JSON ফাইলটি document হিসেবে পাঠান (text নয়)")
        return True
    elif state == "chatbot_test":
        try:
            reply = await chat_test(text, settings=settings, db=db)
        except Exception as e:  # noqa: BLE001
            reply = f"⚠️ {e}"
        await msg.reply_text(reply, parse_mode=ParseMode.HTML)
        return True  # থামাবেন না, আরও মেসেজ গ্রহণ করুন
    else:
        handled = False

    if handled:
        context.user_data.pop("adm_state", None)
    return handled


async def on_admin_document(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    db = context.bot_data["db"]
    user = update.effective_user
    msg = update.effective_message
    if user is None or msg is None or not _is_admin(user.id, db):
        return False
    state = context.user_data.get("adm_state")
    if state == "restore_db":
        doc = msg.document
        if not doc:
            return False
        try:
            file = await context.bot.get_file(doc.file_id)
            data = await file.download_as_bytearray()
            payload = json.loads(bytes(data).decode("utf-8"))
            db.import_all(payload)
            await msg.reply_text("✅ রিস্টোর সম্পন্ন")
        except Exception as e:  # noqa: BLE001
            await msg.reply_text(f"⚠️ রিস্টোর ব্যর্থ: {e}")
        context.user_data.pop("adm_state", None)
        return True
    return False


async def _broadcast(context, db, *, audience: str, text: str) -> None:
    users = db.list_users()
    if audience == "vip":
        users = [u for u in users if u.get("vip_active")]
    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["id"], text=text, parse_mode=ParseMode.HTML
            )
        except Exception:  # noqa: BLE001
            continue


async def _push_to_channels(context, db, text: str) -> None:
    for ch in db.list_ai_channels():
        if not ch.get("enabled"):
            continue
        try:
            await context.bot.send_message(
                chat_id=ch["id"], text=text, parse_mode=ParseMode.HTML
            )
        except Exception:  # noqa: BLE001
            continue


# ---------------------------------------------------------------------------
# কমান্ড-style অ্যাডমিন handler
# ---------------------------------------------------------------------------


async def _ensure_admin(update: Update, db) -> bool:
    user = update.effective_user
    if user is None or not _is_admin(user.id, db):
        await _send(update, t("admin_only", db))
        return False
    return True


async def cmd_setviplink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/setviplink &lt;plan&gt; &lt;url&gt;</code>")
        return
    plan, url = args[0], args[1]
    links = db.get_setting("vip_links", {})
    links[plan] = url
    db.set_setting("vip_links", links)
    await _send(update, f"✅ <b>{plan}</b> লিংক সেট হয়েছে")


async def cmd_setplan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/setplan &lt;key&gt; name=... price=... days=...</code>")
        return
    key = args[0]
    plans = db.get_setting("vip_plans", {})
    plan = plans.get(key, {"name": key, "price": 0, "days": 30})
    for token in args[1:]:
        if "=" in token:
            k, v = token.split("=", 1)
            if k in {"price", "days"}:
                n = safe_int(v)
                if n is not None:
                    plan[k] = n
            else:
                plan[k] = v
    plans[key] = plan
    db.set_setting("vip_plans", plans)
    await _send(update, f"✅ প্ল্যান <b>{key}</b> আপডেট হয়েছে")


async def cmd_setpublic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/setpublic channel|group &lt;url&gt;</code>")
        return
    db.set_public_link(args[0], args[1])
    await _send(update, f"✅ {args[0]} লিংক সেট")


async def cmd_addpay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/addpay &lt;method&gt; &lt;number&gt; [hint]</code>")
        return
    method, number = args[0], args[1]
    hint = " ".join(args[2:])
    db.add_payment_method(method, number, hint)
    await _send(update, "✅ পেমেন্ট পদ্ধতি যোগ হয়েছে")


async def cmd_delpay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    idx = safe_int(args[0]) if args else None
    if idx is None:
        await _send(update, "ব্যবহার: <code>/delpay &lt;index&gt;</code>")
        return
    ok = db.remove_payment_method(idx - 1)
    await _send(update, "✅ মুছে ফেলা হয়েছে" if ok else "⚠️ পাওয়া যায়নি")


async def cmd_addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    uid = safe_int(args[0]) if args else None
    if uid is None:
        await _send(update, "ব্যবহার: <code>/addadmin &lt;user_id&gt;</code>")
        return
    extras = list(db.get_setting("extra_admins", []))
    if uid not in extras:
        extras.append(uid)
    db.set_setting("extra_admins", extras)
    await _send(update, f"✅ <code>{uid}</code> অ্যাডমিন হিসেবে যুক্ত")


async def cmd_deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    uid = safe_int(args[0]) if args else None
    if uid is None:
        await _send(update, "ব্যবহার: <code>/deladmin &lt;user_id&gt;</code>")
        return
    extras = [x for x in db.get_setting("extra_admins", []) if x != uid]
    db.set_setting("extra_admins", extras)
    await _send(update, f"✅ <code>{uid}</code> সরানো হয়েছে")


async def cmd_addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/addchannel &lt;chat_id&gt; [শিরোনাম]</code>")
        return
    chat_id = args[0]
    title = " ".join(args[1:]) if len(args) > 1 else ""
    db.add_ai_channel(chat_id, title=title)
    await _send(update, f"✅ চ্যানেল যুক্ত: <code>{chat_id}</code>")


async def cmd_delchannel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/delchannel &lt;chat_id&gt;</code>")
        return
    ok = db.delete_ai_channel(args[0])
    await _send(update, "✅" if ok else "⚠️ পাওয়া যায়নি")


async def cmd_setchprompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/setchprompt &lt;chat_id&gt; &lt;prompt&gt;</code>")
        return
    chat_id = args[0]
    prompt = " ".join(args[1:])
    upd = db.update_ai_channel(chat_id, prompt=prompt)
    await _send(update, "✅" if upd else "⚠️ চ্যানেল পাওয়া যায়নি")


async def cmd_addfb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/addfb &lt;page_id&gt; &lt;access_token&gt;</code>")
        return
    db.add_fb_page(args[0], access_token=args[1])
    await _send(update, "✅ FB পেজ যুক্ত")


async def cmd_delfb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/delfb &lt;page_id&gt;</code>")
        return
    ok = db.delete_fb_page(args[0])
    await _send(update, "✅" if ok else "⚠️ পাওয়া যায়নি")


async def cmd_addpromo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/addpromo &lt;text&gt;</code>")
        return
    pid = db.add_promo(" ".join(args))
    await _send(update, f"✅ প্রমো যুক্ত: <code>{pid}</code>")


async def cmd_delpromo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/delpromo &lt;id&gt;</code>")
        return
    ok = db.delete_promo(args[0])
    await _send(update, "✅" if ok else "⚠️ পাওয়া যায়নি")


async def cmd_sendpromo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/sendpromo &lt;id&gt;</code>")
        return
    promos = {p["id"]: p for p in db.list_promos()}
    p = promos.get(args[0])
    if not p:
        await _send(update, "⚠️ প্রমো পাওয়া যায়নি")
        return
    sent = 0
    for ch in db.list_ai_channels():
        if not ch.get("enabled"):
            continue
        try:
            await context.bot.send_message(
                chat_id=ch["id"], text=p["text"], parse_mode=ParseMode.HTML
            )
            sent += 1
        except Exception:  # noqa: BLE001
            continue
    await _send(update, f"✅ {sent} চ্যানেলে পাঠানো হয়েছে")


async def cmd_promointv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    n = safe_int(args[0]) if args else None
    if n is None or n < 1:
        await _send(update, "ব্যবহার: <code>/promointv &lt;minutes&gt;</code>")
        return
    db.set_setting("promo_interval_min", n)
    await _send(update, f"✅ প্রমো interval: {n} মিনিট\n<i>পরিবর্তনের জন্য restart দরকার।</i>", parse_mode=ParseMode.HTML)


async def cmd_addkick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/addkick &lt;chat_id&gt;</code>")
        return
    targets = list(db.get_setting("kick_targets", []))
    if args[0] not in targets:
        targets.append(args[0])
    db.set_setting("kick_targets", targets)
    await _send(update, "✅ যুক্ত")


async def cmd_delkick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/delkick &lt;chat_id&gt;</code>")
        return
    targets = [x for x in db.get_setting("kick_targets", []) if x != args[0]]
    db.set_setting("kick_targets", targets)
    await _send(update, "✅ মুছে ফেলা হয়েছে")


async def cmd_setui(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/setui &lt;key&gt; &lt;text&gt;</code>")
        return
    db.set_ui_text(args[0], " ".join(args[1:]))
    await _send(update, "✅ সেট হয়েছে")


async def cmd_setbtn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/setbtn &lt;key&gt; &lt;label&gt;</code>")
        return
    db.set_menu_button(args[0], " ".join(args[1:]))
    await _send(update, "✅ সেট হয়েছে")


async def cmd_addhelp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    raw = " ".join(context.args or [])
    if "|" not in raw:
        await _send(update, "ব্যবহার: <code>/addhelp &lt;title&gt; | &lt;text&gt;</code>")
        return
    title, body = raw.split("|", 1)
    items = list(db.list_help_items())
    items.append({"title": title.strip(), "text": body.strip()})
    db.set_help_items(items)
    await _send(update, "✅ যুক্ত")


async def cmd_clearhelp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    db.set_help_items([])
    await _send(update, "✅ Help আইটেম clear")


async def cmd_addebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    raw = " ".join(context.args or [])
    parts = [x.strip() for x in raw.split("|")]
    if len(parts) < 3:
        await _send(update, "ব্যবহার: <code>/addebook &lt;title&gt; | &lt;desc&gt; | &lt;price&gt;</code>\nতারপর ফাইল reply দিয়ে পাঠান")
        return
    title, desc, price_s = parts[0], parts[1], parts[2]
    price = safe_int(price_s) or 0
    eid = db.add_ebook(title, desc, price, is_free=(price == 0))
    context.user_data["pending_ebook_file"] = eid
    await _send(update, f"📝 ই-বুক তৈরি: <code>{eid}</code>\nএখন ফাইল reply দিয়ে পাঠান (ফ্রি/পেইড উভয়ের জন্য)।")


async def cmd_editebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if len(args) < 2:
        await _send(update, "ব্যবহার: <code>/editebook &lt;id&gt; field=value ...</code>\nfields: title, description, price, is_free, active, link")
        return
    eid = args[0]
    fields: dict = {}
    for token in args[1:]:
        if "=" in token:
            k, v = token.split("=", 1)
            if k == "price":
                fields[k] = safe_int(v) or 0
            elif k in {"is_free", "active"}:
                fields[k] = v.lower() in {"1", "true", "yes", "y"}
            else:
                fields[k] = v
    upd = db.update_ebook(eid, **fields)
    await _send(update, "✅" if upd else "⚠️ পাওয়া যায়নি")


async def cmd_delebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data["db"]
    if not await _ensure_admin(update, db):
        return
    args = context.args or []
    if not args:
        await _send(update, "ব্যবহার: <code>/delebook &lt;id&gt;</code>")
        return
    ok = db.delete_ebook(args[0])
    await _send(update, "✅" if ok else "⚠️ পাওয়া যায়নি")


async def on_admin_ebook_file(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> bool:
    db = context.bot_data["db"]
    user = update.effective_user
    msg = update.effective_message
    if user is None or msg is None or not _is_admin(user.id, db):
        return False
    eid = context.user_data.get("pending_ebook_file")
    if not eid:
        return False
    file_id = ""
    if msg.document:
        file_id = msg.document.file_id
    elif msg.photo:
        file_id = msg.photo[-1].file_id
    elif msg.video:
        file_id = msg.video.file_id
    if not file_id:
        return False
    db.update_ebook(eid, file_id=file_id)
    context.user_data.pop("pending_ebook_file", None)
    await msg.reply_text(f"✅ ফাইল সংযুক্ত করা হয়েছে: <code>{eid}</code>", parse_mode=ParseMode.HTML)
    return True


async def on_manual_vip_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """`adm:vip:manual_plan:<uid>:<key>` callback হ্যান্ডলার।"""
    db = context.bot_data["db"]
    query = update.callback_query
    if query is None:
        return
    if not _is_admin(update.effective_user.id, db):
        await query.answer(t("admin_only", db), show_alert=True)
        return
    await query.answer()
    parts = (query.data or "").split(":")
    # adm:vip:manual_plan:<uid>:<key>
    if len(parts) < 5:
        return
    uid = safe_int(parts[3])
    key = parts[4]
    plan = db.get_setting("vip_plans", {}).get(key)
    if uid is None or not plan:
        return
    days = plan.get("days", 30)
    db.grant_vip(uid, key, days)
    try:
        link = db.get_setting("vip_links", {}).get(key, "")
        await context.bot.send_message(
            chat_id=uid,
            text=t(
                "vip_approved",
                db,
                plan=plan.get("name", key),
                expiry=fmt_ts(int(time.time()) + days * 86400),
                links=(f"🔗 {link}" if link else ""),
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception:  # noqa: BLE001
        pass
    await _send(update, f"✅ <code>{uid}</code> কে <b>{plan.get('name', key)}</b> দেওয়া হয়েছে")
