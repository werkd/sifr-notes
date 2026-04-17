from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
    create_session_token,
    verify_password
)
from app.database import get_db
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "login.html",
        { "error": None})
    return response

@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request, 
    username: str = Form(...),
    password: str = Form(...), 
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username==username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid username or Password."},
            status_code=401,
        )

    token = create_session_token(user.id)
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=SESSION_MAX_AGE,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return response

