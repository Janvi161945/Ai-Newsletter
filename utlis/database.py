from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


def save_preferences(email: str, topics: list):
    """Save or update user preferences"""
    try:
        # First check if the email exists
        existing = supabase.table('user_preference').select('id').eq('email', email).execute()

        if existing.data:
            # Update existing record
            data = supabase.table('user_preference').update({
                'topics': topics
            }).eq('email', email).execute()
        else:
            # Insert new record
            data = supabase.table('user_preference').insert({
                'email': email,
                'topics': topics
            }).execute()

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_user_preferences(email: str):
    """Get user preferences by email"""
    try:
        response = supabase.table('user_preference')\
            .select("*")\
            .eq('email', email)\
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error: {e}")
        return None


def save_twitter_prefs(email: str, handles: list, hashtags: list):
    """Save user Twitter preferences (handles and hashtags) into user_preference."""
    try:
        existing = supabase.table('user_preference').select('id').eq('email', email).execute()
        payload = {
            'twitter_handles': handles,
            'twitter_hashtags': hashtags
        }
        if existing.data:
            supabase.table('user_preference').update(payload).eq('email', email).execute()
        else:
            payload.update({'email': email, 'topics': []})
            supabase.table('user_preference').insert(payload).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_twitter_prefs(email: str):
    """Get twitter handles/hashtags from user_preference."""
    try:
        response = supabase.table('user_preference')\
            .select("twitter_handles, twitter_hashtags")\
            .eq('email', email)\
            .execute()
        if response.data:
            row = response.data[0]
            return row.get('twitter_handles') or [], row.get('twitter_hashtags') or []
        return [], []
    except Exception as e:
        print(f"Error: {e}")
        return [], []


def save_style_samples(email: str, samples: list):
    """Save or update user's writing style samples (list of text blocks)."""
    try:
        # Upsert by email
        existing = supabase.table('user_style_samples').select('id').eq('email', email).execute()
        if existing.data:
            supabase.table('user_style_samples').update({
                'samples': samples
            }).eq('email', email).execute()
        else:
            supabase.table('user_style_samples').insert({
                'email': email,
                'samples': samples
            }).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_style_samples(email: str):
    """Fetch user's writing style samples (list of text blocks) or []."""
    try:
        resp = supabase.table('user_style_samples').select('samples').eq('email', email).execute()
        if resp.data:
            return resp.data[0].get('samples') or []
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def save_feedback(email: str, rating: str, notes: str, subject: str):
    """Save inline feedback on a generated draft."""
    try:
        supabase.table('newsletter_feedback').insert({
            'email': email,
            'rating': rating,  # 'up' | 'down'
            'notes': notes,
            'subject': subject
        }).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def log_send(email: str, subject: str, categories: list):
    """Log a sent newsletter event for analytics (acceptance proxy)."""
    try:
        supabase.table('newsletter_sends').insert({
            'email': email,
            'subject': subject,
            'categories': categories
        }).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
