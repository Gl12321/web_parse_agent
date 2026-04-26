from fastapi import FastAPI
from src.interfaces.api.routes import parse_router
import uvicorn

app = FastAPI(title="Web Parse Agent API")
app.include_router(parse_router, prefix="api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)