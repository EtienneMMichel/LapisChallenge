import numpy as np

class Dummy():
    def __init__(self) -> None:
        self.name = "dummy"


    def allocation(self, odds, probs):
        alloc = np.random.rand(len(odds))
        alloc = alloc/sum(alloc)
        return alloc.tolist()
    def act(self, inputs):
        """
        inputs: [{"comb":[0,1,0,0,1], "prob":0.3, "odd":3.5 }, ]
        alloc: [{"comb":[0,1,0,0,1], "prob":0.3, "odd":3.5 , "alloc": 0.1}, ]
        """
        odds = np.array([comb["odd"] for comb in inputs])
        probs = np.array([comb["prob"] for comb in inputs])
        
        allocs = self.allocation(odds, probs)
        res = []
        for comb, alloc in zip(inputs, allocs):
            comb["alloc"] = alloc
            res.append(comb)
        return res
            
