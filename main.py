from pymailtm import Account
import glaider
from dotenv import load_dotenv
import os


load_dotenv()

glaider.init(api_key=os.getenv('GLAIDER_API_KEY'))

glaider.openai.api_key = os.getenv('OPENAI_API_KEY')


_id = os.getenv('EMAIL_ID')
address = os.getenv('EMAIL_ADDRESS')
password = os.getenv('EMAIL_PASSWORD')


account = Account(_id, address, password)


def analyze_email_phishing(sender, title, content):

    result = glaider.protection.detect_prompt_injection(content)
    if result['is_prompt_injection']:
        print("Prompt Injection Detected")
        return

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
    print("Waiting for new emails...")
    received_email = account.wait_for_message()
    print(received_email)
    if received_email:
        email_body = received_email.html if received_email.html else received_email.text

        phishing_result = analyze_email_phishing(
            sender=received_email.from_['address'],
            title=received_email.subject,
            content=email_body
        )
        print(phishing_result)




