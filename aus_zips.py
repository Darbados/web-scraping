from urllib2 import urlopen
from bs4 import BeautifulSoup as soup


all_regions = ["act","nsw","nt","qld","sa","tas","vic","wa"]

filename = "aus_zips.csv"
f = open(filename, "w")

headers = "Region\n\n"

f.write(headers)

for x in all_regions:
    #get the first australian region
    act_url = "https://postcodes-australia.com/state-postcodes/{}".format(x)
    uClient = urlopen(act_url)
    page_html = uClient.read()
    uClient.close()

    #parsing the page html in readable format with the BeautifulSoup

    page_soup = soup(page_html, "html.parser")
    zips_container = page_soup.find("ul", {"class":"pclist"})
    all_zips = zips_container.findAll("li")
    region = page_soup.findAll("h1")[1].text

    f.write(region.replace("All postcodes in ", "") + "\n")

    for code in all_zips:
        try:
            f.write(code.a.text + "\n")
        except:
            pass
    f.write("\n")

f.close()
