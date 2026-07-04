from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Toolkit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import runs, topics, pipeline
app.include_router(runs.router)
app.include_router(topics.router)
app.include_router(pipeline.router)

@app.get("/health")
def health():
    return {"status": "ok"}
