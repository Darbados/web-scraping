import requests
import json
import re

live_events_url = "https://e1-api.aws.kambicdn.com/offering/api/v2/ub/event/live/open.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid={}".format(r'\d+')

class LiveEvents:
    def __init__(self):
        self.url = live_events_url
        self.filename = "live_events.txt"
        self.structure = {}
        self.response = {}
        self.in_event_bets = {}

    def get_initial_data(self,url):
        req = requests.get(url)
        self.response = req.json()

    def get_event_data(self,url):
        req = requests.get(url)
        self.in_event_bets = req.json()

    def printSomething(self, *args):
        print ', '.join(args)

    def saveStructure(self, data, structure):
        for i,event in enumerate(data["liveEvents"]):

            event_id = event["event"]["id"]
            sport = event["event"]["sport"].encode('utf-8')
            name = event["event"]["name"].encode('utf-8')
            home = (event["event"]["homeName"].encode('utf-8') if event["event"].has_key("homeName") else 'None')
            away = (event["event"]["awayName"].encode('utf-8') if event["event"].has_key("awayName") else 'None')
            type_e = event["event"]["type"].encode('utf-8')
            eventClock = event["liveData"]["matchClock"]
            league = event["event"]["path"][1]["name"].encode('utf-8')
            country = event["event"]["group"].encode('utf-8')

            self.printSomething(sport,league,country)

            if not structure.has_key(sport):
                structure[sport] = []
                structure[sport].append({
                    "event_id": event_id,
                    "event": name,
                    "home": home,
                    "away": away,
                    "state": event["event"]["state"],
                    "league": league,
                    "country": country,
                    "liveData": {
                        "matchClock": eventClock,
                    }
                })

                try:
                    offers = []
                    in_live_event_bets = "https://e1-api.aws.kambicdn.com/offering/api/v2/ub/betoffer/live/event/{0}.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid={1}".format(event_id,r'\d+')
                    self.get_event_data(in_live_event_bets)
                    for bet in self.in_event_bets["betoffers"]:
                        offers.append({
                            "live": (bet["live"] if bet.has_key("live") else None),
                            "label": (bet["criterion"]["label"] if bet.has_key("criterion") and bet["criterion"].has_key("label") else None),
                            "betOfferType": (bet["betOfferType"]["name"] if bet.has_key("betOfferType") else None),
                            "cashIn": (bet["cashIn"] if bet.has_key("cashIn") else None),
                            "outcomes": ([{
                                "label": x["label"],
                                "odds": x["odds"],
                                "status": x["status"]
                            } for x in bet["outcomes"]] if bet.has_key("outcomes") else None)
                        })
                    structure[sport][0]["betOffers"] = offers
                except Exception as e:
                    print e

                if event["liveData"].has_key("score"):
                    structure[sport][0]["liveData"]["score"] = event["liveData"]["score"]
            else:
                index = len(structure[sport])
                structure[sport].append({
                    "event_id": event_id,
                    "event": name,
                    "home": home,
                    "away": away,
                    "state": event["event"]["state"],
                    "league": league,
                    "country": country,
                    "liveData": {
                        "matchClock": eventClock,
                    }
                })

                if event["liveData"].has_key("score"):
                    structure[sport][index]["liveData"]["score"] = event["liveData"]["score"]

                try:
                    offers = []
                    in_live_event_bets = "https://e1-api.aws.kambicdn.com/offering/api/v2/ub/betoffer/live/event/{0}.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid={1}".format(event_id,r'\d+')
                    self.get_event_data(in_live_event_bets)
                    for bet in self.in_event_bets["betoffers"]:
                        offers.append({
                            "live": (bet["live"] if bet.has_key("live") else None),
                            "label": (bet["criterion"]["label"] if bet.has_key("criterion") and bet["criterion"].has_key("label") else None),
                            "betOfferType": (bet["betOfferType"]["name"] if bet.has_key("betOfferType") else None),
                            "cashIn": (bet["cashIn"] if bet.has_key("cashIn") else None),
                            "outcomes": ([{
                                "label": x["label"],
                                "odds": x["odds"],
                                "status": x["status"]
                            } for x in bet["outcomes"]] if bet.has_key("outcomes") else None)
                        })
                    structure[sport][index]["betOffers"] = offers
                except Exception as e:
                    print e

                if event["liveData"].has_key("score"):
                    structure[sport][index]["liveData"]["score"] = event["liveData"]["score"]


    def storeInFile(self):
        f = open('unibet/output/' + self.filename, "w")
        f.write(json.dumps(self.structure))
        f.close()

    def handle(self):
        print "=============START SCRAPING=============="
        self.get_initial_data(self.url)
        self.saveStructure(self.response, self.structure)
        self.storeInFile()
        print "=============END SCRAPING================"
