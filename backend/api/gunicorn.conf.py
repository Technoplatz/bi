import os

bind = "0.0.0.0:80"
worker_class = "gevent"
# the in-memory rate limiter is per worker; keep one worker unless the limiter is moved to the database
workers = int(os.environ.get("API_WORKERS", "1"))
worker_connections = int(os.environ.get("API_WORKER_CONNECTIONS", "500"))
timeout = int(os.environ.get("API_REQUEST_TIMEOUT_SEC", "120"))
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("API_LOG_LEVEL", "info").lower()
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(L)ss'
