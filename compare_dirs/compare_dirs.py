
from enum import Enum, auto
import os
import argparse
import time


class Compare(Enum):
    equal = auto()  # files are the same
    nonexistent = auto()  # doesn't exist
    different_sizes = auto()  # different sizes
    different_mtimes = auto()  # different mtimes


def log_differences(log_string, init_file=False):
    file_open_mode = 'a'
    if init_file:
        file_open_mode = 'w'
    with open('differences.txt', file_open_mode) as f:
        f.write(log_string)
        f.write('\n')


def _file_compare(path_a: str, path_b: str, ignore_mtime: bool):
    comparison = Compare.equal
    if not os.path.exists(path_a):
        comparison = Compare.nonexistent
        log_differences(f'path does not exist : "{path_a}"')
    elif not os.path.exists(path_b):
        comparison = Compare.nonexistent
        log_differences(f'path does not exist : "{path_b}"')
    elif os.path.getsize(path_a) != os.path.getsize(path_b):
        comparison = Compare.different_sizes
        log_differences(f'different sizes : "{path_a}"={os.path.getsize(path_a)} , "{path_b}"={os.path.getsize(path_b)}')
    elif not ignore_mtime:
        time_diff = abs(os.path.getmtime(path_a) - os.path.getmtime(path_b))
        if time_diff > 3.0:
            comparison = Compare.different_mtimes
            log_differences(f'different mtimes : "{path_a}" , "{path_b}" (difference={time_diff})')
    return comparison


def compare_dirs(source_dir: str, destination_dir: str, ignore_mtime: bool):

    log_differences(f"source : {source_dir} ({os.path.abspath(source_dir)})", True)
    log_differences(f"destination : {destination_dir} ({os.path.abspath(destination_dir)})")
    source_dir = os.path.abspath(source_dir)
    destination_dir = os.path.abspath(destination_dir)

    last_dot = time.time()

    compare_count = 0
    miscompare_count = 0
    printed_a_dot = False
    for dir_path, _, file_names in os.walk(source_dir):
        for file_name in file_names:
            compare_count += 1
            file_path_a = os.path.join(dir_path, file_name)
            sub_dir = file_path_a[len(source_dir) + 1:]
            file_path_b = os.path.join(destination_dir, sub_dir)
            if _file_compare(file_path_a, file_path_b, ignore_mtime) is not Compare.equal:
                miscompare_count += 1

            # print a dot every so often to show we're still alive
            if compare_count % 2000 == 0 and time.time() - last_dot > 7.0:
                print('.', end='', flush=True)
                printed_a_dot = True
                last_dot = time.time()

    if printed_a_dot:
        print()
    for s in [f"total compares : {compare_count}", f"miscompares : {miscompare_count}"]:
        print(s)
        log_differences(s)

    return compare_count, miscompare_count


def main():

    parser = argparse.ArgumentParser(description='Verify all files in the source directory are in destination directory.')
    parser.add_argument('paths', nargs=2, help='paths (source, destination)')
    parser.add_argument('--ignore_mtime', action="store_true", default=False, help="ignore mtimes")
    args = parser.parse_args()

    compare_dirs(args.paths[0], args.paths[1], args.ignore_mtime)


if __name__ == "__main__":
    main()
