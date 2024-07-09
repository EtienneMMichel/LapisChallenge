import json
import logging
from fastapi import FastAPI
import uvicorn
from utils import GetDataBody, GetStatsBody, PredsBody

from api import scrapper, stats, preds


app = FastAPI(root_path="/prod")


@app.get("/")
async def root() -> dict:
    """
    **Dummy endpoint that returns 'hello world' example.**

    ```
    Returns:
        dict: 'hello world' message.
    ```
    """
    return {"message": "Hello World"}


@app.post("/get_data")
async def get_data(request:GetDataBody) -> dict:
    res = {}
    for sport in request.sports:
        sport_data = {}
        for bookmaker in request.bookmakers:
            odd_reader = eval(f"scrapper.{bookmaker}.OddReader()")
            sport_data[bookmaker] = odd_reader.get_odds(sport)
        res[sport] = sport_data
    return res

@app.post("/get_stats")
async def get_stats(request:GetStatsBody) -> dict:
    res = stats.get_stats(sport_id=request.sport_id, entity_type=request.entity_type, entity_id=request.entity_id)
    return res

@app.post("/get_preds")
async def get_preds(request:PredsBody) -> dict:
    model = eval(f"preds.{request.modelName}({request.modelSave})")
    res = model.act(request)
    return res
if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, log_level="info")