from utils import PickerBody
import numpy as np
from operator import mul
from functools import reduce

NB_COMBS = 4

class Dummy():
    def __init__(self) -> None:
        self.name = "dummy"

    
    def select_combs(self, odds_flatten, preds_flatten):
        nb_combs = NB_COMBS
        return np.random.randint(0,2, size=(nb_combs, len(odds_flatten)))

    def act(self, inputs:PickerBody):
        """
        return: [{"comb":[0,1,0,0,1], "prob":0.3, "odd":3.5 }]
        """
        odds = np.array(inputs.odds)
        odds_flatten = odds.flatten()

        preds = np.array(inputs.preds)
        preds_flatten = preds.flatten()

        combs = self.select_combs(odds_flatten, preds_flatten)

        res = []
        for comb in combs:
            res.append({
                "comb":comb.tolist(),
                "odd": reduce(mul, list(filter(lambda o:  o > 0, np.multiply(comb, odds_flatten).tolist()))), 
                "prob": reduce(mul, list(filter(lambda o:  o > 0, np.multiply(comb, preds_flatten).tolist()))) 
            })
        return res
            

        # alloc = np.random.rand(len(odds_flatten))
        # alloc = alloc/sum(alloc)
        # alloc = alloc.reshape(odds.shape)
        # return alloc.tolist()
            
