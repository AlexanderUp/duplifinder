'''Duplicate checker.'''

import os
import shutil
import sys
from time import perf_counter

from sqlalchemy.orm import mapper

from config import Config
from dpf_aux import get_hash, get_session
from dpf_model import FileHash, table_hashes

mapper(FileHash, table_hashes)

config = Config()


class DpfChecker():

    def __init__(self,
                 path_to_db: str,
                 folder: str,
                 extensions: set) -> None:
        self._path_to_db = path_to_db
        self.folder = folder
        self.extensions = extensions
        self.session = get_session(self._path_to_db)

    def check(self) -> None:
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension not in self.extensions:
                    continue

                path_to_file: str = os.path.join(
                    root, file
                )
                hash: str = get_hash(path_to_file,
                                     block_size=config.BLOCK_SIZE)
                is_exists: tuple = (self.session
                                        .query(FileHash.hash)
                                        .filter_by(hash=hash)
                                        .one_or_none())
                if is_exists:
                    print(f'>>> To be deleted: {path_to_file}', end='\t')
                    dest_trashbin_path: str = os.path.join(config.TRASHBIN,
                                                           file)
                    try:
                        shutil.move(path_to_file, dest_trashbin_path)
                    except OSError as err:
                        print('Error occured!')
                        print(err)
                    else:
                        print('=== Deleted! ===')
                else:
                    print(f'*** New file: {path_to_file}')
        print('>>>>>> Check completed! <<<<<<')


if __name__ == '__main__':
    print('*' * 125)

    path_to_db = sys.argv[1]
    folder = os.path.dirname(path_to_db)
    print(f'DB: {path_to_db}')
    print(f'Folder: {folder}')

    checker = DpfChecker(path_to_db, folder, config.MEDIA_EXTENSIONS)
    start = perf_counter()
    checker.check()
    elapsed = perf_counter() - start
    print(f'Time elapsed: {elapsed}')

    print('-' * 125)
