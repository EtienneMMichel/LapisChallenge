import requests
import json
from datetime import datetime
from datetime import timezone

ODDS_URL = "https://offer.cdn.begmedia.com/api/pub/v4/events?application=2&countrycode=fr&fetchMultipleDefaultMarkets=true&hasSwitchMtc=false&language=fr&limit={limit}&offset=0&sitecode=frfr&sortBy=ByLiveRankingPreliveDate&sportIds={sportIds}"
SPORTS_DICT = {"foot": "1", "tennis": "2"}


class OddReader():
    def __init__(self):
        self.headers = {
            # "referer": "https://www.oddsportal.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _convert_date_to_timestamp(self, date_string):

        date_time = datetime.fromisoformat(date_string[:-1]).astimezone(timezone.utc)
        timestamp = int(datetime.timestamp(date_time))
        return timestamp
    
    def _transform(self,data):
        res = []
        data = json.loads(data)
        for match in data:
            if "markets" in match.keys():
                if len(match["markets"]) > 0:
                    match_info = {}
                    match_info["sport"] = match["competition"]["sport"]["name"]
                    match_info["competition"] = match["competition"]["name"]
                    match_info["label"] = match["name"]
                    match_info["date"] = self._convert_date_to_timestamp(match["date"])
                    match_info["team1"] = match["contestants"][0]["name"]
                    match_info["team2"] = match["contestants"][1]["name"]
                    match_info["odds"] = {}
                    if len(match["markets"][0]["selections"]) == 2:
                        match_info["odds"]["team1_odd"] =  match["markets"][0]["selections"][0]["odds"]
                        match_info["odds"]["team2_odd"] =  match["markets"][0]["selections"][1]["odds"]
                    elif len(match["markets"][0]["selections"]) == 3:
                        match_info["odds"]["team1_odd"] =  match["markets"][0]["selections"][0]["odds"]
                        match_info["odds"]["null_odd"] =  match["markets"][0]["selections"][1]["odds"]
                        match_info["odds"]["team2_odd"] =  match["markets"][0]["selections"][2]["odds"]
                    else:
                        print("______________")
                    res.append(match_info)
        return res

    def get_url(self, sport):
        if not sport in SPORTS_DICT.keys():
            raise f"{sport} is not in the list of available sport"
        sportIds = SPORTS_DICT[sport]
        url = ODDS_URL.format(limit=140, sportIds=sportIds)
        return url


    def get_odds(self,sport):
        data = None
        url = self.get_url(sport)
        response = self.session.get(url)
        data = response.text
        matches_info = self._transform(data)
        return matches_info