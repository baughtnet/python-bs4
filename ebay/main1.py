import time
import loguru

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=canon+powershot+a2400&_sacat=0'

driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, features='html.parser')

# Find the <div> with class "s-item__info"
item_info_div = soup.find('div', class_='s-item__info')

# Find the <div> with class "s-item__title" with the "s-item__info" div
titles = soup.find_all('div', class_='s-item__title')

# Extract and print the text content of the title
for title in titles:
    print(title.getText())


driver.quit()
