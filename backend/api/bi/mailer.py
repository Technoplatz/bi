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

SMTP e-mail delivery.
"""

import os
import smtplib
from unidecode import unidecode
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pymongo

from bi import config as cfg
from bi.db import Mongo
from bi.errors import APIError
from bi.misc import Misc


class Email:
    """
    docstring is in progress
    """

    def send_email_f(self, msg):
        """
        docstring is in progress
        """
        try:
            op_ = msg["op"] if "op" in msg else None
            files_ = msg["files"] if "files" in msg and len(msg["files"]) > 0 else []
            html_ = f"{msg['html']} {cfg.EMAIL_DISCLAIMER_HTML_}" if "html" in msg else cfg.EMAIL_DISCLAIMER_HTML_
            tags_ = msg["tags"] if "tags" in msg and len(msg["tags"]) > 0 else None
            personalizations_ = msg["personalizations"] if "personalizations" in msg else []
            subject_ = msg["subject"] if "subject" in msg else None
            flag_ = "flag" in msg and msg["flag"] is True

            if subject_ is None:
                subject_ = (
                    cfg.EMAIL_UPLOADERR_SUBJECT_
                    if op_ in ["uploaderr", "importerr"]
                    else (
                        cfg.EMAIL_SIGNIN_SUBJECT_
                        if op_ == "signin" else (
                            cfg.EMAIL_TFA_SUBJECT_ if op_ == "tfa"
                            else (
                                cfg.EMAIL_SIGNUP_SUBJECT_
                                if op_ == "signup" else (msg["subject"] if msg["subject"] else cfg.EMAIL_DEFAULT_SUBJECT_)
                            )
                        )
                    )
                )

            if subject_ is None:
                raise APIError("subject is missing")

            que_id_ = msg["que_id"] if "que_id" in msg else "query"

            if html_ is None or html_ == "":
                raise APIError("email message is missing")

            if tags_:
                get_users_from_tags_f_ = Misc().get_users_from_tags_f(tags_)
                if not get_users_from_tags_f_["result"]:
                    raise APIError(f"personalizations error {get_users_from_tags_f_['msg']}")
                personalizations_ = (
                    get_users_from_tags_f_["personalizations"]
                    if "personalizations" in get_users_from_tags_f_ else None)

            if not personalizations_:
                raise APIError("email personalizations is missing")

            recipients_, to_ = [], []
            for recipient_ in personalizations_:
                recipients_.append(recipient_["email"])
                to_.append(
                    f"{unidecode(recipient_['name'])} <{recipient_['email']}>"
                    if "name" in recipient_ and recipient_["name"] != "" else recipient_["email"])

            if not recipients_:
                return {"result": True}

            message_ = MIMEMultipart()
            message_["From"] = f"{unidecode(cfg.COMPANY_NAME_)} <{cfg.FROM_EMAIL_}>"
            message_["Subject"] = unidecode(f"{cfg.EMAIL_SUBJECT_PREFIX_}{subject_}")
            message_["To"] = ", ".join(to_)

            if flag_:
                message_["X-Priority"] = "2"
                message_["X-Message-Flag"] = "Follow up"
                message_["Importance"] = "High"

            message_.attach(MIMEText(html_, "html"))

            for file_ in files_:
                filename_ = (file_["name"].replace(f"{cfg.API_TEMPFILE_PATH_}/", "") if "name" in file_ else None)
                if not filename_:
                    raise APIError("file not defined")
                fullpath_ = os.path.normpath(os.path.join(cfg.API_TEMPFILE_PATH_, filename_))
                if not fullpath_.startswith(cfg.TEMP_PATH_):
                    raise APIError("file path not allowed [email]")
                with open(fullpath_, "rb") as attachment_:
                    part_ = MIMEBase("application", "octet-stream")
                    part_.set_payload(attachment_.read())
                encoders.encode_base64(part_)
                part_.add_header("Content-Disposition", f"attachment; filename= {filename_}")
                message_.attach(part_)

            endpoint_ = smtplib.SMTP(cfg.SMTP_ENDPOINT_, cfg.SMTP_TLS_PORT_)
            endpoint_.ehlo()
            endpoint_.starttls()
            endpoint_.login(cfg.SMTP_USERID_, cfg.SMTP_PASSWORD_)
            endpoint_.sendmail(cfg.FROM_EMAIL_, recipients_, message_.as_string())
            endpoint_.close()

            if op_ == "query":
                Mongo().db_["_announcement"].insert_one({
                    "ano_id": Misc().get_timestamp_f(),
                    "ano_que_id": que_id_,
                    "ano_date": Misc().get_now_f(),
                    "ano_subject": subject_,
                    "ano_to": to_,
                    "files": files_,
                    "_tags": tags_,
                    "_created_at": Misc().get_now_f(),
                    "_created_by": "api",
                    "_modified_at": Misc().get_now_f(),
                    "_modified_by": "api",
                })

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except smtplib.SMTPResponseException as exc__:
            return Misc().notify_exception_f(f"smtp error: {exc__.smtp_error}")

        except smtplib.SMTPServerDisconnected as exc__:
            return {"result": True, "msg": str(exc__)}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)
