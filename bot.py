import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===== ENV VARIABLES =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ===== GLOBAL STATE =====
SECRET_TEXT = "এখনো কিছু set করা হয়নি"
verified_users = set()

# ===== KEYBOARD =====
def start_kb():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📌 Join Channel", url=CHANNEL_LINK),
        InlineKeyboardButton("✅ Verify", callback_data="verify")
    )
    return kb

# ===== CHECK SUBSCRIBE =====
def is_subscriber(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_ID, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

# ===== START =====
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id

    if uid not in verified_users:
        if is_subscriber(uid):
            verified_users.add(uid)
        else:
            bot.send_message(
                message.chat.id,
                "❌ আগে channel join করো, তারপর Verify চাপো",
                reply_markup=start_kb()
            )
            return

    bot.send_message(
        message.chat.id,
        f"<code>{SECRET_TEXT}</code>"
    )

# ===== VERIFY BUTTON =====
@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(call):
    uid = call.from_user.id

    if is_subscriber(uid):
        verified_users.add(uid)
        bot.edit_message_text(
            f"<code>{SECRET_TEXT}</code>",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ আগে channel join করো",
            show_alert=True
        )

# ===== ADMIN SET COMMAND =====
@bot.message_handler(commands=["set"])
def set_text(message):
    global SECRET_TEXT

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/set", "").strip()
    if not text:
        bot.reply_to(message, "❌ ব্যবহার: /set তোমার লেখা")
        return

    SECRET_TEXT = text
    bot.reply_to(message, "✅ Text update হয়েছে")

# ===== BLOCK OTHERS =====
@bot.message_handler(func=lambda m: True)
def block(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "ℹ️ /set ব্যবহার করে text পরিবর্তন করো")
    else:
        bot.reply_to(message, "🔒 /start দিয়ে verify করো")

# ===== SAFE POLLING =====
while True:
    try:
        print("Bot running...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Bot crashed:", e)
