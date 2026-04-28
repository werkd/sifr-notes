from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import Note, Tag, User


router = APIRouter(tags=["tags"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{tag_name}", response_class=HTMLResponse)
async def notes_by_tag(
    tag_name: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tag_result = await db.execute(
        select(Tag).where(Tag.name == tag_name, Tag.user_id == user.id)
    )

    tag = tag_result.scalar_one_or_none()

    if tag is None:
        return RedirectResponse(url="/notes/", status_code=303)

    notes_result = await db.execute(
        select(Note)
        .where(Note.user_id == user.id)
        # .join(Note.note_tags)
        .where(Note.note_tags.any(tag_id=tag.id))
        .options(selectinload(Note.tags))
        .order_by(Note.updated_at.desc())
    )

    notes = notes_result.scalars().all()

    all_tags_result = await db.execute(
        select(Tag)
        .where(Tag.user_id == user.id)
        .order_by(Tag.name)
    )
    all_tags = all_tags_result.scalars().all()

    return templates.TemplateResponse(
        request,
        "notes/list.html",
        {
            "notes":notes,
            "all_tags": all_tags,
            "filter_tag": tag_name,
            },
    )