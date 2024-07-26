import pandas as pd
from utils import DATA_PATH
import os
import json
from datetime import datetime

NB_MATCHES_BY_ALLOC = 5 # will be a request parameter in the future


class Backtester():
    def __init__(self) -> None:
        pass

    def fetch_data(self, sport, zone , competition):
        with open(os.path.join(DATA_PATH, sport, zone, f"{competition}.json"), encoding='utf-8') as fh:
            data = json.load(fh)
        df = pd.DataFrame.from_records(data)
        df["competition"] = [competition for _ in range(df.shape[0])]
        df["zone"] = [zone for _ in range(df.shape[0])]
        df["sport"] = [sport for _ in range(df.shape[0])]
        return df

    def retrieve_dataset(self, sport, start_year, end_year, zone=None, competitions=None):
        dataset = None
        sport_path = os.path.join(DATA_PATH, sport)
        if not zone is None:
            if competitions is None:
                competitions = [comp[:-5] for comp in os.listdir(os.path.join(sport_path, zone))]
            
            for competition in competitions:
                    df = self.fetch_data(sport, zone, competition)
                    if dataset is None:
                        dataset = df
                    else:
                        dataset = pd.concat([dataset, df], axis=0)
            dataset.reset_index(inplace=True, drop=True)

        else:
            zones_availables = os.listdir(sport_path)
            for zone in zones_availables:
                sport_zone_path = os.path.join(sport_path, zone)
                competitions_availables = [comp[:-5] for comp in os.listdir(sport_zone_path)]
                for competition in competitions_availables:
                    df = self.fetch_data(sport, zone, competition)
                    if dataset is None:
                        dataset = df
                    else:
                        dataset = pd.concat([dataset, df], axis=0)
            dataset.reset_index(inplace=True, drop=True)

        dataset["date"] = [pd.Timestamp(t, unit='s') for t in dataset["current_date"]]
        start_date = datetime(start_year, 1,1,0,0)        
        end_date = datetime(end_year, 1,1,0,0)   
        dataset = dataset.loc[(dataset['date'] > start_date) & (dataset['date'] <= end_date)]
        dataset = dataset.sort_values(by='date')
        self.dataset = dataset.to_dict('records')

    def dataset_gen(self):
        i = NB_MATCHES_BY_ALLOC
        while i < len(self.dataset):
            yield self.dataset[i - NB_MATCHES_BY_ALLOC:i]
            i += NB_MATCHES_BY_ALLOC

                        
