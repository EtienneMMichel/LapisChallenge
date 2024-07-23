import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def get_optimizer_backtest(payload):
    url = f"{BASE_URL}/get_optimizer_backtest"
    # payload = json.dumps({payload})
    headers = {
    'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)
