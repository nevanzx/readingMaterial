import json
import os

# Load API keys from key.json file
try:
    with open('key.json', 'r') as f:
        data = json.load(f)
    
    apis = {api['name']: api['keys'][0] for api in data['apis']}
    print("API keys loaded successfully:")
    for name, key in apis.items():
        print(f"  {name}: {key[:10]}..." if len(key) > 10 else f"  {name}: {key}")
        
    # Check for the specific API key mentioned in your app
    nano_banana_key = apis.get('nano_banana_gemini')
    if nano_banana_key:
        print(f"\nFound nano_banana_gemini key: {nano_banana_key[:10]}...")
    else:
        print("\nnano_banana_gemini key not found!")
        
except FileNotFoundError:
    print("key.json file not found!")
except Exception as e:
    print(f"Error loading API keys: {e}")