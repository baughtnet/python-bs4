# import libraries
import math
import time
import loguru
import requests
from prettytable import PrettyTable

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
    Column('search_id', String),
    Column('title', String),
    Column('price', Float),
    Column('seller_name', String),
    Column('feedback', String),
    Column('seller_rating', String),
    Column('ship_price', Float),
    Column('combined_subtotal', Float),
    Column('tax', Float),
    Column('combined_total', Float),
)

metadata.create_all(engine, checkfirst=True)

# Connect to the database
conn = sqlite3.connect('ebay.db')

# Create the table(if it doesn't exist)
conn.execute('''
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id TEXT,
    title TEXT,
    price REAL,
    seller_name TEXT,
    feedback TEXT,
    seller_rating TEXT,
    ship_price REAL,
    combined_subtotal REAL,
    tax REAL,
    combined_total REAL
    )
''')

def start_program():
    # Ask the user whether they have a url or want to search for a product
    choice = input("Do you have a url or want to search for a product? ([u]rl/[s]earch/[v]iew database/[q]uit): ")

    if choice == "url" or choice == "u":
        url = input("Enter the url: ")
        soup, number_of_results, number_of_pages, search_id = base_info(url)
        scraper(url, 1, number_of_pages, soup, search_id)

    elif choice == "search" or choice == "s":
        search_term = input("Enter the search term: ")
        search_term = search_term.replace(" ", "+")
        url = f'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw={search_term}&_sacat=0'
        soup, number_of_results, number_of_pages, search_id = base_info(url)
        scraper(url, 1, number_of_pages, soup, search_id)

    elif choice == "view database" or choice == "v":
        view_database()

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

    # Create a variable for the search_id
    url_start_index = url.find('nkw=') + 4
    url_end_index = url.find('&', url_start_index)

    search_id = url[url_start_index:url_end_index]
    search_id = search_id.replace('+', ' ')

    print(search_id)

    return soup, number_of_results, number_of_pages, search_id


def append_listings(listing_data):
    Session = sessionmaker(bind=engine)
    session = Session()

    session.execute(listings_table.insert(), listing_data)

    session.commit()


def view_database():
    Session = sessionmaker(bind=engine)
    session = Session()

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM listings')
    data = cursor.fetchall()

    # Get the column names
    columns = [desc[0] for desc in cursor.description]

    # Create a PrettyTable
    table = PrettyTable(columns)

    # Add data to the table
    for row in data:
        table.add_row(row)

    html_table = table.get_html_string()

    with open('table.html', 'w') as html_file:
        html_file.write(html_table)

    # Print the table
    print(table)

    conn.close()

def scrape(soup, search_id):
    listing_data = []

    # Find the <div> with class "s-item__info"
    items = soup.find_all('li', class_='s-item')

    for item in items:
        try:
            title = item.find('div', class_='s-item__title').getText()
        except AttributeError:
            continue

        try:
            price = item.find('span', class_='s-item__price').getText()
            price = price.split('$')[1].split('$')
            price = float(price[0])
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

            if shipping == 'Free':
                shipping = 0

            shipping = float(shipping)

        except AttributeError:
            continue

        subtotal = price + shipping
        tax = subtotal * 0.12
        total = subtotal + tax

        listing = {
            'search_id': search_id,
            'title': title,
            'price': price,
            'seller_name': seller_name,
            'feedback': feedback,
            'seller_rating': seller_rating,
            'ship_price': shipping,
            'combined_subtotal': subtotal,
            'tax': tax,
            'combined_total': total
        }

        listing_data.append(listing)

    # Insert listings into the database
    append_listings(listing_data)
        

        # Print the extracted information
        # print(f'Item Title: {title}')
        # print(f'Item Price: ${price}')
        # # print(seller_info)
        # print(f'Seller Name: {seller_name}')
        # print(f'Number of Feedback left: {feedback}')
        # print(f'Seller Rating: {seller_rating}')
        # print(f'Shipping Cost: ${shipping}')
        # print('\n')


def scraper(url, current_page, max_page, current_soup, search_id):

    if current_page <= max_page and max_page > 1:
        scrape(current_soup)
        while current_page <= max_page:
            url = f'{url}&_pgn={current_page}'
            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, features='html.parser')
            scrape(soup, search_id)

            current_page += 1

    else:
        scrape(current_soup, search_id)

start_program()

# Close Selenium WebDriver
driver.quit()
