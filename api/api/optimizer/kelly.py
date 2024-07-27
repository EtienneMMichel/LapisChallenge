import numpy as np
import cvxpy as cp


class Kelly():
    def __init__(self) -> None:
        self.name = "kelly"


    def allocation(self, odds, probs):
        w = cp.Variable(len(odds), nonneg=True)
        O = np.array([odds for _ in range(len(odds))])
        obj_f = cp.sum(probs@cp.log(O@w))
        obj = cp.Maximize(obj_f)
        constraints = [sum(w) == 1, w>=0]
        prob = cp.Problem(obj, constraints)

        prob.solve()
        if prob.status == "optimal" and sum(np.array(w.value)) <= 1:
            allocations = np.round(np.array(w.value),decimals=3)
                
        else:
            allocations = np.zeros(len(odds))
        return allocations
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
            
