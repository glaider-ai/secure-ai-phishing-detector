## Private Phishing Detector

The Private Phishing Detector is a Python-based application designed to monitor incoming emails and detect potential phishing threats using OpenAI's API and the pymailtm library. It features real-time email monitoring, anti-phishing analysis, and prompt injection checks to prevent misuse of the machine learning model.

### Features

- **Real-Time Email Monitoring**: Listens and processes incoming emails in real-time.
- **Phishing Detection**: Analyzes emails to identify potential phishing threats, leveraging OpenAI's machine learning capabilities.
- **Prompt Injection Prevention**: Includes checks for prompt injections to ensure the integrity of interactions with the OpenAI model.
- **Secure Credential Management**: Uses environment variables to manage sensitive information securely.

### Prerequisites

- Python 3.9
- pymailtm
- glaider
- python-dotenv
- pyTelegramBotAPI
- requests

### Installation

1. Install the required packages:
   ```
   pip install pymailtm glaider python-dotenv
   ```
2. Create a `.env` file in the root directory with the following variables:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   GLAIDER_API_KEY=your_glaider_api_key_here
   ```

### Usage

Execute the script using the command:
```
python main.py
```
The application will continuously monitor for new emails and display the phishing analysis results, including checks for prompt injections.

### How It Works

- **Email Account Configuration**: Sets up an email account using credentials from environment variables.
- **Continuous Email Monitoring**: Listens for and processes each new email as it arrives.
- **Phishing Analysis and Security Checks**:
  - Detects potential phishing attempts based on the email's content, sender, and subject.
  - Performs prompt injection checks using the glaider API before sending content to OpenAI, enhancing security.
- **Reporting**: Outputs the phishing analysis and prompt injection results to the console.

for any question or more information about glaider write un an email at info@glaider.it
