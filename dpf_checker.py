import os
import shutil
import sys
from time import perf_counter
from typing import Union

from sqlalchemy.orm import Query

from config import Config
from dpf_aux import get_hash, get_session
from dpf_model import FileHash

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
        self._size_processed = 0

    def get_human_readable_size(self):
        '''Convert size of processed files in Mb.'''
        return self._size_processed / 1024 / 1024

    def check(self) -> None:
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension not in self.extensions:
                    continue

                path_to_file: str = os.path.join(root, file)
                hash: str = get_hash(path_to_file,
                                     block_size=config.BLOCK_SIZE)
                self._size_processed += os.path.getsize(path_to_file)

                is_exists: Union[Query, None] = (self.session
                                                     .query(FileHash.hash)
                                                     .filter_by(hash=hash)
                                                     .first())

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
    gigabytes_processed = checker.get_human_readable_size()

    print(f'Time elapsed: {elapsed}')
    print('Total processed:', gigabytes_processed, 'Mb')
    print('Avarage hashing speed:', gigabytes_processed / elapsed, 'Mb/second (hashlib.sha256)')
    print('>> NB! Calculated speed affected by db quering overhead! <<')

    print('-' * 125)
