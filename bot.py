import os
import telebot
from telebot import types
from flask import Flask
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.environ.get("ADMIN_GROUP_ID"))
OWNER_ID = int(os.environ.get("OWNER_ID"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    text = """
👨‍⚕️ <b>Welcome to THE SARCASTIC DOCTOR Official Study Assistant</b>

📚 Free Study Materials
🎓 Paid Lecture Packages
📩 Anonymous Admin Support
🔗 Broken Link Reports

Choose an option below:
"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📚 Request Free Lecture")
    markup.row("🎓 Buy Paid Lecture")
    markup.row("📩 Contact Admin")
    markup.row("🔗 Report Broken Link")
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📚 Request Free Lecture")
def ask_free(message):
    msg = bot.send_message(message.chat.id, "Send lecture name / teacher / subject you need:")
    bot.register_next_step_handler(msg, save_free_request)

def save_free_request(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
📥 <b>NEW FREE LECTURE REQUEST</b>

👤 User: {username}
🆔 ID: <code>{message.chat.id}</code>

📚 Request:
{message.text}
"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Done Uploaded", callback_data=f"done_{message.chat.id}"))

    bot.send_message(ADMIN_GROUP_ID, admin_text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Your request has been sent to admin. Please wait for approval.")

@bot.message_handler(func=lambda m: m.text == "🎓 Buy Paid Lecture")
def paid_lecture(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
💰 <b>PAID LECTURE PURCHASE REQUEST</b>

👤 User: {username}
🆔 ID: <code>{message.chat.id}</code>
"""
    bot.send_message(ADMIN_GROUP_ID, admin_text)
    bot.send_message(message.chat.id, "✅ Admin has received your paid lecture inquiry. We will contact you shortly.")

@bot.message_handler(func=lambda m: m.text == "📩 Contact Admin")
def contact_admin(message):
    msg = bot.send_message(message.chat.id, "Type your message for admin:")
    bot.register_next_step_handler(msg, forward_admin_message)

def forward_admin_message(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
📨 <b>NEW MESSAGE TO ADMIN</b>

👤 User: {username}
🆔 ID: <code>{message.chat.id}</code>

💬 Message:
{message.text}
"""
    bot.send_message(ADMIN_GROUP_ID, admin_text)
    bot.send_message(message.chat.id, "✅ Message sent to admin.")

@bot.message_handler(func=lambda m: m.text == "🔗 Report Broken Link")
def broken_link(message):
    msg = bot.send_message(message.chat.id, "Send broken link / screenshot / lecture name:")
    bot.register_next_step_handler(msg, save_broken_report)

def save_broken_report(message):
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

    admin_text = f"""
🚨 <b>BROKEN LINK REPORT</b>

👤 User: {username}
🆔 ID: <code>{message.chat.id}</code>

🔗 Report:
{message.text}
"""
    bot.send_message(ADMIN_GROUP_ID, admin_text)
    bot.send_message(message.chat.id, "✅ Broken link report sent. Thank you.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def fulfilled(call):
    uid = int(call.data.split("_")[1])

    try:
        bot.send_message(uid, "🎉 Your requested lecture has been uploaded / arranged by admin. Please check channel/group.")
        bot.answer_callback_query(call.id, "Student notified.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        bot.answer_callback_query(call.id, "Could not notify user.")

@app.route('/')
def home():
    return "Bot Running"

def run_bot():
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
