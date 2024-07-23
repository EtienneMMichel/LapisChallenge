from utils import AllocBody
import numpy as np

class Dummy():
    def __init__(self) -> None:
        self.name = "dummy"

    def act(self, inputs:AllocBody):
        """
        alloc: [match_1, match_2, ...]
        match_i : [team_1, team_2, team_null]
        """
        odds = np.array(inputs.odds)
        odds_flatten = odds.flatten()
        alloc = np.random.rand(len(odds_flatten))
        alloc = alloc/sum(alloc)
        alloc = alloc.reshape(odds.shape)
        return alloc.tolist()
            
