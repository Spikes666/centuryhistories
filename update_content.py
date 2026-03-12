#!/usr/bin/env python3
"""
Weekly content updater — calls Claude API to generate new facts,
adds them to content.json, and pushes to GitHub.
"""
import json, os, subprocess, random
from datetime import datetime
import urllib.request, urllib.error

CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flashcards/content.json')
API_KEY_PATH = os.path.expanduser('~/.anthropic_api_key')
FACTS_TO_ADD = 5
LOG_PATH     = os.path.expanduser('~/centuryhistories/update.log')

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def get_api_key():
    if os.path.exists(API_KEY_PATH):
        with open(API_KEY_PATH) as f:
            return f.read().strip()
    return os.environ.get('ANTHROPIC_API_KEY', '')

def call_claude(prompt, api_key):
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data['content'][0]['text']

def generate_facts(century, existing_facts, api_key):
    existing_sample = '\n'.join(f'- {f["fact"]}' for f in existing_facts[:5])
    prompt = f"""You are a historian generating flashcard facts for an educational history app.

Century: {century['label']}
Era: {century['era']}
Summary: {century['summary']}

The app draws on these sources:
- "Misquoting Jesus" by Bart Ehrman (early Christianity, textual criticism, Biblical history)
- "The Rest is History" podcast by Tom Holland and Dominic Sandbrook (world history)
- "Dominion" by Tom Holland (how Christianity shaped Western civilization)

Here are some existing facts for this century (do NOT repeat these):
{existing_sample}

Generate exactly {FACTS_TO_ADD} new, distinct historical facts for this century.
Each fact should be 1-3 sentences, specific, and educational.
Draw on the same sources and themes as the existing facts.
Focus on facts not already covered above.

Return ONLY a JSON array of strings, no other text. Example format:
["Fact one here.", "Fact two here.", "Fact three here."]"""

    response = call_claude(prompt, api_key)
    response = response.strip()
    if response.startswith('```'):
        response = response.split('\n', 1)[1]
        response = response.rsplit('```', 1)[0]
    return json.loads(response.strip())

def get_region(fact_text):
    lower = fact_text.lower()
    QUICK_REGIONS = [
        (["constantinople","istanbul"],         41.0,  28.9, 8, "Constantinople (Istanbul), Turkey"),
        (["jerusalem"],                          31.8,  35.2, 9, "Jerusalem"),
        (["rome,","in rome","of rome","roman empire"], 41.9, 12.5, 6, "Rome, Italy"),
        (["egypt","alexandria","cairo"],         26.8,  30.8, 5, "Egypt"),
        (["persia","persian","iran"],            32.4,  53.7, 5, "Persia (modern Iran)"),
        (["mecca","medina","arabia","arab","islam","muslim"], 24.0, 45.0, 5, "Arabian Peninsula"),
        (["france","paris","french"],            46.2,   2.2, 5, "France"),
        (["england","britain","london"],         52.0,  -1.5, 6, "England / Britain"),
        (["germany","berlin","german"],          51.2,  10.5, 5, "Germany"),
        (["china","chinese","beijing"],          35.9, 104.2, 4, "China"),
        (["japan","japanese","tokyo"],           36.2, 138.3, 5, "Japan"),
        (["india","indian","delhi"],             20.6,  79.0, 4, "India"),
        (["russia","soviet","moscow"],           55.8,  37.6, 4, "Russia"),
        (["america","united states","washington"], 38.9, -95.7, 4, "United States"),
        (["greece","greek","athens"],            37.9,  23.7, 6, "Greece"),
        (["ottoman","turkey","turkish"],         39.0,  35.0, 5, "Ottoman Empire (modern Turkey)"),
        (["mongol","genghis","kublai"],          47.9, 106.9, 4, "Mongolia"),
        (["africa","mali","timbuktu"],            8.0,  21.0, 4, "Africa"),
    ]
    for keys, lat, lng, zoom, label in QUICK_REGIONS:
        if any(k in lower for k in keys):
            d = {2:60,3:35,4:22,5:12,6:6,7:3,8:1.5,9:0.7}.get(zoom, 8)
            bbox = f"{lng-d},{lat-d},{lng+d},{lat+d}"
            return {
                "map_label": label,
                "map_iframe": f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lng}"
            }
    return {
        "map_label": "The Mediterranean & Ancient World",
        "map_iframe": "https://www.openstreetmap.org/export/embed.html?bbox=-15,25,55,55&layer=mapnik"
    }

def git_push(message):
    repo = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(['git', '-C', repo, 'add', 'flashcards/content.json'], check=True)
    subprocess.run(['git', '-C', repo, 'commit', '-m', message], check=True)
    subprocess.run(['git', '-C', repo, 'push'], check=True)

def main():
    log("=== Content update starting ===")

    api_key = get_api_key()
    if not api_key:
        log("ERROR: No API key found. Create ~/.anthropic_api_key or set ANTHROPIC_API_KEY")
        return

    with open(CONTENT_PATH) as f:
        data = json.load(f)

    century = random.choice(data['centuries'])
    log(f"Updating: {century['label']} (currently {len(century['facts'])} facts)")

    try:
        new_fact_texts = generate_facts(century, century['facts'], api_key)
        log(f"Generated {len(new_fact_texts)} new facts")
    except Exception as e:
        log(f"ERROR generating facts: {e}")
        return

    added = 0
    for text in new_fact_texts:
        if text and text not in [f['fact'] for f in century['facts']]:
            maps = get_region(text)
            century['facts'].append({
                "fact": text,
                "map_label": maps['map_label'],
                "map_iframe": maps['map_iframe']
            })
            added += 1
            log(f"  + [{maps['map_label']}] {text[:70]}...")

    if added == 0:
        log("No new facts added — all duplicates or empty")
        return

    with open(CONTENT_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total = sum(len(c['facts']) for c in data['centuries'])
    log(f"Saved. Total facts: {total}")

    try:
        git_push(f"Auto: +{added} facts for {century['label']} [{datetime.now().strftime('%Y-%m-%d')}]")
        log("Pushed to GitHub successfully")
    except Exception as e:
        log(f"ERROR pushing to GitHub: {e}")

    log("=== Done ===")

if __name__ == '__main__':
    main()