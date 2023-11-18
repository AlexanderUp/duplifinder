"""SQLAlchemy tables."""
from sqlalchemy import Boolean, Column, Integer, String, Table
from sqlalchemy.orm import registry

from models.dpf_models import FileHash

mapper_registry = registry()


table_hashes = Table(
    'hashes',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('file_hash', String, nullable=False),
    Column('path', String, unique=True, nullable=False),
    Column('creation_time', Integer, nullable=False),
    Column('is_deleted', Boolean, default=False, nullable=False),
)


mapper_registry.map_imperatively(FileHash, table_hashes)
