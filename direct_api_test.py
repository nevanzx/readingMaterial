import json
import requests
import base64
import tempfile
import os

# Load API keys
try:
    with open('key.json', 'r') as f:
        data = json.load(f)
    apis = {api['name']: api['keys'][0] for api in data['apis']}
    nano_banana_key = apis.get('nano_banana_gemini')
except:
    nano_banana_key = None

# Write result directly to file
with open('api_test_result.txt', 'w') as f:
    if nano_banana_key:
        f.write(f"Found Nano Banana Pro API key: {nano_banana_key[:10]}...\n")
        
        # Test the API with a simple request
        try:
            model = "gemini-3-pro-image-preview"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={nano_banana_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "A simple red apple on a table"}
                    ]
                }]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            f.write(f"API Response Status: {response.status_code}\n")
            
            if response.status_code == 200:
                f.write("API call successful!\n")
                response_data = response.json()
                f.write(f"Response keys: {list(response_data.keys())}\n")
                
                # Check for candidates in response
                if 'candidates' in response_data:
                    f.write(f"Found {len(response_data['candidates'])} candidates\n")
                    for i, candidate in enumerate(response_data['candidates']):
                        if 'content' in candidate and 'parts' in candidate['content']:
                            f.write(f"Candidate {i} has {len(candidate['content']['parts'])} parts\n")
                            for j, part in enumerate(candidate['content']['parts']):
                                f.write(f"Part {j} keys: {list(part.keys())}\n")
                                if 'inlineData' in part or 'inline_data' in part:
                                    f.write("Found image data in response!\n")
                                    # Try to save the image
                                    image_data_key = 'inlineData' if 'inlineData' in part else 'inline_data'
                                    image_data = base64.b64decode(part[image_data_key]['data'])
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                                        tmp_file.write(image_data)
                                        f.write(f"Saved image to: {tmp_file.name}\n")
                                        break
                                elif 'text' in part:
                                    f.write(f"Text response: {part['text'][:100]}...\n")
                        break  # Only check first candidate
            else:
                f.write(f"API Error: {response.text}\n")
        except Exception as e:
            f.write(f"Error during API call: {str(e)}\n")
    else:
        f.write("Nano Banana Pro API key not found\n")
    
    f.write("Test completed\n")