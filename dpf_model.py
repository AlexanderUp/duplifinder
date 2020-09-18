# encoding:utf-8
# database model for duplifinder


from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


metadata = MetaData()

table_hashes = Table('hashes', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('hash', String, nullable=False),
                    Column('path', String, unique=True, nullable=False),
                    )


class HashTable():

    def __init__(self, hash, path):
        self.hash = hash
        self.path = path

    def get_file_name(self):
        pass

    def get_file_folder(self):
        pass
