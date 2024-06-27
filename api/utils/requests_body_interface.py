from pydantic import BaseModel

class GetDataBody(BaseModel):
    sports:list[str]
    bookmakers: list[str]

class GetStatsBody(BaseModel):
    sport_id:str
    entity_type:str
    entity_id: str