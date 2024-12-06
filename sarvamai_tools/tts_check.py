import requests
import base64
import os
from typing import Optional
from dotenv import load_dotenv
from sarvamai_tools.translation_check import translate_text

load_dotenv()

def text_to_speech(
    text: str,
    target_language: str = "en-IN",
    speaker: str = "meera"
) -> Optional[str]:
    """Convert text to speech using Sarvam.ai API"""
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("API key is required")
    
    # Truncate text to 500 characters
    text = text[:500]
    
    # Translate text if target language is not English
    if target_language != "en-IN":
        try:
            text = translate_text(
                input_text=text,
                target_language=target_language,
                source_language="en-IN"
            )

            print("text after translation is ", text)

        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    text = text[:500]
    
    url = "https://api.sarvam.ai/text-to-speech"
    
    payload = {
        "inputs": [text],
        "target_language_code": target_language,
        "speaker": speaker,
        "model": "bulbul:v1"
    }
    
    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result["audios"][0] if result["audios"] else None
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")