
import os

from compare_dirs import compare_dirs, windows_long_path_prefix, ignore_files


def test_compare_dirs_ignore_files():
    test_base_path = windows_long_path_prefix + os.path.abspath(os.path.join('test', 'data', 'ignore_files'))
    os.makedirs(test_base_path, exist_ok=True)

    for ignore_file in ignore_files:
        with open(os.path.join(test_base_path, ignore_file), 'w') as f:
            f.write(ignore_file)

    for no_ignore_files in [True, False]:
        compare_count, micompare_count = compare_dirs(test_base_path, test_base_path, False, False, False, False, no_ignore_files)
        if no_ignore_files:
            assert(compare_count == len(ignore_files))
        else:
            assert(compare_count == 0)


if __name__ == '__main__':
    test_compare_dirs_ignore_files()
