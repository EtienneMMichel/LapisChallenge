from .base_model import PredBaseModel


class Dummy(PredBaseModel):
    def __init__(self, model_save = None):
        if not model_save is None:
            # load saved model
            pass
        super(Dummy, self).__init__()

    def get_data(self, raw_data):
        return raw_data
    
    def preds(self, data):
        return {}

    def act(self, request_data):
        raw_data = self.retrieve_data(request_data)
        data = self.get_data(raw_data)
        preds = self.preds(data)
        return preds