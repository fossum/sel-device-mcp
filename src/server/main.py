from fastapi import FastAPI

from .routes import router as api_router

app = FastAPI()

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "MCP Server is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
