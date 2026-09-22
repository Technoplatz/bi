"""
Technoplatz BI

Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see https://www.gnu.org/licenses.

If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "Source" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
https://www.gnu.org/licenses.

Application factory for the Technoplatz BI api.
"""

import logging
import os

from flask import Flask
from flask_cors import CORS

from bi import config as cfg
from bi.routes import bp


def configure_logging(level_=None):
    """
    one consistent line format for the api and the scheduler; gunicorn reuses the root handlers
    """
    level_ = level_ or os.environ.get("API_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level_, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def create_app():
    """
    builds the Flask application with cors, upload limits and the api blueprint
    """
    configure_logging()
    app = Flask(__name__)
    app.config["CORS_SUPPORTS_CREDENTIALS"] = True
    app.config["MAX_CONTENT_LENGTH"] = cfg.API_MAX_CONTENT_LENGTH_MB_ * 1024 * 1024
    app.config["CORS_ORIGINS"] = cfg.API_CORS_ORIGINS_
    app.config["UPLOAD_FOLDER"] = cfg.API_TEMPFILE_PATH_
    app.config["CORS_HEADERS"] = cfg.CORS_HEADERS_
    app.config["UPLOAD_EXTENSIONS"] = cfg.UPLOAD_EXTENSIONS_
    CORS(app)
    app.register_blueprint(bp)
    return app
