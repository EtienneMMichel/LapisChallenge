from .backtester import Backtester
from utils import PredsBody, PickerBody
import numpy as np

from api import picker

class OptimizerBacktester(Backtester):
    def __init__(self, forecaster_model, optimizer_model, sport, start_year, end_year, zone=None, competitions=None) -> None:
        self.forecaster_model = forecaster_model
        self.optimizer_model = optimizer_model
        self.sport = sport
        self.start_year = start_year
        self.end_year = end_year
        self.zone = zone
        self.competitions = competitions
        self.retrieve_dataset(sport, start_year, end_year, zone, competitions)
        self.picker_model = picker.SingleMatch()

    def build_pred_input(self, match):
        return PredsBody(team_1_id=match["team_1_name"],
                         team_2_id=match["team_2_name"],
                         date=match["current_date"],
                         modelName="")
    
    def build_picker_inputs(self, matches, preds):
        return PickerBody(
            preds=preds,
            odds=[[match[odd_key] for odd_key in filter(lambda key: key[:4] == "odd_", list(match.keys()))] for match in matches]
        )
    
    def get_winners_vect(self,matches):
        winning_alloc_2_mapping = {
            "1":0,
            "2":1,
        }

        winning_alloc_3_mapping = {
            "1":0,
            "null":1,
            "2":2,
        }
        matches_nb_issues = [len(list(filter(lambda key: key[:4] == "odd_", list(match.keys())))) for match in matches]
        winners = []
        for i_match, match in enumerate(matches):
            winning_alloc_index = eval(f"winning_alloc_{matches_nb_issues[i_match]}_mapping[match['winner']]")
            match_vector = [0 for _ in range(matches_nb_issues[i_match])]
            match_vector[winning_alloc_index] = 1
            winners.extend(match_vector)
        return np.array(winners)
    
    def reward(self, matches, portfolio_alloc):
       
        winners = self.get_winners_vect(matches)
        gain = 0
        for comb_info in portfolio_alloc:
            if np.array(np.array(np.multiply(comb_info["comb"], winners) - comb_info["comb"]) == 0).all(): # check if it's winning combinaison
                gain += (comb_info["odd"] - 1)*comb_info["alloc"]
            else:
                gain -= comb_info["alloc"]
        return gain


    def process(self):
        res = []
        for matches in self.dataset_gen():
            pred_inputs = [self.build_pred_input(match) for match in matches]
            #2. make preds
            preds = self.forecaster_model.act(pred_inputs)
            #2. pick combs
            picker_inputs = self.build_picker_inputs(matches, preds)
            selected_combs = self.picker_model.act(picker_inputs)
            #3. allocation
            portfolios_alloc = {}
            rewards = {}
            for optimizer_model in self.optimizer_model:
                portfolio_alloc = optimizer_model.act(selected_combs)
                portfolios_alloc[optimizer_model.name] = portfolio_alloc
                rewards[optimizer_model.name] = self.reward(matches, portfolio_alloc)
            res.append({
                "date":matches[0]["date"],
                "matches":matches,
                "preds":preds,
                "portfolios_alloc":portfolios_alloc,
                "rewards":rewards
            })
        
        return res