from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import models
from app.routers import auth, notes, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")


app.include_router(auth.router, prefix="/auth")
app.include_router(notes.router, prefix="/notes")
app.include_router(tags.router, prefix="/tags")


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/health")
async def health():
    return {"status": "ok"}