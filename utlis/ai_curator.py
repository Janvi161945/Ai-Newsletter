from groq import Groq
import os
from typing import List
from utils.database import get_style_samples

def curate_newsletter(articles: list, user_topics: list, user_email: str = None):
    """Use Groq LLM to curate and summarize articles with optional style guidance.
    Returns a single draft string that includes two subject variants labeled SUBJECT_A and SUBJECT_B.
    """
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Combine articles into context
    context = "\n\n".join([
        f"Source: {a['source']}\n{a['content']}" 
        for a in articles
    ])
    
    # Style guidance
    style_examples: List[str] = []
    if user_email:
        style_examples = get_style_samples(user_email) or []
    style_block = "\n\n".join([f"STYLE_EXAMPLE:\n{ex.strip()}" for ex in style_examples[:5]])
    style_hint = ("If STYLE_EXAMPLE blocks are provided, match tone, cadence, and structure. "
                  "Keep the draft concise and scannable.") if style_block else ""

    prompt = f"""You are an AI newsletter curator. Based on these articles about {', '.join(user_topics)}, create:

1. TWO catchy subject lines (distinct). Label them SUBJECT_A and SUBJECT_B.
2. A 3-paragraph summary of the most important developments
3. One key learning point
4. One action item the reader can do today

Articles:
{context}

{style_block}

Guidance: {style_hint}

Format your response as:
SUBJECT_A: [subject A]
SUBJECT_B: [subject B]
SUMMARY: [3 paragraphs]
LEARNING: [key point]
ACTION: [one specific task]
"""
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content


def regenerate_section(articles: list, user_topics: list, section: str, user_email: str = None):
    """Regenerate a specific section: SUMMARY | LEARNING | ACTION."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    context = "\n\n".join([
        f"Source: {a['source']}\n{a['content']}" 
        for a in articles
    ])
    style_examples: List[str] = []
    if user_email:
        style_examples = get_style_samples(user_email) or []
    style_block = "\n\n".join([f"STYLE_EXAMPLE:\n{ex.strip()}" for ex in style_examples[:5]])
    style_hint = ("Match tone, cadence, and structure of examples if provided.") if style_block else ""

    prompt = f"""Regenerate ONLY the {section} for a newsletter about {', '.join(user_topics)}.

Articles:
{context}

{style_block}

Guidance: {style_hint}

Respond with exactly one block labeled {section}: and nothing else.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
