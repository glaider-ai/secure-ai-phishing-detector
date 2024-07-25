import os
from pymailtm import Account
from dotenv import load_dotenv
import glaider
import telebot
import threading
import time
import requests

# Load environment variables
load_dotenv()
glaider.init(os.getenv("GLAIDER_API_KEY"))
glaider.openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Telegram bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to store user email accounts
user_emails = {}


def analyze_email_phishing(sender, title, content):
    """
    Uses OpenAI API to analyze if an email is phishing.
    """
    if glaider.protection.detect_prompt_injection(content)["is_prompt_injection"]:
        return "Prompt Injection Detected!"
    response = glaider.openai.chat_completion_create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Is this email phishing? Reply with just True or False: "
                f"Email from: {sender}\nSubject: {title}\nContent: {content}\n",
            }
        ],
    )
    return response["choices"][0]["message"]["content"]


def create_email_account():
    """
    Creates a new email account using Mail.tm API
    """
    domains_url = "https://api.mail.tm/domains"
    response = requests.get(domains_url)
    domains = response.json()["hydra:member"]

    if not domains:
        return None

    domain = domains[0]["domain"]
    username = f"user_{int(time.time())}"
    email = f"{username}@{domain}"
    password = "password123"  # You might want to generate a random password

    account_url = "https://api.mail.tm/accounts"
    data = {"address": email, "password": password}
    response = requests.post(account_url, json=data)

    if response.status_code == 201:
        account_data = response.json()
        account_id = account_data["id"]
        return Account(id=account_id, address=email, password=password)
    else:
        return None


def listen_for_emails(chat_id):
    email_account = user_emails[chat_id]
    token = get_auth_token(email_account.address, email_account.password)

    while True:
        print(f"Listening for new emails for user {chat_id}...")
        unread_messages = get_unread_messages(token)
        for message in unread_messages:
            message_details = get_message_details(token, message["id"])
            email_body = message_details.get("text", "")
            phishing_result = analyze_email_phishing(
                sender=message["from"]["address"],
                title=message["subject"],
                content=email_body,
            )
            bot.send_message(
                chat_id,
                f"New email received!\nFrom: {message['from']['address']}\nSubject: {message['subject']}\nPhishing Analysis Result: {phishing_result}",
            )

            # Mark the message as read
            mark_as_read(token, message["id"])

        time.sleep(10)  # Check for new messages every 10 seconds


def get_unread_messages(token):
    messages_url = "https://api.mail.tm/messages"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(messages_url, headers=headers)
    if response.status_code == 200:
        all_messages = response.json()["hydra:member"]
        return [msg for msg in all_messages if not msg["seen"]]
    return []


def mark_as_read(token, message_id):
    message_url = f"https://api.mail.tm/messages/{message_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/merge-patch+json",
    }
    data = {"seen": True}
    response = requests.patch(message_url, headers=headers, json=data)
    return response.status_code == 200


# The other functions (get_auth_token, get_message_details) remain the same


def get_auth_token(email, password):
    token_url = "https://api.mail.tm/token"
    data = {"address": email, "password": password}
    response = requests.post(token_url, json=data)
    if response.status_code == 200:
        return response.json()["token"]
    return None


def get_messages(token):
    messages_url = "https://api.mail.tm/messages"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(messages_url, headers=headers)
    if response.status_code == 200:
        return response.json()["hydra:member"]
    return []


def get_message_details(token, message_id):
    message_url = f"https://api.mail.tm/messages/{message_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(message_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {}


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "Welcome! Use /create_email to generate a new email address.")


@bot.message_handler(commands=["create_email"])
def create_email(message):
    chat_id = message.chat.id
    new_account = create_email_account()
    if new_account:
        user_emails[chat_id] = new_account
        bot.reply_to(
            message,
            f"Your new email address is: {new_account.address}\nYou can now forward emails to this address.",
        )

        # Start listening for emails in a separate thread
        email_thread = threading.Thread(target=listen_for_emails, args=(chat_id,))
        email_thread.start()
    else:
        bot.reply_to(message, "Failed to create email account. Please try again later.")


# Start the bot
bot.polling()
