
from sundry import to_bool

from backupjca import compare_dirs


def test_compare_dirs():

    for test_type in range(0, 32):

        use_mtime = to_bool(test_type & 1)
        quiet = to_bool(test_type & 2 == 2)
        use_hash = to_bool(test_type & 4 == 4)
        no_long_path = to_bool(test_type & 8 == 8)
        no_ignore_files = to_bool((test_type & 16 == 16))

        compare_count, micompare_count = compare_dirs("venv", "venv", use_mtime, quiet, use_hash, no_long_path, no_ignore_files)
        assert(compare_count > 0)
        assert(micompare_count == 0)

        compare_count, micompare_count = compare_dirs("test", "venv", use_mtime, quiet, use_hash, no_long_path, no_ignore_files)
        assert(compare_count > 0)
        assert(micompare_count > 0)

        compare_count, micompare_count = compare_dirs("venv", "test", use_mtime, quiet, use_hash, no_long_path, no_ignore_files)
        assert(compare_count > 0)
        assert(micompare_count > 0)


if __name__ == "__main__":
    test_compare_dirs()
