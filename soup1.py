from typing import get_args
from bs4 import BeautifulSoup
import requests

URL = 'https://www.amazon.com/Sony-PlayStation-Pro-1TB-Console-4/dp/B07K14XKZH/'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'Accept-Encoding':'gzip, deflate', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT':'1','Connection':'close', 'Upgrade-Insecure-Requests':'1'}

webpage = requests.get(URL, headers=headers)

soup = BeautifulSoup(webpage.content, 'html.parser')


get_title = soup.find('span', attrs={'id':'productTitle'})
get_price = soup.find('span', class_='a-offscreen')

title = get_title.text.strip()
price = get_price.text.strip()

print(title)
print(price)

