import os
import shutil
import sys
from time import perf_counter
from typing import Union

from sqlalchemy.orm import Query

from config import Config, logger
from dpf_aux import get_hash, get_human_readable_size, get_session
from models.dpf_models import FileHash

config = Config()


class DpfChecker:
    def __init__(self, session, folder: str, extensions: set) -> None:
        self.session = session
        self.folder = folder
        self.extensions = extensions
        self.size_processed = 0

    def check(self) -> None:
        for root, _, files in os.walk(self.folder):
            for data_file in files:
                _, extension = os.path.splitext(data_file)
                if extension not in self.extensions:
                    continue

                path_to_file: str = os.path.join(root, data_file)
                file_hash: str = get_hash(path_to_file, block_size=config.BLOCK_SIZE)
                self.size_processed += os.path.getsize(path_to_file)

                is_exists: Union[Query, None] = self.session.query(FileHash.file_hash).filter_by(file_hash=file_hash).first()

                if is_exists:
                    dest_trashbin_path: str = os.path.join(config.TRASHBIN, data_file)
                    try:
                        shutil.move(path_to_file, dest_trashbin_path)
                    except OSError as err:
                        logger.error(err)
                    else:
                        logger.info(f">>> Deleted: {path_to_file}")
                else:
                    logger.info(f"*** New file: {path_to_file}")
        logger.info(">>>>>> Check completed! <<<<<<")


if __name__ == "__main__":
    path_to_db = sys.argv[1]
    session = get_session(path_to_db)
    folder = os.path.dirname(path_to_db)

    logger.info(f"DB: {path_to_db}")
    logger.info(f"Folder: {folder}")
    logger.info("Hash algo used: hashlib.sha256")

    checker = DpfChecker(session, folder, config.MEDIA_EXTENSIONS)

    start = perf_counter()
    checker.check()

    elapsed = perf_counter() - start
    megabytes_processed = get_human_readable_size(checker.size_processed)

    logger.info(f"Time elapsed: {elapsed} seconds")
    logger.info(f"Total processed: {megabytes_processed} Mb")
    logger.info(
        "Avarage hashing speed: {0} Mb/second".format(megabytes_processed / elapsed),
    )
    logger.info("NB! Calculated speed affected by db quering overhead!")
