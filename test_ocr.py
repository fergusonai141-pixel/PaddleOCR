import base64
import requests
import json

image_path = r"C:\Users\const\.gemini\antigravity\brain\c488d266-f40a-45c8-8e42-b031884d2665\media__1778529786960.jpg"
server_url = "http://173.212.225.250:8000/ocr"

with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

payload = {
    "arguments": {
        "input_data": encoded_string,
        "output_mode": "simple"
    }
}

print(f"Sending image to {server_url}...")
try:
    response = requests.post(server_url, json=payload, timeout=60)
    response.raise_for_status()
    print("Response from server:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
