# 📜 Century Histories

A daily history flashcard game covering world history from pre-CE Middle East through the centuries, plus a daily nudge sent straight to your phone.

Content drawn from **Misquoting Jesus** (Bart Ehrman), **The Rest is History** (Tom Holland & Dominic Sandbrook), and **Dominion** (Tom Holland).

Live site: **https://spikes666.github.io/centuryhistories/**

---

## What's here

- **The web app** — static HTML/JS, no build step. `game.html` is the main game (Subject Thread Journey + Classic minigame modes); `index.html` is a simple flashcard browser. Deployed automatically to GitHub Pages by `.github/workflows/deploy.yml`: pushes to `main` go live at the root, pushes to `dev` go live at `/dev/` as a preview.
- **The daily nudge** — `daily_flashcards_imessage.py` sends one fact per day via iMessage (macOS only, uses `osascript` + Messages.app), scheduled with `cron`. `send_sms.py` is an alternative that works anywhere (including a Raspberry Pi) via a Gmail-to-SMS gateway instead of iMessage. See below.
- **Content** — `flashcards/content.json` holds every century, fact, and thematic "thread." `update_content.py` calls the Claude API weekly to generate new facts and pushes them straight to `main`.

## Running the daily iMessage script

This needs to run on a Mac (iMessage delivery is macOS-only), on a `cron` schedule:

```bash
crontab -e
# Add this line to send at 8:00 AM daily:
# 0 8 * * * /usr/bin/python3 /path/to/centuryhistories/daily_flashcards_imessage.py >> /path/to/centuryhistories/log.txt 2>&1
```

It picks a fact deterministically from today's date (same fact all day, a different one each morning) and sends it to the number hardcoded in the script (`TO_NUMBER`). No API keys or `.env` file needed — it reads directly from `flashcards/content.json`.

### Alternative: Gmail-to-SMS gateway

`send_sms.py` is a second delivery option that emails a fact through a carrier's email-to-SMS gateway (e.g. `vtext.com`) via Gmail SMTP instead of iMessage — useful if you want this running on a Raspberry Pi or anything that isn't a Mac. It keeps a shuffled "deck" in `sms_state.json` so every fact is seen once before any repeat. Requires a `~/.gmail_address` and `~/.gmail_app_password` file (a Gmail [app password](https://myaccount.google.com/apppasswords), not your real password).

## Updating content

`update_content.py` picks a random century, asks the Claude API for 5 new non-duplicate facts, geotags them, and commits + pushes the result to `flashcards/content.json` on `main`. It reads the API key from `~/.anthropic_api_key` or `$ANTHROPIC_API_KEY`. Run it manually or on its own schedule (e.g. weekly via cron) wherever you have git push access to this repo.

## Content coverage

Facts cycle sequentially through 23 centuries, from the pre-CE Middle East through the modern world. Facts within a century are also organized into cross-century "threads" (e.g. Medicine & Science) that the Journey mode in `game.html` walks you through.
