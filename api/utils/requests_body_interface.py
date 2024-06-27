from pydantic import BaseModel

class GetDataBody(BaseModel):
    sports:list[str]
    bookmakers: list[str]