# encoding:utf-8
# find file duplicates in given folder


import os
import argparse
import hashlib
import shutil
import sys
import fnmatch
import datetime

from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper

import dpf_model as dbm

from dpf_model import HashTable

mapper(dbm.HashTable, dbm.table_hashes)

BLOCK_SIZE = 1024 * 1024 # one megabyte
MEDIA_EXTENSIONS = ['avi', 'mp3', 'mp4', 'mkv', 'webm', 'mpg', 'jpg', 'png']
DOCS_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'numbers', 'pages', 'djvu', 'txt', 'epub', 'png', 'jpg', 'gif', 'zip', 'rar', 'djv']
TRASHBIN = os.path.expanduser('~/.Trash')

DB_NAME = 'hash_db.sqlite3'
DB_BACKUP_NAME_PATTERN = 'hash_db.sqlite3_backup_{}_{}_{}_{}_{}'
BACKUP_MAX_NUMBER = 5


class Duplifinder():

    def __init__(self, path, path_to_be_excluded):
        '''
        Current limitations: only one excluded folders supported.
        '''
        if os.path.isdir(path):
            self._path = path
        else:
            raise TypeError('Target path is not specified or is not a directory!')

        if path_to_be_excluded == None or os.path.isdir(path_to_be_excluded):
            self._path_to_be_excluded = path_to_be_excluded
        else:
            raise TypeError('Excluded path is not specified or is not a directory!')

        self._path_to_db = os.path.join(self._path, DB_NAME)

        self.engine = create_engine('sqlite:///' + self._path + os.sep + DB_NAME)
        dbm.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.extensions = None
        return None

    def _create_db_backup(self):
        if os.path.exists(self._path_to_db):
            print('Database already exists! Backuping...')
            time = datetime.datetime.now()
            db_backup_name = DB_BACKUP_NAME_PATTERN.format(time.year, time.month, time.day, time.hour, time.minute)
            path_to_db_backup = os.path.join(self._path, db_backup_name)

            try:
                shutil.copyfile(self._path_to_db, path_to_db_backup)
            except OSError as err:
                print(err)
                print('Error during backup creation! Exiting...')
                sys.exit()
            else:
                print('Backup created!')

        backup_files = fnmatch.filter(os.listdir(self._path), 'hash_db.sqlite3_backup_*')
        backup_files = [(backup_file, os.stat(os.path.join(self._path, backup_file)).st_birthtime) for backup_file in backup_files]
        backup_files.sort(key=lambda file: file[1])

        for file in backup_files[:-BACKUP_MAX_NUMBER]:
            shutil.move(os.path.join(self._path, file[0]), os.path.join(TRASHBIN, file[0]))
        print('Backup cleared!')
        return None

    def _clean_up_db(self):
        print('Cleaning database..')
        files = self.session.query(HashTable).all()
        for file in files:
            if not os.path.exists(file.path):
                print(f'File doesn\'t exist! Deleting from db... {file.path}')
                self.session.delete(file)
        try:
            self.session.commit()
        except Exception as err:
            print(err)
            self.session.rollback()
        print('Database clean!')
        return None

    @staticmethod
    def get_hash(file, block_size = BLOCK_SIZE):
        with open(file, 'br') as f:
            hasher = hashlib.sha256()
            while True:
                binary_content = f.read(block_size)
                if binary_content:
                    hasher.update(binary_content)
                else:
                    break
        return hasher.hexdigest()

    def update_db(self):
        if self.extensions:
            self._create_db_backup()
            for root, dirs, files in os.walk(self._path):
                for file in files:
                    path = os.path.join(root, file)
                    if self._path_to_be_excluded and os.path.commonpath((self._path_to_be_excluded, path)) == self._path_to_be_excluded:
                        print(f'>>>> Excluded: <{path}>')
                        continue

                    if file.split('.')[-1].lower() not in self.extensions:
                        print(f'==== Passed! File type is not allowed! <{file}>')
                        continue

                    is_path_to_file_in_db = self.session.query(HashTable).filter(HashTable.path==path).first()
                    if is_path_to_file_in_db:
                        print(f'>>>> Already in db! <{path}>')
                        continue

                    hash = self.get_hash(path)
                    creation_time = os.stat(path).st_birthtime
                    print(f'******** Adding: <{path}> **** Added!')
                    try:
                        self.session.add(HashTable(hash, path, creation_time))
                        self.session.commit()
                    except Exception as err:
                        print(err)
                        self.session.rollback()
            self._clean_up_db()
        else:
            print('No extensions specified!')
        self.session.close()
        return None

    def feed_duplicate_hash_query(self):
        # returns list of duplicate enrties (instance of class <HashTable>), not a hash itself
        duplicates = self.session.query(HashTable).group_by(HashTable.hash).having(func.count(HashTable.hash)>1).all()
        print(f'Duplicated files found: {len(duplicates)}')
        for duplicate in duplicates:
            query = self.session.query(HashTable).filter(HashTable.hash==duplicate.hash).all()
            query.sort(key=lambda duplicate: duplicate.creation_time)
            yield query

    def print_duplicates_list(self):
        for query in self.feed_duplicate_hash_query():
            for duplicate in query:
                print(f'{duplicate.hash} =>> {duplicate.path}')
            print('************************************')
        self.session.close()
        return None

    def remove_duplicates(self):
        for query in self.feed_duplicate_hash_query():
            for duplicate in query[1:]:
                try:
                    self.session.delete(duplicate)
                    shutil.move(q.path, TRASHBIN + os.sep + os.path.basename(q.path))
                except sqlalchemy.exec.SQLAlchemyError as err:
                    print(err)
                except OSError as err:
                    print(err)
                else:
                    print(f'Deleteted! {duplicate.path}')
                finally:
                    self.session.rollback()
                    self.session.close()
            self.session.commit()
        self.session.close()
        return None


if __name__ == '__main__':
    print('=' * 75)

    parser = argparse.ArgumentParser(description='Find file duplicates in given directory')
    parser.add_argument('path_to_be_processed')
    parser.add_argument('-e', '--exclude', default=None, help='Folders to be excluded from processing', dest='path_to_be_excluded')
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument('-m', '--media', action='store_true', help='Update database with hashes of media files in given directory')
    type_group.add_argument('-d', '--documents', action='store_true', help='Update database with hashes of document and non-media files in given directory')
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('-r', '--remove_duplicates', action='store_true', help='Find and delete file duplicates')
    action_group.add_argument('-l', '--list', action='store_true', help='Print list of file duplicates')
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

    # replace d.extensions with non-state changing method
    if args.media:
        d.extensions = MEDIA_EXTENSIONS
        print('Media files will be processed...')
        print('Database update in progress...')
        d.update_db()
        print('Database updated!')
    elif args.documents:
        d.extensions = DOCS_EXTENSIONS
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
