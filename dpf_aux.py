"""Auxiliary functions for duplifinder."""

import fnmatch
import hashlib
import os
import shutil
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config, logger
from dpf_db_tables import mapper_registry

config = Config()


def get_session(path_to_db: str, mapper=mapper_registry):
    engine = create_engine(f"sqlite:///{path_to_db}")
    mapper.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_hash(source_file: str, block_size: int) -> str:
    with open(source_file, "br") as source:
        hasher = hashlib.sha256()
        while True:
            binary_content: bytes = source.read(block_size)
            if not binary_content:
                break
            hasher.update(binary_content)
    return hasher.hexdigest()


def get_human_readable_size(size_in_bytes):
    """Convert size of processed files in Mb."""
    return size_in_bytes / 1024 / 1024


def create_db_backup(path_to_db: str) -> None:
    if os.path.exists(path_to_db):
        logger.info("Database already exists! Backuping...")
        time: datetime = datetime.now()
        db_backup_name: str = config.DB_BACKUP_NAME_PATTERN.format(
            config.DB_NAME,
            time.year,
            time.month,
            time.day,
            time.hour,
            time.minute,
        )
        db_folder_path: str = os.path.dirname(path_to_db)
        path_to_db_backup: str = os.path.join(db_folder_path, db_backup_name)

        try:
            shutil.copyfile(path_to_db, path_to_db_backup)
        except OSError as copy_err:
            logger.error(copy_err)
            logger.error("Error during backup creation! Exiting...")
            sys.exit()
        else:
            logger.info("Backup created!")

        backup_file_names: list = fnmatch.filter(
            os.listdir(db_folder_path),
            f"{config.DB_NAME}_backup_*",
        )
        backup_file_names.sort(
            key=lambda backup_file: os.stat(
                os.path.join(db_folder_path, backup_file),
            ).st_birthtime,
        )

        for db_file in backup_file_names[: -config.BACKUP_MAX_NUMBER]:
            try:
                shutil.move(
                    os.path.join(db_folder_path, db_file),
                    os.path.join(config.TRASHBIN, db_file),
                )
            except OSError as move_err:
                logger.error(move_err)
                logger.error("Error during deleting old db backups! Exiting...")
        logger.info("Backups cleared!")
