import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import time
import datetime

SAVING_PATH = "DATA/fifa_dates_indecis.json"

def get_date(raw_date):
    month_mapping = {
         "Jan":1,
         "Feb":2,
         "Mar":3,
         "Apr":4,
         "May":5,
         "Jun":6,
         "Jul":7,
         "Aug":8,
         "Sep":8,
         "Oct":10,
         "Nov":11,
         "Dec":12,
    }
    raw_date = raw_date.split(", ")
    try:
        year = int(raw_date[1])
        raw_month_day = raw_date[0].split(" ")
        month = month_mapping[raw_month_day[0]]
        day = int(raw_month_day[1])
    except IndexError:
        return None
    return int(datetime.datetime.timestamp(datetime.datetime(year, month, day, 0, 0)))

if __name__ == "__main__":
    # Get date ids
    driver = webdriver.Chrome()
    driver.get("https://sofifa.com/teams?type=club&r=240047&set=true&potential=hide")
    
    fifa_list_element = driver.find_element(By.XPATH, '//*[@id="body"]/header/section/p/select[1]')
    fifa_indices = {}
    date_indecis = dict(((child.text, child.get_attribute("value").split("=")[2].split("&")[0]) for child in fifa_list_element.find_elements(By.XPATH, ".//*")))
    for fifa_name, fifa_index in date_indecis.items():
        driver.get(f"https://sofifa.com/teams?type=club&r={fifa_index}&set=true&potential=hide")
        time.sleep(1)
        dates_element = driver.find_element(By.XPATH, '//*[@id="body"]/header/section/p/select[2]')
        date_indecis = dict(((get_date(child.text), child.get_attribute("value").split("=")[2].split("&")[0]) for child in dates_element.find_elements(By.XPATH, ".//*")))
        fifa_indices[fifa_name] = date_indecis

    with open(SAVING_PATH, 'w', encoding='utf-8') as f:
        json.dump(fifa_indices, f, ensure_ascii=False, indent=4)