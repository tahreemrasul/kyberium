"""Image blob storage. Keys look like 'uploads/<owner>/<uuid>.jpg'."""

import asyncio
import re
from pathlib import Path
from typing import Protocol

_KEY = re.compile(r"^[a-z]+/[A-Za-z0-9_-]{1,64}/[A-Za-z0-9_-]{1,64}\.(jpg|png|webp|svg)$")


def check_key(key: str) -> None:
    if not _KEY.match(key):
        raise ValueError(f"invalid blob key: {key!r}")


class BlobStore(Protocol):
    async def put(self, key: str, data: bytes, content_type: str) -> None: ...
    async def get(self, key: str) -> tuple[bytes, str] | None: ...
    async def delete(self, key: str) -> None: ...


class LocalBlobStore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        check_key(key)
        return self.root / key

    async def put(self, key: str, data: bytes, content_type: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.with_name(path.name + ".ct").write_text(content_type)

    async def get(self, key: str) -> tuple[bytes, str] | None:
        path = self._path(key)
        if not path.exists():
            return None
        ct_path = path.with_name(path.name + ".ct")
        ct = ct_path.read_text() if ct_path.exists() else "application/octet-stream"
        return path.read_bytes(), ct

    async def delete(self, key: str) -> None:
        path = self._path(key)
        path.unlink(missing_ok=True)
        path.with_name(path.name + ".ct").unlink(missing_ok=True)


class GcsBlobStore:
    def __init__(self, bucket: str, project: str | None) -> None:
        from google.cloud import storage

        self._bucket = storage.Client(project=project).bucket(bucket)

    async def put(self, key: str, data: bytes, content_type: str) -> None:
        check_key(key)
        blob = self._bucket.blob(key)
        await asyncio.to_thread(blob.upload_from_string, data, content_type=content_type)

    async def get(self, key: str) -> tuple[bytes, str] | None:
        check_key(key)
        from google.api_core.exceptions import NotFound

        blob = self._bucket.blob(key)
        try:
            data = await asyncio.to_thread(blob.download_as_bytes)
        except NotFound:
            return None
        return data, blob.content_type or "application/octet-stream"

    async def delete(self, key: str) -> None:
        check_key(key)
        from google.api_core.exceptions import NotFound

        try:
            await asyncio.to_thread(self._bucket.blob(key).delete)
        except NotFound:
            pass
