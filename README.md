# LocalServer — Two projects in one repo

This repository now hosts **two independent projects** that share a single git
history but have separate runtimes, build systems, and roadmaps:

| Project | Folder | Stack | What it does |
|---|---|---|---|
| 🤖 **কমপণডত বট** (KamPondit Bot) | repo root (`bot.py`, `handlers_*.py`, `database.py`, …) | Python 3 · aiogram · aiohttp · APScheduler | Bengali Telegram bot — VIP membership, e-book store, AI auto-post, admin panel |
| 🛡️ **SND Shield** | `app/` | Java · AndroidIDE · Gradle 8.4 / AGP 8.2.2 | Android app — anti-spam / anti-bomber defense, neomorphism Day/Night UI |

The two projects do not depend on each other. You can ignore either folder if you only care about the other.

Jump to: [KamPondit Bot](#-কমপণডত-বট) · [SND Shield](#-snd-shield--anti-spam--anti-bomber-defense)

---

# 🤖কমপণডত বট

একট সমপরণ বল Telegram বট — VIP সদসযপদ, ই-বক বকরয, AI অট-পসট ও অযডমন পযনল সহ।

## ✨ফচর

### ইউজর
- 💎**ভআইপ সদসযপদ** (লইফটইম, বরষক, মসক — দম কসটমইজযগয)
- 📚**ই-বক সটর** — ফর ও পইড উভয ধরনর
- 💬**সপরট** — সরসর অযডমনর কছ বরত
- 🎬**ডম** — VIP কনটনটর preview
- 📢**পবলক চযনল/গরপ** লক
- 👤**আমর অযকউনট** — VIP সটযটস, মযদ, অরডর ইতহস

### অযডমন পযনল
- 👥**সদসয বযবসথপন** — তলক, বরডকসট, বযন, আনবযন, মছন
- 💎**VIP বযবসথপন** — পনড অরডর, মযনযল VIP, টরযল, লক, অট-কক
- 📚**ই-বক বযবসথপন** — পনড অরডর, যকত/মছন/এডট
- 🤖**এআই অট-পসট** — মলট-চযনল, পরমপট, রল, ৩ট টকসট AI, ৩ট ইমজ AI
- ⚙ **সটস** — অট-রযকট, গরপ মড, ইউআই টকসট, পমনট, পবলক লক
- 🗄 **সসটম** — JSON বযকআপ/রসটর, AI চযটবট পরকষ

### AI
- **টকসট:** Google AI Studio (Gemini), OpenRouter, Custom OpenAI-compatible
- **ইমজ:** GhostWeb (infip.pro), Pollinations.ai (free fallback), অথব ছড
- **পরমপট:** একক ব মলট-টপক, Undo/Redo (১০ সতর), চযনল-ভততক override

### ডটবজ
- **JSON** (ডফলট) — কন সটআপ ছডই কজ কর (`data.json`)
- **MongoDB** — `MONGO_URI` সট করল
- **Firebase RTDB** — `FIREBASE_URL` সট করল

---

## 🚀দরত শর (Render)

### ১. Bot Token নন
[@BotFather](https://t.me/BotFather) থক নতন বট তর কর token নন।

### ২. Render এ deploy
এই রপট GitHub এ থকল Render → "New Web Service" → এই রপ বছ নন।
`render.yaml` automatically পক হব।

### ৩. Environment variables
| Key | Value |
|-----|-------|
| `BOT_TOKEN` | আপনর BotFather token |
| `ADMIN_IDS` | আপনর Telegram ID (একধক হল কম দয) |
| `RENDER_EXTERNAL_URL` | Render-এ build হওযর পর URL (যমন `https://kampondit-bot.onrender.com`) |
| `PORT` | `10000` (default) |
| `GOOGLE_AI_KEY` | (optional) Gemini API key |
| `OPENROUTER_KEY` | (optional) |
| `GHOSTWEB_KEY` | (optional) ইমজ AI |
| `DB_KIND` | `json` (default), `mongo`, ব `firebase` |
| `MONGO_URI` | mongo backend এর জনয |
| `FIREBASE_URL` | firebase backend এর জনয |
| `FIREBASE_CREDENTIALS` | service-account JSON-এর path |

### ৪. UptimeRobot (Render free plan-এ sleep এডত)
- URL: `https://your-app.onrender.com/ping`
- Interval: 5 minutes

### ৫. বট `/start` দয শর করন
আপনর ID `ADMIN_IDS` এ থকল `/admin` দয অযডমন পযনল ঢকত পরবন।

---

## 🖥 সথনযভব চল

```bash
git clone https://github.com/sketchnoobdeveloper/LocalServer.git
cd LocalServer
pip install -r requirements.txt

cp .env.example .env  # নজর মন বসন
export BOT_TOKEN=...
export ADMIN_IDS=123456789
python bot.py
```

`RENDER_EXTERNAL_URL` সট ন থকল polling মড চল হব।

---

## 🔄মযনজমনট কমনড (অযডমনদর জনয)

| কমনড | কজ |
|--------|-----|
| `/start` | মন খলন |
| `/admin` | অযডমন পযনল |
| `/id` | আপনর Telegram ID |
| `/setviplink <plan> <url>` | VIP লক সট |
| `/setplan <key> name=... price=... days=...` | পলযন edit |
| `/setpublic channel|group <url>` | পবলক লক |
| `/addpay <method> <number> [hint]` | পমনট পদধত |
| `/addadmin <id>` `/deladmin <id>` | অযডমন যগ/সরন |
| `/addchannel <chat_id> [title]` | AI চযনল যগ |
| `/setchprompt <chat_id> <prompt>` | চযনল পরমপট |
| `/addpromo <text>` `/sendpromo <id>` | পরম |
| `/addkick <chat_id>` | কক টরগট |
| `/setui <key> <text>` | ইউআই টকসট override |
| `/setbtn <key> <label>` | বটন লবল override |
| `/addebook <title> | <desc> | <price>` | ই-বক যগ (price=0 → ফর) |
| `/editebook <id> field=value ...` | ই-বক edit |
| `/delebook <id>` | ই-বক মছন |

---

## 📡হলথ এনডপযনট

| Path | কজ |
|------|-----|
| `/` | OK |
| `/ping` | OK (UptimeRobot এখন প দয) |
| `/health` | OK |
| `/status` | JSON: bot username, status |

---

## 🧰আরকটকচর

```
bot.py             — entry point, scheduler ও server চল
config.py          — env var loader
strings_bn.py      — সব বল ইউআই টকসট ও বটন লবল
database.py        — JSON/Mongo/Firebase backend abstraction
ai_providers.py    — টকসট ও ইমজ AI
auto_post.py       — AI পসট সইকল
scheduler.py       — APScheduler জব (trial/VIP/auto-post/promo/scheduled msgs)
server.py          — aiohttp health endpoints + Telegram webhook
keyboards.py       — সব InlineKeyboard
handlers_user.py   — ইউজর-ফস হযনডলর
handlers_admin.py  — অযডমন পযনল হযনডলর
utils.py           — সধরণ helper
```

---

## 📜লইসনস

কমপণডত টম © ২০২৬

---

# 🛡️ SND Shield — Anti-Spam / Anti-Bomber Defense

**Package:** `snd.shield`
**Min SDK:** 21 &nbsp;·&nbsp; **Target SDK:** 34 &nbsp;·&nbsp; **Java:** 17 &nbsp;·&nbsp; **AGP:** 8.2.2

A neomorphism (day & night) Android frontend that helps users **defend against spam, repeat unknown calls, phishing emails, and SMS / WhatsApp bombing** — the opposite direction of an attack tool. Reports spam to a community DB, applies block / allow rules, and surfaces incoming-flood analytics.

> The repo's original `isArmProtectorUpdate.json` is preserved at the root and is now consumed by `InAppUpdateActivity` for update checks.

## Activities (13)

| Activity | Purpose |
|---|---|
| `SplashActivity` | Animated logo entrance, auth-state routing |
| `LoginActivity` | Email + password login, Google / Facebook stubs, animated input toggles |
| `ManageToolsActivity` | Main dashboard hub — neomorphism grid of all tools, master protection toggle |
| `SmsScannerActivity` | Detect SMS flood attacks, threshold + window config, stats grid |
| `CallGuardActivity` | Auto-silence repeat unknown calls, calls/min + delay config |
| `EmailFilterActivity` | Spam / phishing email rules, keyword filtering |
| `SmsRulesActivity` | Custom block / allow lists with segmented control + animated list |
| `WhatsappReportActivity` | Report spam / abuse contacts to community DB |
| `MultiChannelGuardActivity` | Combined dashboard for SMS + Call + Email + WhatsApp toggles |
| `MyProtectionActivity` | Personal protection score ring + safety-tip cards |
| `ManageUsersActivity` | Admin: roles, blocks, broadcast (multi-user) |
| `RequestManagerActivity` | Admin: API endpoints, calls/errors stats, animated row list |
| `InAppUpdateActivity` | Update check with animated icon, progress, force / soft update UI |
| `SubscriptionActivity` | Free / Premium / Lifetime plans, animated CTA |

## Design System

- **Neomorphism Day/Night** — drawables defined in `app/src/main/res/drawable/` reference `@color/neo_*` tokens, which automatically swap between `values/colors.xml` and `values-night/colors.xml`. No separate `drawable-night` files needed.
- **Tokens** — `neo_bg`, `neo_surface`, `neo_highlight` (top-left light), `neo_shadow_soft` (bottom-right dark), brand primary/accent/danger/warning/success.
- **Reusable styles** (`values/themes.xml`) — `Neo.Card`, `Neo.Card.Small`, `Neo.Button`, `Neo.Button.Primary`, `Neo.Button.Danger`, `Neo.IconButton`, `Neo.Input`, `Text.Title`, `Text.Heading`, `Text.Body`, `Text.Caption`, `Text.Stat.Number`, `Text.Stat.Label`, `Section.Header`.
- **Drawables** — `neo_card_bg`, `neo_card_inset`, `neo_button_bg` (selector → raised / pressed-inset), `neo_button_primary_bg`, `neo_button_danger_bg`, `neo_input_bg`, `neo_circle_bg`, `neo_circle_pressed`, `neo_icon_bg`, `neo_pill_bg`, `neo_chip_active`.
- **Animations** (`res/anim/`) — `fade_in`, `fade_out`, `slide_in_right`, `slide_out_right`, `slide_up`, `btn_press`, `btn_release`, `pulse`, `list_layout_anim`, `grid_layout_anim`.
- **Helpers** — `snd.shield.util.NeoAnim` (press/scale, count-up, pulse, screen-enter), `snd.shield.util.Nav` (transition-aware activity navigation).

## Build (AndroidIDE)

1. Clone or open this repo in AndroidIDE.
2. AndroidIDE will sync Gradle (8.4) and AGP 8.2.2 automatically using `gradle/wrapper/gradle-wrapper.properties`.
3. Tap **Build → Build APK (debug)**.
4. Install the APK on your device.

## Build (CLI, with Android SDK)

```bash
./gradlew :app:assembleDebug
# APK at: app/build/outputs/apk/debug/app-debug.apk
```

## Project structure (Android side only)

```
app/
├── build.gradle
├── proguard-rules.pro
└── src/main/
    ├── AndroidManifest.xml
    ├── java/snd/shield/
    │   ├── *Activity.java          (13 activities + Subscription)
    │   ├── util/NeoAnim.java
    │   └── util/Nav.java
    └── res/
        ├── anim/                   (smooth click / list / screen anims)
        ├── drawable/               (neomorphism + vector icons)
        ├── layout/                 (per-activity XML + reusable includes)
        ├── menu/
        ├── mipmap-anydpi-v26/      (adaptive launcher)
        ├── values/                 (colors / strings / themes — day)
        ├── values-night/           (colors / themes — night)
        └── xml/                    (backup + data extraction rules)
build.gradle           (root)
settings.gradle
gradle.properties
gradle/wrapper/gradle-wrapper.properties
isArmProtectorUpdate.json   (legacy; consumed by InAppUpdateActivity)
```

## Subscription model

- **Free** — Basic protection, up to 10 rules, community spam DB
- **Premium** (৳149/mo) — Unlimited rules, real-time bomber detection, cloud sync, priority support
- **Lifetime** (৳2999 one-time) — All Premium features forever

## Roadmap / nice-to-haves

- Wire `LoginActivity` to Firebase Auth (or your API).
- Wire `RequestManagerActivity` to a real backend.
- Replace placeholder spam DB seeds with API calls.
- Add `BroadcastReceiver` for SMS / Call so detection runs in background (with explicit user permission).
- Add Bengali (`values-bn/`) localization for full Bangladeshi audience reach.
- Add per-screen widget tests with Espresso once business logic is wired.

## License

This repository's previous content (`isArmProtectorUpdate.json`) is preserved.
SND Shield code is provided as-is, for educational and defensive-security use.
