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
MAIN_REPO = "odds"

ODDS_URL = "https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{token}/X360488X0X0X0X0X0X0X0X0X0X0X0X0X134217729X0X1048578X0X0X1024X18464X131072X256/1/0/page/{page}//"
ODDS_URL_ONE_PAGE = "https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/{token}/X360488X0X0X0X0X0X0X0X0X0X0X0X0X134217729X0X1048578X0X0X1024X18464X131072X256/1/0/"

SAVING_PATH = "DATA/odds.json"

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
            
def gather_informations_in_response(raw_odds_data):
    data = raw_odds_data["d"]["rows"]
    res = []
    for row in data:
        try:
            res.append({
                "timestamp":row["date-start-timestamp"],
                "result":row["result"],
                "away-name":row["away-name"],
                "home-name":row["home-name"],
                "winner":("home" if row["home-winner"]=="win" else "away"),
                "odds":{
                    "home":{
                        "avgOdds":row["odds"][0]["avgOdds"],
                        "maxOdds":row["odds"][0]["maxOdds"],
                    },
                    "draw":{
                        "avgOdds":row["odds"][1]["avgOdds"],
                        "maxOdds":row["odds"][1]["maxOdds"],
                    },
                    "away":{
                        "avgOdds":row["odds"][2]["avgOdds"],
                        "maxOdds":row["odds"][2]["maxOdds"],
                    }
                }
            })
        except IndexError:
            print(row["odds"])
    return res


if __name__ == "__main__":

    create_dir(f"DATA/{MAIN_REPO}")
    driver = webdriver.Chrome()
    driver.get("https://www.oddsportal.com/football/results/")
    time.sleep(1)

    # 1. Get competitions url
    print("Scrap competitions url...")
    element = driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[3]')
    competitions_list = []
    # for i_child, child in tqdm(enumerate(list(element.find_elements(By.XPATH, './/*'))[1:])):
    list_competetion_element = element.find_elements(By.XPATH, './/a')
    competition_urls = [ c.get_attribute("href") for c in list_competetion_element]
    for competition_url in tqdm(competition_urls):
        if "results" in competition_url:
            zone = competition_url.split("/")[-4]
            create_dir(f"DATA/{MAIN_REPO}/{zone}")
            competition_name = competition_url.split("/")[-3]
            urls = {
                "zone":zone,
                "competition_name":competition_name,
                "url":competition_url,
            }
            competitions_list.append(urls)

    # 2. Gather all results of competitions
    res = {}
    for competition_data in tqdm(competitions_list):
        driver.get(competition_data["url"])
        time.sleep(0.1)
        years_urls = [child.get_attribute("href") for child in driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[3]/div/div[2]').find_elements(By.XPATH, './/a')]
        data_odds_year = []
        for year_url in years_urls:
            driver.get(year_url)
            time.sleep(0.1)
            token = driver.find_element(By.XPATH, '/html/head/script[4]').get_attribute('innerHTML').split('{"id":"')
            if len(token) > 1:
                data_odds = []
                token = token[1].split('"')[0]
                xpath_pages = '//*[@id="app"]/div[1]/div[1]/div/main/div[3]/div[4]/div[1]/div[5]/div' # page xpath
                if check_exists_by_xpath(driver, xpath_pages):
                    nb_pages = len(list(driver.find_element(By.XPATH, xpath_pages).find_elements(By.XPATH, './/a'))) - 1 # -1 due to next button
                    for i_page in range(1, nb_pages + 1):
                        url = ODDS_URL.format(token=token, page = i_page)
                        driver.get(url)
                        time.sleep(0.1)
                        pre = driver.find_element(By.TAG_NAME, "pre")
                        raw_odds_data = pre.text
                        try:
                            raw_odds_data = json.loads(raw_odds_data)
                            odds_data = gather_informations_in_response(raw_odds_data)
                            data_odds.extend(odds_data)
                        except json.decoder.JSONDecodeError:
                            pass
                        
                else:
                    url = ODDS_URL_ONE_PAGE.format(token=token)
                    driver.get(url)
                    time.sleep(0.1)
                    pre = driver.find_element(By.TAG_NAME, "pre")
                    raw_odds_data = pre.text
                    raw_odds_data = json.loads(raw_odds_data)
                    odds_data = gather_informations_in_response(raw_odds_data)
                    data_odds.extend(odds_data)
                data_odds_year.extend(data_odds)
        res[f"{competition_data['zone']}-{competition_data['competition_name']}"] = data_odds_year

    with open(SAVING_PATH, 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)
