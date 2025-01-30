import os
from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/v1")
async def message():
    return { "H e l l o  W o r l d "}


GITHUB_URL = "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/heatmap-rvp-death.geojson"
@app.get("/api/v1/github/accident/heatmap-rvp-death")
async def geojson_from_github_heatmap_rvp_death():
    response = requests.get(GITHUB_URL)
    return response.json()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT
    uvicorn.run(app, host="0.0.0.0", port=port)


