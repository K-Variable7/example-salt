"""Test configuration helpers."""
import os
import sys

# Ensure project root (one level up from tests/) is first on sys.path so top-level
# modules (e.g., `app`, `scripts`) import cleanly during test collection.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import subprocess
import sys
import os
import time
import urllib.request
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))

@pytest.fixture(scope='session', autouse=True)
def server():
    """Start the Flask app before the test session and stop it after.

    The app is started using the current Python interpreter running `app.py`.
    """
    proc = subprocess.Popen([sys.executable, 'app.py'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the server to accept connections
    for _ in range(80):
        try:
            urllib.request.urlopen('http://127.0.0.1:5000', timeout=1)
            break
        except Exception:
            time.sleep(0.1)
    else:
        proc.kill()
        raise RuntimeError('Failed to start Flask app')

    yield

    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
