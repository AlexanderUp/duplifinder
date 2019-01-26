# encoding:utf-8
# file analyser for output file returned by lister.py
# should find duplicated files and move them to storage folder with logfile creation
# after that all redundant number of copies should be deleted

SOURCE_FILE = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/output.sha256.txt'
OUTPUT_FILE = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/output.sha256.log.txt'

import pprint

def create_dict(file=SOURCE_FILE):
    result = {}
    with open(file, 'r') as f:
        for line in f:
            if line[:64] in result.keys():
                result[line[:64]].append(line[65:])
            else:
                result[line[:64]] = [line[65:]]
    return result

def log_to_file(res, file=OUTPUT_FILE):
    with open(file, 'w') as out:
        out.write(pprint.pformat(res, width=1000))
    return None

def find_duplicate(source):
    duplicates = {}
    for key in source.keys():
        # print('{} => {}'.format(key, len(source[key])))
        if len(source[key]) > 1:
            duplicates[key] = source[key]
    return duplicates

def log_to_file_duplicates(duplicates):
    with open('duplicates.txt', 'w') as out:
        out.write(pprint.pformat(duplicates, width=1000))
    return None


if __name__ == '__main__':
    print('*' * 75)
    res = create_dict()
    log_to_file(res)
    dup = find_duplicate(res)
    # pprint.pprint(dup)
    log_to_file_duplicates(dup)
