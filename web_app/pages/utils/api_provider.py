import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def get_optimizer_backtest(sport:str, dates:list[int], forecaster_name:str, optimizers_name:list[str], zone:str, competitions:list[str]):
    url = f"{BASE_URL}/get_optimizer_backtest"

    optimizers_name = ([optimizers_name] if type(optimizers_name) is str else optimizers_name)
    competitions = ([competitions] if type(competitions) is str else competitions)
    payload = json.dumps({
            "sport":sport,
            "start_year":dates[0],
            "end_year":dates[1],
            # "zone":zone,
            # "competitions":competitions,
            "forecaster_name":forecaster_name,
            "optimizers_name":optimizers_name
        })
    headers = {
    'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return json.loads(response.text)
    raise f"get_optimizer_backtest: response status: {response.status_code}"
