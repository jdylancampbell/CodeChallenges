import requests
import re
from bs4 import BeautifulSoup

# Ask the user for the product they want to find prices for
product = input("What product would you like to search for?")
products = product.replace(" ", "+")
# Send a GET request to the URL and get the response
header = ({'User-Agent':
               'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
           'Accept-Language': 'en-US, en;q=0.5'})

items_found = {}


def amazon():
    global product
    global products
    global header
    global items_found

    url = f"https://www.amazon.com/s?k={products}&crid=XXPMXZ4FNAA1&sprefix={products}%2Caps%2C127&ref=nb_sb_noss_1"
    response = requests.get(url, headers=header).text
    doc = BeautifulSoup(response, "html.parser")

    pagetext = doc.find(class_="s-pagination-item s-pagination-disabled")
    max_pages = 3  # int(str(pagetext).split("/")[-2].split(">")[-1][:-1])

    for page_num in range(1, 2):
        url = f"https://www.amazon.com/s?k={products}&page={page_num}&crid=XXPMXZ4FNAA1&qid=1672680996&sprefix={products}%2Caps%2C111&ref=sr_pg_{page_num}"
        response = requests.get(url, headers=header).text
        doc = BeautifulSoup(response, "html.parser")

        div = doc.find(class_="s-main-slot s-result-list s-search-results sg-row")
        items = div.find_all(text=re.compile(product.title()))

        for item in items:
            parent = item.parent.parent
            if parent.name != "a":
                continue
            if "/gp/" in parent['href']:
                continue
            link = "https://amazon.com" + parent['href']
            next_parent = item.find_parent(class_="a-section a-spacing-small a-spacing-top-small")

            try:
                prices = next_parent.find(class_="a-price-whole").text
                price = prices.replace(".", "")
                items_found[item] = {"price": int(price.replace(",", "")), "link": link}
            except:
                pass


def newegg():
    global product
    global products
    global header
    global items_found

    url = f"https://www.newegg.com/p/pl?d={products}&N=4131"
    response = requests.get(url).text
    doc = BeautifulSoup(response, "html.parser")

    # Finds the last page number so we know where to stop looking
    pagetext = doc.find(class_="list-tool-pagination-text").strong
    max_pages = int(str(pagetext).split("/")[-2].split(">")[-1][:-1])

    items_found = {}

    for page_num in range(1, 2):
        url = f"https://www.newegg.com/p/pl?d={products}&N=4131&page={page_num}"
        response = requests.get(url).text
        doc = BeautifulSoup(response, "html.parser")

        div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = div.find_all(text=re.compile(product.title()))

        for item in items:
            parent = item.parent
            if parent.name != "a":
                continue

            link = parent['href']
            next_parent = item.find_parent(class_="item-container")
            try:
                price = next_parent.find(class_="price-current").find("strong").string
                items_found[item] = {"price": int(price.replace(",", "")), "link": link}
            except:
                pass

amazon()
sorted_itemsA = sorted(items_found.items(), key=lambda x: x[1]['price'])
newegg()
sorted_itemsN = sorted(items_found.items(), key=lambda x: x[1]['price'])
sorted_items = sorted(sorted_itemsN + sorted_itemsA, key=lambda x: x[1]['price'])
for item in sorted_items:
    print(item[0])
    print(f"${item[1]['price']}")
    print(item[1]['link'])
    print("---------------------------------------------------------")

