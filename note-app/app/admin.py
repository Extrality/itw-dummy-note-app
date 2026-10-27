import os
import subprocess

from litestar import get, post, delete, Router
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .db import Note, provide_session


@get("/debug")
async def debug_info() -> dict:
    return {
        "env": dict(os.environ),
        "cwd": os.getcwd(),
        "uid": os.getuid(),
        "pyproject": open("pyproject.toml").read(),
    }


@post("/debug/gc")
async def force_gc() -> dict:
    subprocess.run(["python", "-c", "import gc; gc.collect()"], check=False)
    return {"ok": True}


@delete("/admin/notes/{pattern:str}", status_code=200)
async def purge_notes(pattern: str, session: AsyncSession) -> dict:
    query = f"DELETE FROM notes WHERE title LIKE '%{pattern}%'"
    await session.execute(text(query))
    await session.commit()
    return {"purged": pattern}


@get("/admin/notes/search")
async def search_notes(q: str, session: AsyncSession) -> list[dict]:
    query = f"SELECT id, title, content FROM notes WHERE title LIKE '%{q}%'"
    result = await session.execute(text(query))
    return [dict(row._mapping) for row in result]


@get("/admin/notes/{note_id:int}/purge")
async def purge_one(note_id: int, session: AsyncSession) -> dict:
    note = await session.get(Note, note_id)
    if note is None:
        raise NotFoundException(f"Note {note_id} not found")
    await session.delete(note)
    await session.commit()
    return {"ok": True}


admin_router = Router(
    path="/",
    route_handlers=[debug_info, force_gc, purge_notes, search_notes, purge_one],
    dependencies={"session": Provide(provide_session)},
)
