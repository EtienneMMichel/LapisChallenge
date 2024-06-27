import json
import logging
from fastapi import FastAPI
import uvicorn
from utils import GetDataBody

from api import scrapper


app = FastAPI(root_path="/prod")
# register_all_models()


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

if __name__ == "__main__":
    
    uvicorn.run("app:app", port=5000, log_level="info")