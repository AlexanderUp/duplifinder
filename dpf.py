# encoding:utf-8
# create list of files in folder


import os
import argparse
import hashlib
import shutil


from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper


import dpf_model as dbm
from dpf_model import HashTable


mapper(dbm.HashTable, dbm.table_hashes)


BLOCK_SIZE = 1024 * 1024 # one megabyte
EXTENSIONS = ['avi', 'mp3', 'mp4', 'mkv', 'webm', 'mpg']

TEST_FOLDER = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder_test_folder'
TRASHBIN = '/Users/alexanderuperenko/.Trash'


class Duplifinder():

    def __init__(self, path):
        if os.path.isdir(path):
            self._path = path
        else:
            raise ValueError('Path is not specified or is not a directory!')
        # self._path = None
        # if sys.argv[-1] and os.path.isdir(sys.argv[-1]):
        #     print('Target folder: {}'.format(sys.argv[-1]))
        #     self._path = sys.argv[-1]
        # else:
        #     self._path = TEST_FOLDER
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
                    print(f'Passed! {file}')
                    continue
                    print('Continue!!!')
                else:
                    path = os.path.join(root, file)
                    path_to_file_in_db = self.session.query(HashTable).filter(HashTable.path==path).first()
                    if not path_to_file_in_db:
                        hash = self.get_hash(path)
                        print(f'{hash} {path}', end=' ')
                        try:
                            self.session.add(HashTable(hash, path))
                            self.session.commit()
                        except Exception as err:
                            print('Error occured!')
                            print(err)
                            self.session.rollback()
                        else:
                            print('Added!')
        self.session.close()
        return None

    def find_duplicates(self):
        duplicates = self.session.query(HashTable).group_by(HashTable.hash).having(func.count(HashTable.hash)>1).all()
        print(f'Duplicates found: {len(duplicates)}')
        duplicate_hashes = [dup.hash for dup in duplicates]
        for hash in duplicate_hashes:
            dup_paths = self.session.query(HashTable).filter(HashTable.hash==hash).all()
            for dup_path in dup_paths:
                print(dup_path.hash, dup_path.path)
        self.session.close()
        return None

    def remove_duplicates(self):
        pass

    def clean_up_db(self):
        files = self.session.query(HashTable).all()
        for file in files:
            if not os.path.exists(file.path):
                print(f'File doesn\'t exist! Deleting from db... {file.path}')
                self.session.delete(file)
                self.session.commit()
        self.session.close()
        return None


def get_session(path_to_db):
    engine = create_engine('sqlite:///' + path_to_db)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def merge_db(path):
    engine = create_engine('sqlite:///' + path + os.sep + 'main_hash_db.sqlite3')
    dbm.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for basedir, dirs, files in os.walk(path):
        for file in files:
            if file == 'hash_db.sqlite3':
                path_to_inner_db = os.path.join(basedir, file)
                print(f'Processed: {path_to_inner_db}')
                inner_session = get_session(path_to_inner_db)
                entries = inner_session.query(HashTable).all()
                inner_session.close()
                for entry in entries:
                    print(f'{entry.hash} {entry.path}')
                entries_to_be_added = [HashTable(entry.hash, entry.path) for entry in entries]
                session.add_all(entries_to_be_added)
                session.commit()
                print(f'{len(entries)} entries added!')
    session.close()
    print('Databases merged!')
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
