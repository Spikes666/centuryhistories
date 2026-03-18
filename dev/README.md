<<<<<<< HEAD
# centuryhistories
Daily History Facts
=======
# 📜 Daily History Flashcards

Daily SMS flashcards covering world history from pre-CE Middle East through the centuries.  
Content drawn from **Misquoting Jesus** (Bart Ehrman) and **The Rest is History** (Tom Holland & Dominic Sandbrook).

**10 facts per day • Sequential by century • Delivered at 8:00 AM CST**

---

## 🚀 Deploy on Render (Recommended)

### Step 1: Set Up Twilio

1. Go to [twilio.com](https://twilio.com) → sign up free
2. Verify your phone number during signup
3. From the Twilio Console dashboard, copy:
   - **Account SID** (starts with `AC...`)
   - **Auth Token**
   - **Your Twilio phone number** (assigned free during signup)

> Free trial gives ~$15 credit — enough for hundreds of daily texts.

---

### Step 2: Push to GitHub

```bash
# Create a new repo on github.com, then:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/history-flashcards.git
git push -u origin main
```

**Important:** Make sure `.env` is in `.gitignore` (it is by default). Never push your real credentials.

---

### Step 3: Deploy on Render

1. Go to [render.com](https://render.com) → sign up free
2. Click **"New +"** → **"Cron Job"**
3. Connect your GitHub account and select the `history-flashcards` repo
4. Render will auto-detect `render.yaml` — confirm the settings:
   - **Name:** history-flashcards
   - **Schedule:** `0 13 * * *` (8:00 AM CST)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python daily_flashcards.py`
5. Click **"Advanced"** → **"Add Environment Variable"** and add all four:

| Key | Value |
|-----|-------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_FROM_NUMBER` | Your Twilio phone number (e.g. `+16155551234`) |
| `TO_NUMBER` | `+16156046386` |

6. Click **"Create Cron Job"**

That's it. Render will run the script every day at 8:00 AM CST and text you 10 flashcards.

---

### Step 4: Test It Manually

In the Render dashboard, find your cron job and click **"Trigger Run"** to send a test text immediately.

---

## 🥧 Alternative: Raspberry Pi

If you prefer self-hosting on your Raspberry Pi:

```bash
# On your Pi:
git clone https://github.com/YOUR_USERNAME/history-flashcards.git
cd history-flashcards
pip3 install -r requirements.txt

# Create your .env file
cp .env.example .env
nano .env   # fill in your real Twilio credentials

# Test it
python3 daily_flashcards.py

# Schedule with cron (8:00 AM daily)
crontab -e
# Add this line:
# 0 8 * * * /usr/bin/python3 /home/pi/history-flashcards/daily_flashcards.py >> /home/pi/history-flashcards/log.txt 2>&1
```

---

## 📚 Content Coverage

| Century | Period |
|---------|--------|
| Pre-CE Middle East | 3000 BCE – 1 BCE |
| 1st Century CE | 1 – 99 CE |
| 2nd Century CE | 100 – 199 CE |
| 3rd Century CE | 200 – 299 CE |
| 4th Century CE | 300 – 399 CE |
| 5th Century CE | 400 – 499 CE |
| *(More centuries to be added)* | ... |

Facts cycle sequentially — all facts in a century are delivered before moving to the next.  
When all content is exhausted, the cycle restarts.

---

## 🔧 Troubleshooting

- **No text received:** Check Render logs → Dashboard → your cron job → "Logs"
- **Wrong time:** Render uses UTC. 8:00 AM CST = `0 14 * * *` during CDT (summer). Adjust `render.yaml` seasonally or use a timezone-aware approach.
- **Twilio error:** Verify your trial account has verified the destination phone number at twilio.com/console/phone-numbers/verified
>>>>>>> b39830c (Initial commit)
