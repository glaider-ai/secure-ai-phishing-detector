from pymailtm import Account
from dotenv import load_dotenv
import os
import glaider

# Load environment variables
load_dotenv()

glaider.init(os.getenv('GLAIDER_API_KEY'))

_id = os.getenv('EMAIL_ID')
address = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_PASSWORD')

glaider.openai.api_key = os.getenv('OPENAI_API_KEY')

# Create the Account object using environment variables
email_account = Account(id=_id, address=address, password=password)


def analyze_email_phishing(sender, title, content):
    """
    Uses OpenAI API to analyze if an email is phishing.
    Parameters:
    - sender: email address of the sender
    - title: subject of the email
    - content: body of the email (HTML or text)
    """

    if glaider.protection.detect_prompt_injection(content)['is_prompt_injection']:
        return "Prompt Injection Detected!"

    response = glaider.openai.chat_completion_create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Is this email phishing? Reply with just True or False: "
                f"Email from: {sender}\nSubject: {title}\nContent: {content}\n"
            }
        ],
    )
    return response


while True:
    print("Listening for emails...")
    received_email = email_account.wait_for_message()
    if received_email:
        # Determine if the email body is HTML or plain text
        email_body = received_email.html if received_email.html else received_email.text

        # Analyze the email for phishing
        phishing_result = analyze_email_phishing(
            sender=received_email.from_['address'],
            title=received_email.subject,
            content=email_body
        )

        print(f"Phishing Analysis Result: {phishing_result}")
