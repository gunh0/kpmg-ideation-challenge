"""gunicorn settings, read from the working directory when the server starts."""
import os

bind = "0.0.0.0:8000"
# Threads keep a slow request (a large export) from blocking a whole worker.
workers = int(os.environ.get("GUNICORN_WORKERS", 3))
threads = int(os.environ.get("GUNICORN_THREADS", 4))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 60))
accesslog = "-"
