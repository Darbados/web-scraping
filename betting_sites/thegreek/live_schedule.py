import requests
from bs4 import BeautifulSoup as soup
import re
import json
from .methods import oddsFormat

class LiveSchedule:
    def __init__(self):
        self.url = "http://www.thegreek.com/sportsbook/quick-search/"
        self.structure = {}
        self.response = {}
        self.in_event_response = {}
        self.dates = []
        self.league = ""
        self.p = []
        self.more_bets = {}

    def get_data(self):
        req = requests.get(self.url + "live-events")
        req_html = soup(req.content, "html.parser")
        self.response = req_html.findAll("div",{"class":"table-container"})

    def get_event_data(self, url):
        req = requests.get(url)
        req_html = soup(req.content, "html.parser")
        self.in_event_response = req_html.find("div",{"class":"table-container"})
        self.more_bets = (req_html.find("div",{"class","simpleContainer"}) if req_html.find("div",{"class":"simpleContainer"}) else None)

    def printSomething(self, *args):
        print ', '.join(args)

    def saveStructure(self):
        for i,events in enumerate(self.response):
            date = events.h2.find("span",{"class":"icon"}).text
            date_events_all = events.find("ul",{"class":"landing-list"})
            date_events = date_events_all.findAll("li")
            self.dates.append(date)
            self.structure[date] = []

            for event in date_events:
                link = self.url + event.a["href"]

                sport = event.a.find("div",{"class":"text-gray"}).text
                teams = event.a.find("div",{"class":"teams"}).get_text()
                league = event.a.find("div",{"class":"teams"}).span.text
                progress = event.a.find("span",{"class":"right"}).text

                self.structure[date].append({
                    "sport": sport,
                    "teams": teams,
                    "league": league,
                    "time": progress,
                    "home": [],
                    "away": []
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
                                h_s = oddsFormat(e.find("li",{"class":"spread"}).findAll('a')[-1].text.replace(u'\xa0',u' ').encode('utf-8'))
                                h_ml = oddsFormat(e.find('li',{'class':'money-line'}).a.text.replace(u'\xa0',u' ').encode('utf-8'))
                                a_s = oddsFormat(away_el[i].find("li",{"class":"spread"}).findAll('a')[-1].text.replace(u'\xa0',u' ').encode('utf-8'))
                                a_ml = oddsFormat(away_el[i].find('li',{'class':'money-line'}).a.text.replace(u'\xa0',u' ').encode('utf-8'))
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
                                bet.find("ul",{"class":"table-head"}).li.div.a.strong.text: [{"name": x.li.a.find("span",{"class":"name"}).text.replace('\u00a0', '').encode('utf-8'), "odd": oddsFormat(x.li.a.find("span",{"class":"odd"}).text.replace('u\00a0', '').encode('utf-8'))} for x in bet.findAll("ul",{"class":"table"})]
                            })
                        self.structure[date][-1]["addBets"] = a_b
                except Exception as e:
                    print e


    def save_in_file(self):
        f = open('thegreek/output/liveEvents_thegreek.txt', "w")
        for date in self.dates:
            f.write(json.dumps(date) + '\n')
            for x in self.structure[date]:
                f.write(json.dumps(x) + '\n')
        f.close()

    def handle(self):
        print "============START SCRAPING============="
        self.get_data()
        self.saveStructure()
        self.save_in_file()
        print "============END SCRAPING============="
