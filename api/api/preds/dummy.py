from .base_model import PredBaseModel
from utils import PredsBody
import numpy as np

NB_MATCH_ISSUES = 3 # will change according to the sport


class Dummy(PredBaseModel):
    def __init__(self, model_save = None):
        if not model_save is None:
            # load saved model
            pass
        super(Dummy, self).__init__()

    def get_data(self, raw_data):
        return raw_data
    
    def preds(self, data):
        preds = np.random.rand(NB_MATCH_ISSUES).tolist()
        s = sum(preds)
        return [pred/s for pred in preds]

    def act(self, pred_inputs):
        pred_inputs = ([pred_inputs] if type(pred_inputs) is PredsBody else pred_inputs)
        preds = []
        for pred_input in pred_inputs:
            raw_data = self.retrieve_data(pred_input)
            data = self.get_data(raw_data)
            preds.append(self.preds(data))
        return preds