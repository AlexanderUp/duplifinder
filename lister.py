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
import shutil
import pprint


'''
CLI arguments:

-debug - debug option;
-wh  - hash list;
-s - specify path to save report;
-r - remove duplicates.

NB!!! Path to folder to be specified LAST!!!

Example:

-debug -wh -s 'path_to_folder'
'''

DEBUG = True if '-debug' in sys.argv else False
WRITE_HASH = True if '-wh' in sys.argv else False
SAVE = True if '-s' in sys.argv else False
REMOVE = True if '-r' in sys.argv else False

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
            self.change_dir()
        self.result_hash_dictionary = None
        self.duplicates = None
        return None

    def change_dir(self):
        self.path = input('Input path:\n').rstrip(os.sep)
        if not self.path:
            print('You input empty path!')
            sys.exit('Exiting...')
        # some checks and exception handlers to be added here
        self.folders = [self.path]
        print('self.folders changed to: {}'.format(self.folders))
        return None

    @staticmethod
    def get_hash(file):
        with open(file, 'br') as f:
            binary_content = f.read()
        h = hashlib.sha256()
        h.update(binary_content)
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

    def get_file_hash_list(self):
        output_file = self.get_output_filename('output_****_file_list.txt')
        assert isinstance(output_file, str)
        with open(output_file, 'w') as f:
            for folder in self.folders:
                for file in sorted(os.listdir(folder)):
                    path_to_file = os.path.join(folder, file)
                    if os.path.isfile(path_to_file):
                        # this condition still alive only as secondary type of output file list report
                        if WRITE_HASH:
                            hash = self.get_hash(path_to_file)
                            f.write('{} {}\n'.format(hash, path_to_file))
                        else:
                            f.write('{}\n'.format(path_to_file))
        return None

    def get_file_hash_list_by_walk(self):
        output_file = self.get_output_filename('output_****_by_walk_file_list.sha256.txt')
        assert isinstance(output_file, str)
        with open(output_file, 'w') as f:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    path_to_file = os.path.join(root, file)
                    hash = self.get_hash(path_to_file)
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

    def save_to_directory(self):
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

    def _create_hash_dictionary(self):
        '''
        Create dictionary of hashes and associated filesself.
        ['hash']:['path to associated files']
        '''
        result = {}
        for folder in self.folders:
            for file in sorted(os.listdir(folder)):
                path_to_file = os.path.join(folder, file)
                if os.path.isfile(path_to_file):
                    hash = self.get_hash(path_to_file)
                    if hash in result.keys():
                        result[hash].append(path_to_file)
                    else:
                        result[hash] = [path_to_file]
        self.result_hash_dictionary = result
        return None

    def _find_duplicates(self):
        duplicates = {}
        for key in self.result_hash_dictionary.keys():
            if len(self.result_hash_dictionary[key]) > 1:
                duplicates[key] = self.result_hash_dictionary[key]
        self.duplicates = duplicates

    def _log_to_file(self):
        '''
        Create a file with written file hash tree.
        '''
        # path_to_out_file, source_file_name to be specified more carefully
        path_to_out_file, source_file_name = os.path.split(self.source_file)
        source_file_name_without_extention, source_file_extention = os.path.splitext(source_file_name)
        out_file = source_file_name_without_extention + '.log' + source_file_extention
        print('out_file: {}'.format(out_file))
        with open(out_file, 'w') as out:
            out.write(pprint.pformat(self.result_hash_dictionary, width=1000))
        return None

    def _log_to_file_duplicates(self):
        # source file to be specified more carefully
        path, file = os.path.split(self.source_file)
        os.chdir(path)
        out_file = os.path.splitext(file)[0] + '_duplicates.txt'
        with open(out_file, 'w') as out:
            out.write(pprint.pformat(self.duplicates, width=1000))
        return None

    def _print_duplicates(self):
        for file in self.duplicates:
            pprint.pprint('{} => {}'.format(file[-10:], self.duplicates[file]), width=150)
        return None

    def _remove_duplicates(self):
        for file_hash in self.duplicates.keys():
            for path_to_hashed_file in self.duplicates[file_hash][1:]:
                try:
                    os.remove(path_to_hashed_file)
                    print('Removed: {}'.format(path_to_hashed_file))
                except Exception as err:
                    print('Error occured: {}'.format(err))
        return None

    # to be refactored
    def _move_duplicates(self, destination_dir_name):
        '''
        Moves all duplicates to specified folder.
        '''
        self._create_destination_dir(destination_dir_name)
        for file_hash in self.duplicates.keys():
            for path_to_hashed_file in self.duplicates[file_hash][1:]:
                file_name = os.path.basename(path_to_hashed_file)
                destination_path = os.path.join(destination_dir_name, file_name)
                # shutil.move(path_to_hashed_file, destination_dir_name)
                shutil.move(path_to_hashed_file, destination_path)
                print('{} ===> {}'.format(path_to_hashed_file[-15:], destination_path[-15:]))
        return None

    # to be refactored
    def _move_duplicates_to_same_named_folder(self):
        '''
        Moves all duplicates to folder with name same to first file in list of file duplicates.
        '''
        next(get_destination_folder_name)
        for file_hash in self.duplicates.keys():
            destination_folder = self._get_destination_folder_name().send(file_hash)
            self._create_destination_dir(destination_folder)
            for path_to_hashed_file in self.duplicates[file_hash][1:]:
                shutil.move(path_to_hashed_file, destination_folder)
                print('{} ===> {}'.format(path_to_hashed_file[-15:], destination_folder[-15:]))
        return None

    # next(get_destination_folder_name)
    # get_destination_folder_name.send(file_hash)
    def _get_destination_folder_name(self):
        destination = ''
        while True:
            file_hash = yield destination
            destination = os.path.splitext(self.duplicates[file_hash][0])[0]
        return None

    def _create_destination_dir(self, destination_dir_name):
        try:
            os.mkdir(destination_dir_name)
            print('Created folder: {}'.format(destination_dir_name))
        except FileExistsError as err:
            print('Error {} occured with {}'.format(err, destination_dir_name))
        # exception to be specified more accurately
        except Exception as err:
            print('Error occured:\n{}'.format(err))
        return None

    def _remove_emtpy_folder(self, path_to_folder):
        # if os.path.isdir(path_to_folder) and len(os.listdir(path_to_folder)) == 0:
        if os.path.isdir(path_to_folder) and not bool(os.listdir(path_to_folder)):
            os.rmdir(path_to_folder)
            print('Removed: {}'.format(path_to_folder))
        return None

def main():
    l = Lister()
    if SAVE:
        l.save_to_directory()
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
        l.save_to_directory()
    l.get_folder_list(l.path)
    l.print_folder_list()
    if WRITE_HASH:
        l.get_file_hash_list()
        l.get_file_hash_list_by_walk()
    else:
        l.get_file_list()
    l.get_files_size()

def main_remove_duplicates():
    l = Lister()
    l.get_folder_list(l.path)
    l.print_folder_list()
    l._create_hash_dictionary()
    l._find_duplicates()
    l._print_duplicates()
    l._remove_duplicates()


if __name__ == '__main__':
    print('=' * 75)
    print('DEBUG is {}'.format(DEBUG))
    print('WRITE_HASH is {}'.format(WRITE_HASH))
    print('SAVE is {}'.format(SAVE))
    print('REMOVE is {}'.format(REMOVE))
    if DEBUG:
        debug()
    elif REMOVE:
        main_remove_duplicates()
    else:
        main()
