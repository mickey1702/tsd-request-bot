import os
import telebot
from telebot import types
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID"))

FREE_GROUP_LINK = "https://t.me/+zRsJjUdCCABhMDI1"
PAID_CONTACT = "https://t.me/TheSarcasticDoctor"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📚 Free Study Materials", "🎓 Paid Lecture Packages")
    markup.row("🔗 Report Broken Link", "ℹ️ Help")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        """
👋 <b>Welcome to THE SARCASTIC DOCTOR Support Bot</b>

📚 Free Study Materials
🎓 Paid Lecture Packages
🔗 Report Broken Links

💬 Simply send any message, screenshot,
lecture request, PDF or voice note.

All messages are automatically delivered
to the admin team.
        """,
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['free_materials'])
def free_materials(message):
    bot.send_message(
        message.chat.id,
        f"📚 <b>FREE STUDY MATERIALS</b>\n\nJoin our free resource hub here:\n{FREE_GROUP_LINK}"
    )

@bot.message_handler(commands=['paid_courses'])
def paid_courses(message):
    bot.send_message(
        message.chat.id,
        f"🎓 <b>PAID LECTURE PACKAGES</b>\n\nContact admin here:\n{PAID_CONTACT}"
    )

@bot.message_handler(commands=['help'])
def help_user(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>HOW TO USE THIS BOT</b>\n\nSend any message, PDF, screenshot, video or voice note. It will automatically reach the admin team."
    )

@bot.message_handler(commands=['broken_link'])
def broken_link(message):
    msg = bot.send_message(message.chat.id, "🔗 Send broken link / screenshot / lecture name:")
    bot.register_next_step_handler(msg, save_broken_report)

def save_broken_report(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
🚨 <b>BROKEN LINK REPORT</b>

👤 User: {username}
🆔 USERID:{message.chat.id}

🔗 {message.text}
"""
    bot.send_message(ADMIN_GROUP_ID, admin_text)
    bot.send_message(message.chat.id, "✅ Broken link report sent. Thank you.")

@bot.message_handler(func=lambda m: m.text == "📚 Free Study Materials")
def btn1(message):
    free_materials(message)

@bot.message_handler(func=lambda m: m.text == "🎓 Paid Lecture Packages")
def btn2(message):
    paid_courses(message)

@bot.message_handler(func=lambda m: m.text == "🔗 Report Broken Link")
def btn3(message):
    broken_link(message)

@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def btn4(message):
    help_user(message)

@bot.message_handler(content_types=['text', 'photo', 'document', 'video', 'audio', 'voice'])
def support_inbox(message):

    if message.chat.id == ADMIN_GROUP_ID:
        return

    ignored = [
        "📚 Free Study Materials",
        "🎓 Paid Lecture Packages",
        "🔗 Report Broken Link",
        "ℹ️ Help"
    ]

    if message.content_type == "text" and message.text in ignored:
        return

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    caption = f"""
📩 <b>NEW SUPPORT MESSAGE</b>

👤 User: {username}
🆔 USERID:{message.chat.id}
"""

    if message.content_type == "text":
        caption += f"\n\n💬 {message.text}"

    try:
        if message.content_type == "photo":
            bot.send_photo(ADMIN_GROUP_ID, message.photo[-1].file_id, caption=caption)

        elif message.content_type == "document":
            bot.send_document(ADMIN_GROUP_ID, message.document.file_id, caption=caption)

        elif message.content_type == "video":
            bot.send_video(ADMIN_GROUP_ID, message.video.file_id, caption=caption)

        elif message.content_type == "audio":
            bot.send_audio(ADMIN_GROUP_ID, message.audio.file_id, caption=caption)

        elif message.content_type == "voice":
            bot.send_voice(ADMIN_GROUP_ID, message.voice.file_id, caption=caption)

        else:
            bot.send_message(ADMIN_GROUP_ID, caption)

    except Exception as e:
        print(e)

@bot.message_handler(func=lambda message: message.chat.id == ADMIN_GROUP_ID and message.reply_to_message is not None)
def admin_reply_relay(message):
    try:
        source_text = (
            getattr(message.reply_to_message, "caption", None)
            or getattr(message.reply_to_message, "text", None)
        )

        if not source_text or "USERID:" not in source_text:
            return

        uid = int(source_text.split("USERID:")[1].split("\\n")[0].strip())
        sender = message.from_user.first_name

        if message.content_type == "text":
            bot.send_message(uid, f"💬 <b>{sender}:</b>\n\n{message.text}")
            bot.reply_to(message, "✅ Reply delivered.")

    except Exception as e:
        print(e)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "TSD BOT WEBHOOK RUNNING"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://tsd-request-bot.onrender.com/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
