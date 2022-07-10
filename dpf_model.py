'''Database model for duplifinder.'''

import os

from sqlalchemy import Boolean, Column, Integer, MetaData, String, Table

metadata = MetaData()


table_hashes = Table('hashes', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('hash', String, nullable=False),
                     Column('path', String, unique=True, nullable=False),
                     Column('creation_time', Integer, nullable=False),
                     Column('is_deleted', Boolean, default=False,
                            nullable=False),
                     )


class FileHash():
    '''Represents FileHash entry.'''

    def __init__(self,
                 hash: str,
                 path: str,
                 creation_time: float,
                 ) -> None:
        self.hash = hash
        self.path = path
        self.creation_time = creation_time
        self.is_deleted = False

    def __repr__(self) -> str:
        path: str = os.path.basename(self.path)
        return (f'<Hash: {self.hash}'
                f', creation time: {self.creation_time}'
                f', path: {path}>')