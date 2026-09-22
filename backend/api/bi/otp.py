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

E-mail and TOTP second factor handling.
"""

import secrets
import pymongo
import pyotp

from bi.db import Mongo
from bi.errors import APIError, AuthError
from bi.mailer import Email
from bi.misc import Misc


class OTP:
    """
    docstring is in progress
    """

    def reset_otp_f(self, email_):
        """
        docstring is in progress
        """
        try:
            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found to reset otp")

            aut_otp_secret_ = pyotp.random_base32()
            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=email_, issuer_name="Technoplatz-BI")

            Mongo().db_["_auth"].update_one(
                {"aut_id": email_},
                {
                    "$set": {
                        "aut_otp_secret": aut_otp_secret_,
                        "aut_otp_validated": False,
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": email_,
                        "_otp_secret_modified_at": Misc().get_now_f(),
                        "_otp_secret_modified_by": email_,
                    },
                    "$inc": {"_modified_count": 1},
                },
            )

            return {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def validate_qr_f(self, email_, request_):
        """
        docstring is in progress
        """
        try:
            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            aut_otp_secret_ = auth_["aut_otp_secret"] if "aut_otp_secret" in auth_ else None
            if not aut_otp_secret_:
                raise AuthError("otp secret is missing")

            otp_ = request_["otp"] if "otp" in request_ else None
            if not otp_:
                raise AuthError("otp is missing")

            totp_ = pyotp.TOTP(aut_otp_secret_)
            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=email_, issuer_name="BI")

            validated_ = False

            if totp_.verify(otp_):
                validated_ = True
                Mongo().db_["_auth"].update_one(
                    {"aut_id": email_},
                    {
                        "$set": {
                            "aut_otp_validated": validated_,
                            "_otp_validated_at": Misc().get_now_f(),
                            "_otp_validated_by": email_,
                            "_otp_validated_ip": Misc().get_client_ip_f(),
                        },
                        "$inc": {"_modified_count": 1},
                    },
                )
            else:
                Mongo().db_["_auth"].update_one(
                    {"aut_id": email_},
                    {
                        "$set": {
                            "aut_otp_validated": validated_,
                            "_otp_not_validated_at": Misc().get_now_f(),
                            "_otp_not_validated_by": email_,
                            "_otp_not_validated_ip": Misc().get_client_ip_f(),
                        },
                        "$inc": {"_modified_count": 1},
                    },
                )
                raise AuthError("invalid otp")

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": "_auth",
                    "op": "validate-otp",
                    "user": email_,
                    "document": {
                        "success": validated_,
                        "ip": Misc().get_client_ip_f(),
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": email_,
                    },
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "success": validated_, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def show_otp_f(self, email_):
        """
        docstring is in progress
        """
        try:
            # read auth
            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            aut_otp_secret_ = (
                auth_["aut_otp_secret"] if "aut_otp_secret" in auth_ else None
            )

            if not aut_otp_secret_:
                reset_otp_f_ = self.reset_otp_f(email_)
                if not reset_otp_f_["result"]:
                    raise APIError(reset_otp_f_["msg"])
                qr_ = reset_otp_f_["qr"]
            else:
                qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(
                    name=email_, issuer_name="Technoplatz-BI"
                )

            return {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def request_otp_f(self, email_):
        """
        docstring is in progress
        """
        try:
            user_ = (
                Mongo()
                .db_["_user"]
                .find_one(
                    {
                        "usr_id": email_,
                        "usr_enabled": True,
                        "usr_scope": {"$in": ["Internal", "Administrator"]},
                    }
                )
            )
            if not user_ or user_ is None:
                raise APIError("user not found")

            usr_id_ = user_["usr_id"]
            name_ = user_["usr_name"]
            tfac_ = secrets.randbelow(900000) + 100000
            Mongo().db_["_auth"].update_one(
                {"aut_id": usr_id_},
                {
                    "$set": {
                        "aut_tfac": tfac_,
                        "aut_tfac_attempts": 0,
                        "_tfac_modified_at": Misc().get_now_f(),
                    },
                    "$inc": {"_modified_count": 1},
                },
            )
            email_sent_ = Email().send_email_f(
                {"op": "tfa", "personalizations": [{"email": usr_id_, "name": name_}],
                 "html":
                 f"<p>Hi {name_},</p><p>Here's your two-factor access code so that you can validate your account;</p><p><h1>{tfac_}</h1></p>",
                 "subject": "Account [OTP]", })
            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)
