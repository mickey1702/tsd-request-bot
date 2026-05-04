import os
import telebot
from telebot import types
from flask import Flask
from threading import Thread

TOKEN = "8537910008:AAGkzmRcH3o0D-eqaq0LVHW4p202GUIoBGo"
OWNER_ID = 5471433381
ADMIN_GROUP_ID = -1003945479408

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

pending_users = {}

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📚 Request Lecture", callback_data="request")
    btn2 = types.InlineKeyboardButton("💬 Contact Admin", url="https://t.me/thesarcasticdoctorbot")
    markup.add(btn1)
    markup.add(btn2)

    txt = f"""
<b>👨‍⚕️ THE SARCASTIC DOCTOR</b>

Welcome {user.first_name}.

Send your academic lecture requirements directly here.

Our admin panel will receive:
• your name
• your user id
• your username
• your request

Click below to begin.
"""
    bot.send_message(message.chat.id, txt, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "request":
        msg = bot.send_message(call.message.chat.id, "📝 Send me the lecture / subject / faculty name you need:")
        bot.register_next_step_handler(msg, get_request)

def get_request(message):
    user = message.from_user
    req = message.text

    pending_users[user.id] = req

    markup = types.InlineKeyboardMarkup()
    done_btn = types.InlineKeyboardButton("✅ Fulfilled", callback_data=f"done_{user.id}")
    markup.add(done_btn)

    username = f"@{user.username}" if user.username else "No Username"

    admin_text = f"""
<b>📥 NEW STUDENT REQUEST</b>

👤 Name: {user.first_name}
🆔 User ID: <code>{user.id}</code>
🔗 Username: {username}

📚 Requirement:
<code>{req}</code>
"""

    bot.send_message(ADMIN_GROUP_ID, admin_text, reply_markup=markup)
    bot.send_message(message.chat.id, "✅ Your request has been sent to admin. Please wait for response.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def fulfilled(call):
    uid = int(call.data.split("_")[1])

    try:
        bot.send_message(uid, "🎉 Your requested lecture has been uploaded in the channel/group. Please check latest posts.")
        bot.answer_callback_query(call.id, "Student notified.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        bot.answer_callback_query(call.id, "Could not notify user.")

@app.route('/')
def home():
    return "Bot Running"

def run_bot():
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_bot).start()
    run_web()
