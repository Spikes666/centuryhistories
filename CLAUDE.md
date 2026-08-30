# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A daily-history-facts project with two halves:

1. **A static web app** (plain HTML/CSS/JS, no build step, no `package.json`) deployed to GitHub Pages via `.github/workflows/deploy.yml`. Pushes to `main` deploy to the site root; pushes to `dev` deploy to `/dev/` (a preview copy, `keep_files: true` so the two don't clobber each other).
2. **Python delivery/content scripts** that text a subset of the facts to one hardcoded phone number daily (Twilio SMS, Gmail-to-SMS gateway, or macOS iMessage) and a script that uses the Claude API to generate new facts weekly.

There is no test suite, linter, or build tooling in this repo — verification is manual (open the HTML in a browser, or run a Python script and read its printed preview/log output).

## Content data model

`flashcards/content.json` is the single source of truth for all facts and is fetched by every frontend **directly from GitHub raw** (`https://raw.githubusercontent.com/Spikes666/centuryhistories/main/flashcards/content.json`), not from a local relative path — so a local edit to this file has no visible effect in a browser until it's pushed to `main`.

Shape:
```
{
  "centuries": [
    { "id", "label", "summary", "era", "facts": [
        { "fact", "map_label", "map_url", "map_iframe" }
    ]}
  ],
  "threads": [
    { "id", "name", "icon", "description", "waypoints": [
        { "century_id", "fact_index", "connective" }
    ]}
  ]
}
```
- `centuries` are ordered chronologically; `facts` within a century are also delivery-ordered (scripts rely on list order, not dates in the text).
- `era` groups centuries into six buckets used for styling/icons (Ancient World, Medieval, Renaissance & Reformation, Age of Exploration & Enlightenment, Industrial Age, Modern World) — see `ERA_ICONS`/`ERA_STYLES` blocks duplicated in each HTML file and in `daily_flashcards_imessage.py`/`send_sms.py`.
- `map_iframe`/`map_url` are OpenStreetMap embed/static-map URLs keyed off a lat/lng the fact's text was matched into. The keyword→coordinate lookup table (`REGIONS`) exists **in triplicate**: `update_content.py`'s `get_region()`, `remap_content.py`, and `remap_content_v2.py`. If you add a new region keyword, keep these in sync (`remap_content_v2.py` is the most refined/latest version; `remap_content.py` is the older one that's still checked in for reference).
- `threads` define "Subject Thread Journey" paths through history (e.g. Medicine & Science) — an ordered list of waypoints, each pointing at a `century_id` + `fact_index` in `centuries`, connected by narrative `connective` sentences. Only `flashcards/content.json` has `threads`; the root-level `content.json` does not (see below).
- There is a second, much smaller `content.json` at the repo root (6 centuries, no `threads`) — it is not fetched by any frontend or script and looks like a stale/earlier snapshot. Don't confuse it with `flashcards/content.json`.

## Frontend apps

Four standalone, single-file HTML documents, each with inline `<style>` and `<script>` — no shared JS module, no bundler. Logic (fact parsing, scoring, localStorage helpers) is duplicated across files rather than factored out; when fixing a bug in one, check whether the same bug exists in the others.

- **`index.html`** — simple flashcard browser: "today's facts" view plus a "browse by era/century" view. Fetches content async in `loadContent()`.
- **`game.html`** — the current, actively-developed game. Combines a "Subject Thread Journey" mode (follow a `threads` entry across centuries, `STORAGE_KEY = 'ch_journey_v1'`) with a "Classic" mode (round-based Jeopardy/Wordle/Chrono-order minigames per century, `CLASSIC_KEY = 'ch_game_v2'`). This is the one most recently touched (see git log) — prefer extending this over the other two game variants unless asked otherwise.
- **`game-classic.html`** — the standalone predecessor of game.html's Classic mode (same `STORAGE_KEY = 'ch_game_v2'`, so state is shared/compatible between the two). Kept for the pre-Journey experience.
- **`retro-game.html`** — a terminal/C64-styled version of the game (ASCII box-drawing UI, on-screen keyboard, theme cycling between "fallout"/other retro palettes). Independent `localStorage` keys (`ch_retro_v2`, `retroTheme`).

All four implement variants of the same minigames: Jeopardy-style Q&A (`Jeo`), Wordle-style keyword guessing (`Wordle`), and chronological-ordering (`Chrono`). Session/round state is kept in a module-level object (`G` in game.html, `SC` for its classic sub-mode) and persisted to `localStorage` under the keys above — there's no server-side state.

The GitHub Pages deploy is dumb static hosting: whatever HTML/JS is committed is what ships, so changes are live as soon as they land on `main` (or `dev` for the `/dev/` preview) and the Pages workflow runs.

## Python scripts

All scripts resolve `flashcards/content.json` relative to their own file location (`os.path.dirname(os.path.abspath(__file__))`), so they work regardless of the caller's cwd — unlike the frontends, they read the **local** file, not the GitHub raw copy.

- **`daily_flashcards.py`** — Twilio SMS delivery of 10 facts/day, sequential (exhausts one century before moving to the next), position derived deterministically from days-since-2025-01-01 modulo total fact count (no external state file). Deployed as a Render cron job (`render.yaml`, runs 13:00 UTC daily). Requires `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `TO_NUMBER` env vars (see `.env.example`).
- **`daily_flashcards_imessage.py`** — macOS-only, sends 1 fact/day via `osascript`/Messages.app, using the date as a random seed so the fact is stable within a day but differs day-to-day (no state file). Twilio-based alternative is left commented out inside the file for future re-use.
- **`send_sms.py`** — Gmail-to-SMS-gateway delivery (`vtext.com`), 1 fact/day, using a persisted shuffled "deck" (`sms_state.json`) so all facts are seen once before any repeat, reshuffling when exhausted. Reads Gmail credentials from `~/.gmail_address` / `~/.gmail_app_password` (not env vars, unlike the other two senders). `sms_state.json` is gitignored — don't expect it to exist in a fresh checkout.
- **`update_content.py`** — weekly content generator: picks a random century, calls the Claude API (model id hardcoded, reads the key from `~/.anthropic_api_key` or `$ANTHROPIC_API_KEY`) to generate 5 new non-duplicate facts, geotags them via the inline `get_region()` keyword table, appends them to `flashcards/content.json`, and **commits + pushes directly to the current git remote** (`git_push()`) — this script has side effects on git history when run for real. Logs to `~/centuryhistories/update.log` (absolute path, not repo-relative like the other logs).
- **`fetch_content.py`** — a one-off migration script that rewrote `index.html` to fetch content remotely instead of inlining it; not part of the regular workflow, kept as a record of that change.
- **`remap_content.py`** / **`remap_content_v2.py`** — one-off batch scripts that re-derive `map_label`/`map_iframe` for every fact in `flashcards/content.json` from a keyword table. Not run automatically; run manually when the geotagging table is improved. v2 has tighter/less-false-positive-prone keyword matching than v1.

## Working in this repo

- There's no install step beyond `pip install -r requirements.txt` (only `twilio` + `python-dotenv`, needed for `daily_flashcards.py`). The other scripts use only the stdlib.
- To "run" a frontend change, just open the HTML file in a browser (or serve the directory) — there's no dev server or build.
- To sanity-check a Python script without sending a real message, read its printed `--- PREVIEW ---` output; every sender script prints the composed message before attempting delivery.
- When editing the fact/century/thread data model, update `flashcards/content.json` (not the root `content.json`), and remember every consumer re-derives its own flattened fact list from `centuries` — there's no shared parsing helper between the frontends and the Python scripts.
- `README.md` currently contains an unresolved git merge-conflict (`<<<<<<<`/`=======`/`>>>>>>>` markers still committed) — be aware the file is not valid Markdown as-is if you need to read or edit it.
