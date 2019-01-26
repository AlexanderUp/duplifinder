# encoding:utf-8
# create list of files in folder / entire disc or volume

# copy and move files
# import shutil

# os.path.exists() - file existance
# os.path.getsize() - return file size in bytes
# os.path.getctime() - time of file creation - return quantity of seconds since epoh
# os.path.basename() - filename without path
# os.path.dirname() - foldername
# os.path.split() - returns tuple of path and filename
# os.path.splitext() - returns tuple of path with filename without extention and extension
# os.path.isdir()
# os.path.isfile()

# os.getcwd() - returns current working directory
# os.chdir() - make mentioned directory working
# os.listdir() - returns list of objects in current directory
# os.walk() - goes through all objects in directory (folders and files)

import os
import os.path
import hashlib

# /Users/alexanderuperenko/Desktop/Python - my projects/test_folder

class Lister():

    def __init__(self):
        self.path = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder'
        self.folders = [self.path]

    def change_dir(self):
        path = input('Input path:\n')
        self.path = path
        return None

    def binary_read(self, file):
        with open(file, 'br') as f:
            res = f.read()
        return res

    def get_hash(self, file):
        h = hashlib.sha256()
        h.update(file)
        return h.hexdigest()

    def get_folder_list(self, temp_path):
        # print('temp_path: {}'.format(temp_path))
        # print('Currently in: {}'.format(temp_path))
        objects = os.listdir(temp_path)
        # print('Objects in {}:\n{}'.format(temp_path, objects))
        for obj in objects:
            if os.path.isdir(temp_path + os.sep + obj):
                # print('Folder found: {}'.format(obj))
                self.folders.append(temp_path + os.sep + obj)
                # print('Folder added: {}'.format(temp_path + os.sep + obj))
                # !!! recursive call !!!
                new_path = temp_path + os.sep + obj
                # print('New temp_path: {}'.format(new_path))
                self.get_folder_list(new_path)
        return None

    def print_folder_list(self):
        print('Folders in self.folders:')
        self.folders.sort()
        for folder in self.folders:
        # for folder in sorted(self.folders):
            print(folder)
        return None

    def get_file_list(self):
        with open('output.sha256.txt', 'w') as f:
            for obj in self.folders:
                for file in os.listdir(obj):
                    path_to_file = obj + os.sep + file
                    if os.path.isfile(path_to_file):
                        # print('file: {}'.format(path_to_file))
                        hash = self.get_hash(self.binary_read(path_to_file))
                        f.write('{} {}\n'.format(hash, path_to_file))
        return None

    def get_file_list_by_walk(self):
        with open('output_by_walk.sha256.txt', 'w') as f:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    path_to_file = os.path.join(root, file)
                    hash = self.get_hash(self.binary_read(path_to_file))
                    f.write('{} {}\n'.format(hash, path_to_file))
        return None

    def get_files_size(self):
        """Returns size of files in folder."""
        for root, dirs, files in os.walk(self.path):
            print('{} consumes {} bytes in {} files.'.format(root, sum([os.path.getsize(os.path.join(root, name)) for name in files]), len(files)))
        return None

    def test_get_file_list(self):
        '''Performance test without file handling - no file open, nothing wrote.'''
        for obj in self.folders:
            for file in os.listdir(obj):
                path_to_file = obj + os.sep + file
                if os.path.isfile(path_to_file):
                    hash = self.get_hash(self.binary_read(path_to_file))
        return None

    def test_get_file_list_by_walk(self):
        '''Performance test without file handling - no file open, nothing wrote.'''
        for root, dirs, files in os.walk(self.path):
            for file in files:
                path_to_file = os.path.join(root, file)
                hash = self.get_hash(self.binary_read(path_to_file))
        return None


if __name__ == '__main__':
    print('=' * 75)
    # times = 1000
    times = 1
    print('Doing {}'.format(times))
    for i in range(times):
        l = Lister()
        l.get_folder_list(l.path)
        # l.print_folder_list()
        l.get_file_list()
        # l.get_files_size()
        l.get_file_list_by_walk()
        # l.test_get_file_list()
        # l.test_get_file_list_by_walk()
