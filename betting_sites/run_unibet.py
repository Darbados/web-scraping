from unibet import LiveEvents, Sports
import schedule
from unibet import _urls

filenames = ["TENNIS","FOOTBALL","BASKETBALL","ICE_HOCKEY","AMERICAN_FOOTBALL","BASEBALL","CRICKET","HANDBALL","VOLLEYBALL","AUSTRALIAN_RULES","BANDY","BOXING","CHESS","CYCLING","CYCLO_CROSS","DARTS","ESPORTS","GOLF"]

#liveEvents = LiveEvents()
#liveEvents.handle()

for i,url in enumerate(_urls):
    sport = Sports(url, filenames[i], filenames[i])
    sport.handle()

'''
Used to execute the scrapers every 10 seconds
while True:
    schedule.run_pending()
'''
