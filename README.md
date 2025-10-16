# AI Newsletter MVP (CreatorPulse)

A personalized AI newsletter application built with Streamlit. Users sign up/sign in, pick a topic, and receive an AI‑curated newsletter via email. Optional daily cron can send newsletters automatically for saved users.





https://github.com/user-attachments/assets/748f62e9-1d83-4f6d-99be-74fd88e50c09



## What happens when you clone and run

1. You install Python deps and start Streamlit (`streamlit run app.py`).
2. On first launch, the app initializes Supabase auth session state. You'll see tabs for Sign In / Sign Up.
3. After signing in, you land on the main page:
   - Choose a topic tab (AI, Machine Learning, Data Science, Technology) sourced from `config/sources.py`.
   - Optionally enter Twitter handles/hashtags to personalize sources.
   - Click "Generate My Newsletter":
     - The app scrapes recent items from configured APIs (Hacker News, Reddit, ArXiv) and, if configured, Twitter API v2.
     - It calls Groq LLM to curate a draft with two subject lines, a summary, learning, and action.
     - It appends a SOURCES block listing links used.
     - It sends an email via Resend to your account email and shows a preview in the UI.
4. Preferences and analytics are saved to Supabase tables (`user_preference`, `user_style_samples`, `newsletter_feedback`, `newsletter_sends`).

If required environment variables are missing, you may see warnings/errors: missing Supabase URL/Key (auth/storage fails), missing GROQ_API_KEY (AI curation fails), missing RESEND_API_KEY (email sending fails), or missing TWITTER_BEARER_TOKEN (Twitter scrape is skipped and the app falls back to default sources).

## Requirements

- Python 3.10+
- Accounts/keys:
  - Supabase project: `SUPABASE_URL`, `SUPABASE_KEY`
  - Groq API: `GROQ_API_KEY`
  - Resend API: `RESEND_API_KEY`
  - Twitter API v2 bearer: `TWITTER_BEARER_TOKEN` (optional but recommended)

## Environment setup

Create a `.env` file in `MVP-c5/` with:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_key
RESEND_API_KEY=your_resend_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

For Streamlit secrets used by the database module, also add a `.streamlit/secrets.toml` file (or set these via Streamlit Cloud secrets):

```
[general]

[secrets]
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key"
```

Note: `utils/database.py` reads `st.secrets["SUPABASE_URL"]` and `st.secrets["SUPABASE_KEY"]`. `utils/auth.py` uses dotenv and `os.getenv`. Ensure both are set appropriately for local runs.

## Install and run

1. Clone:

   ```bash
   git clone https://github.com/Janvi161945/Ai-Newsletter
   cd Ai-Newsletter
   ```

2. Create venv and install:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment: add `.env` and `.streamlit/secrets.toml` as above.

4. Run app:

   ```bash
   streamlit run app.py
   ```

5. Open in browser: `http://localhost:8501`

## Data model (Supabase)

Create these tables in Supabase:

- `user_preference` { id UUID pk, email text unique, topics jsonb, twitter_handles jsonb, twitter_hashtags jsonb }
- `user_style_samples` { id UUID pk, email text unique, samples jsonb }
- `newsletter_feedback` { id UUID pk, email text, subject text, rating text, notes text, created_at timestamp default now() }
- `newsletter_sends` { id UUID pk, email text, subject text, categories jsonb, sent_at timestamp default now() }

## Sources configuration

Edit `config/sources.py` to adjust categories, API sources (Hacker News, Reddit, ArXiv), and default Twitter handles/hashtags per category.

## Optional: Twitter integration

Set `TWITTER_BEARER_TOKEN` in `.env`. Users can add handles/hashtags in the UI; the scraper fetches recent tweets via v2 endpoints. If Twitter is unavailable, the app falls back to non‑Twitter sources.

## Optional: Daily cron

You can trigger bulk sends for all users with saved preferences using `utils/daily_send.py`. Example cron (daily 08:00):

```bash
0 8 * * * cd /path/to/MVP-c5 && /usr/bin/bash -lc 'source venv/bin/activate && python -m utils.daily_send >> cron.log 2>&1'
```

## Project Structure

```
MVP-c5/
├── app.py                 # Streamlit app: auth, topic selection, generate/send
├── config/
│   └── sources.py         # News source config per category
├── utils/
│   ├── ai_curator.py      # Groq LLM prompt/curation
│   ├── auth.py            # Supabase auth helpers
│   ├── daily_send.py      # Cron entrypoint to send to all users
│   ├── database.py        # Supabase reads/writes (uses st.secrets)
│   ├── email_sender.py    # Resend email sending
│   └── scraper.py         # Scraping APIs (HN, Reddit, ArXiv, Twitter)
├── requirements.txt
└── README.md
```

## Troubleshooting

- Sign in fails: verify `SUPABASE_URL`/`SUPABASE_KEY` in both `.env` (for `auth.py`) and `secrets.toml` (for `database.py`).
- Generation fails: check `GROQ_API_KEY`.
- Email not delivered: ensure `RESEND_API_KEY` and sender domain; logs printed in console.
- Twitter errors: set `TWITTER_BEARER_TOKEN` or disable Twitter by clearing handles/hashtags.

