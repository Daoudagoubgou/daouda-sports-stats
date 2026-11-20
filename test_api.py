import requests
from config import API_FOOTBALL_KEY, API_FOOTBALL_URL

headers = {
    "x-apisports-key": API_FOOTBALL_KEY
}

response = requests.get(
    f"{API_FOOTBALL_URL}/status",
    headers=headers,
    timeout=20
)

print("Code HTTP :", response.status_code)
print(response.json())