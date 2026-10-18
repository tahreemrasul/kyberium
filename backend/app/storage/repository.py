"""Owner-scoped JSON document store.

Collections used by the app: garments, uploads, inspirations, generations,
saved_looks, analysis_cache. Documents are plain JSON-able dicts; callers
validate them into Pydantic models. Every method requires the owner id, so
there is no API for reading across owners.
"""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Protocol

_SAFE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def _check(*parts: str) -> None:
    for p in parts:
        if not _SAFE.match(p):
            raise ValueError(f"unsafe storage key: {p!r}")


class Repository(Protocol):
    async def get(self, owner: str, collection: str, doc_id: str) -> dict[str, Any] | None: ...
    async def put(self, owner: str, collection: str, doc_id: str, data: dict[str, Any]) -> None: ...
    async def delete(self, owner: str, collection: str, doc_id: str) -> bool: ...
    async def list(self, owner: str, collection: str) -> list[dict[str, Any]]: ...


class LocalRepository:
    """One JSON file per (owner, collection). Fine for dev, tests and demos."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._locks: dict[str, asyncio.Lock] = {}

    def _path(self, owner: str, collection: str) -> Path:
        _check(owner, collection)
        return self.root / owner / f"{collection}.json"

    def _lock(self, path: Path) -> asyncio.Lock:
        return self._locks.setdefault(str(path), asyncio.Lock())

    def _read(self, path: Path) -> dict[str, dict[str, Any]]:
        if not path.exists():
            return {}
        return json.loads(path.read_text("utf-8"))

    def _write(self, path: Path, data: dict[str, dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, default=str), "utf-8")
        os.replace(tmp, path)

    async def get(self, owner: str, collection: str, doc_id: str) -> dict[str, Any] | None:
        _check(doc_id)
        path = self._path(owner, collection)
        async with self._lock(path):
            return self._read(path).get(doc_id)

    async def put(self, owner: str, collection: str, doc_id: str, data: dict[str, Any]) -> None:
        _check(doc_id)
        path = self._path(owner, collection)
        async with self._lock(path):
            docs = self._read(path)
            docs[doc_id] = json.loads(json.dumps(data, default=str))
            self._write(path, docs)

    async def delete(self, owner: str, collection: str, doc_id: str) -> bool:
        _check(doc_id)
        path = self._path(owner, collection)
        async with self._lock(path):
            docs = self._read(path)
            existed = docs.pop(doc_id, None) is not None
            if existed:
                self._write(path, docs)
            return existed

    async def list(self, owner: str, collection: str) -> list[dict[str, Any]]:
        path = self._path(owner, collection)
        async with self._lock(path):
            return list(self._read(path).values())


class FirestoreRepository:
    """Documents at owners/{owner}/{collection}/{doc_id}."""

    def __init__(self, project: str | None, database: str = "(default)") -> None:
        from google.cloud import firestore

        self._client = firestore.AsyncClient(project=project, database=database)

    def _col(self, owner: str, collection: str):
        _check(owner, collection)
        return self._client.collection("owners").document(owner).collection(collection)

    async def get(self, owner: str, collection: str, doc_id: str) -> dict[str, Any] | None:
        _check(doc_id)
        snap = await self._col(owner, collection).document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    async def put(self, owner: str, collection: str, doc_id: str, data: dict[str, Any]) -> None:
        _check(doc_id)
        await self._col(owner, collection).document(doc_id).set(json.loads(json.dumps(data, default=str)))

    async def delete(self, owner: str, collection: str, doc_id: str) -> bool:
        _check(doc_id)
        ref = self._col(owner, collection).document(doc_id)
        snap = await ref.get()
        if not snap.exists:
            return False
        await ref.delete()
        return True

    async def list(self, owner: str, collection: str) -> list[dict[str, Any]]:
        return [d.to_dict() async for d in self._col(owner, collection).stream()]
