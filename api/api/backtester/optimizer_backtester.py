from .backtester import Backtester
from utils import PredsBody, AllocBody

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

    def build_pred_input(self, match):
        return PredsBody(team_1_id=match["team_1_name"],
                         team_2_id=match["team_2_name"],
                         date=match["current_date"],
                         modelName="")
    
    def build_alloc_input(self, matches, preds):
        return AllocBody(
            preds=preds,
            odds=[[match[odd_key] for odd_key in filter(lambda key: key[:4] == "odd_", list(match.keys()))] for match in matches]
        )
    
    def reward(self, matches, portfolio_alloc):
        winning_alloc_mapping = {
            "1":0,
            "2":1,
            "null":2,
        }
        gain = 0
        for match, portfolio_alloc_to_match in zip(matches, portfolio_alloc):
            winning_odd = match[f"odd_team_{match['winner']}"]
            winning_alloc_index = winning_alloc_mapping[match['winner']]
            gain += winning_odd*portfolio_alloc_to_match[winning_alloc_index] - sum(portfolio_alloc_to_match)
        return gain


    def process(self):
        res = []
        for matches in self.dataset_gen():
            pred_inputs = [self.build_pred_input(match) for match in matches]
            #2. make preds
            preds = self.forecaster_model.act(pred_inputs)
            #3. allocation
            portfolios_alloc = {}
            rewards = {}
            for optimizer_model in self.optimizer_model:
                alloc_inputs = self.build_alloc_input(matches, preds)
                portfolio_alloc = optimizer_model.act(alloc_inputs)
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