import requests
from bs4 import BeautifulSoup as soup
import re
import json
from .methods import oddsFormat

class Sport:
    def __init__(self, url, sport):
        self.url = url
        self.events = []
        self.dates = {}
        self.events = {}
        self.structure = {}
        self.p = []
        self.sport = sport
        self.league = ""

    def printSomething(self, *args):
        print ', '.join(args)

    def get_data(self):
        football_req = requests.get(self.url)
        football_soup = soup(football_req.content, "html.parser")
        self.dates = football_soup.findAll('h2',{'class':'date'})
        self.events = football_soup.findAll('div',{'class':'table-container'})
        self.sport = self.events[0].findAll('h3')[0].text

    def saveStructure(self):
        self.structure[self.sport] = []
        all_events = self.events
        home_periods = []
        away_periods = []

        for i,events in enumerate(all_events):
            date = self.dates[i].find('span',{'class':'icon'}).text
            matches = events.findAll('div',{'class':'lines'})

            for match in matches:
                self.league = match.findPrevious('h4').text
                self.p = [(x.find('li',{'class':'period'}).span.text + ' ' + x.find('li',{'class':'period'}).sub.text) for x in match.findAll('ul',{'row-away'})]

                self.printSomething(self.sport, self.league)

                #getting home data
                home_el = match.findAll('ul',{'class':'row-home'})
                home_name = home_el[0].find('li',{'class':'name'}).a.text.strip().replace('\n','').encode('utf-8')
                #getting away data
                away_el = match.findAll('ul',{'class':'row-away'})
                away_name = away_el[0].find('li',{'class':'name'}).a.text.strip().replace('\n','').encode('utf-8')

                self.structure[self.sport].append({
                    'sport':self.sport,
                    'league':self.league,
                    'date':date,
                    'home':home_name,
                    'away':away_name,
                    'periods':[]
                })
                for i,e in enumerate(self.p):
                    #need this in odds format
                    h_s = oddsFormat(home_el[i].find("li",{"class":"spread"}).findAll('a')[-1].text.replace(u'\xa0',u' ').encode('utf-8'))
                    h_ml = oddsFormat(home_el[i].find('li',{'class':'money-line'}).a.text.replace(u'\xa0',u' ').encode('utf-8'))
                    a_s = oddsFormat(away_el[i].find("li",{"class":"spread"}).findAll('a')[-1].text.replace(u'\xa0',u' ').encode('utf-8'))
                    a_ml = oddsFormat(away_el[i].find('li',{'class':'money-line'}).a.text.replace(u'\xa0',u' ').encode('utf-8'))
                    self.structure[self.sport][-1]["periods"].append({
                        'period': e,
                        'homeSpread': h_s,
                        'homeMoneyLine': h_ml,
                        'awaySpread': a_s,
                        'awayMoneyLine': a_ml
                    })


    def save_in_file(self):
        f = open('thegreek/output/' + (self.sport + '_thegreek.txt'), "w")
        for date in self.dates:
            d = date.find('span',{'class':'icon'}).text
            f.write(json.dumps(d) + '\n')
            for x in self.structure[self.sport]:
                if d == x["date"]:
                    f.write(json.dumps(x) + '\n')
        f.close()

    def handle(self):
        print "=============START SCRAPING==============="
        self.get_data()
        self.saveStructure()
        self.save_in_file()
        print "=============END SCRAPING==============="
