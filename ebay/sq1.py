import time
import loguru

import sqlite3
from sqlalchemy import create_engine, Column, String, Float, Integer, MetaData, Table
from sqlalchemy.orm import sessionmaker

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup SQLite database for SQLAlchemy
engine = create_engine('sqlite:///ebay.db')
metadata = MetaData()

listings_table = Table(
    'listings', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('price', Float),
    Column('seller_info', String),
    Column('ship_price', Float),
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
    seller_info TEXT,
    ship_price REAL
    )
''')

# Insert a listing
listing_data = {
        'title': 'Sample Product',
        'price': 9.99,
        'seller_info': 'rebate_retailer',
        'ship_price': 10.00,
}

conn.execute('INSERT INTO listings (title, price, seller_info, ship_price) VALUES (?, ?, ?, ?)',
             tuple(listing_data.values()))

cursor = conn.execute('SELECT * FROM listings')
results = cursor.fetchall()
print(results)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.ebay.ca/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw=canon+powershot+a2400&_sacat=0'

driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, features='html.parser')

# Find the <div> with class "s-item__info"
item_detail_divs = soup.find_all('div', class_='s-item__info')

Session = sessionmaker(bind=engine)
session = Session()

for item_details in item_detail_divs:
    # Extract info from each item
    title = soup.find_all('div', class_='s-item__title')
    price_str = item_details.find('span', class_='s-item__price').text.strip()
    price = float(price_str('C $', '').replace(',', ''))
    seller_info = item_details.find('span', class_='s-item__seller-info-text').text.strip()
    shipping = item_details.find('span', class_='s-item__shipping s-item__logisticsCost').text.strip()
    ship_price = float(shipping('+C $', '').replace(',', ''))

    # Insert the listing into the database
    session.execute(listings_table.insert().values(
        title=title,
        price=price,
        seller_info=seller_info,
        ship_price=ship_price,
        ))

# Commit the changes
session.commit()

# Close Selenium WebDriver
driver.quit()
