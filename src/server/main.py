from fastapi import FastAPI
from src.server.routes import router as api_router

app = FastAPI()

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "MCP Server is running"}
