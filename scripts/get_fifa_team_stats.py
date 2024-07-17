import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import time
import datetime
import os

FIFA_DATES_INDEX_PATH = "DATA/fifa_dates_indecis.json"
SAVING_PATH = "DATA/team_stats/{fifa_name}/{timestamp}.json"

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH,xpath)
    except NoSuchElementException:
        return False
    return True

def fetch_data(date_index):
    url = "https://sofifa.com/teams?type=club&r={date_index}&set=true&potential=hide&offset={offset}"
    driver = webdriver.Chrome()
    scrollable = True
    offset = 0
    res = {}
    while offset <= 660:
        formatted_url = url.format(date_index=date_index, offset=offset)
        offset += 60
        driver.get(formatted_url)
        time.sleep(1)
        # if check_exists_by_xpath(driver,'//*[@id="body"]/main/article/div/a[2]'):
        #     scrollable = False
        # else:
        #     offset += 60
        
        teams_elements = driver.find_element(By.XPATH, '//*[@id="body"]/main/article/table/tbody')
        for team_element in teams_elements.find_elements(By.XPATH, ".//tr"):
            team_name = team_element.find_element(By.XPATH, './td[2]/a[1]').get_attribute("href").split('/')[-2]
            overall = team_element.find_element(By.XPATH, './td[3]/em').get_attribute("title")
            attack = team_element.find_element(By.XPATH, './td[4]/em').get_attribute("title")
            midfield = team_element.find_element(By.XPATH, './td[5]/em').get_attribute("title")
            defence = team_element.find_element(By.XPATH, './td[6]/em').get_attribute("title")
            res[team_name] = {
                "overall":overall,
                "attack":attack,
                "midfield":midfield,
                "defence":defence,
            }
    return res
            
        

if __name__ == "__main__":
    with open(FIFA_DATES_INDEX_PATH, encoding='utf-8') as fh:
            fifa_indecis = json.load(fh)

    create_dir("DATA/team_global_stats")
    
    for fifa_name, date_indecis in tqdm(fifa_indecis.items()):
        create_dir(f"DATA/team_global_stats/{fifa_name}")
        for timestamp, date_index in tqdm(date_indecis.items()):
            data_stored = fetch_data(date_index)
            with open(f"DATA/team_global_stats/{fifa_name}/{timestamp}.json", 'w', encoding='utf-8') as f:
                json.dump(data_stored, f, ensure_ascii=False, indent=4)