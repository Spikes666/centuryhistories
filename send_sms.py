#!/usr/bin/env python3
"""
Daily SMS delivery — sends one history fact via Gmail-to-SMS gateway.
"""
import json, os, random, smtplib
from datetime import date
from email.mime.text import MIMEText

CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flashcards/content.json')
GMAIL_ADDRESS  = open(os.path.expanduser('~/.gmail_address')).read().strip()
GMAIL_PASSWORD = open(os.path.expanduser('~/.gmail_app_password')).read().strip()
TO_NUMBER      = '6156046386'
CARRIER_GATEWAY = 'vtext.com'
WEBAPP_URL     = 'https://spikes666.github.io/centuryhistories/'

def get_todays_fact():
    with open(CONTENT_PATH) as f:
        data = json.load(f)
    all_facts = []
    for century in data['centuries']:
        for fact in century['facts']:
            all_facts.append({**fact, 'century': century['label'], 'era': century['era']})
    random.seed(int(date.today().strftime('%Y%m%d')))
    return random.choice(all_facts)

def send_sms(fact):
    era_icons = {
        "Ancient World (Pre-CE – 500 CE)":               "🏛️",
        "Medieval (500–1300)":                            "⚔️",
        "Renaissance & Reformation (1300–1600)":          "🎨",
        "Age of Exploration & Enlightenment (1600–1800)": "🔭",
        "Industrial Age (1800–1900)":                     "⚡",
        "Modern World (1900–present)":                    "🌐",
    }
    icon = era_icons.get(fact['era'], '📜')
    body = (
        f"{WEBAPP_URL}\n\n"
        f"{icon} {fact['century']}\n\n"
        f"{fact['fact']}\n\n"
        f"📍 {fact['map_label']}"
    )

    msg = MIMEText(body)
    msg['From']    = GMAIL_ADDRESS
    msg['To']      = f"{TO_NUMBER}@{CARRIER_GATEWAY}"
    msg['Subject'] = ''

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.send_message(msg)
    print(f"Sent: {fact['century']} — {fact['fact'][:60]}...")

if __name__ == '__main__':
    fact = get_todays_fact()
    send_sms(fact)
