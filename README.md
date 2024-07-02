# COOKIEBOT-Telegram-Group-Bot

Telegram chatbot responsible for protecting chats against spammers, conversating using natural language, perform speech-to-text, search media, schedule posts and provides fun features for events.

## Installation on Ubuntu

```bash
sudo apt update
sudo apt-get install git-all
sudo apt install python3.11
sudo apt install python3-pip
sudo apt install ffmpeg
sudo apt-get install screen
git clone https://github.com/MekhyW/COOKIEBOT-Telegram-Group-Bot.git
cd COOKIEBOT-Telegram-Group-Bot
pip3 install -r requirements.txt --break-system-packages
```

## Provide credentials

```bash
cd Bot
nano cookiebot_backendauth.json # Add your credentials
nano cookiebot_basecredentials.json # Add your credentials
nano cookiebot_cloudserviceaccount.json # Add your credentials
nano cookiebot_pubsub.json # Add your credentials
```

## Set timezone

```bash
tzselect # Select your timezone
timedatectl
```

## Run the bot

```bash
screen
python3.11 COOKIEBOT.py
# Press CTRL+A+D to detach from the screen
```