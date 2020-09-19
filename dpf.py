# encoding:utf-8
# create list of files in folder


import os
import argparse
import hashlib
import shutil

import dpf_model as dbm


from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper


from dpf_model import HashTable


mapper(dbm.HashTable, dbm.table_hashes)


BLOCK_SIZE = 1024 * 1024 # one megabyte
EXTENSIONS = ['avi', 'mp3', 'mp4', 'mkv', 'webm', 'mpg', 'jpg', 'png']


TRASHBIN = os.path.expanduser('~/.Trash')


class Duplifinder():

    def __init__(self, path):
        if os.path.isdir(path):
            self._path = path
        else:
            raise ValueError('Path is not specified or is not a directory!')
        self.engine = create_engine('sqlite:///' + self._path + os.sep + 'hash_db.sqlite3')
        dbm.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        return None

    @staticmethod
    def get_hash(file, block_size = BLOCK_SIZE):
        with open(file, 'br') as f:
            hasher = hashlib.sha256()
            binary_content = f.read(block_size)
            while len(binary_content):
                hasher.update(binary_content)
                binary_content = f.read(block_size)
        return hasher.hexdigest()

    def update_db(self):
        for root, dirs, files in os.walk(self._path):
            for file in files:
                if file.split('.')[-1].lower() not in EXTENSIONS:
                    print(f'Passed! File type is not allowed! {file}')
                    continue
                else:
                    path = os.path.join(root, file)
                    is_path_to_file_in_db = self.session.query(HashTable).filter(HashTable.path==path).first() # bool value is subject of interest
                    if not is_path_to_file_in_db:
                        hash = self.get_hash(path)
                        creation_time = os.stat(path).st_birthtime
                        print(f'{hash} {creation_time} {path}', end=' ')
                        try:
                            self.session.add(HashTable(hash, path, creation_time))
                            self.session.commit()
                        except Exception as err:
                            print('Error occured!')
                            print(err)
                            self.session.rollback()
                        else:
                            print('Added!')
                    else:
                        print(f'Already in db! {path}')
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
                # shutil.copyfile(q.path, TRASHBIN + os.sep + os.path.basename(q.path))
                shutil.move(q.path, TRASHBIN + os.sep + os.path.basename(q.path))
                print(f'Moved! {q.path}')
            print('Query completed!')
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
    parser.add_argument('path')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--update', action='store_true', help='Update database of hashes of file in given directory')
    group.add_argument('-c', '--cleanup', action='store_true', help='Clean up database')
    parser.add_argument('-f', '--find_duplicates', action='store_true', help='Find file duplicates')
    args = parser.parse_args()

    print(args)
    print(f'Target directory: {args.path}')

    d = Duplifinder(args.path)

    if args.update:
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
    else:
        print('Unknown option!')
    print('Exiting...')
