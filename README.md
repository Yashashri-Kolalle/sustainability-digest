# 🌱 Daily Sustainability News Digest

A lightweight Python script that runs every morning on GitHub Actions, searches the web for today's sustainability news using Claude's built-in web search, summarizes it around your focus areas, and emails a clean digest to your inbox.

**Focus areas:** Corporate net zero · Green tech & startups · Clean energy & renewables · Climate policy & regulation

---

## How it works

```
GitHub Actions (7am daily)
  → digest.py
      → Claude API with web_search  →  finds today's news articles
      → Claude API (summarize)      →  structures into themed digest
      → Gmail SMTP                  →  sends HTML email to your inbox
```

**Cost:** ~$0.05–0.15 per day (Claude API). GitHub Actions is free.  
**Runtime:** ~30 seconds.

---

## Setup (15 minutes)

### 1. Fork / clone this repo to GitHub

Push these two files to a new GitHub repository:
- `digest.py`
- `.github/workflows/digest.yml`

### 2. Get your API keys

**Anthropic API key**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account and go to API Keys
3. Create a new key → copy it

**Gmail App Password** (for sending emails)
1. Go to your Google Account → Security
2. Enable 2-Step Verification if not already on
3. Search "App passwords" → create one named "Sustainability Digest"
4. Copy the 16-character password (you won't see it again)

> Note: This uses Gmail's SMTP to *send* the email. The recipient can be any email address.

### 3. Add secrets to GitHub

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

Add these four secrets:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `RECIPIENT_EMAIL` | Where you want the digest sent (e.g. you@gmail.com) |
| `SENDER_EMAIL` | The Gmail address that sends it (e.g. you@gmail.com — can be the same) |
| `SENDER_APP_PASSWORD` | The 16-char Gmail App Password from step 2 |

### 4. Test it

Go to your repo → **Actions** tab → **Daily Sustainability Digest** → **Run workflow** → **Run workflow**

Wait ~30 seconds and check your inbox. ✓

---

## Customise

**Change the topics:** Edit `FOCUS_AREAS` in `digest.py`

**Change the schedule:** Edit the cron in `.github/workflows/digest.yml`  
Use [crontab.guru](https://crontab.guru) to build your expression.  
`"0 7 * * 1-5"` = 7am UTC weekdays

**Add more sources:** Claude's web search already casts a wide net, but you can add a list of preferred outlets to the search prompt.

---

## Stack

- **Python 3.12** — no framework, minimal dependencies
- **Anthropic Python SDK** — web search + summarization
- **Claude claude-opus-4-5** — the model doing the work
- **GitHub Actions** — free cloud scheduler
- **Gmail SMTP** — email delivery (built into Python's standard library)

---

*Built with Claude · [Anthropic API docs](https://docs.anthropic.com)*
