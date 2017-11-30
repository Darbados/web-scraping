from thegreek import Football, Basketball, Hockey, Soccer, LiveSchedule, football_url, basketball_url, hockey_url, soccer_url

scrapeF = Football(football_url,"football")
scrapeF.handle()

scrapeB = Basketball(basketball_url, "basketball")
scrapeB.handle()

scrapeH = Hockey(hockey_url, "hockey")
scrapeH.handle()

scrapeS = Soccer(soccer_url, "soccer")
scrapeS.handle()

scrapeL = LiveSchedule()
scrapeL.handle()
