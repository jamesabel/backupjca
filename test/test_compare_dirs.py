
from compare_dirs import compare_dirs


def test_compare_dirs():
    compare_count, micompare_count = compare_dirs("venv", "venv", False)
    assert(compare_count > 0)
    assert(micompare_count == 0)

    compare_count, micompare_count = compare_dirs("test", "venv", False)
    assert(compare_count > 0)
    assert(micompare_count > 0)


if __name__ == "__main__":
    test_compare_dirs()
