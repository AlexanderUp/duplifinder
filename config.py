"""Duplifinder configurations."""
import logging
import os
from hashlib import (
    md5,
    sha1,
    sha3_224,
    sha3_256,
    sha3_384,
    sha3_512,
    sha224,
    sha256,
    sha384,
    sha512,
)
from typing import Callable, Union

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging_handler = logging.StreamHandler()
formatter = logging.Formatter(fmt='[%(levelname)s] %(message)s')

logging_handler.setFormatter(formatter)
logger.addHandler(logging_handler)


class Config:
    BLOCK_SIZE: int = 1024 * 1024  # one megabyte
    MEDIA_EXTENSIONS: set[str] = {
        '.avi',
        '.mp3',
        '.mp4',
        '.mkv',
        '.webm',
        '.mpg',
        '.jpg',
        '.png',
    }
    DOCS_EXTENSIONS: set[str] = {
        '.pdf',
        '.doc',
        '.docx',
        '.xls',
        '.xlsx',
        '.numbers',
        '.pages',
        '.djvu',
        '.djv',
        '.txt',
        '.epub',
        '.png',
        '.jpg',
        '.gif',
        '.zip',
        '.rar',
    }
    TRASHBIN = os.path.expanduser('~/.Trash')
    DB_NAME = 'hash_db.sqlite3'
    DB_BACKUP_NAME_PATTERN = '{0}_backup_{1}_{2}_{3}_{4}_{5}'
    BACKUP_MAX_NUMBER = 5


class TestConfig(Config):
    TEST_FOLDER: str = '~/Desktop/Python - my projects/duplifinder_test_folder'


class HashSpeedTestConfig(Config):
    TEST_FOLDER: str = '~/Downloads/stp'
    BLOCK_SIZE: int = 1024  # one kbyte
    HASH_ALGOS: tuple[Callable, ...] = (
        md5,
        sha1,
        sha224,
        sha256,
        sha384,
        sha512,
        sha3_224,
        sha3_256,
        sha3_384,
        sha3_512,
    )
    SIZES: dict[Union[int, None], str] = {
        1024: '1 Kbyte',
        1048576: '1 Mbyte',
        5242880: '5 Mbyte',
        10485760: '10 Mbyte',
        None: 'Entire file',
    }
    # one kbyte, one mbyte, five mbyte, ten mbyte, entire file
    BLOCK_SIZES: tuple[Union[int, None], ...] = (
        1024,
        1024**2,
        1024**2 * 5,
        1024**2 * 10,
        None,
    )
