#!/usr/bin/env python3
"""
Daily SMS delivery — sends one history fact via Gmail-to-SMS gateway.
Uses a shuffled deck approach so all facts are seen before any repeat.
"""
import json, os, random, smtplib
from datetime import date
from email.mime.text import MIMEText

SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
CONTENT_PATH   = os.path.join(SCRIPT_DIR, 'flashcards/content.json')
STATE_PATH     = os.path.join(SCRIPT_DIR, 'sms_state.json')
GMAIL_ADDRESS  = open(os.path.expanduser('~/.gmail_address')).read().strip()
GMAIL_PASSWORD = open(os.path.expanduser('~/.gmail_app_password')).read().strip()
TO_NUMBER      = '6156046386'
CARRIER_GATEWAY = 'vtext.com'
WEBAPP_URL     = 'https://spikes666.github.io/centuryhistories/'

ERA_ICONS = {
    "Ancient World (Pre-CE – 500 CE)":               "🏛️",
    "Medieval (500–1300)":                            "⚔️",
    "Renaissance & Reformation (1300–1600)":          "🎨",
    "Age of Exploration & Enlightenment (1600–1800)": "🔭",
    "Industrial Age (1800–1900)":                     "⚡",
    "Modern World (1900–present)":                    "🌐",
}

def load_all_facts():
    with open(CONTENT_PATH) as f:
        data = json.load(f)
    facts = []
    for century in data['centuries']:
        for fact in century['facts']:
            facts.append({
                **fact,
                'century': century['label'],
                'era': century.get('era', '')
            })
    return facts

def load_state(total_facts):
    """Load or initialize the shuffled deck state."""
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            state = json.load(f)
        # If content has grown significantly, rebuild deck
        if len(state.get('deck', [])) == 0:
            state['deck'] = build_deck(total_facts, state.get('seen', []))
        return state
    # Fresh start
    deck = list(range(total_facts))
    random.shuffle(deck)
    return {'deck': deck, 'seen': [], 'total_sent': 0}

def build_deck(total_facts, seen):
    """Build a new shuffled deck excluding recently seen facts."""
    deck = list(range(total_facts))
    random.shuffle(deck)
    return deck

def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)

def get_todays_fact():
    facts = load_all_facts()
    total = len(facts)
    state = load_state(total)

    # Pop next fact from deck
    idx = state['deck'].pop(0)

    # Handle index out of range if content grew
    if idx >= total:
        idx = idx % total

    state['seen'].append(idx)
    # Keep seen list from growing unbounded
    if len(state['seen']) > total:
        state['seen'] = state['seen'][-total:]

    state['total_sent'] = state.get('total_sent', 0) + 1

    # If deck exhausted, reshuffle
    if len(state['deck']) == 0:
        print(f"Deck exhausted after {state['total_sent']} facts — reshuffling")
        state['deck'] = build_deck(total, state['seen'])

    save_state(state)
    return facts[idx], state['total_sent'], total

def send_sms(fact, sent, total):
    icon = ERA_ICONS.get(fact['era'], '📜')
    remaining = total - (sent % total)
    body = (
        f"{WEBAPP_URL}\n\n"
        f"{icon} {fact['century']}\n\n"
        f"{fact['fact']}\n\n"
        f"📍 {fact['map_label']}\n"
        f"#{sent} · {remaining} until reshuffle"
    )

    msg = MIMEText(body)
    msg['From']    = GMAIL_ADDRESS
    msg['To']      = f"{TO_NUMBER}@{CARRIER_GATEWAY}"
    msg['Subject'] = ''

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
        server.send_message(msg)

    print(f"[{date.today()}] Sent #{sent}: {fact['century']} — {fact['fact'][:60]}...")

if __name__ == '__main__':
    fact, sent, total = get_todays_fact()
    send_sms(fact, sent, total)