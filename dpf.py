import argparse
import os
import shutil
from typing import Generator

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from config import Config, logger
from dpf_aux import create_db_backup, get_hash, get_session
from models.dpf_models import FileHash

config = Config()


class Duplifinder:
    """Duplifinder class.
    Looking for file duplicates in specified folder taking into account
    calculated hash.
    """

    def __init__(self, path: str, path_to_be_excluded: str) -> None:
        """Current limitations: only one excluded folder supported."""
        if os.path.isdir(path):
            self._path = path
        else:
            raise TypeError('Target path is not specified or is not a directory!')

        if path_to_be_excluded is None or os.path.isdir(path_to_be_excluded):
            self._path_to_be_excluded = path_to_be_excluded
        else:
            raise TypeError('Excluded path is not specified or is not a directory!')

        self._path_to_db: str = os.path.join(self._path, config.DB_NAME)
        self.session = get_session(self._path_to_db)

    def set_extensions(self, extensions: set[str]) -> None:
        self._extensions: set[str] = extensions

    def update_db(self) -> None:
        if self._extensions:
            create_db_backup(self._path_to_db)

            for root, _, files in os.walk(self._path):
                for data_file in files:
                    path = os.path.join(root, data_file)

                    if (
                        self._path_to_be_excluded
                        and os.path.commonpath(
                            (self._path_to_be_excluded, path),
                        )
                        == self._path_to_be_excluded
                    ):
                        logger.info(f'>>>> Excluded: <{path}>')
                        continue

                    _, extention = os.path.splitext(data_file)

                    if extention.lower() not in self._extensions:
                        logger.info(
                            f'==== Passed! File type is not allowed! <{data_file}>',
                        )
                        continue

                    is_path_to_file_in_db: FileHash | None = (
                        self.session.query(FileHash)
                        .filter(FileHash.path == path)
                        .first()
                    )

                    if is_path_to_file_in_db:
                        logger.info(f'>>>> Already in db! <{path}>')
                        continue

                    file_hash: str = get_hash(path, block_size=config.BLOCK_SIZE)
                    creation_time: float = os.stat(path).st_birthtime
                    logger.info(f'**** Added: <{path}>')

                    self.session.add(FileHash(file_hash, path, creation_time))
            try:
                self.session.commit()
            except SQLAlchemyError as err:
                logger.info(err)
                self.session.rollback()
            self._clean_up_db()
        else:
            logger.info('No extensions specified!')
        self.session.close()

    def duplicate_hash_query_generator(self) -> Generator[list, None, None]:
        """Duplicate hash query generator.

        Yields list of duplicate enrties (instances of class <FileHash>),
        not a list of hashes itself.

        Yields:
            list[FileHash]
        """
        duplicate_hash_entities: list[tuple[str]] = (
            self.session.query(FileHash.file_hash)
            .filter(~FileHash.is_deleted)
            .group_by(FileHash.file_hash)
            .having(func.count(FileHash.file_hash) > 1)
            .all()
        )
        logger.info('Duplicated hashes found: {0}'.format(len(duplicate_hash_entities)))
        duplicate_hashes = (entity[0] for entity in duplicate_hash_entities)
        logger.info('************************************')

        for duplicate_hash in duplicate_hashes:
            query: list[FileHash] = (
                self.session.query(FileHash)
                .filter(FileHash.file_hash == duplicate_hash)
                .all()
            )
            query.sort(key=lambda duplicate: duplicate.creation_time)
            yield query

    def print_duplicates_list(self) -> None:
        for query in self.duplicate_hash_query_generator():
            for duplicate in query:
                logger.info(f'{duplicate.file_hash} =>> {duplicate.path}')
            logger.info('************************************')
        self.session.close()

    def remove_duplicates(self):
        for query in self.duplicate_hash_query_generator():
            for duplicate in query[1:]:
                try:
                    shutil.move(
                        duplicate.path,
                        os.path.join(config.TRASHBIN, os.path.basename(duplicate.path)),
                    )
                except OSError as os_err:
                    logger.info(os_err)
                else:
                    duplicate.is_deleted = True
                    logger.info(f'Deleteted! {duplicate.path}')
        try:
            self.session.commit()
        except SQLAlchemyError as orm_err:
            logger.error(orm_err)
            self.session.rollback()
        else:
            logger.info('Files deleted, db updated.')
        finally:
            self.session.close()

    def _clean_up_db(self) -> None:
        logger.info('Cleaning database...')
        files: list[FileHash] = self.session.query(FileHash).all()
        for db_file in files:
            if not os.path.exists(db_file.path) and not db_file.is_deleted:
                logger.info(
                    "File doesn\'t exist! Marking as has been deleted...\t{file.path}",
                )
                db_file.is_deleted = True
        try:
            self.session.commit()
        except SQLAlchemyError as err:
            logger.error(err)
            self.session.rollback()
            logger.error('DB cleaning failed.')
        else:
            logger.info('Database clean!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Find file duplicates in given directory',
    )
    parser.add_argument('path_to_be_processed')
    parser.add_argument(
        '-e',
        '--exclude',
        default=None,
        help='Folders to be excluded from processing',
        dest='path_to_be_excluded',
    )
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        '-m',
        '--media',
        action='store_true',
        help='Update database with hashes of media files in given directory',
    )
    type_group.add_argument(
        '-d',
        '--documents',
        action='store_true',
        help=(
            'Update database with hashes of document and '
            'non-media files in given directory'
        ),
    )
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '-r',
        '--remove_duplicates',
        action='store_true',
        help='Find and delete file duplicates',
    )
    action_group.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='Print list of file duplicates',
    )
    args = parser.parse_args()

    logger.info('Running Duplifinder...')
    logger.info(f'Target directory: {args.path_to_be_processed}')
    logger.info(f'Excluded directory: {args.path_to_be_excluded}')
    logger.info(f'Media: {args.media}')
    logger.info(f'Documents: {args.documents}')
    logger.info(f'Delete duplicates: {args.remove_duplicates}')
    logger.info(f'Print duplicates list: {args.list}')

    duplifinder = Duplifinder(args.path_to_be_processed, args.path_to_be_excluded)

    if args.media:
        duplifinder.set_extensions(config.MEDIA_EXTENSIONS)
        logger.info('Media files will be processed...')
        logger.info('Database update in progress...')
        duplifinder.update_db()
        logger.info('Database updated!')
    elif args.documents:
        duplifinder.set_extensions(config.DOCS_EXTENSIONS)
        logger.info('Documents and non-media files will be processed...')
        logger.info('Database update in progress...')
        duplifinder.update_db()
        logger.info('Database updated!')
    elif args.remove_duplicates:
        logger.info('Looking for duplicates...')
        duplifinder.remove_duplicates()
        logger.info('All duplicates moved to trashbin!')
    elif args.list:
        logger.info('Printing list of duplicates...')
        duplifinder.print_duplicates_list()
        logger.info('Duplicates list printed!')
    logger.info('Exiting...')
