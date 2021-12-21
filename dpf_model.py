# encoding:utf-8
# database model for duplifinder


from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


import os


metadata = MetaData()


table_hashes = Table('hashes', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('hash', String, nullable=False),
                    Column('path', String, unique=True, nullable=False),
                    Column('creation_time', Integer, nullable=False),
                    )


class HashTable():

    def __init__(self, hash, path, creation_time):
        self.hash = hash
        self.path = path
        self.creation_time = creation_time

    def __repr__(self):
        return f'<File(Hash: {self.hash}, creation time: {self.creation_time}, path: {os.path.basename(self.path)})>'
