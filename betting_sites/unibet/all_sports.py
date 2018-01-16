import requests, json, re, os, sys, random, time, traceback
from datetime import datetime

PROXIES = ['46.4.10.204:3369', '46.4.10.204:3370', '46.4.10.204:3365', '46.4.10.204:3366', '46.4.10.204:3367', '46.4.10.204:3368']
PERIODS_MAP = {
    'soccer': {
        '1st half': '1H',
        '2nd half': '2H'
    }
}


class Sports:
    def __init__(self, sport, timesleep, period):
        self.sport = sport
        self.timesleep = timesleep
        self.session = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
        self.DOMAINS = ['e1-api.kambi.com', 'e1-api.kambicdn.com', 'e2-api.kambi.com', 'e3-api.kambi.com', 'e4-api.kambi.com']
        self.domain = self.DOMAINS[0]
        self.proxy = random.choice(PROXIES)
        self.period = period
        self.URLS = {
            'soccer': {
                'ft': {
                    'ml_ft':'https://{}/offering/api/v3/ub/listView/football.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&categoryGroup=COMBINED&category=match'
                },
                'fh': {
                    'ml_fh': 'https://{}/offering/api/v3/ub/listView/football.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&categoryGroup=BET_OFFER_CATEGORY_SELECTION&category=Half%20Time',
                    'ou': 'https://{}/offering/api/v3/ub/listView/football.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&categoryGroup=BET_OFFER_CATEGORY_SELECTION&category=Total%20Goals%20-%201st%20Half'
                }
            }
        }

    def get_data(self, url):
        req_cont = requests.get(url.format(self.domain), headers=self.headers).content

        try:
            data = json.loads(req_cont)['events']
        except:
            if '410 Content may have moved' in req_cont:
                for dmn in self.DOMAINS:
                    self.domain = dmn
                    req_cont = requests.get(url.format(self.domain), headers=self.headers).content

                    if '410 Content may have moved' not in req_cont:
                        break
                data = json.loads(req_cont)['events']
            else:
                try:
                    self.proxy = random.choice([x for x in PROXIES if x != self.proxy])
                    r_cont = requests.get(url.format(self.domain), proxies={'http': self.proxy, 'https': self.proxy}, headers=self.headers).content
                    data = json.loads(r_cont)['events']
                except:
                    print r_cont
        return data

    def scrape_soccer(self, is_live):

        print "TEST COMMENT"

        json_events = []
        for url in [self.URLS['soccer']['ft']['ml_ft'], self.URLS['soccer']['fh']['ml_fh'], self.URLS['soccer']['fh']['ou']]:
            data = self.get_data(url)
            json_events += data

        print "Events count: {}".format(len(json_events))

        events = {}
        for event in json_events:
            if is_live:
                if event['event']['state'] != 'STARTED':
                    continue
            else:
                if event['event']['state'] == 'STARTED':
                    continue
            if event["event"]["id"] in events:
                e = events[event["event"]["id"]]
            else:
                ev_id = event["event"]["id"]
                ev_name = event["event"]["englishName"].encode("utf-8")
                ev_home_name = event["event"]["homeName"].encode("utf-8")
                ev_away_name = event["event"]["awayName"].encode("utf-8")
                ev_league_title = ' - '.join([x["englishName"].encode("utf-8") for x in event["event"]["path"][1:]])
                ev_start_date = datetime.fromtimestamp(event["event"]["start"]/1000).strftime("%Y-%m-%d %H:%M:%S")
                ev_started = (1 if event["event"]["state"] == "STARTED" else 0)
                e = {
                    "id": ev_id,
                    "name": ev_name,
                    "homeName": ev_home_name,
                    "awayName": ev_away_name,
                    "startTime": ev_start_date,
                    "started": ev_started,
                    "league_title": ev_league_title,
                    "markets_data": {}
                }

            for bet in event["betOffers"]:
                if len(bet["outcomes"]) == 0:
                    continue
                if bet["betOfferType"]["name"].lower() == "match" and bet["criterion"]["label"].lower() == "full time":
                    if not "ft" in e["markets_data"]:
                        e["markets_data"]["ft"] = {"ml": {}}
                    else:
                        e["markets_data"]["ft"]["ml"] = {}
                    odd_home = float(bet["outcomes"][0]["odds"])/1000
                    odd_draw = float(bet["outcomes"][1]["odds"])/1000
                    odd_away = float(bet["outcomes"][2]["odds"])/1000

                    e["markets_data"]["ft"]["ml"] = {
                        "homeName": e["homeName"],
                        "awayName": e["awayName"],
                        "odd_home": odd_home,
                        "odd_draw": odd_draw,
                        "odd_away": odd_away
                    }
                elif bet["betOfferType"]["name"].lower() == "over/under" and bet["criterion"][
                    "label"].lower() == "total goals":
                    if not "ft_ou" in e["markets_data"]:
                        e["markets_data"]["ft_ou"] = {"ml": {}}
                    else:
                        e["markets_data"]["ft_ou"]["ml"] = {}
                    odd_over = float(bet["outcomes"][0]["odds"]) / 1000
                    odd_under = float(bet["outcomes"][1]["odds"]) / 1000
                    spread_line = float(bet["outcomes"][1]["line"]) / 1000

                    e["markets_data"]["ft_ou"]["ml"] = {
                        "homeName": e["homeName"],
                        "awayName": e["awayName"],
                        "odd_over": odd_over,
                        "odd_under": odd_under,
                        "spread": spread_line
                    }
                elif bet["betOfferType"]["name"].lower() == "match" and bet["criterion"][
                    "label"].lower() == "half time":
                    if not "fh" in e["markets_data"]:
                        e["markets_data"]["fh"] = {"ml": {}}
                    else:
                        e["markets_data"]["fh"]["ml"] = {}
                    odd_home = float(bet["outcomes"][0]["odds"]) / 1000
                    odd_draw = float(bet["outcomes"][1]["odds"]) / 1000
                    odd_away = float(bet["outcomes"][2]["odds"]) / 1000

                    e["markets_data"]["fh"]["ml"] = {
                        "homeName": e["homeName"],
                        "awayName": e["awayName"],
                        "odd_home": odd_home,
                        "odd_draw": odd_draw,
                        "odd_away": odd_away
                    }
                else:
                    continue
                if is_live:
                    e["liveData"] = {}
                    score = {
                        "home": event["liveData"]["score"]["home"],
                        "away": event["liveData"]["score"]["away"],
                    }
                    liveMinute = event["liveData"]["matchClock"]["minute"] if event["liveData"]["matchClock"]["period"] == '1st half' else event["liveData"]["matchClock"]["minute"] - 45
                    period = '1H' if PERIODS_MAP[self.sport.lower()] == '1st half' else '2H' if PERIODS_MAP[self.sport.lower()] == '2nd half' else 'HT' if liveMinute == 0 and event["liveData"]["matchClock"]["period"] != '1st half' else 'LIVE'
                    statisticsHome = event["liveData"]["statistics"]["football"]["home"]
                    statisticsAway = event["liveData"]["statistics"]["football"]["away"]

                    e["liveData"]["score"] = score
                    e["liveData"]["minute"] = liveMinute
                    e["liveData"]["period"] = period
                    e["liveData"]["statistics"] = {
                        "home": statisticsHome,
                        "away": statisticsAway
                    }

                events[event["event"]["id"]] = e
        return events

    def scrape_soccer_prematch(self):
        return self.scrape_soccer(False)
    def scrape_soccer_live(self):
        return self.scrape_soccer(True)

    def saveInFile(self, data):
        try:
            dirname = os.path.abspath(os.path.join("E:\Projects\Mine\web-scraping\Betting_sites", "unibet/results"))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            filename = '{}/{}_{}.json'.format(dirname, self.sport, self.period)
            with open(filename, "w") as outfile:
                json.dump(data, outfile, ensure_ascii=False)
                print "FILENAME: {}".format(filename)
            return filename
        except:
            traceback.print_exc()
            print "PROBLEM WITH SAVING THE FILE"

    def handle(self):
        general_time = datetime.now()
        while True:
            print "============START SCRAPING============="
            start_time = datetime.now()
            method_call = 'scrape_{}_{}'.format(self.sport.lower(), self.period)
            data = getattr(self, method_call)()
            if ((start_time-general_time).seconds > 4*60*60) or len(data.keys()) == 0:
                sys.exit()
            self.saveInFile(data)
            end_time = datetime.now()
            iteration_time = (end_time - start_time).seconds
            print "Scraping time: {} seconds".format(iteration_time)
            print "============END SCRAPING============="
            print "Will sleep for {} seconds".format(self.timesleep - iteration_time)
            time.sleep(self.timesleep-iteration_time)