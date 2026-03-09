#!/usr/bin/env python3
"""
Daily History Flashcard - iMessage Delivery Script
Sends 1 random fact per day via iMessage on macOS.
Sources: Misquoting Jesus (Ehrman), The Rest is History, Dominion (Tom Holland)
"""

import json
import os
import sys
import random
import subprocess
import tempfile
from datetime import date

# ── Config ───────────────────────────────────────────────────────────────────
TO_NUMBER  = "+16156046386"
WEBAPP_URL = "https://spikes666.github.io/centuryhistories/"
CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flashcards", "content.json")

# ── Load content ──────────────────────────────────────────────────────────────
def load_content():
    with open(CONTENT_PATH, "r") as f:
        return json.load(f)

# ── Pick today's random fact ──────────────────────────────────────────────────
def get_todays_fact(data):
    """
    Uses today's date as a seed so the same fact shows all day,
    but a different one appears each morning.
    """
    all_facts = []
    for century in data["centuries"]:
        for fact in century["facts"]:
            all_facts.append({
                "century_label": century["label"],
                "fact": fact
            })

    today_seed = int(date.today().strftime("%Y%m%d"))
    random.seed(today_seed)
    return random.choice(all_facts)

# ── Format message ────────────────────────────────────────────────────────────
def format_message(item):
    today_str = date.today().strftime("%B %d, %Y")
    lines = [
        WEBAPP_URL,
        "",
        "📜 HISTORY FLASHCARD — " + today_str,
        "📅 " + item["century_label"],
        "─" * 30,
        "",
        item["fact"],
        "",
        "─" * 30,
        "📚 Sources: Misquoting Jesus (Ehrman) · The Rest is History · Dominion (Tom Holland)",
    ]
    return "\n".join(lines)

# ── Send via iMessage — writes AppleScript to a temp file to avoid escaping issues ──
def send_imessage(message):
    # Write the message to a temp file so AppleScript reads it cleanly
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(message)
        tmp_path = f.name

    script = f'''
set msgText to read POSIX file "{tmp_path}" as «class utf8»
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "{TO_NUMBER}" of targetService
    send msgText to targetBuddy
end tell
do shell script "rm " & quoted form of "{tmp_path}"
'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"iMessage error: {result.stderr.strip()}")
        sys.exit(1)
    else:
        print("Sent via iMessage successfully.")

# ── Twilio SMS (kept for future use / A2P 10DLC) ─────────────────────────────
# def send_sms(message):
#     from twilio.rest import Client
#     client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
#     msg = client.messages.create(
#         body=message,
#         from_=os.environ["TWILIO_FROM_NUMBER"],
#         to=os.environ["TO_NUMBER"]
#     )
#     print(f"Sent via Twilio: SID={msg.sid}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[{date.today()}] Daily History Flashcard starting...")
    try:
        data = load_content()
        item = get_todays_fact(data)
        message = format_message(item)

        print("\n--- PREVIEW ---")
        print(message)
        print(f"\n--- Total chars: {len(message)} ---\n")

        send_imessage(message)
        print("Done!")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
