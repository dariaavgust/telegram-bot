import pyTelegramBotAPI
import sqlite3
from flask import Flask
import threading

TOKEN = "ВСТАВЬ_ТОКЕН"
ADMIN_ID = 123456789

bot = telebot.TeleBot(TOKEN)
app = Flask(name)

# база
conn = sqlite3.connect("stories.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    text TEXT
)
""")
conn.commit()

def save_story(user_id, username, text):
    cur.execute(
        "INSERT INTO stories (user_id, username, text) VALUES (?, ?, ?)",
        (user_id, username, text)
    )
    conn.commit()

# веб (для UptimeRobot)
@app.route('/')
def home():
    return "Bot is alive"

# бот
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "Привет, балаганец!\n\n"
        "Отправь свою историю (до 500 символов)"
    )

@bot.message_handler(func=lambda message: True)
def handle(message):
    text = message.text
    user_id = message.chat.id
    username = message.from_user.username or "no_username"

    if len(text) > 500:
        bot.send_message(user_id, "Слишком длинная история (до 500)")
        return

    save_story(user_id, username, text)

    bot.send_message(user_id, "Спасибо! История отправлена 📖")

    bot.send_message(ADMIN_ID,
        f"📩 Новая история\n\n@{username}\n{text}"
    )

def run_bot():
    bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()
threading.Thread(target=run_bot).start()