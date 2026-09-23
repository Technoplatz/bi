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

Sign-up, sign-in, sessions, permissions and the ip firewall.
"""

import os
import re
import secrets
import hashlib
from datetime import timedelta
import pymongo
import pyotp
import jwt
from flask import request

from bi import config as cfg
from bi.db import Mongo
from bi.errors import APIError, AuthError, PassException
from bi.mailer import Email
from bi.misc import Misc
from bi.otp import OTP


class Auth:
    """
    docstring is in progress
    """

    def is_admin_f(self, user_):
        """
        docstring is in progress
        """
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        in_admin_tags_ = any(tag_ in tags_ for tag_ in cfg.API_ADMIN_TAGS_)
        in_admin_ips_ = Misc().in_admin_ips_f()
        return in_admin_tags_ and in_admin_ips_

    def is_manager_f(self, user_):
        """
        docstring is in progress
        """
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        in_permissive_tags_ = any(tag_ in tags_ for tag_ in cfg.API_PERMISSIVE_TAGS_)
        in_admin_ips_ = Misc().in_admin_ips_f()
        return in_permissive_tags_ and in_admin_ips_

    def is_qadmin_f(self, user_):
        """
        docstring is in progress
        """
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        in_qadmin_tags_ = any(tag_ in tags_ for tag_ in cfg.API_QADMIN_TAGS_)
        return in_qadmin_tags_

    def access_validate_by_api_token_f(self, bearer_, operation_, qid_):
        """
        docstring is in progress
        """
        try:
            ip_ = Misc().get_client_ip_f()
            token__ = re.split(" ", bearer_)
            token_ = token__[1] if token__ and len(token__) > 0 and token__[0].lower() == "bearer" else None
            if not token_:
                raise AuthError("token not found")

            header_ = jwt.get_unverified_header(token_)
            token_finder_ = header_["finder"] if "finder" in header_ and header_["finder"] is not None else None
            if not token_finder_:
                raise AuthError("please use an api access token")

            find_ = (
                Mongo()
                .db_["_token"]
                .find_one({"tkn_finder": token_finder_, "tkn_is_active": True})
            )
            if not find_:
                raise AuthError("invalid token")
            jwt_secret_ = find_["tkn_secret"]

            options_ = {"iss": "Technoplatz", "aud": "api", "sub": "bi"}
            jwt_proc_f_ = Misc().jwt_proc_f("decode", token_, jwt_secret_, options_, None)

            if not jwt_proc_f_["result"]:
                raise AuthError(jwt_proc_f_["msg"])

            grant_ = f"tkn_grant_{operation_}"
            if not find_[grant_]:
                raise AuthError(f"token is not allowed to perform {operation_}")

            if (qid_ and "tkn_allowed_queries" in find_ and len(find_["tkn_allowed_queries"]) > 0):
                if qid_ not in find_["tkn_allowed_queries"]:
                    raise AuthError(f"token is not allowed to read {qid_}")

            if not (
                "tkn_allowed_ips" in find_
                and len(find_["tkn_allowed_ips"]) > 0
                and (ip_ in find_["tkn_allowed_ips"] or "0.0.0.0" in find_["tkn_allowed_ips"])
            ):
                raise AuthError(f"IP is not allowed to do {operation_}")

            return {"result": True, "token": find_}

        except AuthError as exc__:
            return {"result": False, "msg": str(exc__)}

        except jwt.ExpiredSignatureError as exc__:
            return {"result": False, "msg": str(exc__)}

        except jwt.InvalidTokenError as exc__:
            return {"result": False, "msg": str(exc__)}

        except Exception as exc__:
            return {"result": False, "msg": str(exc__)}

    def verify_otp_f(self, email_, tfac_, op_):
        """
        docstring is in progress
        """
        try:
            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError(f"user auth not found {email_}")

            compile_ = re.compile("^[0-9]{6,6}$")
            if not re.search(compile_, str(tfac_)):
                raise AuthError("invalid otp format")

            aut_otp_secret_ = auth_["aut_otp_secret"] if "aut_otp_secret" in auth_ and auth_["aut_otp_secret"] is not None else None
            aut_tfac_ = auth_["aut_tfac"] if "aut_tfac" in auth_ and auth_["aut_tfac"] is not None else None
            if not aut_tfac_:
                raise AuthError("otp not provided")

            age_ = Misc().age_minutes_f(auth_["_tfac_modified_at"] if "_tfac_modified_at" in auth_ else None)
            if age_ is None or age_ > cfg.API_OTP_EXP_MINUTES_ or age_ < 0:
                Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {"aut_tfac": None}})
                raise AuthError("otp expired, please request a new code")

            attempts_ = int(auth_["aut_tfac_attempts"]) if "aut_tfac_attempts" in auth_ and auth_["aut_tfac_attempts"] else 0
            if attempts_ >= cfg.API_OTP_MAX_ATTEMPTS_:
                Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {"aut_tfac": None}})
                raise AuthError("too many invalid attempts, please request a new code")

            otp_validated_ = "aut_otp_validated" in auth_ and auth_["aut_otp_validated"] is True
            if not secrets.compare_digest(str(aut_tfac_), str(tfac_)):
                # an authenticator code is checked without side effects: validate_qr_f would
                # clear the pairing on a mistyped code
                totp_ok_ = bool(aut_otp_secret_ and otp_validated_ and pyotp.TOTP(aut_otp_secret_).verify(str(tfac_), valid_window=1))
                if not totp_ok_:
                    Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$inc": {"aut_tfac_attempts": 1}})
                    raise AuthError("invalid otp")

            Mongo().db_["_auth"].update_one(
                {"aut_id": email_},
                {
                    "$set": {
                        "aut_tfac": None,
                        "aut_tfac_attempts": 0,
                        "aut_tfac_ex": aut_tfac_,
                        "_modified_at": Misc().get_now_f(),
                    },
                    "$inc": {"_modified_count": 1},
                },
            )

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except AuthError as exc__:
            Misc().log_f(
                {
                    "type": "Error",
                    "collection": "_auth",
                    "op": op_,
                    "user": email_,
                    "document": {
                        "exception": str(exc__),
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": email_,
                    },
                }
            )
            return Misc().auth_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def checkup_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            if "email" not in input_ or input_["email"] is None:
                raise APIError("E-mail is missing")
            if "name" not in input_ or input_["name"] is None:
                raise APIError("full name is missing")
            pat = re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
            if not re.search(pat, input_["email"]):
                raise APIError("invalid e-mail address")
            if "password" not in input_ or input_["password"] is None:
                raise APIError("invalid email or password")

            return {"result": True}

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def password_hash_f(self, password_, salted_):
        """
        docstring is in progress
        """
        try:
            pat = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z0-9@$!#%*.-_?&]{8,32}$")
            if not re.search(pat, password_):
                raise APIError("Invalid password")

            salt_ = os.urandom(32) if salted_ is None else salted_
            key_ = hashlib.pbkdf2_hmac("sha512", password_.encode("utf-8"), salt_, 101010, dklen=128)

            return {"result": True, "salt": salt_, "key": key_}

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def signout_f(self, auth_):
        """
        docstring is in progress
        """
        try:
            aut_id_ = auth_["aut_id"]
            Mongo().db_["_auth"].update_one(
                {"aut_id": aut_id_},
                {
                    "$set": {
                        "aut_jwt_secret": None,
                        "aut_jwt_token": None,
                        "aut_tfac": None,
                        "_signed_out_at": Misc().get_now_f(),
                    },
                    "$inc": {"_modified_count": 1},
                },
            )
            return {"result": True, "user": None}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def permission_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["user"]
            user_id_ = user_["usr_id"] if "usr_id" in user_ else None
            usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
            collection_id_ = input_["collection"] if "collection" in input_ and input_["collection"] is not None else None
            op_ = input_["op"] if "op" in input_ else None
            adminops_ = ["dumpu", "dumpr"]
            read_permissive_colls_ = ["_collection", "_query", "_announcement"]
            read_permissive_ops_ = ["read", "query", "savequery", "savejob", "queries",
                                    "collection", "collections", "announcements", "visuals", "visual", ]
            insert_permissive_ops_ = ["clone"]
            is_crud_ = collection_id_ and collection_id_[:1] != "_"
            allowmatch_ = []

            if not op_:
                raise APIError("no operation provided")

            if not user_id_:
                raise APIError(f"no user defined: {user_id_}")

            if not collection_id_:
                raise AuthError("no collection provided")

            if Auth().is_admin_f(user_):
                return {"result": True}

            if op_ in adminops_:
                raise AuthError(f"{op_} is not allowed")

            if Auth().is_manager_f(user_):
                return {"result": True}

            if op_ in read_permissive_ops_ and collection_id_ in read_permissive_colls_:
                return {"result": True}

            if not is_crud_ and collection_id_ != "_query":
                raise AuthError(f"collection is not allowed to {op_}")

            if op_ in read_permissive_ops_:
                op_ = "read"

            if op_ in insert_permissive_ops_:
                op_ = "insert"

            permit_ = False
            for usr_tag_ in usr_tags_:
                permission_ = (
                    Mongo()
                    .db_["_permission"]
                    .find_one(
                        {
                            "per_collection_id": collection_id_,
                            "per_is_active": True,
                            "per_tag": usr_tag_,
                        }
                    )
                )
                if permission_:
                    per_insert_ = (
                        "per_insert" in permission_
                        and permission_["per_insert"] is True
                    )
                    per_read_ = (
                        "per_read" in permission_ and permission_[
                            "per_read"] is True
                    )
                    per_update_ = (
                        "per_update" in permission_
                        and permission_["per_update"] is True
                    )
                    per_delete_ = (
                        "per_delete" in permission_
                        and permission_["per_delete"] is True
                    )
                    per_action_ = (
                        "per_action" in permission_
                        and permission_["per_action"] is True
                    )
                    per_query_ = (
                        "per_query" in permission_ and permission_[
                            "per_query"] is True
                    )
                    if (
                        (op_ == "read" and per_read_)
                        or (op_ in ["savequery", "savejob"] and per_query_)
                        or (op_ == "insert" and per_insert_ and per_read_)
                        or (op_ == "import" and per_insert_ and per_read_)
                        or (op_ == "update" and per_update_ and per_read_)
                        or (op_ == "action" and per_action_ and per_read_)
                        or (op_ == "clone" and per_insert_ and per_read_)
                        or (op_ == "delete" and per_read_ and per_delete_)
                    ):
                        permit_ = True
                        per_match_ = (
                            permission_["per_match"]
                            if "per_match" in permission_
                            and len(permission_["per_match"]) > 0
                            and op_ != "action"
                            else None
                        )
                        if per_match_:
                            allowmatch_ = per_match_
                        break

            if not permit_:
                raise AuthError(
                    f"user is not allowed to perform this operation")

            return {"result": True, "allowmatch": allowmatch_}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def firewall_f(self, user_):
        """
        docstring is in progress
        """
        try:
            ip_ = Misc().get_client_ip_f()
            tags_ = (user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else [])
            allowed_ = (
                Mongo()
                .db_["_firewall"]
                .find_one(
                    {
                        "fwa_source_ip": ip_,
                        "fwa_enabled": True,
                        "_tags": {"$elemMatch": {"$in": tags_}},
                    }
                )
            )
            if not allowed_:
                if not Misc().in_admin_ips_f():
                    raise AuthError(f"connection is not allowed from {ip_}")

            return {"result": True}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except AuthError as exc__:
            Misc().log_f(
                {
                    "type": "Error",
                    "collection": "_firewall",
                    "op": "block",
                    "user": user_["usr_id"],
                    "document": {
                        "ip": ip_,
                        "exception": str(exc__),
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": user_["usr_id"],
                    },
                }
            )
            return Misc().auth_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def forgot_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            if "email" not in input_ or input_["email"] is None:
                raise APIError("e-mail is missing")

            email_ = Misc().clean_f(input_["email"])

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if auth_:
                otp_send_ = OTP().request_otp_f(email_)
                if not otp_send_["result"]:
                    raise APIError(otp_send_["msg"])
            else:
                Misc().log_f({"type": "Info", "collection": "_auth", "op": "forgot", "user": email_,
                              "document": {"exception": "unknown account", "_modified_at": Misc().get_now_f()}})

            # L-4: identical answer for known and unknown addresses
            return {"result": True, "user": None, "msg": "if the account exists, a code has been e-mailed"}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def reset_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            email_ = Misc().clean_f(input_["email"])
            password_ = str(input_["password"]).strip()
            tfac_ = Misc().clean_f(input_["tfac"])

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, "reset")
            if not verify_otp_f_["result"]:
                raise AuthError(verify_otp_f_["msg"])

            hash_f_ = self.password_hash_f(password_, None)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])

            salt_ = hash_f_["salt"]
            key_ = hash_f_["key"]

            Mongo().db_["_auth"].update_one(
                {"aut_id": email_},
                {
                    "$set": {
                        "aut_salt": salt_,
                        "aut_key": key_,
                        "aut_tfac": None,
                        "aut_expires": 0,
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": email_,
                    },
                    "$inc": {"_modified_count": 1},
                },
            )

            return {"result": True, "user": None}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def tfac_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            email_ = Misc().clean_f(input_["email"])
            password_ = str(input_["password"]).strip()
            tfac_ = Misc().clean_f(input_["tfac"])

            user_validate_ = self.user_validate_by_auth_f({"userid": email_, "password": password_})
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])

            user_ = user_validate_["user"] if "user" in user_validate_ else None
            auth_ = user_validate_["auth"] if "auth" in user_validate_ else None

            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, "signin")
            if not verify_otp_f_["result"]:
                raise AuthError(verify_otp_f_["msg"])

            usr_name_ = user_["usr_name"]
            locale_ = user_["usr_locale"] if "usr_locale" in user_ else cfg.DEFAULT_LOCALE_
            perm_ = Auth().is_manager_f(user_) or Auth().is_admin_f(user_)
            perma_ = Auth().is_admin_f(user_)
            permqa_ = Auth().is_qadmin_f(user_)

            payload_ = {
                "iss": "Technoplatz",
                "aud": "api",
                "sub": "bi",
                "exp": Misc().get_now_f() + timedelta(minutes=int(cfg.API_SESSION_EXP_MINUTES_)),
                "iat": Misc().get_now_f(),
                "id": email_,
                "name": usr_name_,
                "perm": perm_,
                "perma": perma_,
                "permqa": permqa_
            }
            secret_ = pyotp.random_base32()
            jwt_proc_f_ = Misc().jwt_proc_f("encode", None, secret_, payload_, None)
            if not jwt_proc_f_["result"]:
                raise AuthError(jwt_proc_f_["msg"])
            token_ = jwt_proc_f_["jwt"]

            api_key_ = (
                auth_["aut_api_key"]
                if "aut_api_key" in auth_ and auth_["aut_api_key"] is not None
                else None
            )
            if api_key_ is None:
                api_key_ = secrets.token_hex(16)

            Mongo().db_["_auth"].update_one(
                {"aut_id": email_},
                {
                    "$set": {
                        "aut_jwt_secret": secret_,
                        "aut_jwt_token": None,
                        "aut_tfac": None,
                        "aut_verified": True,
                        "aut_api_key": api_key_,
                        "_modified_at": Misc().get_now_f(),
                        "_jwt_at": Misc().get_now_f(),
                    },
                    "$inc": {"_modified_count": 1},
                },
            )

            ip_ = Misc().get_client_ip_f()
            user_payload_ = {
                "token": token_,
                "name": usr_name_,
                "email": email_,
                "perm": perm_,
                "perma": perma_,
                "permqa": permqa_,
                "api_key": api_key_,
                "ip": ip_,
                "locale": locale_,
            }

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": "_auth",
                    "op": "signin",
                    "user": email_,
                    "document": {
                        "_signedin_at": Misc().get_now_f(),
                        "ip": ip_,
                        "perm": perm_,
                        "perma": perma_,
                        "permqa": permqa_,
                    },
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            if (
                "_otp_validated_ip" in auth_
                and auth_["_otp_validated_ip"] is not None
                and auth_["_otp_validated_ip"] != ip_
            ):
                email_sent_ = Email().send_email_f(
                    {
                        "op": "signin",
                        "personalizations": [{"email": email_, "name": usr_name_}],
                        "html": f"<p>Hi {usr_name_},<br /><br />You have now signed-in from {ip_}.</p>",
                        "subject": "Account [Sign-in Reminder]",
                    }
                )
                if not email_sent_["result"]:
                    raise APIError(email_sent_["msg"])

            return {"result": True, "user": user_payload_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def jwt_validate_f(self):
        """
        docstring is in progress
        """
        try:
            authorization_ = request.headers.get("Authorization", None)
            if not authorization_:
                raise AuthError("authorization required")

            authb_ = "Bearer "
            ix_ = authorization_.find(authb_)
            if ix_ != 0:
                raise PassException("invalid access token")

            token_ = authorization_.replace(authb_, "")
            if not token_:
                raise PassException("no access token provided")

            x_api_key_ = request.headers.get("X-Api-Key", None)
            if not x_api_key_:
                raise AuthError("no api key provided")

            auth_ = Mongo().db_["_auth"].find_one({"aut_api_key": x_api_key_})
            if not auth_:
                raise AuthError("account not found")
            aut_id_ = auth_["aut_id"]

            jwt_secret_ = (
                auth_["aut_jwt_secret"]
                if "aut_jwt_secret" in auth_ and auth_["aut_jwt_secret"] is not None
                else None
            )

            options_ = {"iss": "Technoplatz", "aud": "api", "sub": "bi"}
            jwt_proc_f_ = Misc().jwt_proc_f("decode", token_, jwt_secret_, options_, None)
            if not jwt_proc_f_["result"]:
                raise PassException(jwt_proc_f_["msg"])

            claims_ = jwt_proc_f_["jwt"]
            usr_id_ = claims_["id"] if "id" in claims_ and claims_["id"] is not None else None
            if not usr_id_:
                raise PassException("invalid user token")

            if usr_id_ != aut_id_:
                raise PassException("invalid user validation")

            user_ = (
                Mongo()
                .db_["_user"]
                .find_one(
                    {
                        "usr_id": aut_id_,
                        "usr_enabled": True,
                        "usr_scope": {"$in": ["Internal", "Administrator"]},
                    }
                )
            )
            if not user_:
                raise AuthError("user not found")

            user_["email"] = user_["usr_id"]
            user_["api_key"] = auth_["aut_api_key"]

            return {"result": True, "user": user_, "auth": auth_}

        except PassException as exc__:
            return Misc().pass_exception_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except Exception as exc__:
            return {"result": False, "msg": "invalid session", "exc": str(exc__)}

    def user_validate_by_auth_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_id_ = input_["userid"] if "userid" in input_ else None
            password_ = input_["password"] if "password" in input_ else None
            if not password_ or not user_id_:
                raise AuthError("invalid user credentials")

            pat_ = re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
            if not re.search(pat_, user_id_):
                raise AuthError("invalid user id")

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": user_id_})
            if not auth_:
                raise AuthError("invalid email or password")

            user_ = (
                Mongo()
                .db_["_user"]
                .find_one(
                    {
                        "usr_id": user_id_,
                        "usr_enabled": True,
                        "usr_scope": {"$in": ["Internal", "Administrator"]},
                    }
                )
            )
            if not user_:
                raise AuthError("invalid email or password")

            firewall_f_ = self.firewall_f(user_)
            if not firewall_f_["result"]:
                raise AuthError(firewall_f_["msg"])

            # salt and key are raw bytes; stripping them corrupts values that begin or end with whitespace bytes
            aut_salt_ = auth_["aut_salt"] if "aut_salt" in auth_ and auth_["aut_salt"] is not None else None
            aut_key_ = auth_["aut_key"] if "aut_key" in auth_ and auth_["aut_key"] is not None else None
            if isinstance(aut_salt_, str):
                aut_salt_ = aut_salt_.strip().encode("utf-8")
            if isinstance(aut_key_, str):
                aut_key_ = aut_key_.strip().encode("utf-8")
            if not aut_salt_ or not aut_key_:
                raise AuthError("please set a new password")

            hash_f_ = self.password_hash_f(password_, aut_salt_)
            if not hash_f_["result"]:
                raise AuthError(hash_f_["msg"])

            new_key_ = hash_f_["key"]
            if not secrets.compare_digest(new_key_, aut_key_):
                # L-3: older records were hashed on the html-escaped password; accept once and re-hash raw
                legacy_ = Misc().clean_f(password_)
                legacy_hash_ = self.password_hash_f(legacy_, aut_salt_) if legacy_ and legacy_ != password_ else None
                if not (legacy_hash_ and legacy_hash_["result"] and secrets.compare_digest(legacy_hash_["key"], aut_key_)):
                    raise AuthError("invalid email or password")
                rehash_ = self.password_hash_f(password_, None)
                if rehash_["result"]:
                    Mongo().db_["_auth"].update_one(
                        {"aut_id": user_id_},
                        {"$set": {"aut_salt": rehash_["salt"], "aut_key": rehash_["key"], "_modified_at": Misc().get_now_f()}},
                    )

            user_["aut_api_key"] = auth_["aut_api_key"] if "aut_api_key" in auth_ and auth_["aut_api_key"] is not None else None

            return {"result": True, "user": user_, "auth": auth_}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def signin_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            email_ = Misc().clean_f(input_["email"])
            password_ = str(input_["password"]).strip()

            user_validate_ = self.user_validate_by_auth_f({"userid": email_, "password": password_})
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])

            otp_send_ = OTP().request_otp_f(email_)
            if not otp_send_["result"]:
                raise APIError(otp_send_["msg"])

            return {"result": True, "msg": "2FA required", "user": None}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def signup_f(self):
        """
        docstring is in progress
        """
        try:
            checkup_ = self.checkup_f()
            if not checkup_["result"]:
                raise APIError(checkup_["msg"])

            input_ = request.json
            user_id_ = Misc().clean_f(input_["email"])
            password_ = str(input_["password"]).strip()

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": user_id_})
            # a record that never completed its first second-factor check may be re-registered,
            # so that whoever controls the mailbox always wins over a pre-registration attempt
            if auth_ and not ("aut_verified" in auth_ and auth_["aut_verified"] is False):
                raise AuthError("account already exists")

            user_ = (
                Mongo()
                .db_["_user"]
                .find_one(
                    {
                        "usr_id": user_id_,
                        "usr_enabled": True,
                        "usr_scope": {"$in": ["Internal", "Administrator"]},
                    }
                )
            )
            if not user_:
                raise AuthError("no user found")

            usr_scope_ = user_["usr_scope"] if "usr_scope" in user_ else None
            if not usr_scope_ or usr_scope_ not in ["Internal", "Administrator"]:
                raise AuthError("invalid signup request")

            hash_f_ = self.password_hash_f(password_, None)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])

            salt_ = hash_f_["salt"]
            key_ = hash_f_["key"]

            aut_otp_secret_ = pyotp.random_base32()
            api_key_ = secrets.token_hex(16)

            # the totp secret is never returned here; it is shown only to an authenticated
            # session (otp show) and only counts as a factor once validated
            doc_ = {
                "aut_id": user_id_,
                "aut_salt": salt_,
                "aut_key": key_,
                "aut_api_key": api_key_,
                "aut_tfac": None,
                "aut_tfac_attempts": 0,
                "aut_expires": 0,
                "aut_otp_secret": aut_otp_secret_,
                "aut_otp_validated": False,
                "aut_verified": False,
                "aut_jwt_secret": None,
                "aut_jwt_token": None,
                "_qr_modified_at": Misc().get_now_f(),
                "_qr_modified_by": user_id_,
                "_qr_modified_count": 0,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_id_,
                "_created_ip": Misc().get_client_ip_f(),
            }
            if auth_:
                Mongo().db_["_auth"].update_one({"aut_id": user_id_}, {"$set": doc_, "$inc": {"_modified_count": 1}})
            else:
                doc_["_created_at"] = Misc().get_now_f()
                doc_["_created_by"] = user_id_
                Mongo().db_["_auth"].insert_one(doc_)

            return {"result": True, "user": None, "msg": "account created, please sign in to verify your e-mail address"}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)
