'''Find file duplicates in given folder.'''

import argparse
import fnmatch
import os
import shutil
import sys
from datetime import datetime
from typing import Generator

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import mapper

from config import Config
from dpf_aux import get_hash, get_session
from dpf_model import FileHash, table_hashes

mapper(FileHash, table_hashes)

config = Config()


class Duplifinder():
    '''
    Looking for file duplicates in specified folder taking into account
    calculated hash.
    '''

    def __init__(self, path: str, path_to_be_excluded: str) -> None:
        '''
        Current limitations: only one excluded folders supported.
        '''
        if os.path.isdir(path):
            self._path = path
        else:
            raise TypeError('Target path is not specified or is not'
                            'a directory!')

        if path_to_be_excluded is None or os.path.isdir(path_to_be_excluded):
            self._path_to_be_excluded = path_to_be_excluded
        else:
            raise TypeError('Excluded path is not specified or is not'
                            'a directory!')

        self._path_to_db: str = os.path.join(self._path, config.DB_NAME)
        self.session = get_session(self._path_to_db)

    def _create_db_backup(self) -> None:
        if os.path.exists(self._path_to_db):
            print('Database already exists! Backuping...')
            time: datetime = datetime.now()
            db_backup_name: str = config.DB_BACKUP_NAME_PATTERN.format(
                config.DB_NAME, time.year, time.month, time.day, time.hour,
                time.minute)
            path_to_db_backup: str = os.path.join(self._path, db_backup_name)

            try:
                shutil.copyfile(self._path_to_db, path_to_db_backup)
            except OSError as err:
                print(err)
                print('Error during backup creation! Exiting...')
                sys.exit()
            else:
                print('Backup created!')

        backup_file_names: list = fnmatch.filter(os.listdir(self._path),
                                                 f'{config.DB_NAME}_backup_*')
        backup_file_names.sort(
            key=lambda file: os.stat(
                os.path.join(self._path, file)
                ).st_birthtime
            )

        for file in backup_file_names[:-config.BACKUP_MAX_NUMBER]:
            try:
                shutil.move(os.path.join(self._path, file),
                            os.path.join(config.TRASHBIN, file))
            except OSError as err:
                print(err)
                print('Error during deleting old db backups! Exiting...')
        print('Backups cleared!')

    def _clean_up_db(self):
        print('Cleaning database...')
        files: list = self.session.query(FileHash).all()
        for file in files:
            if not os.path.exists(file.path):
                print('File doesn\'t exist! Marking as has been deleted...\t'
                      f'{file.path}')
                file.is_deleted = True
        try:
            self.session.commit()
        except Exception as err:
            print(err)
            self.session.rollback()
            print('DB cleaning failed.')
        else:
            print('Database clean!')

    def set_extensions(self, extensions: set[str]) -> None:
        self._extensions: set[str] = extensions

    def update_db(self) -> None:
        if self._extensions:
            self._create_db_backup()
            for root, dirs, files in os.walk(self._path):
                for file in files:
                    path = os.path.join(root, file)

                    if self._path_to_be_excluded:
                        if os.path.commonpath(
                                (self._path_to_be_excluded,
                                 path)) == self._path_to_be_excluded:
                            print(f'>>>> Excluded: <{path}>')
                            continue

                    _, extention = os.path.splitext(file)
                    extention.lower()
                    if extention not in self._extensions:
                        print('==== Passed! File type is not allowed!'
                              f'<{file}>')
                        continue

                    is_path_to_file_in_db: FileHash = (
                        self.session
                        .query(FileHash)
                        .filter(FileHash.path == path)
                        .first()
                        )
                    if is_path_to_file_in_db:
                        print(f'>>>> Already in db! <{path}>')
                        continue

                    hash: str = get_hash(path, block_size=config.BLOCK_SIZE)
                    creation_time: float = os.stat(path).st_birthtime
                    print(f'******** Adding: <{path}> **** Added!')

                    self.session.add(FileHash(hash, path, creation_time))
                    try:
                        self.session.commit()
                    except Exception as err:
                        print(err)
                        self.session.rollback()
            self._clean_up_db()
        else:
            print('No extensions specified!')
        self.session.close()

    def duplicate_hash_query_generator(self) -> Generator[list, None, None]:
        '''
        Yields list of duplicate enrties (instances of class <FileHash>),
        not a list of hashes itself.
        '''
        duplicate_hash_entities: list[tuple[str]] = (
            self.session
                .query(FileHash.hash)
                .group_by(FileHash.hash)
                .having(func.count(FileHash.hash) > 1)
                .all()
            )
        print(f'Duplicated hashes found: {len(duplicate_hash_entities)}')
        duplicate_hashes = (entity[0] for entity in duplicate_hash_entities)
        print('************************************')
        for duplicate_hash in duplicate_hashes:
            query: list[FileHash] = (
                self.session
                    .query(FileHash)
                    .filter(FileHash.hash == duplicate_hash)
                    .all()
                )
            query.sort(key=lambda duplicate: duplicate.creation_time)
            yield query

    def print_duplicates_list(self) -> None:
        for query in self.duplicate_hash_query_generator():
            for duplicate in query:
                print(f'{duplicate.hash} =>> {duplicate.path}')
            print('************************************')
        self.session.close()

    def remove_duplicates(self):
        for query in self.duplicate_hash_query_generator():
            for duplicate in query[1:]:
                duplicate.is_deleted = True
                try:
                    shutil.move(duplicate.path,
                                os.path.join(config.TRASHBIN,
                                             os.path.basename(duplicate.path)))
                except OSError as err:
                    print(err)
                else:
                    print(f'Deleteted! {duplicate.path}')
        try:
            self.session.commit()
        except SQLAlchemyError as err:
            print(err)
            self.session.rollback()
        else:
            print('Files deleted, db updated.')
        finally:
            self.session.close()


