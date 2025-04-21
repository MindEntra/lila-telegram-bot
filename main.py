import os
import telebot
from flask import Flask, request

# ✅ Securely pull API token from environment
API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Set this to your webhook URL

if not API_TOKEN:
    raise ValueError("API_TOKEN is missing. Please set it in your environment variables.")

bot = telebot.TeleBot(API_TOKEN)

# In-memory storage
todos = []
contacts = {}
schedules = []

# Set webhook
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# Flask app setup
app = Flask(__name__)

@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_json()
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route('/' + API_TOKEN, methods=['GET'])
def webhook():
    return 'Webhook is set up!', 200

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "Hello Michael, I'm Lila, your virtual secretary!\n\n"
        "Commands:\n"
        "/todo [task] - Add a task\n"
        "/list - View tasks\n"
        "/remove [#] - Remove task\n"
        "/schedule [event] at [time] - Add reminder\n"
        "/contacts - Show contacts\n"
        "/jw [topic] - Search JW.org"
    )

@bot.message_handler(commands=['todo'])
def add_task(message):
    task = message.text[6:].strip()
    if task:
        todos.append(task)
        bot.reply_to(message, f"Task added: {task}")
    else:
        bot.reply_to(message, "Please enter a task.")

@bot.message_handler(commands=['list'])
def show_tasks(message):
    if not todos:
        bot.reply_to(message, "No tasks yet.")
    else:
        response = "\n".join([f"{i+1}. {task}" for i, task in enumerate(todos)])
        bot.reply_to(message, f"Your tasks:\n{response}")

@bot.message_handler(commands=['remove'])
def remove_task(message):
    try:
        index = int(message.text[8:].strip()) - 1
        removed = todos.pop(index)
        bot.reply_to(message, f"Removed: {removed}")
    except:
        bot.reply_to(message, "Use: /remove [task number]")

@bot.message_handler(commands=['schedule'])
def schedule_event(message):
    pattern = r"/schedule (.+) at (.+)"
    match = re.search(pattern, message.text, re.IGNORECASE)
    if match:
        event, time = match.groups()
        schedules.append((event, time))
        bot.reply_to(message, f"Scheduled: {event} at {time}")
    else:
        bot.reply_to(message, "Use: /schedule [event] at [time]")

@bot.message_handler(commands=['contacts'])
def list_contacts(message):
    if not contacts:
        bot.reply_to(message, "No contacts saved.")
    else:
        response = "\n".join([f"{name}: {info}" for name, info in contacts.items()])
        bot.reply_to(message, f"Contacts:\n{response}")

@bot.message_handler(commands=['jw'])
def search_jw(message):
    topic = message.text[4:].strip()
    if topic:
        bot.reply_to(message,
            f"Search results for '{topic}':\n"
            f"https://www.jw.org/finder?wtlocale=E&pub=all&srcid=share&srchword={topic.replace(' ', '%20')}")
    else:
        bot.reply_to(message, "Type: /jw [topic]")

@bot.message_handler(func=lambda msg: True)
def fallback(message):
    bot.reply_to(message, "How can I assist you, Michael?")

# ✅ Start the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
