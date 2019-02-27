# encoding:utf-8

'''
File analyser for output file returned by lister.py should find duplicated files
and move them to storage folder with logfile created after that all redundant
number of copies should be deleted.

Call example:

python3 file_analyser.py 'path_to_source_file'

Outfile will be stored in the same directory as source file.
'''


import os
import shutil
import sys
import pprint


class FileAnalyzer():

    def __init__(self):
        print('Sys.argv: {}'.format(sys.argv))
        if len(sys.argv)!=1 and os.path.isfile(sys.argv[-1]):
            self.source_file = sys.argv[-1]
        else:
            source_file = input('Input path to source file...\n')
            if os.path.isfile(source_file):
                self.source_file = source_file
            else:
                sys.exit('Source file not specified! Exiting...\n')
        self.result_hash_dictionary = None
        self.duplicates = None
        return None

    def create_dict(self):
        result = {}
        with open(self.source_file, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                if line[:64] in result.keys():
                    result[line[:64]].append(line[65:])
                else:
                    result[line[:64]] = [line[65:]]
        self.result_hash_dictionary = result

    def log_to_file(self):
        path_to_out_file, source_file_name = os.path.split(self.source_file)
        source_file_name_without_extention, source_file_extention = os.path.splitext(source_file_name)
        out_file = source_file_name_without_extention + '.log' + source_file_extention
        print('out_file: {}'.format(out_file))
        with open(out_file, 'w') as out:
            out.write(pprint.pformat(self.result_hash_dictionary, width=1000))
        return None

    def find_duplicates(self):
        duplicates = {}
        for key in self.result_hash_dictionary.keys():
            if len(self.result_hash_dictionary[key]) > 1:
                duplicates[key] = self.result_hash_dictionary[key]
        self.duplicates = duplicates

    def log_to_file_duplicates(self):
        path, file = os.path.split(self.source_file)
        os.chdir(path)
        out_file = os.path.splitext(file)[0] + '_duplicates.txt'
        with open(out_file, 'w') as out:
            out.write(pprint.pformat(self.duplicates, width=1000))
        return None

    def remove_duplicates(self):
        self.move_duplicates()
        return None

    def move_duplicates(self):
        for file_hash in self.duplicates.keys():
            destination_folder = os.path.splitext(self.duplicates[file_hash][0])[0]
            try:
                os.mkdir(destination_folder)
            except FileExistsError as err:
                print('Error {} occured with {}'.format(err, destination_folder))
            print('Created folder: {}'.format(destination_folder))
            for path_to_hashed_file in self.duplicates[file_hash][1:]:
                shutil.move(path_to_hashed_file, destination_folder)
                print('{} ===> {}'.format(path_to_hashed_file[-15:], destination_folder[-15:]))
        return None


if __name__ == '__main__':
    print('*' * 75)
    analyzer = FileAnalyzer()
    analyzer.create_dict()
    # analyzer.log_to_file()
    analyzer.find_duplicates()
    # analyzer.log_to_file_duplicates()
    analyzer.move_duplicates()
