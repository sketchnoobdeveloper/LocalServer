"""কামপণ্ডিত বটের সব বাংলা টেক্সট ও বাটন লেবেল।

অ্যাডমিন প্যানেলের ⚙️ সেটিংস → ✍️ ইউআই টেক্সট ও 🔲 মেনু বাটন থেকে
এই ভ্যালুগুলো DB তে override করা যায় (`ui_texts` ও `menu_buttons` কী)।
"""

from __future__ import annotations

DEFAULT_UI_TEXTS: dict[str, str] = {
    "welcome": (
        "আসসালামু আলাইকুম! আমি <b>কামপণ্ডিত বট</b> 🤖\n\n"
        "এখানে পাবেন VIP চ্যানেল, প্রিমিয়াম ই-বুক ও AI-চালিত কন্টেন্ট।\n"
        "নিচের মেনু থেকে আপনার পছন্দের অপশন বেছে নিন।"
    ),
    "vip_intro": (
        "💎 <b>ভিআইপি সদস্যপদ</b>\n\n"
        "ভিআইপি হলে পাবেন: প্রিমিয়াম চ্যানেল ও গ্রুপ অ্যাক্সেস, "
        "একচেটিয়া কন্টেন্ট, এবং সরাসরি অ্যাডমিন সাপোর্ট।\n\n"
        "নিচ থেকে আপনার পছন্দের প্ল্যান বেছে নিন:"
    ),
    "payment_guide": (
        "💳 <b>পেমেন্ট নির্দেশিকা</b>\n\n"
        "১️⃣ নিচের যেকোনো নম্বরে <b>{amount}৳</b> Send Money করুন\n"
        "২️⃣ পেমেন্টের <b>স্ক্রিনশট</b> এই চ্যাটে পাঠান\n"
        "৩️⃣ অ্যাডমিন approve করার পর VIP লিংক পাবেন\n\n"
        "{methods}\n\n"
        "<i>সমস্যায় পড়লে 💬 সাপোর্ট মেনুতে যান।</i>"
    ),
    "no_payment_methods": (
        "⚠️ এখনো কোনো পেমেন্ট পদ্ধতি সেট করা হয়নি। "
        "অ্যাডমিন কনফিগার করার পর আবার চেষ্টা করুন।"
    ),
    "screenshot_received": (
        "✅ আপনার পেমেন্ট স্ক্রিনশট পেয়েছি।\n"
        "অ্যাডমিন verify করার পর আপনাকে জানানো হবে। ধন্যবাদ!"
    ),
    "ebooks_intro": (
        "📚 <b>ই-বুক স্টোর</b>\n\n"
        "আমাদের কালেকশন থেকে যেকোনো ই-বুক বেছে নিন।\n"
        "ফ্রি ই-বুক চ্যানেলে যোগ দিলেই পাবেন। পেইড ই-বুক পেমেন্টের পরে।"
    ),
    "no_ebooks": "📭 এখনো কোনো ই-বুক যুক্ত করা হয়নি।",
    "support_text": (
        "💬 <b>সাপোর্ট</b>\n\n"
        "আপনার প্রশ্ন বা সমস্যা এই চ্যাটে লিখে পাঠান। "
        "অ্যাডমিন দ্রুততম সময়ে আপনাকে উত্তর দেবেন।"
    ),
    "support_sent": "✅ আপনার বার্তাটি অ্যাডমিনকে পাঠানো হয়েছে।",
    "demo_default": (
        "🎬 এখনো কোনো ডেমো কন্টেন্ট সেট করা হয়নি।\n"
        "অ্যাডমিন শীঘ্রই যুক্ত করবেন।"
    ),
    "public_links_default": (
        "📢 এখনো কোনো পাবলিক চ্যানেল/গ্রুপ লিংক সেট করা হয়নি।"
    ),
    "account_template": (
        "👤 <b>আপনার অ্যাকাউন্ট</b>\n\n"
        "🆔 ID: <code>{user_id}</code>\n"
        "👤 নাম: {name}\n"
        "💎 VIP স্ট্যাটাস: {vip_status}\n"
        "📅 মেয়াদ: {expiry}\n"
        "🛒 অর্ডার: {orders}টি"
    ),
    "vip_active": "✅ সক্রিয়",
    "vip_inactive": "❌ নিষ্ক্রিয়",
    "vip_expired": "⏰ মেয়াদ শেষ",
    "vip_trial": "🎫 ট্রায়াল",
    "banned_user": (
        "🚫 দুঃখিত, আপনাকে এই বটে ব্যান করা হয়েছে।"
    ),
    "bot_disabled": (
        "🔒 বটটি বর্তমানে রক্ষণাবেক্ষণে আছে। অনুগ্রহ করে কিছুক্ষণ পরে আবার চেষ্টা করুন।"
    ),
    "admin_only": "⛔ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য।",
    "admin_panel": (
        "🛠️ <b>অ্যাডমিন প্যানেল</b>\n\n"
        "নিচের সেকশনগুলো থেকে আপনার পছন্দের অপশন বেছে নিন।"
    ),
    "vip_approved": (
        "🎉 অভিনন্দন! আপনার <b>{plan}</b> VIP সদস্যপদ অনুমোদিত হয়েছে।\n\n"
        "মেয়াদ: <b>{expiry}</b> পর্যন্ত\n\n"
        "{links}"
    ),
    "vip_rejected": (
        "❌ দুঃখিত, আপনার VIP request বাতিল করা হয়েছে।\n"
        "কারণ: {reason}\n\n"
        "প্রশ্ন থাকলে 💬 সাপোর্ট এ যোগাযোগ করুন।"
    ),
    "vip_expiring_soon": (
        "⏰ আপনার VIP মেয়াদ <b>{days}</b> দিনের মধ্যে শেষ হবে।\n"
        "নবায়নের জন্য 💎 ভিআইপি মেনুতে যান।"
    ),
    "vip_expired_msg": (
        "❗ আপনার VIP মেয়াদ শেষ হয়েছে। চ্যানেল থেকে remove করা হয়েছে।\n"
        "নবায়নের জন্য 💎 ভিআইপি মেনুতে যান।"
    ),
    "trial_welcome": (
        "🎉 অভিনন্দন! আপনি <b>{duration}</b> ট্রায়াল VIP অ্যাক্সেস পেয়েছেন।\n\n"
        "{links}\n\n"
        "<i>মেয়াদ শেষে স্বয়ংক্রিয়ভাবে remove করা হবে।</i>"
    ),
    "ebook_approved": (
        "📥 আপনার <b>{title}</b> ই-বুক অর্ডার অনুমোদিত হয়েছে।\n"
        "ফাইল/লিংক নিচে দেওয়া হলো।"
    ),
}

