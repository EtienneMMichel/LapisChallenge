from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
r = driver.get("https://sofifa.com/")
r = driver.get("https://sofifa.com/api/team/history?id=1")
pre = driver.find_element(By.TAG_NAME, "pre")
print(pre.text)