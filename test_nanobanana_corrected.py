#!/usr/bin/env python3
"""
Corrected test file to generate images using the official Nano Banana Pro API (gemini-3-pro-image-preview)
based on actual API response.
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
        return {}
    except Exception as e:
        return {}


def generate_image_with_nanobanana_pro(prompt, api_key):
    """
    Generate an image using the official Nano Banana Pro API (gemini-3-pro-image-preview).
    
    Args:
        prompt (str): The text prompt for image generation
        api_key (str): The Gemini API key
    
    Returns:
        str: Path to the saved image file, or error message if failed
    """
    try:
        # Validate API key
        if not api_key or api_key == "YOUR_NANO_BANANA_PRO_API_KEY_HERE":
            return "No valid API key provided for image generation"
        
        # Prepare the API request
        model = "gemini-3-pro-image-preview"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Prepare the payload - removing invalid fields based on error
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt}
                ]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Debug: Print the full response to see structure
            print(f"Full response: {json.dumps(response_data, indent=2)}")
            
            # Extract the generated image from the response
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                for candidate in response_data['candidates']:
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            if 'inlineData' in part:  # Changed from 'inline_data' based on typical Gemini API
                                # This is a base64-encoded image
                                image_mime_type = part['inlineData'].get('mimeType', 'image/png')
                                image_data = base64.b64decode(part['inlineData']['data'])
                                
                                # Determine file extension from MIME type
                                ext = '.png' if 'png' in image_mime_type.lower() else '.jpg'
                                
                                # Create a temporary file to save the image
                                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                                    tmp_file.write(image_data)
                                    return f"Successfully generated and saved image to: {tmp_file.name}"
                            elif 'text' in part:
                                return f"Received text response: {part['text'][:200]}..."
            
            return "No image data found in the response"
        else:
            return f"API Error: {response.status_code}, Response: {response.text}"
            
    except requests.exceptions.Timeout:
        return "API request timed out (60 seconds)"
    except requests.exceptions.ConnectionError:
        return "Failed to connect to the API"
    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


def main():
    """Main function to test Nano Banana Pro image generation."""
    print("Testing Nano Banana Pro Image Generation")
    print("=" * 50)
    
    # Load API keys
    api_keys = load_api_keys()
    
    if not api_keys:
        print("No API keys found. Please ensure key.json exists with valid API keys.")
        return
    
    # Get the Nano Banana Pro API key
    nano_banana_key = api_keys.get('nano_banana_gemini')
    if not nano_banana_key:
        print("Nano Banana Pro API key not found in key.json")
        return
    
    print(f"Found Nano Banana Pro API key: {nano_banana_key[:10]}...")
    print()
    
    # Define a simple test prompt
    prompt = "A colorful sunset over mountains with a lake in the foreground, photorealistic style"
    print(f"Testing with prompt: {prompt}")
    
    result = generate_image_with_nanobanana_pro(prompt, nano_banana_key)
    print(f"Result: {result}")
    
    print("")
    print("=" * 50)
    print("Nano Banana Pro image generation test completed.")


if __name__ == "__main__":
    main()