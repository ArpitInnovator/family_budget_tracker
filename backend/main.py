from fastapi import FastAPI
from routes import auth , users, categories, transactions, dashboard
from database import Base, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
app = FastAPI(title="Family Budget Tracker Backend" , lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Welcome to Family Budget Tracker"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)

