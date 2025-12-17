import json
import hashlib
from app import app


def test_empty_password():
    client = app.test_client()
    payload = {'passwords': ['']}
    rv = client.post('/api/hash', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    j = rv.get_json()
    assert j[0]['unsalted_sha256'] == hashlib.sha256(b'').hexdigest()


def test_non_string_password_converted():
    client = app.test_client()
    payload = {'passwords': [12345]}
    rv = client.post('/api/hash', data=json.dumps(payload), content_type='application/json')
    assert rv.status_code == 200
    j = rv.get_json()
    assert j[0]['password'] == '12345'


def test_long_password():
    client = app.test_client()
    long_pw = 'p' * 10000
    rv = client.post('/api/hash', data=json.dumps({'passwords': [long_pw]}), content_type='application/json')
    assert rv.status_code == 200
    j = rv.get_json()
    assert j[0]['unsalted_sha256'] == hashlib.sha256(long_pw.encode()).hexdigest()


def test_unicode_password():
    client = app.test_client()
    pw = 'pässwörd🔒'
    rv = client.post('/api/hash', data=json.dumps({'passwords': [pw]}), content_type='application/json')
    assert rv.status_code == 200
    j = rv.get_json()
    assert j[0]['unsalted_sha256'] == hashlib.sha256(pw.encode('utf-8')).hexdigest()
