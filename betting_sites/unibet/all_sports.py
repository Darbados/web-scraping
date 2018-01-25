import requests, json, re, os, sys, random, time, traceback
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

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
        self.session.headers.update(self.headers)
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
                },
                'hdp': {
                    'ml_ft': 'https://{}/offering/api/v3/ub/listView/football.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&categoryGroup=BET_OFFER_CATEGORY_SELECTION&category=Asian%20Handicap'
                }
            }
        }

    def get_data(self, url):
        formatted_url = url.format(self.domain)
        print formatted_url
        req_cont = self.session.get(url.format(self.domain), proxies={'https:': self.proxy, 'http:': self.proxy}).content

        try:
            data = json.loads(req_cont)['events']
            print "Events available: {}".format(len(data))
        except:
            if '410 Content may have moved' in req_cont:
                for dmn in self.DOMAINS:
                    self.domain = dmn
                    req_cont = requests.get(url.format(self.domain), headers=self.headers, proxies={'http:': self.proxy, 'https:': self.proxy}).content

                    if '410 Content may have moved' not in req_cont:
                        break
                data = json.loads(req_cont)['events']
            else:
                try:
                    self.proxy = random.choice([x for x in PROXIES if x != self.proxy])
                    r_cont = self.session.get(url.format(self.domain), proxies={'http': self.proxy, 'https': self.proxy}, headers=self.headers).content
                    data = json.loads(r_cont)['events']
                except:
                    print traceback.print_exc()
        return data

    def scrape_soccer(self, is_live):
        json_events = []
        for url in [self.URLS['soccer']['ft']['ml_ft'], self.URLS['soccer']['fh']['ml_fh'], self.URLS['soccer']['fh']['ou'], self.URLS['soccer']['hdp']['ml_ft']]:
            data = self.get_data(url)
            json_events += data


        events = {}
        for event in json_events:
            if is_live:
                if event['event']['state'] != 'STARTED':
                    continue
            else:
                if event['event']['state'] == 'STARTED':
                    continue

            leagueTitle = (' - '.join([x["englishName"] for x in event["event"]["path"]])).encode('utf-8')
            homeTitle = event["event"]["homeName"].encode('utf-8')
            awayTitle = event["event"]["awayName"].encode('utf-8')
            start_date = datetime.fromtimestamp(event["event"]["start"]/1000).strftime("%d-%m-%Y %H:%M:%S")
            sport_title = self.sport
            ev = {
                "sport_title": sport_title,
                "league_title": leagueTitle,
                "home_title": homeTitle,
                "away_title": awayTitle,
                "start_date": start_date,
                "markets_data": {}
            }
            if len(event["betOffers"]) == 0:
                continue
            else:
                for bet in event["betOffers"]:
                    if bet["betOfferType"]["name"].lower() == 'match' and bet["criterion"]["label"].lower() == 'full time':
                        period = "ft"
                        mkt = {
                            "market_type": "ml",
                            "option_index": int(bet["sortOrder"]),
                            "odd_home": {
                                "external": {
                                    "home_title": ev["home_title"],
                                    "away_title": ev["away_title"],
                                    "league_title": ev["league_title"]
                                },
                                "value": float(bet["outcomes"][0]["odds"]/1000)
                            },
                            "odd_away": {
                                "external": {
                                    "home_title": ev["home_title"],
                                    "away_title": ev["away_title"],
                                    "league_title": ev["league_title"]
                                },
                                "value": float(bet["outcomes"][2]["odds"] / 1000)
                            },
                            "odd_draw": {
                                "external": {
                                    "home_title": ev["home_title"],
                                    "away_title": ev["away_title"],
                                    "league_title": ev["league_title"]
                                },
                                "value": float(bet["outcomes"][1]["odds"] / 1000)
                            }
                        }
                if period not in ev["markets_data"]:
                    ev["markets_data"][period] = []
                ev["markets_data"][period].append(mkt)
                #if is_live:

            key = "{}${}${}${}".format(self.sport, leagueTitle, homeTitle, awayTitle)
            events[key] = ev
        return events

    def scrape_soccer_prematch(self):
        return self.scrape_soccer(False)
    def scrape_soccer_live(self):
        return self.scrape_soccer(True)

    def saveInFile(self, data):
        try:
            dirname = os.path.abspath(os.path.join(BASE_DIR, "results"))
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