import json
import hashlib

from app import app


def test_hash_endpoint_basic():
    client = app.test_client()
    payload = {'passwords': ['test123']}
    rv = client.post('/api/hash', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    j = rv.get_json()
    assert isinstance(j, list)
    assert len(j) == 1
    row = j[0]
    assert row['password'] == 'test123'
    # Unsalted should equal SHA256(password)
    expected_unsalted = hashlib.sha256(b'test123').hexdigest()
    assert row['unsalted_sha256'] == expected_unsalted
    # Salt should be hex string of 16 bytes
    assert isinstance(row['salted']['salt_hex'], str)
    assert len(row['salted']['salt_hex']) == 32
    # salted sha should equal sha256(salt + password)
    salt_bytes = bytes.fromhex(row['salted']['salt_hex'])
    salted_expected = hashlib.sha256(salt_bytes + b'test123').hexdigest()
    assert row['salted']['salted_sha256'] == salted_expected
    # Argon2 hash present
    assert 'argon2' in row['argon2_hash'].lower() or row['argon2_hash'].startswith('$argon2')
