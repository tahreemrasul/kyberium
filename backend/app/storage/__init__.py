"""Persistence: a small owner-scoped document store plus a blob store.

``local`` keeps JSON files and images on disk (dev/tests/demo mode).
``gcp`` uses Firestore for documents and Cloud Storage for images.
"""

from functools import lru_cache

from app.config import get_settings
from app.storage.blobs import BlobStore, GcsBlobStore, LocalBlobStore
from app.storage.repository import FirestoreRepository, LocalRepository, Repository

__all__ = ["BlobStore", "Repository", "get_blobs", "get_repo"]


@lru_cache
def get_repo() -> Repository:
    s = get_settings()
    if s.storage_backend == "gcp":
        return FirestoreRepository(project=s.google_cloud_project, database=s.firestore_database)
    return LocalRepository(s.local_data_dir / "owners")


@lru_cache
def get_blobs() -> BlobStore:
    s = get_settings()
    if s.storage_backend == "gcp":
        if not s.gcs_bucket:
            raise RuntimeError("GCS_BUCKET must be set when STORAGE_BACKEND=gcp")
        return GcsBlobStore(bucket=s.gcs_bucket, project=s.google_cloud_project)
    return LocalBlobStore(s.local_data_dir / "blobs")
