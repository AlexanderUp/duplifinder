# encoding:utf-8
# multiprocessing lister implementation

import multiprocessing
import hashlib
import os
from lister import Lister

# path = '/Users/alexanderuperenko/Desktop/Python - my projects/duplifinder/test_folder'
path = '/Users/alexanderuperenko/Downloads/671854b0df07ae4198879ccde5e759f0a77949331a111046b04b3f936460f51d/media'


def consumer(input_q):
    while True:
        item = input_q.get()
        hash = Lister.get_hash(item)
        # hash = get_hash(item)
        print('{} => {}'.format(hash, item))
        input_q.task_done()
    return None

def producer(sequence, output_q):
    for item in sequence:
        output_q.put(item)
    return None

def main():
    q = multiprocessing.JoinableQueue()

    cons_p1 = multiprocessing.Process(target=consumer, args=(q,))
    cons_p1.daemon = True
    cons_p1.start()

    cons_p2 = multiprocessing.Process(target=consumer, args=(q,))
    cons_p2.daemon = True
    cons_p2.start()

    cons_p3 = multiprocessing.Process(target=consumer, args=(q,))
    cons_p3.daemon = True
    cons_p3.start()

    cons_p4 = multiprocessing.Process(target=consumer, args=(q,))
    cons_p4.daemon = True
    cons_p4.start()

    sequence = []
    print('path: {}'.format(path))
    for root, dirs, files in os.walk(path):
        for file in files:
            sequence.append(os.path.join(root, file))
    # print('sequence: {}'.format(sequence))
    producer(sequence, q)

    q.join()
    return None


if __name__ == '__main__':
    main()
