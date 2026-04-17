from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import models
from app.auth import NotAuthenticatedException, get_current_user
from app.routers import auth, notes, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")


app.include_router(auth.router, prefix="/auth")
app.include_router(notes.router, prefix="/notes", dependencies=[Depends(get_current_user)])
app.include_router(tags.router, prefix="/tags", dependencies=[Depends(get_current_user)])


@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_handler(
    request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url="/auth/login", status_code=302)

@app.get("/health")
async def health():
    return {"status": "ok"}
