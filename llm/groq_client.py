"""
SolarSathi AI - Groq LLM Client

Phase 6

This module provides a safe and simple interface
between SolarSathi AI and the Groq API.

The API key is NEVER hardcoded.
It is read from Streamlit Secrets.
"""

import streamlit as st
from groq import Groq


DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_groq_client():
    """
    Create and return a Groq client.

    The API key is loaded from Streamlit Secrets.
    """

    try:

        api_key = st.secrets["GROQ_API_KEY"]

    except Exception:

        return None

    if not api_key:

        return None

    try:

        return Groq(
            api_key=api_key
        )

    except Exception:

        return None


def generate_ai_response(
    system_prompt,
    user_prompt,
    model=DEFAULT_MODEL,
    temperature=0.2,
):
    """
    Send a prompt to Groq and return the response.

    Returns:
        dict containing success status and response.
    """

    client = get_groq_client()

    if client is None:

        return {
            "success": False,
            "response": "",
            "error": (
                "Groq API key is missing or the "
                "Groq client could not be initialized."
            ),
        }

    try:

        completion = client.chat.completions.create(

            model=model,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],

            temperature=temperature,

        )

        response_text = (
            completion
            .choices[0]
            .message
            .content
        )

        return {
            "success": True,
            "response": response_text,
            "error": None,
        }

    except Exception as error:

        return {
            "success": False,
            "response": "",
            "error": str(error),
        }
