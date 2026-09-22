from gevent.pywsgi import WSGIServer

from bi import create_app

app = create_app()

if __name__ == "__main__":
    # development fallback; production runs gunicorn (see gunicorn.conf.py) and scheduler.py separately
    http_server = WSGIServer(("0.0.0.0", 80), app)
    http_server.serve_forever()
