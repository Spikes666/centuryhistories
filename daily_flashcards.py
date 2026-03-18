#!/usr/bin/env python3
"""
Daily History Flashcards — SMS Delivery Script
Sends 10 sequential flashcards via Twilio every morning.
Draws on content from Misquoting Jesus (Bart Ehrman) and The Rest is History.
"""

import json
import os
import sys
from datetime import date
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
ACCOUNT_SID  = os.environ["TWILIO_ACCOUNT_SID"]
AUTH_TOKEN   = os.environ["TWILIO_AUTH_TOKEN"]
FROM_NUMBER  = os.environ["TWILIO_FROM_NUMBER"]
TO_NUMBER    = os.environ["TO_NUMBER"]
FACTS_PER_DAY = 10

CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flashcards", "content.json")

# ── Load content ─────────────────────────────────────────────────────────────
def load_content():
    with open(CONTENT_PATH, "r") as f:
        return json.load(f)

# ── Determine today's facts ───────────────────────────────────────────────────
def get_todays_facts(data):
    """
    Sequential delivery: exhaust one century before moving to the next.
    Uses a global day index based on days since epoch to determine position.
    """
    # Flatten all facts with century metadata
    all_facts = []
    for century in data["centuries"]:
        for fact in century["facts"]:
            all_facts.append({
                "century_label": century["label"],
                "century_summary": century["summary"],
                "fact": fact
            })

    total_facts = len(all_facts)
    
    # Day index: days since a fixed start date (Jan 1, 2025)
    start_date = date(2025, 1, 1)
    today = date.today()
    day_index = (today - start_date).days

    # Calculate which block of 10 we're on (wraps around when content exhausted)
    block_start = (day_index * FACTS_PER_DAY) % total_facts
    block_end = block_start + FACTS_PER_DAY

    # Handle wrap-around
    if block_end <= total_facts:
        todays_block = all_facts[block_start:block_end]
    else:
        todays_block = all_facts[block_start:] + all_facts[:block_end - total_facts]

    return todays_block, day_index, total_facts

# ── Format message ────────────────────────────────────────────────────────────
def format_message(facts_block, day_index, total_facts):
    today_str = date.today().strftime("%B %d, %Y")
    total_days = (total_facts + FACTS_PER_DAY - 1) // FACTS_PER_DAY
    cycle_day = (day_index % total_days) + 1

    # Detect century header (may span multiple centuries in one block)
    centuries_in_block = []
    for item in facts_block:
        if item["century_label"] not in centuries_in_block:
            centuries_in_block.append(item["century_label"])
    century_header = " & ".join(centuries_in_block)

    lines = [
        f"📜 HISTORY FLASHCARDS — {today_str}",
        f"📅 Day {cycle_day} of {total_days} | {century_header}",
        "─" * 30,
    ]

    # Check if this is the first fact of a new century (add summary)
    first_fact_index = (day_index * FACTS_PER_DAY) % total_facts
    if first_fact_index == 0 or facts_block[0]["century_label"] != facts_block[-1]["century_label"]:
        for century_label in centuries_in_block:
            for item in facts_block:
                if item["century_label"] == century_label:
                    lines.append(f"\n🗺️ {century_label}")
                    lines.append(item["century_summary"])
                    lines.append("")
                    break

    for i, item in enumerate(facts_block, 1):
        lines.append(f"{i}. {item['fact']}")
        lines.append("")  # blank line between facts

    lines.append("─" * 30)
    lines.append("📚 Sources: Misquoting Jesus (Ehrman) • The Rest is History (Holland & Sandbrook)")

    return "\n".join(lines)

# ── Split long SMS ────────────────────────────────────────────────────────────
def split_message(message, max_length=1600):
    """Split message into chunks if needed (Twilio handles up to 1600 chars per segment)."""
    if len(message) <= max_length:
        return [message]
    
    chunks = []
    lines = message.split("\n")
    current_chunk = []
    current_length = 0
    
    for line in lines:
        if current_length + len(line) + 1 > max_length and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = len(line)
        else:
            current_chunk.append(line)
            current_length += len(line) + 1
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks

# ── Send SMS ──────────────────────────────────────────────────────────────────
def send_sms(message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    chunks = split_message(message)
    
    print(f"Sending {len(chunks)} message(s) to {TO_NUMBER}...")
    
    for i, chunk in enumerate(chunks, 1):
        msg = client.messages.create(
            body=chunk,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print(f"  Sent part {i}/{len(chunks)}: SID={msg.sid}")

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
        
        send_sms(message)
        print("✅ Done!")
        
    except KeyError as e:
        print(f"❌ Missing environment variable: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
