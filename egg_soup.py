# same app as soup1.py, used for confirming knowledge/testing purposes

from bs4 import BeautifulSoup
import requests

URL = "https://www.newegg.ca/p/pl?d=sata+ssd"

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'Accept-Encoding':'gzip, deflate', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT':'1','Connection':'close', 'Upgrade-Insecure-Requests':'1'}

print("Retrieving webpage")
webpage = requests.get(URL, headers=headers)
soup = BeautifulSoup(webpage.text, 'html.parser')
results = soup.find_all("div", class_="item-cell")

for result in results:
    item = result.find("a", class_="item-title")
    price = result.find("li", class_="price-current")
    if price:
        print(price.text.strip())
    else:
        print("No price found for item", item.text.strip())
    try:
        print(item.text.strip())
    except AttributeError:
        print("No price found for item", item.text.strip())
