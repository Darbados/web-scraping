import requests, json, re, os, sys, random, time, traceback
from datetime import datetime

PROXIES = ['46.4.10.204:3369', '46.4.10.204:3370', '46.4.10.204:3365', '46.4.10.204:3366', '46.4.10.204:3367', '46.4.10.204:3368']

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
                    r_cont = requests.get(url.format(self.domain), headers=self.headers).content
                    data = json.loads(r_cont)['events']
                except:
                    print r_cont
        return data

    def scrape_soccer(self, is_live):
        json_events = []
        for url in [self.URLS['soccer']['ft']['ml_ft'], self.URLS['soccer']['fh']['ml_fh'], self.URLS['soccer']['fh']['ou']]:
            data = self.get_data(url)
            json_events += data

        events = {}
        for event in json_events:
            ev_id = event["event"]["id"]
            en_name = event["event"]["englishName"].encode("utf-8")
            ev_home_name = event["event"]["homeName"].encode("utf-8")
            ev_away_name = event["event"]["awayName"].encode("utf-8")
            ev_league_title = ' - '.join([x["englishName"].encode("utf-8") for x in event["event"]["path"][1:]])
            ev_start_date = datetime.fromtimestamp(event["event"]["start"]/1000).strftime("%Y-%m-%d %H:%M:%S")
            key = "{}|||{}|||{}|||{}".format(self.sport, ev_league_title, ev_home_name, ev_away_name)
            e = {}
            e["id"] = ev_id
            e["name"] = en_name
            e["homeName"] = ev_home_name
            e["awayName"] = ev_away_name
            e["startTime"] = ev_start_date
            events[key] = e

        return events

    def scrape_soccer_prematch(self):
        return self.scrape_soccer(False)


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
        while True:
            print "============START SCRAPING============="
            start_time = datetime.now()
            method_call = 'scrape_{}_{}'.format(self.sport, self.period)
            data = getattr(self, method_call)()

            self.saveInFile(data)
            end_time = datetime.now()
            iteration_time = (end_time - start_time).seconds
            print iteration_time
            print "============END SCRAPING============="
            time.sleep(self.timesleep)