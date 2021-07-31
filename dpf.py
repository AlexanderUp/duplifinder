# encoding:utf-8
# create list of files in folder


import os
import argparse
import hashlib
import shutil
import sys
import fnmatch
import datetime


import dpf_model as dbm


from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper


from dpf_model import HashTable


mapper(dbm.HashTable, dbm.table_hashes)


BLOCK_SIZE = 1024 * 1024 # one megabyte
MEDIA_EXTENSIONS = ['avi', 'mp3', 'mp4', 'mkv', 'webm', 'mpg', 'jpg', 'png']
DOCS_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'numbers', 'pages', 'djvu', 'txt', 'epub', 'png', 'jpg', 'gif', 'zip', 'rar', 'djv']
TRASHBIN = os.path.expanduser('~/.Trash')

DB_NAME = 'hash_db.sqlite3'
DB_NAME_PATTERN = 'hash_db.sqlite3_backup_{}_{}_{}_{}_{}'
MAX_BACKUP_NUMBER = 5


class Duplifinder():

    def __init__(self, path, path_to_be_excluded):
        '''
        Current limitations: only one excluded folders supported.
        '''
        if os.path.isdir(path):
            self._path = path
        else:
            raise ValueError('Target path is not specified or is not a directory!')
        if path_to_be_excluded==None or os.path.isdir(path_to_be_excluded):
            self._path_to_be_excluded = path_to_be_excluded
        else:
            raise ValueError('Excluded path is not specified or is not a directory!')

        ##### Backup #####

        path_to_db = os.path.join(self._path, DB_NAME)

        if os.path.exists(path_to_db):
            print('DB already exists! Backuping...')
            time = datetime.datetime.now()
            db_backup_name = DB_NAME_PATTERN.format(time.year, time.month, time.day, time.hour, time.minute)
            path_to_db_backup = os.path.join(self._path, db_backup_name)

            try:
                shutil.copyfile(path_to_db, path_to_db_backup)
            except OSError as err:
                print(err)
                print('Exiting...')
                sys.exit()
            else:
                print('Backup created!')

        backup_files = fnmatch.filter(os.listdir(self._path), 'hash_db.sqlite3_backup_*')
        backup_files_creation_time = [os.stat(os.path.join(self._path, backup_file)).st_birthtime for backup_file in backup_files]
        backup_files_sorted_list = list(zip(backup_files, backup_files_creation_time))
        backup_files_sorted_list.sort(key=lambda file: file[1])

        for file in backup_files_sorted_list[:-MAX_BACKUP_NUMBER]:
            shutil.move(os.path.join(self._path, file[0]), os.path.join(TRASHBIN, file[0]))

        print('Backup cleared!')

        self.engine = create_engine('sqlite:///' + self._path + os.sep + DB_NAME)
        dbm.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.extensions = None
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
            for root, dirs, files in os.walk(self._path):
                for file in files:
                    path = os.path.join(root, file)
                    if self._path_to_be_excluded and os.path.commonpath((self._path_to_be_excluded, path)) == self._path_to_be_excluded:
                        print(f'Excluded: {path}')
                        continue
                    if file.split('.')[-1].lower() not in self.extensions:
                        print(f'Passed! File type is not allowed! {file}')
                        continue
                    else:
                        is_path_to_file_in_db = self.session.query(HashTable).filter(HashTable.path==path).first() # bool value is subject of interest
                        if not is_path_to_file_in_db:
                            hash = self.get_hash(path)
                            creation_time = os.stat(path).st_birthtime
                            print(f'***** Adding: {hash} {creation_time} {path}', end=' ')
                            try:
                                self.session.add(HashTable(hash, path, creation_time))
                                self.session.commit()
                            except Exception as err:
                                print('Error occured!')
                                print(err)
                                self.session.rollback()
                            else:
                                print('***** Added! *****')
                        else:
                            print(f'Already in db! {path}')
        else:
            print('No extensions specified! Aborting...')
            sys.exit()
        self.session.close()
        return None

    def find_duplicates(self):
        duplicates = self.session.query(HashTable).group_by(HashTable.hash).having(func.count(HashTable.hash)>1).all()
        print(f'Duplicates found: {len(duplicates)}')
        duplicate_hashes = [dup.hash for dup in duplicates]
        for hash in duplicate_hashes:
            print('Query started!')
            query = self.session.query(HashTable).filter(HashTable.hash==hash).all()
            query.sort(key=lambda x: x.creation_time)
            for q in query[1:]:
                shutil.move(q.path, TRASHBIN + os.sep + os.path.basename(q.path))
                print(f'Moved! {q.path}')
            print('Query completed!')
        self.session.close()
        return None

    def print_duplicates_list(self):
        duplicates = self.session.query(HashTable).group_by(HashTable.hash).having(func.count(HashTable.hash)>1).all()
        print(f'Total duplicates found: {len(duplicates)}')
        for dup in duplicates:
            query = self.session.query(HashTable).filter(HashTable.hash==dup.hash).all()
            for q in query:
                print(f'{q.hash} =>> {q.path}')
        self.session.close()
        return None

    def clean_up_db(self):
        files = self.session.query(HashTable).all()
        for file in files:
            if not os.path.exists(file.path):
                print(f'File doesn\'t exist! Deleting from db... {file.path}')
                self.session.delete(file)
                self.session.commit()
        self.session.close()
        return None


if __name__ == '__main__':
    print('=' * 75)

    parser = argparse.ArgumentParser(description='Find file duplicates in given directory')
    parser.add_argument('path_to_be_processed')
    parser.add_argument('-e', '--exclude', default=None, help='Folders to be excluded from processing', dest='path_to_be_excluded')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--media', action='store_true', help='Update database with hashes of media files in given directory')
    group.add_argument('-d', '--documents', action='store_true', help='Update database with hashes of non-media files in given directory')
    group.add_argument('-c', '--cleanup', action='store_true', help='Clean up database')
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('-f', '--find_duplicates', action='store_true', help='Find file duplicates')
    action_group.add_argument('-l', '--list', action='store_true', help='Print list of duplicates')
    args = parser.parse_args()

    print(args)
    print(f'Target directory: {args.path_to_be_processed}')
    print(f'Excluded directory: {args.path_to_be_excluded}')

    d = Duplifinder(args.path_to_be_processed, args.path_to_be_excluded)

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
    elif args.cleanup:
        print('Database cleanup in progress...')
        d.clean_up_db()
        print('Database clean!')
    elif args.find_duplicates:
        print('Looking for duplicates...')
        d.find_duplicates()
        print('All duplicates found!')
    elif args.list:
        print('Printing list of duplicates...')
        d.print_duplicates_list()
        print('Duplicates list printed!')
    else:
        print('Unknown option!')
    print('Exiting...')
