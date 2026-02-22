import requests
import json
import base64
from pathlib import Path

API_KEY_1 = "openrouter api keys 1"
API_KEY_2 = "openrouter api keys 2"
API_KEY_3 = "openrouter api keys 3"
API_KEY_4 = "openrouter api keys 4"
API_KEY_5 = "openrouter api keys 5"
API_KEY_6 = "openrouter api keys 6"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def image_verification(promt, image_path, model_id, api_key):
    # Default to API_KEY_1 if no api_key is provided
    api_keys = {
        1: API_KEY_6,
        2: API_KEY_2,
        3: API_KEY_3,
        4: API_KEY_4,
        5: API_KEY_5
    }
    image_api = api_keys.get(api_key, API_KEY_1)  # Use the provided api_key or default to API_KEY_1

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {image_api}",
        "Content-Type": "application/json"
    }
    base64_image = encode_image_to_base64(image_path)
    data_url = f"data:image/jpeg;base64,{base64_image}"
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": promt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }
            ]
        }
    ]

    payload = {
        "model": model_id,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def report_verification(report,model_id,api_key):
    api_keys = {
        1: API_KEY_1,
        2: API_KEY_2,
        3: API_KEY_3,
        4: API_KEY_4,
        5: API_KEY_5
    }
    report_api = api_keys.get(api_key, API_KEY_6)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {report_api}",
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": report
                }
            ]
        }
    ]
    payload = {
        "model": model_id,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def risk_assessment_system(report,model_id, api_key):
    api_keys = {
        1: API_KEY_2,
        2: API_KEY_3,
        3: API_KEY_4,
        4: API_KEY_5,
        5: API_KEY_6
    }
    risk_api = api_keys.get(api_key, API_KEY_1)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {risk_api}",
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": report
                }
            ]
        }
    ]
    payload = {
        "model": model_id,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def summarize(report,model_id, api_key):
    api_keys = {
        1: API_KEY_3,
        2: API_KEY_4,
        3: API_KEY_5,
        4: API_KEY_6,
        5: API_KEY_1
    }
    summarizetion_api = api_keys.get(api_key, API_KEY_2)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {summarizetion_api}",
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": report
                }
            ]
        }
    ]
    payload = {
        "model": model_id,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

