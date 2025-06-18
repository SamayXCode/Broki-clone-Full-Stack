import requests
import json

# Load your property data
with open('sample_properties.json', 'r') as file:
    data = json.load(file)

# Replace with your actual API endpoint
url = "http://127.0.0.1:8000/api/upload-properties/"

# Send POST request
response = requests.post(url, json=data)

# Print response
print(response.status_code)
print(response.json())
