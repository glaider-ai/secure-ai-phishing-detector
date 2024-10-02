import gradio as gr
import glaider
import openai
from dotenv import load_dotenv
import os

# Load environment variables and initialize APIs
load_dotenv()
glaider.init(api_key=os.getenv('GLAIDER_API_KEY'))
glaider.openai.api_key = os.getenv('OPENAI_API_KEY')


def analyze_email_phishing(sender, title, content, check_prompt_injection):
    prompt_injection_result = " - "

    if check_prompt_injection:
        # Check for prompt injection
        result = glaider.protection.detect_prompt_injection(content)
        if result['is_prompt_injection']:
            return "Prompt Injection Detected", " - "
        prompt_injection_result = "No Prompt Injection Detected"

    # Analyze for phishing
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Is this email phishing? Reply with just True or False: "
                           f"Email from: {sender}\nSubject: {title}\nContent: {content}\n"
            }
        ],
    )
    print(response.choices[0].message.content)
    is_phishing = response.choices[0].message.content.strip().lower() == "true"
    return prompt_injection_result, "Phishing Detected" if is_phishing else "Not Phishing"


with gr.Blocks() as demo:
    gr.Markdown("# Email Phishing Analyzer")
    gr.Markdown("Enter email details to analyze for phishing and optionally check for prompt injection.")

    with gr.Row():
        with gr.Column(scale=1):
            sender = gr.Textbox(label="Sender")
            subject = gr.Textbox(label="Subject")
            content = gr.Textbox(label="Email Content", lines=10)
            check_injection = gr.Checkbox(label="Enable Prompt Injection Check", value=True)
            analyze_button = gr.Button("Analyze")

        with gr.Column(scale=1):
            injection_result = gr.Textbox(label="Prompt Injection Result")
            phishing_result = gr.Textbox(label="Phishing Analysis Result")

    analyze_button.click(
        fn=analyze_email_phishing,
        inputs=[sender, subject, content, check_injection],
        outputs=[injection_result, phishing_result]
    )

demo.launch()
