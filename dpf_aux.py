'''Auxiliary functions for <dpf.py>.'''

import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import dpf_model as dbm


def get_session(path_to_db: str, model=dbm):
    engine = create_engine('sqlite:///' + path_to_db)
    model.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_hash(file: str, block_size: int) -> str:
    with open(file, 'br') as f:
        hasher = hashlib.sha256()
        while True:
            binary_content: bytes = f.read(block_size)
            if not binary_content:
                break
            hasher.update(binary_content)
    return hasher.hexdigest()
