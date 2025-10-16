import os
import sys
from dotenv import load_dotenv
from utils.database import get_user_preferences
from utils.scraper import scrape_sources, detect_trends
from utils.ai_curator import curate_newsletter
from utils.email_sender import send_newsletter
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def main():
    # Fetch all users with preferences
    resp = supabase.table('user_preference').select('email, topics').execute()
    users = resp.data or []
    for row in users:
        email = row.get('email')
        topics = row.get('topics') or []
        if not email or not topics:
            continue
        category = topics[0]
        try:
            articles = scrape_sources(category)
            trends = detect_trends(articles)
            content = curate_newsletter(articles, [category], user_email=email)
            if trends:
                trends_block = "\n".join([f"- {t['topic'].title()}: {t['title']} ({t['link']}) — {t['why']}" for t in trends])
                content += f"\n\nTRENDS TO WATCH:\n{trends_block}"
            send_newsletter(email, content)
            print(f"Sent to {email}")
        except Exception as e:
            print(f"Error for {email}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()


