import time
import loguru

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.baughserve.com/'

driver.get(url)

soup = BeautifulSoup(driver.page_source, features='lxml')

headings = soup.find_all(name='h2')
for heading in headings:
    print(heading.getText())

    time.sleep(1)

    driver.quit()
