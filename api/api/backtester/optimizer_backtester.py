class OptimizerBacktester():
    def __init__(self, forecaster_model, optimizer_model, sport, start_year, end_year, zones=None, competitions=None) -> None:
        self.forecaster_model = forecaster_model
        self.optimizer_model = optimizer_model
        self.sport = sport
        self.start_year = start_year
        self.end_year = end_year
        self.zones = zones
        self.competitions = competitions

    def process(self):
        return {}