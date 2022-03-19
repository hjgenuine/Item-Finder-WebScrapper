import requests
from bs4 import BeautifulSoup
from PIL import Image
import re
from collections import OrderedDict

# Just to make it simple to get url for an item
def getUrl(index, item):
    item = item.replace(" ", "+")
    if index == 0:
        return f"https://www.flipkart.com/search?q={item}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off"
    elif index == 1:
        return f"https://www.pcshop.in/?s={item}&product_cat=0&post_type=product"
    else:
        return f"https://www.newegg.com/global/in-en/p/pl?d={item}"

item = input("Looking for: ")
print()
data = []

# Get all the required urls
for i in range(3):
    data.append(getUrl(i, item))
# Get the html document corresponding to the Urls
for i, link in enumerate(data):
    data[i] = requests.get(link).text

# For BeautifulSoup documents
documents = []
for doc in data:
    documents.append(BeautifulSoup(doc, "html.parser"))

# Scrapping
info = []
websites = {"flipkart": documents[0], "pcShop": documents[1], "newegg": documents[2]}

# Flipkart
container = websites["flipkart"].find_all("div", class_="_1YokD2 _3Mn1Gg")[0]
if container:
    itemContainer = container.contents[1]
    divContainer = itemContainer.contents[0]
    innerContainer = divContainer.contents
    if len(innerContainer) == 4:
        item = innerContainer[0].find("div", class_="_4ddWXP")
        anchorTag = item.find("a",  class_="_2rpwqI")
        link = anchorTag["href"]
        imageTag = item.find("img", class_="_396cs4 _3exPp9")
        image = imageTag["src"]
        price = item.find("div", class_="_30jeq3").text
        name = imageTag["alt"]
    else:
        item = container.find("div", class_="_1AtVbE col-12-12")
        anchorTag = item.find("a", class_="_1fQZEK")
        link = anchorTag["href"]
        name = item.find("div", class_="_4rR01T").text
        price = item.find("div", class_="_30jeq3 _1_WHN1").text
        image = item.find("img", class_="_396cs4 _3exPp9")["src"]
    info.append(OrderedDict({"name": name, "price": price, "image": image, "link": "https://www.flipkart.com/" + link}))
else:
    info.append(False)

# PCshop.in
try:
    itemTag = websites["pcShop"].find("div", class_="product-outer product-item__outer")
    divTag = itemTag.find("div", class_="product-thumbnail product-item__thumbnail")
    image = divTag.find_all("img")[0]["data-src"]
    link = itemTag.find("a")["href"]
    name = itemTag.find("h2", class_="woocommerce-loop-product__title").text
    price = itemTag.find("bdi").text
    info.append(OrderedDict({"name": name, "price": price, "image": image, "link": link}))
except:
    info.append(False)

# Newegg
try:
    itemTag = websites["newegg"].find("div", class_="item-cell")
    image = itemTag.find("img")["src"]
    divTag = itemTag.find("div", class_="item-info")
    linkTag = divTag.contents[1]
    name = linkTag.text
    link = linkTag["href"]
    link = link.replace(" ", "")
    priceTag = itemTag.find("li", class_="price-current")
    price = re.search("₹\s\d*\,\d*", priceTag.text)[0]
    info.append(OrderedDict({"name": name, "price": price, "image": image, "link": link}))
except:
    info.append(False)

# Priting the details
index = {0: "Flipkart", 1:"PC_Shop", 2: "Newegg"}
for i, details in enumerate(info):
    tempImage = None
    print("*" * 50)
    print(index[i])
    print("-" * 50)
    if info[i]:
        for key in info[i]:
            if key == "image":
                if not tempImage:
                    tempImage = info[i][key]
            print(f"{key.capitalize()}: {info[i][key]}")
    else:
        print("Not Available")
    print("*" * 50)
    print()

# Display the image
if tempImage:
    image = Image.open(requests.get(tempImage, stream=True).raw)
    image.show()
    