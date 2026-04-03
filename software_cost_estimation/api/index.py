import os
import sys

# Ensure project root is importable when running as a Vercel Function.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app as fastapi_app

# Vercel's Python runtime serves a top-level ASGI app named `app`.
app = fastapi_app
