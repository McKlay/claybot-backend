import requests

data = {
    "content": "This is a test document about Clay Sarte's project called ClayBot.",
    "metadata": {"source": "unit test"}
}

res = requests.post("http://127.0.0.1:8000/embed", json=data)
print("Status:", res.status_code)
print("Response:", res.json())
