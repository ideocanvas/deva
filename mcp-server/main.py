from fastapi import FastAPI

app = FastAPI(title="MCP Server")

@app.get("/")
def read_root():
    return {"message": "Master Control Program for Project Deva is online."}