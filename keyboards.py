"""সব inline keyboard বিল্ডার এক জায়গায়।"""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from strings_bn import b


def _b(label: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(label, callback_data=data)


def main_menu_kb(db) -> InlineKeyboardMarkup:
    rows = [
        [_b(b("vip", db), "user:vip"), _b(b("ebooks", db), "user:ebooks")],
        [_b(b("support", db), "user:support"), _b(b("demo", db), "user:demo")],
        [_b(b("public_links", db), "user:public")],
        [_b(b("account", db), "user:account")],
    ]
    return InlineKeyboardMarkup(rows)


def vip_plans_kb(db) -> InlineKeyboardMarkup:
    plans = db.get_setting("vip_plans", {})
    rows = []
    keymap = {
        "lifetime": "plan_lifetime",
        "yearly": "plan_yearly",
        "monthly": "plan_monthly",
    }
    for key, plan in plans.items():
        label_key = keymap.get(key, "vip")
        label = b(label_key, db, price=plan.get("price", "?"))
        rows.append([_b(label, f"user:vip:plan:{key}")])
    rows.append([_b(b("back", db), "user:menu")])
    return InlineKeyboardMarkup(rows)


def ebook_list_kb(db, ebooks: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for eb in ebooks:
        tag = "🆓" if eb.get("is_free") else f"৳{eb.get('price', 0)}"
        rows.append([_b(f"{tag} {eb.get('title', 'ই-বুক')}", f"user:eb:{eb['id']}")])
    rows.append([_b(b("back", db), "user:menu")])
    return InlineKeyboardMarkup(rows)


def admin_root_kb(db) -> InlineKeyboardMarkup:
    rows = [
        [_b(b("adm_members", db), "adm:members")],
        [_b(b("adm_vip", db), "adm:vip")],
        [_b(b("adm_ebooks", db), "adm:ebooks")],
        [_b(b("adm_ai", db), "adm:ai")],
        [_b(b("adm_settings", db), "adm:settings")],
        [_b(b("adm_system", db), "adm:system")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_members_kb(db) -> InlineKeyboardMarkup:
    rows = [
        [_b(b("adm_user_list", db), "adm:members:list")],
        [_b(b("adm_msg_center", db), "adm:members:msg")],
        [_b(b("adm_ban", db), "adm:members:ban"),
         _b(b("adm_unban", db), "adm:members:unban")],
        [_b(b("adm_delete_user", db), "adm:members:del")],
        [_b(b("back", db), "adm:root")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_vip_kb(db) -> InlineKeyboardMarkup:
    auto_kick = db.get_setting("auto_kick", True)
    rows = [
        [_b(b("adm_vip_pending", db), "adm:vip:pending")],
        [_b(b("adm_vip_list", db), "adm:vip:list")],
        [_b(b("adm_trial", db), "adm:vip:trial")],
        [_b(b("adm_vip_links", db), "adm:vip:links")],
        [_b(
            b("adm_autokick" if auto_kick else "adm_autokick_off", db),
            "adm:vip:autokick",
        )],
        [_b(b("adm_kick_settings", db), "adm:vip:kicks")],
        [_b(b("back", db), "adm:root")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_ebooks_kb(db) -> InlineKeyboardMarkup:
    rows = [
        [_b(b("adm_ebook_pending", db), "adm:ebooks:pending")],
        [_b(b("adm_ebook_manage", db), "adm:ebooks:manage")],
        [_b(b("back", db), "adm:root")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_ai_kb(db) -> InlineKeyboardMarkup:
    auto_post = db.get_setting("auto_post", False)
    auto_promo = db.get_setting("auto_promo", False)
    rows = [
        [_b(b("adm_ai_channels", db), "adm:ai:channels"),
         _b(b("adm_ai_fb", db), "adm:ai:fb")],
        [_b(b("adm_ai_prompt", db), "adm:ai:prompt"),
         _b(b("adm_ai_role", db), "adm:ai:role")],
        [_b(b("adm_ai_text", db), "adm:ai:text"),
         _b(b("adm_ai_image", db), "adm:ai:image")],
        [_b(b("adm_ai_schedule", db), "adm:ai:schedule")],
        [_b(
            b("adm_ai_toggle_on" if auto_post else "adm_ai_toggle_off", db),
            "adm:ai:toggle",
        )],
        [_b(b("adm_ai_promo", db), "adm:ai:promo")],
        [_b(
            b("adm_ai_promo_on" if auto_promo else "adm_ai_promo_off", db),
            "adm:ai:promo_toggle",
        )],
        [_b(b("adm_ai_now", db), "adm:ai:now"),
         _b(b("adm_ai_push", db), "adm:ai:push")],
        [_b(b("back", db), "adm:root")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_settings_kb(db) -> InlineKeyboardMarkup:
    react = db.get_setting("auto_react", False)
    group = db.get_setting("group_mode", False)
    bot_on = db.get_setting("bot_enabled", True)
    rows = [
        [_b(
            b("adm_set_react_on" if react else "adm_set_react_off", db),
            "adm:set:react",
        )],
        [_b(
            b("adm_set_group_on" if group else "adm_set_group_off", db),
            "adm:set:group",
        )],
        [_b(
            b("adm_set_bot_on" if bot_on else "adm_set_bot_off", db),
            "adm:set:bot",
        )],
        [_b(b("adm_set_ui_text", db), "adm:set:ui"),
         _b(b("adm_set_menu_btn", db), "adm:set:menu")],
        [_b(b("adm_set_vip", db), "adm:set:vip"),
         _b(b("adm_set_vip_links", db), "adm:set:viplinks")],
        [_b(b("adm_set_help", db), "adm:set:help"),
         _b(b("adm_set_public", db), "adm:set:public")],
        [_b(b("adm_set_demo", db), "adm:set:demo"),
         _b(b("adm_set_payment", db), "adm:set:payment")],
        [_b(b("adm_set_admins", db), "adm:set:admins")],
        [_b(b("back", db), "adm:root")],
    ]
    return InlineKeyboardMarkup(rows)


def admin_system_kb(db) -> InlineKeyboardMarkup:
    rows = [
        [_b(b("adm_sys_backup", db), "adm:sys:backup"),
         _b(b("adm_sys_restore", db), "adm:sys:restore")],
        [_b(b("adm_sys_db", db), "adm:sys:db")],
        [_b(b("adm_sys_chatbot", db), "adm:sys:chat")],
        [_b(b("back", db), "adm:root")],
    ]
    return InlineKeyboardMarkup(rows)


def back_kb(db, target: str = "user:menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[_b(b("back", db), target)]])


def approve_reject_kb(prefix: str, oid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                _b("✅ অনুমোদন", f"{prefix}:approve:{oid}"),
                _b("❌ প্রত্যাখ্যান", f"{prefix}:reject:{oid}"),
            ]
        ]
    )


def trial_duration_kb() -> InlineKeyboardMarkup:
    rows = [
        [_b("৫ মিনিট", "adm:trial:dur:5m"), _b("৭ দিন", "adm:trial:dur:7d")],
        [_b("১৪ দিন", "adm:trial:dur:14d"), _b("২১ দিন", "adm:trial:dur:21d")],
        [_b("⌨️ কাস্টম", "adm:trial:dur:custom")],
        [InlineKeyboardButton("🔙 পেছনে", callback_data="adm:vip")],
    ]
    return InlineKeyboardMarkup(rows)
