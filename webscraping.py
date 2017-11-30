from urllib2 import urlopen
from urllib import urlretrieve
from bs4 import BeautifulSoup as soup


#grabbing the needed html
myUrl = "https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card"
uClient = urlopen(myUrl)
page_html = uClient.read()
uClient.close()

page_soup = soup(page_html, "html.parser")
containers = page_soup.findAll("div", {"class":"item-container"})

filename = "products.csv"
f = open(filename, "w")

headers = "brand, product_name, image_address, shipping\n"

f.write(headers)

for container in containers:
    brand = container.div.div.a.img["title"]

    #getting the img adreess
    img_address = container.a.img["data-src"]

    #downloading the image itself
    img = urlretrieve("https:" + img_address, img_address.split('/')[-1])

    name_container = container.findAll("a", {"class":"item-title"})
    name = name_container[0].text.strip()

    shipping_container = container.findAll("li",{"class":"price-ship"})
    ship = shipping_container[0].text.strip()

    f.write(brand + "," + name.replace(",", " ") + ", " + ("https:"+img_address) + "," + ship + "\n")

f.close()
