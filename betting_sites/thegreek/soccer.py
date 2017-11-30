import requests
from bs4 import BeautifulSoup as soup
import re
import json
from .methods import oddsFormat
from .Main_Scraper import Sport

class Soccer(Sport):
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

                #getting draw data
                draw_el = match.findAll('ul',{'class':'row-draw'})
                draw_ml = oddsFormat(draw_el[0].find('li',{'class':'money-line'}).a.text.strip().replace('\n','').encode('utf-8'))

                self.structure[self.sport].append({
                    'sport':self.sport,
                    'league':self.league,
                    'date':date,
                    'home':home_name,
                    'away':away_name,
                    'periods':[],
                    'draw':draw_ml
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
                    #print """home {5} - {6} away \nperiod: {0}\nhomeSpread: {1:.2f}\nhomeMoneyLine: {2:.2f}\nawaySpread: {3:.2f}\nawayMoneyLine: {4:.2f}\n""".format(e,h_s,h_ml,a_s,a_ml,home_name,away_name)
