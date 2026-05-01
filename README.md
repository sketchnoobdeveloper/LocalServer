# 🤖 কামপণ্ডিত বট

একটি সম্পূর্ণ বাংলা Telegram বট — VIP সদস্যপদ, ই-বুক বিক্রয়, AI অটো-পোস্ট ও অ্যাডমিন প্যানেল সহ।

## ✨ ফিচার

### ইউজার
- 💎 **ভিআইপি সদস্যপদ** (লাইফটাইম, বার্ষিক, মাসিক — দাম কাস্টমাইজযোগ্য)
- 📚 **ই-বুক স্টোর** — ফ্রি ও পেইড উভয় ধরনের
- 💬 **সাপোর্ট** — সরাসরি অ্যাডমিনের কাছে বার্তা
- 🎬 **ডেমো** — VIP কনটেন্টের preview
- 📢 **পাবলিক চ্যানেল/গ্রুপ** লিংক
- 👤 **আমার অ্যাকাউন্ট** — VIP স্ট্যাটাস, মেয়াদ, অর্ডার ইতিহাস

### অ্যাডমিন প্যানেল
- 👥 **সদস্য ব্যবস্থাপনা** — তালিকা, ব্রডকাস্ট, ব্যান, আনব্যান, মুছুন
- 💎 **VIP ব্যবস্থাপনা** — পেন্ডিং অর্ডার, ম্যানুয়াল VIP, ট্রায়াল, লিংক, অটো-কিক
- 📚 **ই-বুক ব্যবস্থাপনা** — পেন্ডিং অর্ডার, যুক্ত/মুছুন/এডিট
- 🤖 **এআই অটো-পোস্ট** — মাল্টি-চ্যানেল, প্রম্পট, রোল, ৩টি টেক্সট AI, ৩টি ইমেজ AI
- ⚙️ **সেটিংস** — অটো-রিয়েক্ট, গ্রুপ মোড, ইউআই টেক্সট, পেমেন্ট, পাবলিক লিংক
- 🗄️ **সিস্টেম** — JSON ব্যাকআপ/রিস্টোর, AI চ্যাটবট পরীক্ষা

### AI
- **টেক্সট:** Google AI Studio (Gemini), OpenRouter, Custom OpenAI-compatible
- **ইমেজ:** GhostWeb (infip.pro), Pollinations.ai (free fallback), অথবা ছাড়া
- **প্রম্পট:** একক বা মাল্টি-টপিক, Undo/Redo (১০ স্তর), চ্যানেল-ভিত্তিক override

### ডেটাবেজ
- **JSON** (ডিফল্ট) — কোনো সেটআপ ছাড়াই কাজ করে (`data.json`)
- **MongoDB** — `MONGO_URI` সেট করলে
- **Firebase RTDB** — `FIREBASE_URL` সেট করলে

---

## 🚀 দ্রুত শুরু (Render)

### ১. Bot Token নিন
[@BotFather](https://t.me/BotFather) থেকে নতুন বট তৈরি করে token নিন।

### ২. Render এ deploy
এই রিপোটি GitHub এ থাকলে Render → "New Web Service" → এই রিপো বেছে নিন।
`render.yaml` automatically পিক হবে।

### ৩. Environment variables
| Key | Value |
|-----|-------|
| `BOT_TOKEN` | আপনার BotFather token |
| `ADMIN_IDS` | আপনার Telegram ID (একাধিক হলে কমা দিয়ে) |
| `RENDER_EXTERNAL_URL` | Render-এ build হওয়ার পর URL (যেমন `https://kampondit-bot.onrender.com`) |
| `PORT` | `10000` (default) |
| `GOOGLE_AI_KEY` | (optional) Gemini API key |
| `OPENROUTER_KEY` | (optional) |
| `GHOSTWEB_KEY` | (optional) ইমেজ AI |
| `DB_KIND` | `json` (default), `mongo`, বা `firebase` |
| `MONGO_URI` | mongo backend এর জন্য |
| `FIREBASE_URL` | firebase backend এর জন্য |
| `FIREBASE_CREDENTIALS` | service-account JSON-এর path |

### ৪. UptimeRobot (Render free plan-এ sleep এড়াতে)
- URL: `https://your-app.onrender.com/ping`
- Interval: 5 minutes

### ৫. বটে `/start` দিয়ে শুরু করুন
আপনার ID `ADMIN_IDS` এ থাকলে `/admin` দিয়ে অ্যাডমিন প্যানেলে ঢুকতে পারবেন।

---

## 🖥️ স্থানীয়ভাবে চালু

```bash
git clone https://github.com/sketchnoobdeveloper/LocalServer.git
cd LocalServer
pip install -r requirements.txt

cp .env.example .env  # নিজের মান বসান
export BOT_TOKEN=...
export ADMIN_IDS=123456789
python bot.py
```

`RENDER_EXTERNAL_URL` সেট না থাকলে polling মোডে চালু হবে।

---

## 🔄 ম্যানেজমেন্ট কমান্ড (অ্যাডমিনদের জন্য)

| কমান্ড | কাজ |
|--------|-----|
| `/start` | মেনু খুলুন |
| `/admin` | অ্যাডমিন প্যানেল |
| `/id` | আপনার Telegram ID |
| `/setviplink <plan> <url>` | VIP লিংক সেট |
| `/setplan <key> name=... price=... days=...` | প্ল্যান edit |
| `/setpublic channel|group <url>` | পাবলিক লিংক |
| `/addpay <method> <number> [hint]` | পেমেন্ট পদ্ধতি |
| `/addadmin <id>` `/deladmin <id>` | অ্যাডমিন যোগ/সরান |
| `/addchannel <chat_id> [title]` | AI চ্যানেল যোগ |
| `/setchprompt <chat_id> <prompt>` | চ্যানেল প্রম্পট |
| `/addpromo <text>` `/sendpromo <id>` | প্রমো |
| `/addkick <chat_id>` | কিক টার্গেট |
| `/setui <key> <text>` | ইউআই টেক্সট override |
| `/setbtn <key> <label>` | বাটন লেবেল override |
| `/addebook <title> | <desc> | <price>` | ই-বুক যোগ (price=0 → ফ্রি) |
| `/editebook <id> field=value ...` | ই-বুক edit |
| `/delebook <id>` | ই-বুক মুছুন |

---

## 📡 হেলথ এন্ডপয়েন্ট

| Path | কাজ |
|------|-----|
| `/` | OK |
| `/ping` | OK (UptimeRobot এখানে পিং দেয়) |
| `/health` | OK |
| `/status` | JSON: bot username, status |

---

## 🧰 আর্কিটেকচার

```
bot.py             — entry point, scheduler ও server চালু
config.py          — env var loader
strings_bn.py      — সব বাংলা ইউআই টেক্সট ও বাটন লেবেল
database.py        — JSON/Mongo/Firebase backend abstraction
ai_providers.py    — টেক্সট ও ইমেজ AI
auto_post.py       — AI পোস্ট সাইকেল
scheduler.py       — APScheduler জব (trial/VIP/auto-post/promo/scheduled msgs)
server.py          — aiohttp health endpoints + Telegram webhook
keyboards.py       — সব InlineKeyboard
handlers_user.py   — ইউজার-ফেসিং হ্যান্ডলার
handlers_admin.py  — অ্যাডমিন প্যানেল হ্যান্ডলার
utils.py           — সাধারণ helper
```

---

## 📜 লাইসেন্স

কামপণ্ডিত টিম © ২০২৬
