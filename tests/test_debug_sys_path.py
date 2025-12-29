import sys


def test_print_sys_path():
    # This test helps debug import issues by exposing pytest's sys.path during test run
    # It intentionally asserts True so it doesn't fail the suite
    print("\nPYTEST_SYS_PATH:")
    for p in sys.path:
        print(p)
    assert True