if __name__ == '__main__':
    print('=' * 75)

    parser = argparse.ArgumentParser(
        description='Find file duplicates in given directory'
        )
    parser.add_argument('path_to_be_processed')
    parser.add_argument(
        '-e',
        '--exclude',
        default=None,
        help='Folders to be excluded from processing',
        dest='path_to_be_excluded'
        )
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        '-m',
        '--media',
        action='store_true',
        help='Update database with hashes of media files in given directory'
        )
    type_group.add_argument(
        '-d',
        '--documents',
        action='store_true',
        help=('Update database with hashes of document and'
              'non-media files in given directory')
        )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '-r',
        '--remove_duplicates',
        action='store_true',
        help='Find and delete file duplicates'
        )
    action_group.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='Print list of file duplicates'
        )
    args = parser.parse_args()

    print('Running Duplifinder...')
    print('=' * 25)
    print(f'Target directory: {args.path_to_be_processed}')
    print(f'Excluded directory: {args.path_to_be_excluded}')
    print(f'Media: {args.media}')
    print(f'Documents: {args.documents}')
    print(f'Delete duplicates: {args.remove_duplicates}')
    print(f'Print duplicates list: {args.list}')
    print('=' * 25)

    d = Duplifinder(args.path_to_be_processed, args.path_to_be_excluded)

    if args.media:
        d.set_extensions(config.MEDIA_EXTENSIONS)
        print('Media files will be processed...')
        print('Database update in progress...')
        d.update_db()
        print('Database updated!')
    elif args.documents:
        d.set_extensions(config.DOCS_EXTENSIONS)
        print('Documents and non-media files will be processed...')
        print('Database update in progress...')
        d.update_db()
        print('Database updated!')
    elif args.remove_duplicates:
        print('Looking for duplicates...')
        d.remove_duplicates()
        print('All duplicates moved to trashbin!')
    elif args.list:
        print('Printing list of duplicates...')
        d.print_duplicates_list()
        print('Duplicates list printed!')
    print('Exiting...')
