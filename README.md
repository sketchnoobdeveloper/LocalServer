# SND Shield — Anti-Spam / Anti-Bomber Defense

**Package:** `snd.shield`
**Min SDK:** 21 &nbsp;·&nbsp; **Target SDK:** 34 &nbsp;·&nbsp; **Java:** 17 &nbsp;·&nbsp; **AGP:** 8.2.2

A neomorphism (day & night) Android frontend that helps users **defend against spam, repeat unknown calls, phishing emails, and SMS / WhatsApp bombing** — the opposite direction of an attack tool. Reports spam to a community DB, applies block / allow rules, and surfaces incoming-flood analytics.

> This repository previously hosted only `isArmProtectorUpdate.json` (an in-app update config). That file is preserved at the root and is now consumed by `InAppUpdateActivity` for update checks.

---

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

- **Neomorphism Day/Night** — drawables defined in `res/drawable/` reference `@color/neo_*` tokens, which automatically swap between `values/colors.xml` and `values-night/colors.xml`. No separate `drawable-night` files needed.
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

## Project structure

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
