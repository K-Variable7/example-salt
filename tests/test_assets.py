import os


def test_common_passwords_file_present():
    root = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(root, 'data', 'common_passwords.txt')
    assert os.path.exists(path), 'common_passwords.txt should exist'
    with open(path, 'r', encoding='utf-8') as fh:
        lines = [l.strip() for l in fh if l.strip()]
    assert len(lines) >= 20, 'expected a reasonable number of common passwords in the list'
