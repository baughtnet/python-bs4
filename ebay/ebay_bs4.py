import math
import time
import loguru
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# url = 'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=canon+powershot+a2400&_sacat=0'
# url = 'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=canon&_sacat=0'
# url = 'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p2334524.m570.l1311&_nkw=canon+ae-1+program+black&_sacat=0&_odkw=canon+ae-1+program&_osacat=0'

def base_info(url):
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, features='html.parser')

    # Find total number of results to determine total number of pages
    results = soup.find_all('h1', class_='srp-controls__count-heading')
    results_split = results[0].getText().split(" ")
    try:
        number_of_results = results_split[0]
        number_of_results = int(number_of_results)

    except:
        number_of_results = number_of_results.replace('+', '').replace(',', '')
        number_of_results = int(number_of_results)

    number_of_pages = math.ceil(number_of_results / 60)

    print(f'Total number of results: {number_of_results}')
    print(f'Total number of pages: {number_of_pages}')

    return soup, number_of_results, number_of_pages

# MAYBE WRITE A MORE VERSATILE SCRAPE FUNCTION~~~~!!!

def scrape(soup):
    # Find the <div> with class "s-item__info"
    items = soup.find_all('li', class_='s-item')

    for item in items:
        try:
            title = item.find('div', class_='s-item__title').getText()
        except AttributeError:
            continue

        try:
            price = item.find('span', class_='s-item__price').getText()
        except AttributeError:
            continue
    
        try:
            seller_info = item.find('span', class_='s-item__seller-info-text').getText()
            # Extract the seller name feedback and rating from seller_info
            parts = seller_info.split(" ")
            seller_name = parts[0]
            feedback = parts[1].strip("()")
            seller_rating = parts[2]
        except AttributeError:
            continue

        try:
            shipping = item.find('span', class_='s-item__shipping s-item__logisticsCost').getText()
    
            # Extract just the price from shipping
            start_index = shipping.find('$') + 1
            end_index = shipping.find(' ', start_index)
            shipping = shipping[start_index:end_index]

        except AttributeError:
            continue

        # Print the extracted information
        print(f'Item Title: {title}')
        print(f'Item Price: ${price}')
        # print(seller_info)
        print(f'Seller Name: {seller_name}')
        print(f'Number of Feedback left: {feedback}')
        print(f'Seller Rating: {seller_rating}')
        print(f'Shipping Cost: ${shipping}')
        print('\n')

def scraper(url, current_page, max_page, current_soup):

    if max_page > 1:
        scrape(current_soup)
        while current_page <= max_page:
            url = f'{url}&_pgn={current_page}'
            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, features='html.parser')
            scrape(soup)

            current_page += 1

    else:
        scrape(current_soup)

url = input('Enter URL: ')
soup, number_of_results, number_of_pages = base_info(url)
print(number_of_pages)
scraper(url, 1, number_of_pages, soup)


driver.quit()
