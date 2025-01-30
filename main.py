import os
from fastapi import FastAPI


app = FastAPI()
security = HTTPBearer()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/api/v1", tags=["Docs"])
async def message():
    return { "H e l l o  W o r l d "}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
