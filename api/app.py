from app import app as _app

# Vercel expects a top-level `app` for WSGI frameworks like Flask
app = _app
