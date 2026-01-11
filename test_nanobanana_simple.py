#!/usr/bin/env python3
"""
Test file to generate images using the official Nano Banana Pro API (gemini-3-pro-image-preview)
based on the official Google Gemini API documentation.
Results will be written to a log file.
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


def generate_image_with_nanobanana_pro(prompt, api_key, aspect_ratio="16:9", image_size="2K"):
    """
    Generate an image using the official Nano Banana Pro API (gemini-3-pro-image-preview).
    
    Args:
        prompt (str): The text prompt for image generation
        api_key (str): The Gemini API key
        aspect_ratio (str): Aspect ratio for the generated image (default: "16:9")
        image_size (str): Size of the generated image (default: "2K")
    
    Returns:
        str: Path to the saved image file, or None if failed
    """
    try:
        # Validate API key
        if not api_key or api_key == "YOUR_NANO_BANANA_PRO_API_KEY_HERE":
            return "No valid API key provided for image generation"
        
        # Prepare the API request
        model = "gemini-3-pro-image-preview"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        # Prepare the payload according to official documentation
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt}
                ]
            }],
            "response_modalities": ["IMAGE"],  # Request image response
            "image_config": {
                "aspect_ratio": aspect_ratio,
                "image_size": image_size
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the generated image from the response
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                for candidate in response_data['candidates']:
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            if 'inline_data' in part:
                                # This is a base64-encoded image
                                image_mime_type = part['inline_data'].get('mime_type', 'image/png')
                                image_data = base64.b64decode(part['inline_data']['data'])
                                
                                # Determine file extension from MIME type
                                ext = '.png' if 'png' in image_mime_type.lower() else '.jpg'
                                
                                # Create a temporary file to save the image
                                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                                    tmp_file.write(image_data)
                                    return f"Successfully generated and saved image to: {tmp_file.name}"
            
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
    log_content = []
    log_content.append("Testing Nano Banana Pro Image Generation")
    log_content.append("=" * 50)
    
    # Load API keys
    api_keys = load_api_keys()
    
    if not api_keys:
        log_content.append("No API keys found. Please ensure key.json exists with valid API keys.")
        with open('test_results.log', 'w') as f:
            f.write('\n'.join(log_content))
        return
    
    # Get the Nano Banana Pro API key
    nano_banana_key = api_keys.get('nano_banana_gemini')
    if not nano_banana_key:
        log_content.append("Nano Banana Pro API key not found in key.json")
        with open('test_results.log', 'w') as f:
            f.write('\n'.join(log_content))
        return
    
    log_content.append(f"Found Nano Banana Pro API key: {nano_banana_key[:10]}...")
    log_content.append("")
    
    # Define a simple test prompt
    prompt = "A colorful sunset over mountains with a lake in the foreground, photorealistic style"
    log_content.append(f"Testing with prompt: {prompt}")
    
    result = generate_image_with_nanobanana_pro(prompt, nano_banana_key)
    log_content.append(f"Result: {result}")
    
    log_content.append("")
    log_content.append("=" * 50)
    log_content.append("Nano Banana Pro image generation test completed.")
    
    # Write results to log file
    with open('test_results.log', 'w') as f:
        f.write('\n'.join(log_content))
    
    print("Test completed. Results written to test_results.log")


if __name__ == "__main__":
    main()