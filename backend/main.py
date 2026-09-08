from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Energy-Aware Planner API"}

