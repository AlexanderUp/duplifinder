"""Models for Duplifinder."""
import os


class FileHash:
    """Represents FileHash entry."""

    def __init__(self, file_hash: str, path: str, creation_time: float) -> None:
        self.file_hash: str = file_hash
        self.path: str = path
        self.creation_time: float = creation_time
        self.is_deleted: bool = False

    def __repr__(self) -> str:
        path: str = os.path.basename(self.path)
        return '<Hash: {0}, creation time: {1}, path: {2}>'.format(
            self.file_hash,
            self.creation_time,
            path,
        )
