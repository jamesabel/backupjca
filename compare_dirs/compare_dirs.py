
from enum import Enum, auto
import os
import argparse
import time
from functools import lru_cache
import platform
import time

from sundry import get_file_sha256, local_time_string, utc_time_string

from compare_dirs import __version__


class Compare(Enum):
    equal = auto()  # files are the same
    nonexistent = auto()  # doesn't exist
    different_sizes = auto()  # different sizes
    different_mtimes = auto()  # different mtimes
    different_hashes = auto()  # difference hashes


@lru_cache()
def is_windows():
    if platform.system().lower()[0] == 'w':
        return True
    return False


def to_long_path(path, no_long_path):
    if not no_long_path and is_windows():
        # https://docs.microsoft.com/en-us/windows/desktop/FileIO/naming-a-file#maxpath
        windows_long_path_prefix = "\\\\?\\"  # \\?\
        return windows_long_path_prefix + os.path.abspath(path)  # long path must be an absolute path
    return path


def log_differences(log_string, init_file=False):
    file_open_mode = 'a'
    if init_file:
        file_open_mode = 'w'
    with open('differences.txt', file_open_mode) as f:
        f.write(log_string)
        f.write('\n')


def _file_compare(source_path: str, destination_path: str, ignore_mtime: bool, use_hash: bool):
    comparison = Compare.equal

    source_size = os.path.getsize(source_path)
    try:
        destination_size = os.path.getsize(destination_path)
    except FileNotFoundError:
        destination_size = None

    if ignore_mtime:
        time_diff = None
    else:
        try:
            time_diff = abs(os.path.getmtime(source_path) - os.path.getmtime(destination_path))
        except FileNotFoundError:
            time_diff = None

    if use_hash:
        source_hash = get_file_sha256(source_path)
        try:
            destination_hash = get_file_sha256(destination_path)
        except FileNotFoundError:
            destination_hash = None
    else:
        source_hash = destination_hash = None

    if not os.path.exists(destination_path):
        comparison = Compare.nonexistent
        log_differences(f'destination path does not exist : "{destination_path}"')
    elif source_size != destination_size:
        comparison = Compare.different_sizes
        log_differences(f'different sizes : "{source_path}"={os.path.getsize(source_path)} , "{destination_path}"={os.path.getsize(destination_path)}')
    elif time_diff is not None and time_diff > 3.0:
        comparison = Compare.different_mtimes
        log_differences(f'different mtimes : "{source_path}" , "{destination_path}" (difference={time_diff})')
    elif destination_hash != source_hash:
        comparison = Compare.different_hashes
        log_differences(f'different hashes : "{source_path}:{source_hash}" , "{destination_path}:{destination_hash}"')
    return comparison, source_size


def compare_dirs(orig_source_dir: str, orig_destination_dir: str, ignore_mtime: bool, quiet: bool, use_hash: bool, no_long_path: bool):

    source_dir = to_long_path(orig_source_dir, no_long_path)
    destination_dir = to_long_path(orig_destination_dir, no_long_path)

    current_time = time.time()
    log_differences(f"{local_time_string(current_time)} ({utc_time_string(current_time)})", True)
    log_differences(f"source : {orig_source_dir} ({os.path.abspath(source_dir)})")
    log_differences(f"destination : {orig_destination_dir} ({os.path.abspath(destination_dir)})")
    source_dir = os.path.abspath(source_dir)
    destination_dir = os.path.abspath(destination_dir)

    last_dot = time.time()

    compare_count = 0
    miscompare_count = 0
    total_size = 0
    printed_a_dot = False
    for dir_path, _, file_names in os.walk(source_dir):
        for file_name in file_names:
            compare_count += 1
            file_path_a = os.path.join(dir_path, file_name)
            sub_dir = file_path_a[len(source_dir) + 1:]
            file_path_b = os.path.join(destination_dir, sub_dir)
            comparison, size = _file_compare(file_path_a, file_path_b, ignore_mtime, use_hash)
            total_size += size
            if comparison is not Compare.equal:
                miscompare_count += 1

            # print a dot every so often to show we're still alive
            if not quiet and compare_count % 2000 == 0 and time.time() - last_dot > 7.0:
                print('.', end='', flush=True)
                printed_a_dot = True
                last_dot = time.time()

    if printed_a_dot:
        print()
    for s in [f"total size (bytes) : {total_size}", f"total compares : {compare_count}", f"miscompares : {miscompare_count}"]:
        print(s)
        log_differences(s)

    return compare_count, miscompare_count


def main():

    parser = argparse.ArgumentParser(description=f'Verify all files in the source directory are in destination directory.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog=f'v{__version__}, www.abel.co, see github.com/jamesabel/backupjca for LICENSE.')
    parser.add_argument('path', nargs=2, help='paths (source, destination)')
    parser.add_argument('--ignore_mtime', action="store_true", default=False, help="ignore mtimes")
    parser.add_argument('--quiet', action="store_true", default=False, help="turns off status during run (e.g. status dots)")
    parser.add_argument('--use_hash', action="store_true", default=False, help="use hash for compares")
    parser.add_argument('--no_long_path', action="store_true", default=False, help="do not use long paths (affects Windows only)")
    args = parser.parse_args()

    compare_dirs(args.path[0], args.path[1], args.ignore_mtime, args.quiet, args.use_hash, args.no_long_path)


if __name__ == "__main__":
    main()
