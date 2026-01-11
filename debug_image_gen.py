#!/usr/bin/env python3
"""
Debug version of the image generation test to see what's happening.
"""

import json
import requests
import base64
import tempfile
import os
from pathlib import Path

def load_api_keys():
    """Load API keys from key.json file."""
    try:
        with open('key.json', 'r') as f:
            data = json.load(f)

        apis = {api['name']: api['keys'][0] for api in data['apis']}
        return apis
    except FileNotFoundError:
        print("key.json file not found!")
        return {}
    except Exception as e:
        print(f"Error loading API keys: {e}")
        return {}

def generate_image_with_nanobanana_pro(prompt, api_key, aspect_ratio="16:9", image_size="2K"):
    """
    Generate an image using the Gemini 3 Pro Image Preview model via raw HTTP requests.
    """
    try:
        # Validate API key
        if not api_key or api_key == "YOUR_NANO_BANANA_PRO_API_KEY_HERE":
            return False, "No valid API key provided for image generation"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={api_key}"

        headers = {
            "Content-Type": "application/json"
        }

        # Construct the payload
        # Note: explicit aspect_ratio/image_size params for this model
        # often go into generationConfig if supported, or part of the prompt for this specific model.
        # For 'Nano Banana', appending strict visual instructions to the prompt is often most effective
        # if the config param isn't strictly documented for the preview yet.
        full_prompt = f"{prompt} --aspect_ratio {aspect_ratio}"

        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "responseMimeType": "image/jpeg"
            }
        }

        print(f"Making request to: {url}")
        print(f"Payload: {json.dumps(data, indent=2)}")

        response = requests.post(url, headers=headers, json=data, timeout=120)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        response.raise_for_status() # Raise error for bad status codes

        result = response.json()
        print(f"Response JSON: {json.dumps(result, indent=2)}")

        # Parse the response for image data
        # Gemini returns images in 'inlineData' inside the candidate parts
        try:
            candidates = result.get('candidates', [])
            if not candidates:
                safety_msg = result.get('promptFeedback', {}).get('safetyRatings', 'Unknown')
                return False, f"No image generated (likely safety block). Safety ratings: {safety_msg}"

            for candidate in candidates:
                parts = candidate.get('content', {}).get('parts', [])
                for part in parts:
                    if 'inlineData' in part:
                        mime_type = part['inlineData']['mimeType']
                        data_b64 = part['inlineData']['data']

                        # Create a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            temp_file.write(base64.b64decode(data_b64))
                            return True, temp_file.name

            return False, "No inlineData (image) found in response."

        except Exception as e:
            return False, f"Parsing error: {str(e)} - Response: {result}"

    except requests.exceptions.HTTPError as e:
        return False, f"HTTP error: {str(e)}"
    except requests.exceptions.Timeout:
        return False, "API request timed out (120 seconds)"
    except requests.exceptions.ConnectionError:
        return False, "Failed to connect to the API"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def main():
    print("Debug test for image generation")
    print("=" * 50)

    # Load API keys
    api_keys = load_api_keys()

    if not api_keys:
        print("No API keys found.")
        return

    nano_banana_key = api_keys.get('nano_banana_gemini')
    if not nano_banana_key:
        print("Nano Banana Pro API key not found")
        return

    print(f"Found API key: {nano_banana_key[:10]}...")

    # Simple test prompt
    prompt = "A red apple on a table"
    print(f"Testing with prompt: {prompt}")
    
    success, result = generate_image_with_nanobanana_pro(prompt, nano_banana_key)
    
    if success:
        print(f"Success: {result}")
    else:
        print(f"Error: {result}")

if __name__ == "__main__":
    main()