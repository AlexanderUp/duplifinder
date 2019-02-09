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
import sys
import hashlib


'''
-debug debug option;
-fl file list;
-wh hash list;
-s specify path to save report

Example:
-debug -fl -s 'path_to_folder'
'''

DEBUG = True if '-debug' in sys.argv else False
# FILE_LIST = True if '-fl' in sys.argv else False
WRITE_HASH = True if '-wh' is sys.argv else False
SAVE = True if '-s' in sys.argv else False

# /Users/alexanderuperenko/Desktop/Python - my projects/test_folder

class Lister():

    def __init__(self):
        # some more check to be applied here
        self.folders = None
        print('sys.argv: {}'.format(sys.argv))
        if sys.argv[-1] and os.path.isdir(sys.argv[-1]):
            print('sys.argv[-1]: {}'.format(sys.argv[-1]))
            self.path = sys.argv[-1].rstrip(os.sep)
            self.folders = [self.path]
        else:
            # self.path = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder'
            self.change_dir()
        # self.folders = [self.path]

    def change_dir(self):
        self.path = input('Input path:\n').rstrip(os.sep)
        self.folders = [self.path]
        print('self.folders changed to: {}'.format(self.folders))
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
        '''Search in depth is implemented. Memory issues are possible to occure.
        Try to implement search in width.'''
        objects = os.listdir(temp_path)
        for obj in objects:
            if os.path.isdir(os.path.join(temp_path, obj)):
                self.folders.append(os.path.join(temp_path, obj))
                # !!! recursive call !!!
                new_path = os.path.join(temp_path, obj)
                self.get_folder_list(new_path)
        self.folders.sort()
        return None

    def print_folder_list(self):
        print('Folders in self.folders:')
        for folder in self.folders:
            print(folder)
        return None

    def get_file_list(self):
        output_file = self.get_output_filename('output_****_file_list.txt')
        assert isinstance(output_file, str)
        # with open('output_file_list.txt', 'w') as f:
        with open(output_file, 'w') as f:
            f.write('=' * 100 + '\n')
            f.write('*' * 43 +' Folders list ' + '*' * 43 + '\n')
            f.write('=' * 100 + '\n')
            for folder in self.folders:
                # print('folder was wrote: {}'.format(folder))
                f.write(folder + '\n')
            f.write('=' * 100 + '\n\n')
            for folder in self.folders:
                f.write('-' * 75 + '\n')
                p = folder.split('/')[len(self.path.split('/'))-1:]
                p = '/'.join(p)
                f.write('/' + p + '\n')
                f.write('=' * 75 + '\n')
                for file in sorted(os.listdir(folder)):
                    # print(folder + os.sep + file)
                    if os.path.isfile(os.path.join(folder, file)):
                        print(folder + os.sep + file)
                        f.write('\t' + file + '\n')
        return None

    # def get_file_hash_list(self, WRITE_HASH=False):
    def get_file_hash_list(self):
        output_file = self.get_output_filename('output_****_file_list.txt')
        assert isinstance(output_file, str)
        with open(output_file, 'w') as f:
            for folder in self.folders:
                for file in sorted(os.listdir(folder)):
                    path_to_file = os.path.join(folder, file)
                    if os.path.isfile(path_to_file):
                        # print('file: {}'.format(path_to_file))
                        if WRITE_HASH:
                            hash = self.get_hash(self.binary_read(path_to_file))
                            f.write('{} {}\n'.format(hash, path_to_file))
                        else:
                            f.write('{}\n'.format(path_to_file))
        return None

    def get_file_hash_list_by_walk(self):
        output_file = self.get_output_filename('output_by_walk_****_file_list.sha256.txt')
        assert isinstance(output_file, str)
        with open(output_file, 'w') as f:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    path_to_file = os.path.join(root, file)
                    hash = self.get_hash(self.binary_read(path_to_file))
                    f.write('{} {}\n'.format(hash, path_to_file))
        return None

    def get_files_size(self):
        """Returns size of files in folder."""
        for root, dirs, files in os.walk(self.path):
            total_bytes = sum([os.path.getsize(os.path.join(root, name)) for name in files])
            size_in_megabytes = total_bytes / 1024 / 1024
            print('\'{}\' consumes {} bytes in {} files.'.format(root, total_bytes, len(files)))
            print('\'{}\' consumes {} megabytes in {} files.'.format(root, size_in_megabytes, len(files)))
        return None

    def test_get_file_list(self):
        '''Performance test without file handling - no file open, nothing wrote.'''
        for folder in self.folders:
            for file in os.listdir(folder):
                path_to_file = folder + os.sep + file
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

    def save_as(self):
        path_to_save_report = input('Input path to save report...\n')
        if path_to_save_report and os.path.isdir(path_to_save_report):
            # redundant except handling??
            try:
                os.chdir(path_to_save_report)
            except NotADirectoryError as err:
                print('Error occured: {}'.format(err))
            except OSError as err:
                print('Error occured: {}'.format(err))
            except Exception as err:
                print('Error occured: {}'.format(err))
            else:
                print('Report saving directory changed to: {}'.format(path_to_save_report))
        else:
            print('Report will be saved in your current working directory')
        return None

    def get_output_filename(self, mask):
        file_name = self.path.split('/')[-1]
        file_name = file_name.replace(' ', '_')
        print('new output file name will include: {}'.format(file_name))
        return mask.replace('****', file_name)

def main():
    l = Lister()
    if SAVE:
        l.save_as()
    l.get_folder_list(l.path)
    if WRITE_HASH:
        l.get_file_hash_list()
    else:
        l.get_file_list()
    l.get_files_size()

def debug():
    l = Lister()
    # l.change_dir()
    if SAVE:
        l.save_as()
    l.get_folder_list(l.path)
    l.print_folder_list()
    if WRITE_HASH:
        l.get_file_hash_list()
        l.get_file_hash_list_by_walk()
    else:
        l.get_file_list()
    l.get_files_size()
    # l.test_get_file_list()
    # l.test_get_file_list_by_walk()


if __name__ == '__main__':
    print('=' * 75)
    print('DEBUG is {}'.format(DEBUG))
    if DEBUG:
        debug()
    else:
        main()
