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

    def get_event_data(self, url):
        req = requests.get(url)
        req_html = soup(req.content, "html.parser")
        self.in_event_response = req_html.find("div",{"class":"table-container"})
        self.more_bets = (req_html.find("div",{"class","simpleContainer"}) if req_html.find("div",{"class":"simpleContainer"}) else None)

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
                try:
                    self.get_event_data(link)
                    matches = self.in_event_response.findAll('div',{'class':'lines'})

                    for match in matches:
                        self.league = match.findPrevious('h4').text
                        draw_el = []
                        for x in match.findAll("ul",{"class":"row-away"}):
                            if x.find('li',{'class':'period'}):
                                self.p.append(x.find('li',{'class':'period'}).span.text + x.find('li',{'class':'period'}).sub.text)
                            else:
                                self.printSomething(sport, teams, " ----- failed")

                        #getting home data
                        home_el = match.findAll('ul',{'class':'row-home'})

                        #getting away data
                        away_el = match.findAll('ul',{'class':'row-away'})

                        #getting draw data
                        if sport == 'Soccer':
                            draw_el = match.findAll('ul',{'class':'row-draw'})

                        try:
                            for i,e in enumerate(home_el):
                                #need this in odds format
                                h_s = oddsFormat(e.find("li",{"class":"spread"}).findAll('a')[-1].text.replace(u'\00a0',u'').replace(u'\xa0',u'').encode('utf-8'))
                                h_ml = oddsFormat(e.find('li',{'class':'money-line'}).a.text.replace(u'\00a0',u'').replace(u'\xa0',u'').encode('utf-8'))
                                a_s = oddsFormat(away_el[i].find("li",{"class":"spread"}).findAll('a')[-1].text.replace(u'\00a0',u'').replace(u'\xa0',u'').encode('utf-8'))
                                a_ml = oddsFormat(away_el[i].find('li',{'class':'money-line'}).a.text.replace(u'\00a0',u'').replace(u'\xa0',u'').encode('utf-8'))
                                if sport == 'Soccer':
                                    draw_ml = oddsFormat(draw_el[i].find('li',{'class':'money-line'}).a.text.strip().replace('\n','').encode('utf-8'))
                                    self.structure[date][-1]["draw"] = draw_ml
                                self.structure[date][-1]["home"].append({
                                    'period': self.p[i],
                                    'homeSpread': h_s,
                                    'homeMoneyLine': h_ml
                                })
                                self.structure[date][-1]["away"].append({
                                    'period': self.p[i],
                                    'awaySpread': a_s,
                                    'awayMoneyLine': a_ml
                                })
                        except Exception as e:
                            pass

                    if self.more_bets != None:
                        additional_betts_container = self.more_bets.find("div",{"class":"table-container"})
                        self.printSomething("...pulling more bets")
                        a_b = []
                        for bet in additional_betts_container.findAll("div",{"class":"lines"}):
                            a_b.append({
                                bet.find("ul",{"class":"table-head"}).li.div.a.strong.text: [{"name": x.li.a.find("span",{"class":"name"}).text.replace(u'\00a0',u'').replace(u'\xa0',u'').replace(u'\u00BD',u'0xbd').encode('utf-8'), "odd": oddsFormat(x.li.a.find("span",{"class":"odd"}).text.replace(u'\00a0',u'').replace(u'\xa0',u'').encode('utf-8'))} for x in bet.findAll("ul",{"class":"table"})]
                            })
                        self.structure[date][-1]["addBets"] = a_b
                except Exception as e:
                    print e


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