DEFAULT_MENU_BUTTONS: dict[str, str] = {
    # ইউজার মেনু
    "vip": "💎 ভিআইপি সদস্যপদ",
    "ebooks": "📚 ই-বুক স্টোর",
    "support": "💬 সাপোর্ট",
    "demo": "🎬 ডেমো",
    "public_links": "📢 পাবলিক চ্যানেল/গ্রুপ",
    "account": "👤 আমার অ্যাকাউন্ট",
    "back": "🔙 পেছনে",
    # VIP
    "plan_lifetime": "🌟 লাইফটাইম — ৳{price}",
    "plan_yearly": "🗓️ বার্ষিক — ৳{price}",
    "plan_monthly": "📅 মাসিক — ৳{price}",
    # অ্যাডমিন প্যানেল সেকশন
    "adm_members": "👥 সদস্য ব্যবস্থাপনা",
    "adm_vip": "💎 VIP ব্যবস্থাপনা",
    "adm_ebooks": "📚 ই-বুক ব্যবস্থাপনা",
    "adm_ai": "🤖 এআই অটো-পোস্ট",
    "adm_settings": "⚙️ সেটিংস",
    "adm_system": "🗄️ সিস্টেম ও ডেটাবেজ",
    # অ্যাডমিন → সদস্য
    "adm_user_list": "👥 ব্যবহারকারী তালিকা",
    "adm_msg_center": "📨 বার্তা কেন্দ্র",
    "adm_ban": "🚫 ব্যান করুন",
    "adm_unban": "✅ আনব্যান করুন",
    "adm_delete_user": "🗑️ সদস্য মুছুন",
    # অ্যাডমিন → VIP
    "adm_vip_pending": "⏳ VIP অনুমোদন",
    "adm_vip_list": "💎 VIP সদস্য তালিকা",
    "adm_trial": "🎫 ট্রায়াল দিন",
    "adm_vip_links": "🔗 VIP লিংক সেটিংস",
    "adm_autokick": "🟢 অটো-কিক চালু",
    "adm_autokick_off": "🔴 অটো-কিক বন্ধ",
    "adm_kick_settings": "⚙️ কিক সেটিংস",
    # অ্যাডমিন → ই-বুক
    "adm_ebook_pending": "📚 ই-বুক অনুমোদন",
    "adm_ebook_manage": "📖 ই-বুক পরিচালনা",
    # অ্যাডমিন → AI
    "adm_ai_channels": "📢 টেলিগ্রাম চ্যানেল",
    "adm_ai_fb": "📘 ফেসবুক পেজ",
    "adm_ai_prompt": "📝 প্রম্পট",
    "adm_ai_role": "🎭 এআই রোল",
    "adm_ai_text": "🧠 টেক্সট এআই",
    "adm_ai_image": "🖼️ ইমেজ এআই",
    "adm_ai_schedule": "⏰ শিডিউল",
    "adm_ai_toggle_on": "🟢 অটো-পোস্ট চালু",
    "adm_ai_toggle_off": "🔴 অটো-পোস্ট বন্ধ",
    "adm_ai_promo": "📣 প্রমো বার্তা",
    "adm_ai_promo_on": "🟢 প্রমো চালু",
    "adm_ai_promo_off": "🔴 প্রমো বন্ধ",
    "adm_ai_now": "✍️ এখনই পোস্ট",
    "adm_ai_push": "🚀 চ্যানেলে পাঠান",
    # অ্যাডমিন → সেটিংস
    "adm_set_react_on": "🟢 অটো-রিয়েক্ট চালু",
    "adm_set_react_off": "🔴 অটো-রিয়েক্ট বন্ধ",
    "adm_set_group_on": "🟢 গ্রুপ মোড চালু",
    "adm_set_group_off": "🔴 গ্রুপ মোড বন্ধ",
    "adm_set_bot_on": "🟢 বট চালু",
    "adm_set_bot_off": "🔴 বট বন্ধ",
    "adm_set_ui_text": "✍️ ইউআই টেক্সট",
    "adm_set_menu_btn": "🔲 মেনু বাটন",
    "adm_set_vip": "💎 ভিআইপি সেটিংস",
    "adm_set_vip_links": "🔗 ভিআইপি লিংক",
    "adm_set_help": "ℹ️ সাহায্য আইটেম",
    "adm_set_public": "📢 পাবলিক লিংক",
    "adm_set_demo": "🎬 ডেমো সেটিংস",
    "adm_set_payment": "💳 পেমেন্ট",
    "adm_set_admins": "🔑 অ্যাডমিন তালিকা",
    # অ্যাডমিন → সিস্টেম
    "adm_sys_backup": "💾 ব্যাকআপ",
    "adm_sys_restore": "📥 রিস্টোর",
    "adm_sys_db": "🗄️ ডেটাবেজ",
    "adm_sys_chatbot": "🤖 চ্যাটবট পরীক্ষা",
}


def t(key: str, db=None, **fmt) -> str:
    """ইউআই টেক্সট রিটার্ন করে; DB তে override থাকলে সেটি ব্যবহার করে।"""
    base = DEFAULT_UI_TEXTS.get(key, key)
    if db is not None:
        try:
            override = db.get_ui_text(key)
            if override:
                base = override
        except Exception:
            pass
    if fmt:
        try:
            return base.format(**fmt)
        except Exception:
            return base
    return base


def b(key: str, db=None, **fmt) -> str:
    """মেনু বাটন লেবেল রিটার্ন করে; DB তে override থাকলে সেটি ব্যবহার করে।"""
    base = DEFAULT_MENU_BUTTONS.get(key, key)
    if db is not None:
        try:
            override = db.get_menu_button(key)
            if override:
                base = override
        except Exception:
            pass
    if fmt:
        try:
            return base.format(**fmt)
        except Exception:
            return base
    return base
