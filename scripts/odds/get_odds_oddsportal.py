from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import time
import os
from tqdm import tqdm
import json
import datetime


DATA_PATH = "DATA/ODDSPORTAL"
SAVED_COMPETITIONS_PATH = os.path.join(DATA_PATH, "saved_competitions.json")
COMPETITIONS_URL_PATH = os.path.join(DATA_PATH, "competitions_url.json")

COMPETITION_PAGE_URL = "https://www.oddsportal.com/{sport}/results/"
SPORTS = ["football", "basketball", "tennis"]

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_competitions_url(driver, competition_url):
    driver.get(competition_url)
    time.sleep(1)
    res = {}
    # 1. Get competitions url
    element = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[3]')
    competitions_list = []
    list_competition_element = element.find_elements(By.XPATH, './/a')
    competition_urls = [ c.get_attribute("href") for c in list_competition_element]
    for competition_url in tqdm(competition_urls):
        if "results" in competition_url:
            zone = competition_url.split("/")[-4]
            competition_name = competition_url.split("/")[-3]

            if zone in list(res.keys()):
                res[zone][competition_name] = competition_url
            else:
                res[zone] = {competition_name:competition_url}

    return res


def scrap_competitions_url():
    
    if not os.path.exists(COMPETITIONS_URL_PATH):
        competitions_url = {}
        with webdriver.Chrome() as driver:
            for sport in SPORTS:
                competition_url = COMPETITION_PAGE_URL.format(sport=sport)
                competitions_url[sport] = get_competitions_url(driver, competition_url)
        
        with open(COMPETITIONS_URL_PATH, 'w', encoding='utf-8') as f:
                json.dump(competitions_url, f, ensure_ascii=False, indent=4)
    else:
        with open(COMPETITIONS_URL_PATH, encoding='utf-8') as fh:
            competitions_url = json.load(fh)

    return competitions_url

def get_timestamp(raw_date):
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
    raw_date_list = raw_date.split(" ")
    try:
        year = int(raw_date_list[2])
        day = int(raw_date_list[0])
        month = month_mapping[raw_date_list[1]]
    except ValueError:
        year = datetime.datetime.now().year
        month = month_mapping[raw_date_list[2]]
        day = int(raw_date_list[1])
    
        

    return int(datetime.datetime.timestamp(datetime.datetime(year, month, day, 0, 0)))

def scrap_data(data_content):
    res = []
    current_date = None
    for div_element in data_content.find_elements(By.XPATH, "*"):
        div_content = div_element.find_elements(By.XPATH, "*")
        try:
            if len(div_content) == 3:
                current_date = div_content[1].find_element(By.XPATH, "./div[1]/div").text
                current_date = get_timestamp(current_date.split(' - ')[0])
                match_info = div_content[2].find_elements(By.XPATH, "./div/a/div[1]/div[2]/div/div/*")

                team_1_name = match_info[0].find_element(By.XPATH,'./div[1]/p').text
                team_2_name = match_info[2].find_element(By.XPATH,'./div[1]/p').text
                odd_team_1 = float(div_content[2].find_element(By.XPATH, "./div/div[1]/div/div/p").text)
                odd_team_null = float(div_content[2].find_element(By.XPATH, "./div/div[2]/div/div/p").text)
                odd_team_2 = float(div_content[2].find_element(By.XPATH, "./div/div[3]/div/div/p").text)
                result_team_1 = int(match_info[1].find_element(By.XPATH,'./div/div[1]').text)
                result_team_2 = int(match_info[1].find_element(By.XPATH,'./div/div[2]').text)
                
                

                

            elif len(div_content) == 1:
                match_info = div_content[0].find_elements(By.XPATH, "./div/a/div[1]/div[2]/div/div/*")
                team_1_name = match_info[0].find_element(By.XPATH,'./div[1]/p').text
                team_2_name = match_info[2].find_element(By.XPATH,'./div[1]/p').text
                odd_team_1 = float(div_content[0].find_element(By.XPATH, "./div/div[1]/div/div/p").text)
                odd_team_null = float(div_content[0].find_element(By.XPATH, "./div/div[2]/div/div/p").text)
                odd_team_2 = float(div_content[0].find_element(By.XPATH, "./div/div[3]/div/div/p").text)

                result_team_1 = int(match_info[1].find_element(By.XPATH,'./div/div[1]').text)
                result_team_2 = int(match_info[1].find_element(By.XPATH,'./div/div[2]').text)

            
            elif len(div_content) == 2:
                current_date = div_content[0].find_element(By.XPATH, "./div[1]/div").text
                current_date = get_timestamp(current_date.split(' - ')[0])
                match_info = div_content[1].find_elements(By.XPATH, "./div/a/div[1]/div[2]/div/div/*")
                team_1_name = match_info[0].find_element(By.XPATH,'./div[1]/p').text
                team_2_name = match_info[2].find_element(By.XPATH,'./div[1]/p').text
                odd_team_1 = float(div_content[1].find_element(By.XPATH, "./div/div[1]/div/div/p").text)
                odd_team_null = float(div_content[1].find_element(By.XPATH, "./div/div[2]/div/div/p").text)
                odd_team_2 = float(div_content[1].find_element(By.XPATH, "./div/div[3]/div/div/p").text)

                result_team_1 = int(match_info[1].find_element(By.XPATH,'./div/div[1]').text)
                result_team_2 = int(match_info[1].find_element(By.XPATH,'./div/div[2]').text)

            if result_team_1 > result_team_2:
                    winner = "1"
            elif result_team_1 < result_team_2:
                winner = "2"
            else:
                winner = "null"
            data = {
                    "current_date":current_date,
                    "team_1_name":team_1_name,
                    "team_2_name":team_2_name,
                    "result":{
                        "team_1":result_team_1,
                        "team_2":result_team_2,
                    },
                    "winner": winner,
                    "odd_team_1" : odd_team_1,
                    "odd_team_null" : odd_team_null,
                    "odd_team_2" : odd_team_2
                }

            res.append(data)
        except NoSuchElementException:
            print("error")
    return res


