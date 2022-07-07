import os
from dataclasses import asdict, dataclass
from hashlib import (md5, sha1, sha224, sha256, sha384, sha512,
                     sha3_224, sha3_256, sha3_384, sha3_512)
from time import perf_counter
from typing import Callable, Union

from config import TestHashSpeed

BLOCK_SIZE: int = 1024  # one kbyte

HASH_ALGOS: tuple[Callable, ...] = (
    md5, sha1, sha224, sha256, sha384, sha512,
    sha3_224, sha3_256, sha3_384, sha3_512,
    )

SIZES: dict[Union[int, None], str] = {
    1024: '1 Kbyte',
    1048576: '1 Mbyte',
    5242880: '5 Mbyte',
    10485760: '10 Mbyte',
    None: 'Entire file',
    }

# one kbyte, one mbyte, five mbyte, ten mbyte, entire file
BLOCK_SIZES: tuple[Union[int, None], ...] = (
    1024,
    1024 ** 2,
    1024 ** 2 * 5,
    1024 ** 2 * 10,
    None
    )


@dataclass
class TestResult:
    hash_algo: str
    size_bytes: int
    elapsed_time: float
    speed_bytes: float
    speed_mbytes: float
    INFO_MESSAGE: str = ('Algo: {hash_algo:<16}, '
                         'Size: {size_bytes}, '
                         'Time: {elapsed_time:<.20f}, '
                         'Speed (bytes/s): {speed_bytes:<.10f}, '
                         'Speed (Mbytes/s): {speed_mbytes:<.10f}.')

    def __repr__(self) -> str:
        return self.INFO_MESSAGE.format(**asdict(self))


def get_hash(path_to_file: str,
             hash_algo: Callable = sha256,
             block_size: Union[int, None] = BLOCK_SIZE,
             ) -> str:
    hasher: Callable = hash_algo()
    with open(path_to_file, 'br') as source:
        while chunk := source.read(block_size):
            hasher.update(chunk)  # type: ignore
    return hasher.hexdigest()  # type: ignore


def test_speed(path_to_folder: str,
               hash_algo: Callable,
               block_size: Union[int, None]) -> TestResult:
    total_size_file_processed: int = 0
    time_start: float = perf_counter()
    for root, dirs, files in os.walk(path_to_folder):
        for file in files:
            if file.startswith('.'):
                continue
            path_to_file: str = os.path.join(root, file)
            size: int = os.stat(path_to_file).st_size
            total_size_file_processed += size
            get_hash(path_to_file, hash_algo, block_size)
    elapsed_time: float = perf_counter() - time_start
    hash_speed_bytes: float = total_size_file_processed / elapsed_time
    hash_speed_mbytes: float = hash_speed_bytes / 1024 / 1024
    return TestResult(hash_algo.__name__,
                      total_size_file_processed,
                      elapsed_time,
                      hash_speed_bytes,
                      hash_speed_mbytes)


if __name__ == '__main__':
    print('*' * 125)

    test_config: TestHashSpeed = TestHashSpeed()
    test_folder: str = os.path.expanduser(test_config.TEST_FOLDER)
    result_template: str = '{block_size_named!r:<14} {result}'

    for hash_algo in HASH_ALGOS:
        for block_size in BLOCK_SIZES:
            result = test_speed(test_folder, hash_algo, block_size)
            block_size_named = SIZES.get(block_size)
            print(result_template.format(block_size_named=block_size_named,
                                         result=result))

    print('-' * 125)
