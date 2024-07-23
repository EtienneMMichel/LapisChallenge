import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time

URL = "https://sofifa.com/api/team/history?id={id}"

SAVING_PATH = "DATA/raw_fifa_index.json"

PAYLOAD = {}
HEADERS = {}

def is_not_empty(response):
    return isinstance(response[0][1], str)

def fetch_data():
        driver = webdriver.Chrome()
        driver.get("https://sofifa.com/")
        res = {}
        for id in tqdm(range(0,1500)):
            url = URL.format(id=id)
            driver.get(url)
            time.sleep(0.5)
            pre = driver.find_element(By.TAG_NAME, "pre")
            response = pre.text
            try:
                response = json.loads(response)
                response = response["data"]
            except json.decoder.JSONDecodeError:
                print("Stop at id: ", id)
                return res
            if is_not_empty(response):
                response_formatted = {}
                for r in response:
                    response_formatted[r[5]] = {
                        "date":r[0],
                        "Overall":r[1],
                        "Attack":r[2],
                        "Midfield":r[3],
                        "Defence":r[4],
                        "fifa":r[6],
                    }
                res[id] = response_formatted
        return res

if __name__ == "__main__":
    data = fetch_data()
    with open(SAVING_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)