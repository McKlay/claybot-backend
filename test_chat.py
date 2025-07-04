import requests

data = {"message": "Tell me about ClayBot"}
res = requests.post("http://127.0.0.1:8000/chat", json=data)
print("Status:", res.status_code)
print("Response:", res.json())