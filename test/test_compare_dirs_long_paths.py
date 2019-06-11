
import os

from compare_dirs import compare_dirs, windows_long_path_prefix


def test_compare_dirs_long_paths():
    test_base_path = windows_long_path_prefix + os.path.abspath(os.path.join('test', 'data', 'long_paths'))

    test_path = test_base_path
    # longer than the Windows 260 character limit
    for _ in range(0, 30):
        test_path = os.path.join(test_path, 't23456789t')
    os.makedirs(test_path, exist_ok=True)
    test_path = os.path.join(test_path, 'temp.txt')

    print(test_path)
    with open(test_path, 'w') as f:
        f.write('testing')

    compare_count, micompare_count = compare_dirs(test_base_path, test_base_path, False, False, False, False, False)
    assert(compare_count > 0)
    assert(micompare_count == 0)


if __name__ == '__main__':
    test_compare_dirs_long_paths()
