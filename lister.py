# encoding:utf-8
# create list of files in folder


import os
import sys
import hashlib
import shutil

# TODO:
# file names utf-8 encoding
# use argparse module

'''
CLI arguments:

-fl - file list;
-r - remove duplicates;
-m - move_duplicates.

NB!!! Path to folder to be specified LAST!!!

Example:

-hl 'path_to_folder'
'''

FILE_LIST = True if '-fl' in sys.argv else False
REMOVE = True if '-r' in sys.argv else False
MOVE = True if '-m' in sys.argv else False

BLOCK_SIZE = 1024 * 1024 # one megabyte

TEST_FOLDER = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder_test_folder'
TRASHBIN = '/Users/alexanderuperenko/.Trash'

class Lister():

    def __init__(self):
        self._result_hash_dictionary = None
        self._duplicates = None
        self._path = None
        print('sys.argv: {}'.format(sys.argv))
        if sys.argv[-1] and os.path.isdir(sys.argv[-1]):
            print('Target folder: {}'.format(sys.argv[-1]))
            self._path = sys.argv[-1]
        else:
            self._path = TEST_FOLDER
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

    def _create_hash_dictionary(self):
        '''
        Create dictionary of hashes and associated files.
        ['hash']:['path_to_file1', 'path_to_file2']
        '''
        result = {}
        for basedir, dirs, files in os.walk(self._path):
            for file in files:
                path_to_file = os.path.join(basedir, file)
                hash = self.get_hash(path_to_file)
                if hash in result:
                    result[hash].append(path_to_file)
                else:
                    result[hash] = [path_to_file]
        self._result_hash_dictionary = result
        return None

    def _find_duplicates(self):
        duplicates = {}
        for key, value in self._result_hash_dictionary.items():
            if len(value) > 1:
                duplicates[key] = value
        self._duplicates = duplicates
        return None

    def _remove_duplicates(self):
        print('File deletion log...')
        for hash, files in self._duplicates.items():
            shortest_file_name = self._get_shortest_file_name(files)
            for file in files:
                if len(os.path.basename(file)) != shortest_file_name:
                    try:
                        # os.remove(file)
                        print('.', end='')
                    except Exception as err:
                        print('Error occured:')
                        print(err)
                    else:
                        print('Removed: {}'.format(file))
        return None

    def _move_duplicates(self, destination_dir_name=TRASHBIN):
        '''
        Moves all duplicates to specified folder.
        '''
        for hash, files in self._duplicates.items():
            shortest_file_name = self._get_shortest_file_name(files)
            for file in files:
                if len(os.path.basename(file)) != shortest_file_name:
                    file_name = os.path.basename(file)
                    destination_path = os.path.join(destination_dir_name, file_name)
                    # shutil.move(file, destination_path)
                    print('Moved: {} >>>>> {}'.format(file, destination_path))
        return None

    def _get_shortest_file_name(self, files):
        return min(list(map(len, [os.path.basename(f) for f in files])))

    def get_file_list(self):
        output_file = self.get_output_foldername('output_****_file_list.txt')
        with open(output_file, 'w') as f:
            for basedir, dirs, files in os.walk(self._path):
                dirs.sort()
                for file in sorted(files):
                    f.write(os.path.join(basedir, file) + '\n')
        return None

    def get_output_foldername(self, mask):
        file_name = self._path.split('/')[-1]
        file_name = file_name.replace(' ', '_')
        return mask.replace('****', file_name)

    def _remove_empty_directory(self, path_to_directory):
        files = os.listdir(path_to_directory)
        if files and all([file.startswith('.') for file in files]):
            for file in files:
                try:
                    path = os.path.join(path_to_directory, file)
                    os.remove(path)
                    # print('{} deleted'.format(path))
                except Exception as err:
                    print('Error occured:')
                    print(err)
        else:
            print('Directory is not empty.')
            return None
        try:
            os.remove(path_to_directory)
            # print('Directory \'{}\' deleted.'.format(path_to_directory))
        except Exception as err:
            print('Error occured:')
            print(err)
        return None

    def _get_file_list(self):
        for root, dirs, files in os.walk(self._path):
            print('root: ', root)
            for file in files:
                if not file.startswith('.'):
                    path = os.path.join(root, file)
                    hash = self.get_hash(path)
                    print(f'{hash} {path}')
        return None

    def update_db(self):
        pass

def main():
    l = Lister()
    l._create_hash_dictionary()
    l._find_duplicates()
    if FILE_LIST:
        l.get_file_list()
    if REMOVE:
        l._remove_duplicates()
    if MOVE:
        l._move_duplicates()

def test():
    l = Lister()
    l._get_file_list()


if __name__ == '__main__':
    print('=' * 75)
    print('FILE_LIST is {}'.format(FILE_LIST))
    print('REMOVE is {}'.format(REMOVE))
    print('MOVE is {}'.format(MOVE))
    # main()
    test()
