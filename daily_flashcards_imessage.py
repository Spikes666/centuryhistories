#!/usr/bin/env python3
"""
Daily History Flashcards - iMessage Delivery Script
Sends 10 sequential flashcards via iMessage every morning.
Draws on content from Misquoting Jesus (Bart Ehrman) and The Rest is History.
Runs on macOS via osascript. Schedule with crontab.

── Twilio / A2P 10DLC (kept for future SMS use) ─────────────────────────────
To switch back to SMS:
  1. pip install twilio python-dotenv
  2. Set env vars: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TO_NUMBER
  3. Replace send_imessage() with send_sms() in main()
  4. Register at twilio.com/console for A2P 10DLC or use a toll-free number
─────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import sys
import subprocess
from datetime import date

# ── Config ───────────────────────────────────────────────────────────────────
TO_NUMBER     = "+16156046386"   # iMessage phone number or Apple ID email
FACTS_PER_DAY = 10

CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flashcards", "content.json")

# ── Load content ──────────────────────────────────────────────────────────────
def load_content():
    with open(CONTENT_PATH, "r") as f:
        return json.load(f)

# ── Determine today's facts ───────────────────────────────────────────────────
def get_todays_facts(data):
    """
    Sequential delivery: exhaust one century before moving to the next.
    Uses a global day index based on days since a fixed start date.
    """
    all_facts = []
    for century in data["centuries"]:
        for fact in century["facts"]:
            all_facts.append({
                "century_label": century["label"],
                "century_summary": century["summary"],
                "fact": fact
            })

    total_facts = len(all_facts)

    start_date = date(2025, 1, 1)
    today = date.today()
    day_index = (today - start_date).days

    block_start = (day_index * FACTS_PER_DAY) % total_facts
    block_end   = block_start + FACTS_PER_DAY

    if block_end <= total_facts:
        todays_block = all_facts[block_start:block_end]
    else:
        todays_block = all_facts[block_start:] + all_facts[:block_end - total_facts]

    return todays_block, day_index, total_facts

# ── Format message ────────────────────────────────────────────────────────────
def format_message(facts_block, day_index, total_facts):
    today_str  = date.today().strftime("%B %d, %Y")
    total_days = (total_facts + FACTS_PER_DAY - 1) // FACTS_PER_DAY
    cycle_day  = (day_index % total_days) + 1

    centuries_in_block = []
    for item in facts_block:
        if item["century_label"] not in centuries_in_block:
            centuries_in_block.append(item["century_label"])
    century_header = " & ".join(centuries_in_block)

    lines = [
        f"HISTORY FLASHCARDS - {today_str}",
        f"Day {cycle_day} of {total_days} | {century_header}",
        "-" * 32,
    ]

    first_fact_index = (day_index * FACTS_PER_DAY) % total_facts
    if first_fact_index == 0 or facts_block[0]["century_label"] != facts_block[-1]["century_label"]:
        for century_label in centuries_in_block:
            for item in facts_block:
                if item["century_label"] == century_label:
                    lines.append(f"\n[ {century_label} ]")
                    lines.append(item["century_summary"])
                    lines.append("")
                    break

    for i, item in enumerate(facts_block, 1):
        lines.append(f"{i}. {item['fact']}")
        lines.append("")

    lines.append("-" * 32)
    lines.append("Sources: Misquoting Jesus (Ehrman) + The Rest is History")

    return "\n".join(lines)

# ── Split long messages ───────────────────────────────────────────────────────
def split_message(message, max_length=1500):
    """iMessage handles long messages natively, but splitting keeps things readable."""
    if len(message) <= max_length:
        return [message]

    chunks, current, length = [], [], 0
    for line in message.split("\n"):
        if length + len(line) + 1 > max_length and current:
            chunks.append("\n".join(current))
            current, length = [line], len(line)
        else:
            current.append(line)
            length += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks

# ── Send via iMessage (macOS only) ────────────────────────────────────────────
def send_imessage(message):
    chunks = split_message(message)
    print(f"Sending {len(chunks)} iMessage(s) to {TO_NUMBER}...")

    for i, chunk in enumerate(chunks, 1):
        # Escape backslashes and double quotes for AppleScript
        escaped = chunk.replace("\\", "\\\\").replace('"', '\\"')
        script = f'''
            tell application "Messages"
                set targetService to 1st service whose service type = iMessage
                set targetBuddy to buddy "{TO_NUMBER}" of targetService
                send "{escaped}" to targetBuddy
            end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  Error on part {i}: {result.stderr.strip()}")
            sys.exit(1)
        else:
            print(f"  Part {i}/{len(chunks)} sent via iMessage")

# ── Twilio SMS (kept for future use / A2P 10DLC registration) ─────────────────
# def send_sms(message):
#     from twilio.rest import Client
#     client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
#     chunks = split_message(message)
#     for i, chunk in enumerate(chunks, 1):
#         msg = client.messages.create(
#             body=chunk,
#             from_=os.environ["TWILIO_FROM_NUMBER"],
#             to=os.environ["TO_NUMBER"]
#         )
#         print(f"  Sent part {i}/{len(chunks)}: SID={msg.sid}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"[{date.today()}] Daily History Flashcards starting...")

    try:
        data = load_content()
        facts_block, day_index, total_facts = get_todays_facts(data)
        message = format_message(facts_block, day_index, total_facts)

        print("\n--- PREVIEW ---")
        print(message[:500] + "..." if len(message) > 500 else message)
        print(f"--- Total chars: {len(message)} ---\n")

        send_imessage(message)
        print("Done!")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
