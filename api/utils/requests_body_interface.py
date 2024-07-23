from pydantic import BaseModel

class GetDataBody(BaseModel):
    sports:list[str]
    bookmakers: list[str]

class GetStatsBody(BaseModel):
    sport_id:str
    entity_type:str
    entity_id: str

class PredsBody(BaseModel):
    team_1_id:str
    team_2_id:str
    modelName:str
    others: dict| None = None
    modelSave:str | None = None


class OptiBacktestBody(BaseModel):
    sport:str
    start_year:int
    end_year:int
    forecaster_name:str
    forecaster_save:str | None = None
    optimizers_name:list[str]
    zones: list[str]| None = None
    competitions:list[str] | None = None