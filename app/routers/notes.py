from datetime import datetime, timezone

import markdown as md

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.models import Note, NoteTag, Tag, User
from app.utils import parse_tags


router = APIRouter(tags=["notes"])
templates = Jinja2Templates(directory="app/templates")

MD_EXTENSIONS = ["fenced_code", "tables", "nl2br"]


def render_markdown(raw: str) -> str:
    return md.markdown(raw, extensions=MD_EXTENSIONS)


async def _get_note_or_404(note_id: int, user: User, db: AsyncSession) -> Note:
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id, Note.user_id == user.id)
        .options(selectinload(Note.tags))
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found. ")
    return note


async def sync_tags(note_id: int, tag_names: list[str], user_id: int, db: AsyncSession) -> None:
    """Replace all tags on a note. Deletes existing onces and inserts fresh NoteTag rows."""
    await db.execute(sa_delete(NoteTag)
                     .where(NoteTag.note_id == note_id))
    for name in tag_names:
        result = await db.execute(
            select(Tag)
            .where(Tag.name == name, Tag.user_id == user_id)
        )
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(name=name, user_id=user_id)
            db.add(tag)
            await db.flush()

        db.add(NoteTag(note_id=note_id, tag_id=tag.id))


# GET /notes LIST
@router.get("/", response_class=HTMLResponse)
async def list_notes(
        request: Request,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user.id)
        .order_by(Note.updated_at.desc())
        .options(selectinload(Note.tags))
    )
    # result = await db.execute(
    #     select(Note).where(Note.user_id==user.id).order_by(Note.updated_at.desc())
    # )
    notes = result.scalars().all()

    tags_result = await db.execute(
        select(Tag)
        .where(Tag.user_id == user.id)
        .order_by(Tag.name)
    )
    all_tags = tags_result.scalars().all()

    return templates.TemplateResponse(
        request,
        "notes/list.html",
        {"notes": notes, "user": user, "all_tags": all_tags},
    )



# GET /notes/new - empty create form
@router.get("/new", response_class=HTMLResponse)
async def new_note_form(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        "notes/form.html",
        {"user": user},
    )


# GET /notes{note_id} DETAIL
@router.get("/{note_id}", response_class=HTMLResponse)
async def note_detail(
    note_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = await _get_note_or_404(note_id, user, db)
    return templates.TemplateResponse(
        request,
        "notes/detail.html",
        {"note": note, "user": user},
    )

# POST /notes CREATE
@router.post("/", response_class=HTMLResponse)
async def create_note(
    title: str = Form(...),
    body: str = Form(...),
    tags: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    ):
    note = Note(
        title=title,
        body=body,
        body_rendered=render_markdown(body),
        user_id=user.id,
    )
    db.add(note)
    await db.flush()

    tag_names = parse_tags(tags)
    if tag_names:
        await sync_tags(note.id, tag_names, user.id, db)

    await db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


# POST /notes/{note_id}/edit UPDATE
@router.post("/{note_id}/edit", response_class=HTMLResponse)
async def edit_note(
        note_id: int,
        title: str = Form(...),
        body: str = Form(...),
        tags: str = Form(default=""),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    note = await _get_note_or_404(note_id, user, db)
    note.title = title
    note.body = body
    note.body_rendered = render_markdown(body)

    await sync_tags(note.id, parse_tags(tags), user.id, db)

    await db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)

# POST /notes/{note_id}/delete
@router.post("/{note_id}/delete", response_class=HTMLResponse)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = await _get_note_or_404(note_id, user, db)
    await db.delete(note)
    await db.commit()
    return RedirectResponse(url="/notes/", status_code=303)



# GET /{notes_id}/edit - fetch and render form to edit
@router.get("/{note_id}/edit",response_class=HTMLResponse)
async def edit_note_form(
    note_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = await _get_note_or_404(note_id, user, db)
    return templates.TemplateResponse(
        request,
        name="notes/form.html",
        context={"note": note, "user": user},
    )


# @router.get("/")
# async def notes_stub():
#     return {"status": "notes router is live."}