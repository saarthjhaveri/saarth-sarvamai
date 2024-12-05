import requests
import os
from dotenv import load_dotenv

load_dotenv()

def transcribe_and_translate_audio(audio_file_path, prompt=None):
    print("entered inside transcribe and translate ")

    print("audio file path ", audio_file_path)

    """
    Transcribe and translate audio using Sarvam.ai Speech-to-Text-Translate API
    """
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("API key is required")

    url = "https://api.sarvam.ai/speech-to-text-translate"
    
    files = {
        'file': ('audio.wav', open(audio_file_path, 'rb'), 'audio/wav')
    }
    
    data = {
        'model': 'saaras:v1'
    }
    
    if prompt:
        data['prompt'] = prompt
    
    headers = {
        'api-subscription-key': api_key
    }
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        response.raise_for_status()
        print("transcription response is ", response.json())



        return response.json().get("transcript", ""), response.json().get("language_code", "en-IN")
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error occurred: {e}")