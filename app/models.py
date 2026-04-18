from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
    )
from sqlalchemy.orm import relationship as Relationship
from app.database import Base


def now_utc():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    notes = Relationship("Note", back_populates="user", cascade="all, delete-orphan")
    tags = Relationship("Tag", back_populates="user", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    body = Column(Text, nullable=False, default="")
    body_rendered = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = Relationship("User", back_populates="notes")
    note_tags = Relationship("NoteTag", back_populates="note", cascade="all, delete-orphan")
    tags = Relationship("Tag", secondary="note_tags", back_populates="notes", viewonly=True)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = Relationship("User", back_populates="tags")
    note_tags = Relationship('NoteTag', back_populates="tag", cascade="all, delete-orphan")
    notes = Relationship("Note",secondary="note_tags", back_populates="tags", viewonly=True)

    __table_args__ = (
        UniqueConstraint("name", "user_id"),
    )


class NoteTag(Base):
    __tablename__ = "note_tags"
    
    note_id = Column(Integer, ForeignKey("notes.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    note = Relationship("Note", back_populates="note_tags")
    tag = Relationship("Tag", back_populates="note_tags")

