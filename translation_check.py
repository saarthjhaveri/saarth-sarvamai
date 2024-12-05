import requests
import os
from dotenv import load_dotenv

load_dotenv()

def translate_text(
    input_text: str,
    target_language: str,
    source_language: str = "en-IN",
    speaker_gender: str = "Male",
    mode: str = "formal"
) -> str:
    
    print("target_language is ", target_language)
    print("input text in translate text is ", input_text)
    

    """Translate text using Sarvam.ai API"""
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("API key is required")
    
    url = "https://api.sarvam.ai/translate"
    
    payload = {
        "input": input_text,
        "source_language_code": source_language,
        "target_language_code": target_language,
        "speaker_gender": speaker_gender,
        "mode": mode,
        "model": "mayura:v1",
        "enable_preprocessing": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result["translated_text"]
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    


