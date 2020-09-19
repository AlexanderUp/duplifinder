# encoding:utf-8
# auxiliary functions for dpf.py


import sys
import os
import sqlite3


import dpf_model as dbm


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapper


from dpf_model import HashTable


mapper(dbm.HashTable, dbm.table_hashes)


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

def update_schema(path_to_old_db):
    conn = sqlite3.connect(path_to_old_db)
    cur = conn.cursor()
    try:
        cur.execute('ALTER TABLE hashes ADD COLUMN creation_time NOT NULL DEFAULT 0')
        conn.commit()
    except sqlite3.IntegrityError as err:
        print('Error occured!')
        print(err)
    except Exception as err:
        print('General exception occured!')
        print(err)
    else:
        print('SQL statement executed successfully!')
    finally:
        cur.close()
        conn.close()

    session = get_session(path_to_old_db) # path to old database file
    new_engine = create_engine('sqlite:///' + os.path.dirname(path_to_old_db) + os.sep + 'hash_db.sqlite3.updated_schema')
    dbm.metadata.create_all(bind=new_engine)
    Session = sessionmaker(bind=new_engine)
    new_session = Session()
    old_query = session.query(HashTable).all()
    for entry in old_query:
        new_entry = HashTable(entry.hash, entry.path, os.stat(entry.path).st_birthtime)
        try:
            new_session.add(new_entry)
            new_session.commit()
        except IntegrityError as err:
            print('Error occured!')
            print(err)
            new_session.rollback()
        except Exception as err:
            print('General error occured!')
            print(err)
        else:
            print(f'Added: {new_entry.path}')
    session.close()
    new_session.close()
    return None


if __name__ == '__main__':
    print('=' * 75)
    update_schema(sys.argv[-1])
    print('Done!')
