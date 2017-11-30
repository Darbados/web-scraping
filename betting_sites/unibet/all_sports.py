import requests
import json
import re

class Sports:
    def __init__(self, url, sport, filename):
        self.url = url
        self.sport = sport
        self.response = {}
        self.in_event_bets = {}
        self.structure = {"STARTED": {"sport": {}}, "NOT STARTED": {"sport": {}}}
        self.filename = filename

    def printSomething(self, *args):
        print ', '.join(args)

    def get_data(self, url):
        req = requests.get(url)
        self.response = req.json()

    def get_event_data(self,url):
        req = requests.get(url)
        self.in_event_bets = req.json()

    def saveStructure(self, data, structure):
        for i,event in enumerate(data["events"]):
            event_id = event["event"]["id"]
            sport = event["event"]["sport"]
            state = event["event"]["state"]
            name = event["event"]["name"]
            homeName = event["event"]["homeName"]
            awayName = (event["event"]["awayName"] if event["event"].has_key("awayName") else 'None')

            if sport == self.sport:
                if state == "STARTED":
                    if not structure["STARTED"]["sport"].has_key(sport):
                        structure["STARTED"]["sport"][sport] = []
                        structure["STARTED"]["sport"][sport].append({
                            "name": name.encode('utf-8'),
                            "homeName": homeName.encode('utf-8'),
                            "awayName": awayName.encode('utf-8'),
                            "path": [{"name": x["name"], "termKey": x["termKey"]} for x in event["event"]["path"]],
                            "openForLiveBetting": (event["event"]["openForLiveBetting"] if event["event"].has_key('openForLiveBetting') else '')
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
                            structure["STARTED"]["sport"][sport][0]["betOffers"] = offers
                        except Exception as e:
                            structure["STARTED"]["sport"][sport][0]["betOffers"] = ["None offers to bet"]

                        if event.has_key("liveData"):
                            structure["STARTED"]["sport"][event["event"]["sport"]][0]["liveData"] = {
                                "matchClock": (event["liveData"]["matchClock"] if event["liveData"].has_key("matchClock") else ''),
                                "score": (event["liveData"]["score"] if event["liveData"].has_key("score") else ''),
                                "open": event["liveData"]["open"]
                            }
                    else:
                        index = len(structure["STARTED"]["sport"][sport])
                        structure["STARTED"]["sport"][sport].append({
                            "name": name.encode('utf-8'),
                            "homeName": homeName.encode('utf-8'),
                            "awayName": awayName.encode('utf-8'),
                            "path": [{"name": x["name"], "termKey": x["termKey"]} for x in event["event"]["path"]],
                            "openForLiveBetting": (event["event"]["openForLiveBetting"] if event["event"].has_key('openForLiveBetting') else '')
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
                            structure["STARTED"]["sport"][sport][-1]["betOffers"] = offers
                        except Exception as e:
                            structure["STARTED"]["sport"][sport][-1]["betOffers"] = ["None offers to bet"]

                        if event.has_key("liveData"):
                            structure["STARTED"]["sport"][event["event"]["sport"]][-1]["liveData"] = {
                                "matchClock": (event["liveData"]["matchClock"] if event["liveData"].has_key("matchClock") else ''),
                                "score": (event["liveData"]["score"] if event["liveData"].has_key("score") else ''),
                                "open": event["liveData"]["open"]
                            }
                else:
                    if not structure["NOT STARTED"]["sport"].has_key(sport):
                        structure["NOT STARTED"]["sport"][sport] = []
                        structure["NOT STARTED"]["sport"][sport].append({
                            "counter": len(structure["NOT STARTED"]["sport"][sport]),
                            "name": name,
                            "homeName": homeName.encode('utf-8'),
                            "awayName": awayName.encode('utf-8'),
                            "path": [{"name": x["name"], "termKey": x["termKey"]} for x in event["event"]["path"]],
                            "openForLiveBetting": (event["event"]["openForLiveBetting"] if event["event"].has_key("openForLiveBetting") else False)
                        })
                        try:
                            offers = []
                            in_event_bets = "https://e1-api.aws.kambicdn.com/offering/api/v2/ub/betoffer/event/{0}.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid={1}".format(event_id,r'\d+')
                            self.get_event_data(in_event_bets)
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
                            structure["NOT STARTED"]["sport"][sport][-1]["betOffers"] = offers
                        except Exception as e:
                            structure["STARTED"]["sport"][sport][-1]["betOffers"] = ["None offers to bet"]
                    else:
                        index = len(structure["NOT STARTED"]["sport"][sport])
                        structure["NOT STARTED"]["sport"][sport].append({
                            "name": name,
                            "homeName": homeName.encode('utf-8'),
                            "awayName": awayName.encode('utf-8'),
                            "path": [{"name": x["name"], "termKey": x["termKey"]} for x in event["event"]["path"]],
                            "openForLiveBetting": (event["event"]["openForLiveBetting"] if event["event"].has_key("openForLiveBetting") else False)
                        })
                        try:
                            offers = []
                            in_event_bets = "https://e1-api.aws.kambicdn.com/offering/api/v2/ub/betoffer/event/{0}.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid={1}".format(event_id,r'\d+')
                            self.get_event_data(in_event_bets)
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
                            structure["NOT STARTED"]["sport"][sport][-1]["betOffers"] = offers
                        except Exception as e:
                            structure["STARTED"]["sport"][sport][-1]["betOffers"] = ["None offers to bet"]

    def saveInFile(self, structure, filename):
        f = open('unibet/output/%s.txt' %(filename), 'w')
        structure = json.dumps(structure)
        f.write(structure)
        f.close()

    def handle(self):
        print "============START SCRAPING============="
        self.get_data(self.url)
        self.saveStructure(self.response, self.structure)
        self.saveInFile(self.structure, self.filename)
        print "============END SCRAPING============="
