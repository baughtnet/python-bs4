# import libraries
import math
import time
import loguru
import requests

import sqlite3
from sqlalchemy import create_engine, Column, String, Float, Integer, MetaData, Table
from sqlalchemy.orm import sessionmaker

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Setup SQLite database for SQLAlchemy
engine = create_engine('sqlite:///ebay.db')
metadata = MetaData()

listings_table = Table(
    'listings', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('price', Float),
    Column('seller_name', String),
    Column('feedback', Integer),
    Column('seller_rating', Float),
    Column('ship_price', Float),
    Column('combined_subtotal', Float),
    Column('combined_total', Float),
)

metadata.create_all(engine)

# Connect to the database
conn = sqlite3.connect('ebay.db')

# Create the table(if it doesn't exist)
conn.execute('''
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price REAL,
    seller_name TEXT,
    feedback INTEGER,
    seller_rating TEXT,
    ship_price REAL,
    combined_subtotal REAL,
    combined_total REAL
    )
''')

def start_program():
    # Ask the user whether they have a url or want to search for a product
    choice = input("Do you have a url or want to search for a product? ([u]rl/[s]earch/[q]uit): ")

    if choice == "url" or choice == "u":
        url = input("Enter the url: ")
        soup, number_of_results, number_of_pages = base_info(url)
        scraper(url, 1, number_of_pages, soup)

    elif choice == "search" or choice == "s":
        search_term = input("Enter the search term: ")
        search_term = search_term.replace(" ", "+")
        url = f'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw={search_term}&_sacat=0'
        soup, number_of_results, number_of_pages = base_info(url)
        scraper(url, 1, number_of_pages, soup)

    elif choice == "quit" or choice == "q":
        print("Goodbye!")
        exit()


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

    if current_page <= max_page and max_page > 1:
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

    start_program()
# Insert a listing
# listing_data = {
#         'title': 'Sample Product',
#         'price': 9.99,
#         'seller_info': 'rebate_retailer',
#         'ship_price': 10.00,
# }
#
# conn.execute('INSERT INTO listings (title, price, seller_info, ship_price) VALUES (?, ?, ?, ?)',
#              tuple(listing_data.values()))
#
# cursor = conn.execute('SELECT * FROM listings')
# results = cursor.fetchall()
# print(results)

# ~~~OLD CODE THAT NEEDS TO BE REPLACED WITH FUNCTION CALLS!~~~

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#
# url = 'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=canon+powershot+a2400&_sacat=0'
#
# driver.get(url)
# time.sleep(5)
#
# soup = BeautifulSoup(driver.page_source, features='html.parser')
#
# # Find the <div> with class "s-item__info"
# item_detail_divs = soup.find_all('div', class_='s-item__info')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Session = sessionmaker(bind=engine)
# session = Session()
#
# for item_details in item_detail_divs:
#     # ~~~ REPLACE SOME WITH FUNCTION CALLS! ~~~
#     # Extract info from each item
#     title = soup.find_all('div', class_='s-item__title')
#     price_str = item_details.find('span', class_='s-item__price').text.strip()
#     price = float(price_str('C $', '').replace(',', ''))
#     seller_info = item_details.find('span', class_='s-item__seller-info-text').text.strip()
#     shipping = item_details.find('span', class_='s-item__shipping s-item__logisticsCost').text.strip()
#     ship_price = float(shipping('+C $', '').replace(',', ''))
#
#     # Insert the listing into the database
#     session.execute(listings_table.insert().values(
#         title=title,
#         price=price,
#         seller_info=seller_info,
#         ship_price=ship_price,
#         ))
#
# # Commit the changes
# session.commit()


start_program()





# Close Selenium WebDriver
driver.quit()