def scrap_competition(competition_url, saving_path):
    res = []
    with webdriver.Chrome() as driver:
        driver.get(competition_url)
        time.sleep(0.1)
        years_urls = [child.get_attribute("href") for child in driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[3]/div/div[2]').find_elements(By.XPATH, './/a')]
        for year_url in years_urls:
            driver.get(year_url)
            time.sleep(0.5)
            content = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[4]/div[1]')
            childs_content = content.find_elements(By.XPATH, "*")
            if len(childs_content) == 2:
                # only one page
                odds_data = scrap_data(childs_content[0])
            elif len(childs_content) == 3:
                # more than one page
                pages = childs_content[-1].find_elements(By.XPATH, "./div/a")
                odds_data = scrap_data(childs_content[0])
                for page_nb in range(2,len(pages)):
                    year_url_page = year_url + f"#/page/{page_nb}/"
                    driver.get(year_url_page)
                    time.sleep(0.5)
                    content = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[4]/div[1]')
                    childs_content = content.find_elements(By.XPATH, "*")
                    odds_data.extend(scrap_data(childs_content[0]))
            else:
                odds_data = []
            res.extend(odds_data)
    with open(saving_path, 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)


def register_saved_competition(sport, zone, competition_name):
                
    with open(SAVED_COMPETITIONS_PATH, encoding='utf-8') as fh:
        saved_competitions = json.load(fh)

    saved_competitions[sport][zone][competition_name] = True

    with open(SAVED_COMPETITIONS_PATH, 'w', encoding='utf-8') as f:
        json.dump(saved_competitions, f, ensure_ascii=False, indent=4)
    return saved_competitions


def init_saved_competition():
    if not os.path.exists(SAVED_COMPETITIONS_PATH):
        with open(COMPETITIONS_URL_PATH, encoding='utf-8') as fh:
            competitions_url = json.load(fh)
        saved_comp = {}            
        for sport, competitions_url_sport in competitions_url.items():
            saved_comp[sport] = {}
            for zone, competitions_url_sport_zone in competitions_url_sport.items():
                saved_comp[sport][zone] = {}
                for competition_name, competition_url in competitions_url_sport_zone.items():
                    saved_comp[sport][zone][competition_name] = False

        with open(SAVED_COMPETITIONS_PATH, 'w', encoding='utf-8') as f:
            json.dump(saved_comp, f, ensure_ascii=False, indent=4)
    else:
        with open(SAVED_COMPETITIONS_PATH, encoding='utf-8') as fh:
            saved_comp = json.load(fh)
    return saved_comp
                
    


if __name__ == "__main__":
    # driver = webdriver.Chrome()
    create_dir(DATA_PATH)
    print("Scrap competitions url...")
    competitions_url = scrap_competitions_url()

    print("scrap odds data...")
    create_dir(DATA_PATH + "/data")
    saved_comp = init_saved_competition()
    for sport, competitions_url_sport in competitions_url.items():
        create_dir(DATA_PATH + f"/data/{sport}")
        for zone, competitions_url_sport_zone in competitions_url_sport.items():
            create_dir(DATA_PATH + f"/data/{sport}/{zone}")
            for competition_name, competition_url in competitions_url_sport_zone.items():
                if saved_comp[sport][zone][competition_name] == False:
                    saving_path = DATA_PATH + f"/data/{sport}/{zone}/{competition_name}.json"
                    scrap_competition(competition_url, saving_path)
                    saved_comp = register_saved_competition(sport, zone, competition_name)
                
                

    