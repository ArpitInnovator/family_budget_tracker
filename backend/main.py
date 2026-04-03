from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from database import engine

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to Family Budget Tracker"}

Base = declarative_base()
Base.metadata.create_all(engine)