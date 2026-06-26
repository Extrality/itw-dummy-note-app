from dataclasses import dataclass
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from litestar import post, put, delete, get, Router
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ValidationException

from .db import Note, provide_session


@dataclass
class NoteCreate:
    title: str
    content: str = ""


@dataclass
class NoteUpdate:
    title: Optional[str] = None
    content: Optional[str] = None


@dataclass
class NoteResponse:
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str


def note_to_dict(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat() if note.created_at else "",
        "updated_at": note.updated_at.isoformat() if note.updated_at else "",
    }


@get("/")
async def list_notes(session: AsyncSession) -> list[NoteResponse]:
    result = await session.execute(select(Note).order_by(Note.created_at.desc()))
    return [note_to_dict(note) for note in result.scalars().all()]


@post("/", status_code=201)
async def create_note(data: NoteCreate, session: AsyncSession) -> NoteResponse:
    note = Note(title=data.title, content=data.content or "")
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note_to_dict(note)


@get("/{id:int}")
async def get_note(id: int, session: AsyncSession) -> NoteResponse:
    result = await session.execute(select(Note).where(Note.id == id))
    note = result.scalar_one_or_none()
    if note is None:
        raise NotFoundException(f"Note {id} not found")
    return note_to_dict(note)


@put("/{id:int}")
async def update_note(id: int, data: NoteUpdate, session: AsyncSession) -> NoteResponse:
    result = await session.execute(select(Note).where(Note.id == id))
    note = result.scalar_one_or_none()
    if note is None:
        raise NotFoundException(f"Note {id} not found")

    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content

    if data.title is None and data.content is None:
        raise ValidationException("No fields to update")

    await session.commit()
    await session.refresh(note)
    return note_to_dict(note)


@delete("/{id:int}", status_code=204)
async def delete_note(id: int, session: AsyncSession) -> None:
    result = await session.execute(select(Note).where(Note.id == id))
    note = result.scalar_one_or_none()
    if note is None:
        raise NotFoundException(f"Note {id} not found")
    await session.delete(note)
    await session.commit()


@dataclass
class FetchUrlRequest:
    url: str


@dataclass
class FetchUrlResponse:
    content: str


@post("/fetch-url")
async def fetch_url(data: FetchUrlRequest) -> FetchUrlResponse:
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    transport = httpx.AsyncHTTPTransport(verify=ssl_context)
    async with httpx.AsyncClient(transport=transport, follow_redirects=True, timeout=30) as client:
        resp = await client.get(data.url)
    return FetchUrlResponse(content=resp.text)


note_router = Router(
    path="/notes",
    route_handlers=[
        list_notes,
        create_note,
        get_note,
        update_note,
        delete_note,
        fetch_url,
    ],
    dependencies={"session": Provide(provide_session)},
)
