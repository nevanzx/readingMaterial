#!/usr/bin/env python3
"""
Test file to generate images using the official Nano Banana Pro API (gemini-3-pro-image-preview)
based on the official Google Gemini API documentation.
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
    Generate an image using the official Nano Banana Pro API (gemini-3-pro-image-preview).
    
    Args:
        prompt (str): The text prompt for image generation
        api_key (str): The Gemini API key
        aspect_ratio (str): Aspect ratio for the generated image (default: "16:9")
        image_size (str): Size of the generated image (default: "2K")
    
    Returns:
        str: Path to the saved image file, or None if failed
    """
    print(f"Generating image with Nano Banana Pro using prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
    
    try:
        # Validate API key
        if not api_key or api_key == "YOUR_NANO_BANANA_PRO_API_KEY_HERE":
            print("No valid API key provided for image generation")
            return None
        
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
            
            # Debug: Print the full response to see structure
            print(f"API Response Status: {response.status_code}")
            
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
                                    print(f"Successfully generated and saved image to: {tmp_file.name}")
                                    return tmp_file.name
                            elif 'text' in part:
                                print(f"Received text response: {part['text'][:100]}...")
            
            print("No image data found in the response")
            print(f"Full response: {json.dumps(response_data, indent=2)[:500]}...")
            return None
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("API request timed out (60 seconds)")
        return None
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the API - please check your connection")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


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
    
    # Define test prompts
    test_prompts = [
        "A colorful sunset over mountains with a lake in the foreground, photorealistic style",
        "A futuristic cityscape at night with flying vehicles, digital art style",
        "A close-up of a delicious meal on a restaurant table, professional food photography"
    ]
    
    # Test image generation with different aspect ratios and sizes
    aspect_ratios = ["16:9", "1:1", "4:3"]
    image_sizes = ["1K", "2K"]
    
    for i, prompt in enumerate(test_prompts):
        print(f"Test {i+1}: {prompt}")
        
        for aspect_ratio in aspect_ratios:
            for image_size in image_sizes:
                print(f"  Trying {aspect_ratio} aspect ratio, {image_size} size...")
                
                image_path = generate_image_with_nanobanana_pro(
                    prompt, 
                    nano_banana_key, 
                    aspect_ratio=aspect_ratio, 
                    image_size=image_size
                )
                
                if image_path:
                    print(f"  ✓ Successfully generated image: {image_path}")
                    # Optionally, break after first success to save API quota
                    # break
                else:
                    print(f"  ✗ Failed to generate image")
            
            # Uncomment the next line if you want to try only the first size for each aspect ratio
            # break
        
        print()
    
    print("=" * 50)
    print("Nano Banana Pro image generation test completed.")


if __name__ == "__main__":
    main()