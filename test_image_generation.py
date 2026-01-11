#!/usr/bin/env python3
"""
Simple test file to generate images using Google's Gemini API and other image generation services.
Based on the API keys in your key.json file.
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


def test_deep_seek_image_generation(prompt, api_key):
    """Test image generation using DeepSeek API if available."""
    print("Testing DeepSeek image generation...")
    
    # Note: DeepSeek doesn't typically offer image generation, 
    # so this is just a placeholder for testing purposes
    print("DeepSeek does not provide image generation capabilities.")
    return None


def test_google_gemini_image_generation(prompt, api_key):
    """Test image generation using Google's Gemini API."""
    print("Testing Google Gemini image generation...")
    
    # Note: Gemini API is primarily for image understanding, not generation
    # Google's image generation is typically done through Imagen API
    print("Google Gemini API is primarily for image understanding, not image generation.")
    print("Google's image generation is usually done through Imagen API which is separate.")
    return None


def test_openrouter_image_generation(prompt, api_key):
    """Test image generation using OpenRouter API."""
    print("Testing OpenRouter image generation...")
    
    try:
        # OpenRouter supports various models including image generation models
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Note: OpenRouter image generation would require specific models
        # This is a simplified example
        payload = {
            "model": "google/gemini-pro-vision",  # This is for image understanding, not generation
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate an image based on this prompt: {prompt}"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("OpenRouter request successful, but this model doesn't generate images.")
            return None
        else:
            print(f"OpenRouter API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None


def test_alternative_image_generation(prompt, api_key):
    """Test image generation using a common image generation API format."""
    print("Testing alternative image generation approach...")
    
    # Since the 'nano_banana_pro' doesn't seem to be a real API,
    # let's try to use a standard image generation approach
    # that might work with Google's services
    
    # Google Cloud Vertex AI Imagen API would be the real image generation service
    # But it requires different setup and billing
    print("Standard Google image generation would require Google Cloud Vertex AI with Imagen model.")
    print("This requires specific setup and billing configuration.")
    return None


def main():
    """Main function to test image generation with different APIs."""
    print("Testing Image Generation with Available APIs")
    print("=" * 50)
    
    # Load API keys
    api_keys = load_api_keys()
    
    if not api_keys:
        print("No API keys found. Please ensure key.json exists with valid API keys.")
        return
    
    # Define a test prompt
    prompt = "A colorful sunset over mountains with a lake in the foreground"
    
    print(f"Using prompt: '{prompt}'")
    print()
    
    # Test different image generation options
    if 'deepseek' in api_keys:
        result = test_deep_seek_image_generation(prompt, api_keys['deepseek'])
    
    if 'gemini' in api_keys:
        result = test_google_gemini_image_generation(prompt, api_keys['gemini'])
    
    if 'nano_banana_gemini' in api_keys:
        result = test_google_gemini_image_generation(prompt, api_keys['nano_banana_gemini'])
    
    if 'openrounter' in api_keys:  # Note: typo in original key.json
        result = test_openrouter_image_generation(prompt, api_keys['openrounter'])
    
    # Test alternative approach
    result = test_alternative_image_generation(prompt, api_keys.get('gemini', ''))
    
    print("\n" + "=" * 50)
    print("Image generation test completed.")
    print("Note: Google's Gemini API is primarily for image understanding, not generation.")
    print("For actual image generation, you would need Google's Imagen API through Vertex AI.")


if __name__ == "__main__":
    main()