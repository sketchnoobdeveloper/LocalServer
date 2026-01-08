import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError
import openai

# =======================
# CONFIG (ENV REQUIRED)
# =======================
BOT_TOKEN = os.getenv("BOT_TOKEN")          # Telegram Bot Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI / Grok compatible key

REQUIRED_CHANNEL = "@KamPonditOfficial"
REQUIRED_GROUP = "@KamPonditAsor"

openai.api_key = OPENAI_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# =======================
# AI RESPONSE
# =======================
async def generate_response(user_text: str) -> str:
    """
    এখানে পরে আপনি role / personality বদলাতে পারবেন
    """
    system_prompt = (
        "You are a helpful, polite, conversational assistant. "
        "Respond in Bengali in a friendly and respectful tone."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        )
        return response.choices[0].message["content"]
    except Exception:
        return "এই মুহূর্তে উত্তর দিতে সমস্যা হচ্ছে। একটু পরে আবার চেষ্টা করুন।"

# =======================
# JOIN CHECK
# =======================
async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        ch = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        gr = await context.bot.get_chat_member(REQUIRED_GROUP, user_id)
        return ch.status in ("member", "administrator", "creator") and \
               gr.status in ("member", "administrator", "creator")
    except TelegramError:
        return False

async def force_join_message(update: Update):
    await update.message.reply_text(
        "⚠️ বট ব্যবহার করতে হলে আগে অবশ্যই Join করতে হবে:\n\n"
        f"📢 Channel: https://t.me/KamPonditOfficial\n"
        f"💬 Group: https://t.me/KamPonditAsor\n\n"
        "Join করে আবার /start দিন।"
    )

# =======================
# COMMANDS
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined(update, context):
        await force_join_message(update)
        return

    await update.message.reply_text(
        "✅ স্বাগতম!\n\n"
        "আপনি এখন আমার সাথে কথা বলতে পারেন। "
        "প্রাইভেট বা গ্রুপ—দুটোতেই আমি রিপ্লাই দেবো।"
    )

# =======================
# MESSAGE HANDLER
# =======================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    # Join check only for private chat
    if update.message.chat.type == "private":
        if not await is_user_joined(update, context):
            await force_join_message(update)
            return

    user_text = update.message.text.strip()
    reply = await generate_response(user_text)
    await update.message.reply_text(reply)

# =======================
# MAIN
# =======================
def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    app.run_polling()

if __name__ == "__main__":
    main()
