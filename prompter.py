import requests

url = 'http://localhost:5000/api/v1/generate'

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

data = {
    'prompt': 'Can you describe the structure of an atom?',
    'temperature': 0.5,
    'top_p': 0.9,
    "max_length": 200
}

response = requests.post(url, headers=headers, json=data)
response.raise_for_status()
print(response.json()["results"][0]["text"].strip())