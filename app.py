from flask import Flask, request, jsonify, render_template
import os
import hashlib
import binascii
from argon2 import PasswordHasher

app = Flask(__name__, static_folder='static', template_folder='templates')
ph = PasswordHasher()


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/hash', methods=['POST'])
def api_hash():
    data = request.get_json(force=True)
    passwords = data.get('passwords') or []
    result = []
    for pwd in passwords:
        if not isinstance(pwd, str):
            pwd = str(pwd)
        raw = pwd.encode('utf-8')
        # Unsalted (insecure) — SHA-256 of the password
        unsalted = sha256_hex(raw)
        # Salted with a per-password 128-bit (16 byte) salt using CSPRNG
        salt = os.urandom(16)  # 128 bits
        salted_sha256 = sha256_hex(salt + raw)
        salt_hex = binascii.hexlify(salt).decode()
        # Argon2 hash (uses its own internal salt)
        argon2_hash = ph.hash(pwd)
        result.append({
            'password': pwd,
            'unsalted_sha256': unsalted,
            'salted': {
                'salt_hex': salt_hex,
                'salted_sha256': salted_sha256
            },
            'argon2_hash': argon2_hash
        })
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
