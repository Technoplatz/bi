"""
Technoplatz BI

Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat

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
"""

import os
import io
import sys
import logging
import re
import secrets
import json
import operator
import smtplib
import hashlib
import ast
import subprocess
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial
from random import randint
from datetime import datetime, timedelta
from pymongo import MongoClient
from boto3 import session
import botocore
import pymongo
import bson
from bson import json_util
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
import bleach
import pyotp
from jose import jwt
import numexpr as ne
from flask import Flask, request, send_from_directory, make_response
from flask_cors import CORS
from markupsafe import escape
import requests
from croniter import croniter
from get_docker_secret import get_docker_secret
from apscheduler.schedulers.background import BackgroundScheduler


class APIError(BaseException):
    """
    docstring is in progress
    """


class AuthError(BaseException):
    """
    docstring is in progress
    """


class SessionError(BaseException):
    """
    docstring is in progress
    """


class AppException(BaseException):
    """
    docstring is in progress
    """


class PassException(BaseException):
    """
    docstring is in progress
    """


class JSONEncoder(json.JSONEncoder):
    """
    docstring is in progress
    """

    def default(self, o):
        """
        docstring is in progress
        """
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class Schedular:
    """
    docstring is in progress
    """

    def cron_looker_f(self, view_):
        """
        docstring is in progress
        """
        try:
            scheduled_ = view_["scheduled"] if "scheduled" in view_ else None
            if not scheduled_:
                raise PassException("view not scheduled")

            scheduled_cron_ = view_["scheduled_cron"] if "scheduled_cron" in view_ else None
            if not croniter.is_valid(scheduled_cron_):
                return {"result": False, "msg": "invalid crontab"}

            separated_ = re.split(" ", scheduled_cron_)
            if not (separated_ and len(separated_) == 5):
                return {"result": False, "msg": "invalid cron separation"}

            minute_ = separated_[0].strip()
            hour_ = separated_[1].strip()
            day_ = separated_[2].strip()
            month_ = separated_[3].strip()
            day_of_week_ = separated_[4].lower().strip()

            return {"result": True, "minute": str(minute_), "hour": str(hour_), "day": str(day_), "month": str(month_), "day_of_week": str(day_of_week_)}

        except PassException as exc_:
            return Misc().pass_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def schedule_queries_f(self, sched_):
        """
        docstring is in progress
        """
        try:
            queries_ = Mongo().db_["_query"].find({"que_scheduled": True})
            if not queries_:
                return {"result": True}

            for query_ in queries_:
                id__ = query_["que_id"] if "que_id" in query_ else None
                if not id__:
                    continue

                scheduled_cron_ = query_["que_scheduled_cron"] if "que_scheduled_cron" in query_ else None
                if not croniter.is_valid(scheduled_cron_):
                    continue

                separated_ = re.split(" ", scheduled_cron_)
                if not (separated_ and len(separated_) == 5):
                    continue

                minute_ = str(separated_[0].strip())
                hour_ = str(separated_[1].strip())
                day_ = str(separated_[2].strip())
                month_ = str(separated_[3].strip())
                day_of_week_ = str(separated_[4].lower().strip())

                args_ = [{
                    "id": query_["que_id"],
                    "sched": True,
                    "key": SMTP_PASSWORD_
                }]

                sched_.add_job(Crud().query_f, trigger="cron", minute=minute_, hour=hour_, day=day_, month=month_, day_of_week=day_of_week_, id=id__, replace_existing=True, args=args_)

            return {"result": True}

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def main_f(self):
        """
        docstring is in progress
        """
        try:
            sched_ = BackgroundScheduler(daemon=True)
            sched_.remove_all_jobs()
            sched_.add_job(Crud().dump_f, trigger="cron", minute="0", hour=f"{MONGO_DUMP_HOURS_}", day="*", month="*", day_of_week="*", id="schedule_dump", replace_existing=True, args=[{"user": {"email": "cronjob"}, "op": "dumpu"}])
            sched_.add_job(self.schedule_queries_f, trigger="cron", minute=f"*/{API_SCHEDULE_INTERVAL_MIN_}", hour="*", day="*", month="*", day_of_week="*", id="schedule_queries", replace_existing=True, args=[sched_])
            sched_.start()
            return True

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)


class Misc:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.props_ = [
            "bsonType",
            "title",
            "description",
            "pattern",
            "minimum",
            "maximum",
            "minLength",
            "maxLength",
            "enum",
        ]
        self.xtra_props_ = [
            "index",
            "width",
            "required",
            "password",
            "textarea",
            "default",
            "file",
            "prefix",
            "permanent",
            "disabled",
            "objectId",
            "filter",
            "readonly",
            "collection",
            "view",
            "property",
            "object",
            "subType",
            "manualAdd",
            "scan",
            "replacement",
            "placeholder",
            "counter",
            "timestamp",
            "uuid",
            "dateOnly",
            "decimals",
            "trueText",
            "falseText",
            "caseType",
            "query"
        ]

    def boto_s3_f(self, input_):
        """
        docstring is in progress
        """
        try:
            if not API_S3_ACTIVE_:
                return {"result": True}

            op_ = input_["op"]
            origin_ = input_["origin"]
            object_ = input_["object"]

            extra_args_ = {
                "ServerSideEncryption": "AES256"
            }

            boto_client_ = session.Session().client(
                "s3",
                region_name=API_S3_REGION_,
                endpoint_url=API_S3_ENDPOINT_URL_,
                aws_access_key_id=API_S3_ACCESS_ID_,
                aws_secret_access_key=API_S3_SECRET_KEY_
            )

            if op_ in ["dumpr", "dumpd"]:
                try:
                    boto_client_.download_file(API_S3_BUCKET_NAME_, object_, origin_)
                except botocore.exceptions.ClientError as exc__:
                    msg_ = str(exc__)
                    if exc__.response["Error"]["Code"] == "404":
                        msg_ = "object does not exist"
                    return {"result": False, "msg": msg_}
            else:
                boto_client_.upload_file(origin_, API_S3_BUCKET_NAME_, object_, ExtraArgs=extra_args_)

            return {"result": True}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return {"result": False, "msg": str(exc__)}

        finally:
            boto_client_.close()

    def commands_f(self, command_, input_):
        """
        docstring is in progress
        """
        collection_ = input_["collection"] if "collection" in input_ else None
        file_ = input_["file"] if "file" in input_ else None
        type_ = input_["type"] if "type" in input_ else None
        fields_ = input_["fields"] if "fields" in input_ else None
        query_ = input_["query"] if "query" in input_ else None
        loc_ = input_["loc"] if "loc" in input_ else None
        connstr_ = f"mongodb://{MONGO_USERNAME_}:{MONGO_PASSWORD_}@{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}"
        commands_ = {
            "mongoexport": [
                f"--uri={connstr_}",
                f"--db={MONGO_DB_}",
                f"--authenticationDatabase={MONGO_AUTH_DB_}",
                "--ssl",
                f"--collection={collection_}",
                f"--sslPEMKeyFile={MONGO_TLS_CERT_KEYFILE_}",
                f"--sslCAFile={MONGO_TLS_CA_KEYFILE_}",
                f"--sslPEMKeyPassword={MONGO_TLS_CERT_KEYFILE_PASSWORD_}",
                "--tlsInsecure",
                f"--type={type_}",
                f"--fields={fields_}",
                f"--query={query_}",
                f"--out={file_}"
            ],
            "mongorestore": [
                "--uri", connstr_,
                "--db", f"{MONGO_DB_}",
                "--authenticationDatabase", f"{MONGO_AUTH_DB_}",
                "--ssl",
                "--sslPEMKeyFile", f"{MONGO_TLS_CERT_KEYFILE_}",
                "--sslCAFile", f"{MONGO_TLS_CA_KEYFILE_}",
                "--sslPEMKeyPassword", f"{MONGO_TLS_CERT_KEYFILE_PASSWORD_}",
                "--tlsInsecure",
                f"--{type_}",
                f"--archive={loc_}",
                "--drop",
                "--quiet"
            ],
            "mongodump": [
                "--uri", connstr_,
                "--db", f"{MONGO_DB_}",
                "--authenticationDatabase", f"{MONGO_AUTH_DB_}",
                "--ssl",
                "--sslPEMKeyFile", f"{MONGO_TLS_CERT_KEYFILE_}",
                "--sslCAFile", f"{MONGO_TLS_CA_KEYFILE_}",
                "--sslPEMKeyPassword", f"{MONGO_TLS_CERT_KEYFILE_PASSWORD_}",
                "--tlsInsecure",
                f"--{type_}",
                f"--archive={loc_}",
                "--quiet"
            ]
        }
        return commands_[command_] if command_ in commands_ else []

    def jwt_proc_f(self, endecode_, token_, jwt_secret_, payload_, header_):
        """
        docstring is in progress
        """
        try:
            alg_ = "HS256"
            if endecode_ == "decode":
                unverified_claims_ = jwt.get_unverified_claims(token_)
                aud_ = unverified_claims_.get("aud")
                sub_ = unverified_claims_.get("sub")
                iss_ = unverified_claims_.get("iss")
                claims_ = jwt.decode(token_, jwt_secret_, options=payload_, algorithms=[alg_], audience=aud_, issuer=iss_, subject=sub_)
            elif endecode_ == "encode":
                claims_ = jwt.encode(payload_, jwt_secret_, algorithm=alg_, headers=header_)

            return ({"result": True, "jwt": claims_})

        except jwt.ExpiredSignatureError as exc_:
            return ({"result": False, "msg": str(exc_), "exc": str(exc_)})

        except jwt.JWTClaimsError as exc_:
            return ({"result": False, "msg": str(exc_), "exc": str(exc_)})

        except jwt.JWTError as exc_:
            return ({"result": False, "msg": str(exc_), "exc": str(exc_)})

        except Exception as exc_:
            return ({"result": False, "msg": str(exc_), "exc": str(exc_)})

    def post_notification_f(self, notification_):
        """
        docstring is in progress
        """
        if not NOTIFICATION_SLACK_HOOK_URL_:
            return True

        ip_ = self.get_client_ip_f()
        exc_type_, exc_obj_, exc_tb_ = sys.exc_info()
        file_ = os.path.split(exc_tb_.tb_frame.f_code.co_filename)[1]
        line_ = exc_tb_.tb_lineno
        notification_str_ = f"IP: {ip_}, DOMAIN: {DOMAIN_}, TYPE: {exc_type_}, FILE: {file_}, OBJ: {exc_obj_}, LINE: {line_}, EXCEPTION: {notification_}"
        response_ = requests.post(NOTIFICATION_SLACK_HOOK_URL_, json.dumps({"text": str(notification_str_)}), timeout=10)
        if response_.status_code != 200:
            PRINT_("!!! Notification Error", response_.content)

        return True

    def notify_exception_f(self, exc__):
        """
        docstring is in progress
        """
        self.post_notification_f(str(exc__))
        return {"result": False, "msg": str(exc__)}

    def app_exception_f(self, exc__):
        """
        docstring is in progress
        """
        return {"result": False, "msg": str(exc__)}

    def pass_exception_f(self, exc__):
        """
        docstring is in progress
        """
        return {"result": False, "msg": str(exc__)}

    def auth_error_f(self, exc__):
        """
        docstring is in progress
        """
        return {"result": False, "msg": str(exc__)}

    def mongo_error_f(self, exc__):
        """
        docstring is in progress
        """
        details_, msg_ = exc__.details, ""
        if "writeErrors" in details_:
            msg_ = details_
        else:
            splt_ = str(exc__).split(", full error: ")
            splt0_ = splt_[0] if splt_ and len(splt_) > 0 else str(exc__)
            nk_ = splt0_.split(" :: ")
            msg_ = nk_[2] if nk_ and len(nk_) > 1 else splt0_

        return {"result": False, "msg": msg_, "notify": False, "count": 0}

    def log_f(self, obj):
        """
        docstring is in progress
        """
        try:
            doc_ = {
                "log_type": obj["type"],
                "log_date": self.get_now_f(),
                "log_user_id": obj["user"],
                "log_ip": Misc().get_client_ip_f(),
                "log_collection_id": obj["collection"] if "collection" in obj else None,
                "log_operation": obj["op"] if "op" in obj else None,
                "log_document": str(obj["document"]) if "document" in obj else None,
                "_created_at": self.get_now_f(),
                "_created_by": obj["user"],
            }

            Mongo().db_["_log"].insert_one(doc_)
            return {"result": True}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def get_timestamp_f(self):
        """
        docstring is in progress
        """
        dt_ = self.get_now_f()
        mon_ = ("0" + str(dt_.month))[-2:]
        day_ = ("0" + str(dt_.day))[-2:]
        hou_ = ("0" + str(dt_.hour))[-2:]
        min_ = ("0" + str(dt_.minute))[-2:]
        sec_ = ("0" + str(dt_.second))[-2:]
        return f"{dt_.year}{mon_}{day_}{hou_}{min_}{sec_}"

    def set_strip_doc_f(self, doc_):
        """
        docstring is in progress
        """
        for field_ in doc_:
            if isinstance(doc_[field_], str):
                doc_[field_] = doc_[field_].strip()
        return doc_

    def get_now_f(self):
        """
        docstring is in progress
        """
        return datetime.now()

    def get_client_ip_f(self):
        """
        docstring is in progress
        """
        return "0.0.0.0" if not request else request.headers["cf-connecting-ip"] if "cf-connecting-ip" in request.headers else request.access_route[-1]

    def get_except_underdashes(self):
        """
        docstring is in progress
        """
        return ["_tags"]

    def in_admin_ips_f(self):
        """
        docstring is in progress
        """
        ip_ = Misc().get_client_ip_f()
        return ip_ in API_ADMIN_IPS_

    def properties_cleaner_f(self, properties):
        """
        docstring is in progress
        """
        properties_new_ = {}
        for property_ in properties:
            dict_ = {}
            properties_property_ = properties[property_]
            for field_ in properties_property_:
                if field_ not in self.xtra_props_:
                    if field_ == "items":
                        items_ = properties_property_["items"]
                        if "properties" in items_:
                            items_properties_ = items_["properties"]
                            properties_new__ = self.properties_cleaner_f(items_properties_)
                            properties_property_["items"]["properties"] = properties_new__
                    if field_ == "bsonType":
                        if properties_property_[field_] == "object":
                            dict_[field_] = [properties_property_[field_], "array", "null"]
                        else:
                            dict_[field_] = [properties_property_[field_], "null"]
                    else:
                        dict_[field_] = properties_property_[field_]
            properties_new_[property_] = dict_
        return properties_new_

    def get_users_from_tags_f(self, tags_):
        """
        docstring is in progress
        """
        try:
            personalizations_ = []
            to_ = []
            users_ = Mongo().db_["_user"].find({"usr_enabled": True, "_tags": {"$elemMatch": {"$in": tags_}}})
            if users_:
                for member_ in users_:
                    if member_["usr_id"] not in to_:
                        to_.append(member_["usr_id"])
                        personalizations_.append({"email": member_["usr_id"], "name": member_["usr_name"]})

            return {"result": True, "to": personalizations_}

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def set_value_f(self, key_, setto_, properties_, data_):
        """
        docstring is in progress
        """
        setto__ = None
        try:
            if key_ not in properties_:
                raise APIError("missing set key")

            if not setto_:
                raise APIError("missing set to")

            if setto_ in data_:
                setto__ = data_[setto_]
            elif setto_[:1] == "$":
                forward_ = str(setto_[1:]).upper()
                if not forward_:
                    raise APIError("missing $ key name")
                kav_ = Mongo().db_["_kv"].find_one({"kav_key": forward_})
                if not kav_:
                    raise APIError("kv value not found")
                kav_key_ = kav_["kav_key"] if "kav_key" in kav_ and kav_["kav_key"] is not None else None
                kav_as_ = kav_["kav_as"] if "kav_as" in kav_ and kav_["kav_as"] is not None else None
                kav_value_ = kav_["kav_value"] if "kav_value" in kav_ and kav_["kav_value"] is not None else None
                if not kav_key_ or not kav_value_ or not kav_as_:
                    raise APIError("missing kv keys")
                setto__ = datetime.strptime(kav_value_[:10], "%Y-%m-%d") if kav_as_ == "date" \
                    else bool(kav_value_) if kav_as_ == "bool" \
                    else float(kav_value_) if kav_as_ in ["float", "number", "decimal"] \
                    else int(kav_value_) if kav_as_ == "int" \
                    else str(kav_value_) if kav_as_ == "string" \
                    else str(kav_value_)
            elif setto_[:1] == "=":
                decimals_ = int(properties_[key_]["decimals"]) if "decimals" in properties_[key_] and int(properties_[key_]["decimals"]) >= 0 else None
                forward_ = setto_[1:]
                if not forward_:
                    raise APIError("missing = value")
                formula_ = str(forward_).replace(" ", "")
                formula_parts_ = re.split("([+-/*()])", formula_)
                for part_ in formula_parts_:
                    val_ = self.set_value_f(key_, part_, properties_, data_)
                    formula_ = formula_.replace(part_, val_)
                # setto__ = ne.evaluate(formula_)
                setto__ = round(ne.evaluate(formula_), decimals_) if decimals_ else ne.evaluate(formula_)
            else:
                setto__ = setto_

            return setto__

        except pymongo.errors.PyMongoError as exc_:
            return Misc().mongo_error_f(exc_)

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def clean_f(self, data_):
        """
        docstring is in progress
        """
        data_ = escape(data_) if isinstance(data_, str) else data_
        return bleach.clean(data_) if data_ else None


class Mongo:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.mongo_appname_ = "api"
        self.mongo_readpref_primary_ = "primary"
        self.mongo_readpref_secondary_ = "secondary"
        auth_source_ = f"authSource={MONGO_AUTH_DB_}" if MONGO_AUTH_DB_ else ""
        replicaset_ = f"&replicaSet={MONGO_RS_}" if MONGO_RS_ and MONGO_RS_ is not None else ""
        read_preference_primary_ = f"&readPreference={self.mongo_readpref_primary_}" if self.mongo_readpref_primary_ else ""
        appname_ = f"&appname={self.mongo_appname_}" if self.mongo_appname_ else ""
        tls_ = "&tls=true" if MONGO_TLS_ else "&tls=false"
        tls_certificate_key_file_ = f"&tlsCertificateKeyFile={MONGO_TLS_CERT_KEYFILE_}" if MONGO_TLS_CERT_KEYFILE_ else ""
        tls_certificate_key_file_password_ = f"&tlsCertificateKeyFilePassword={MONGO_TLS_CERT_KEYFILE_PASSWORD_}" if MONGO_TLS_CERT_KEYFILE_PASSWORD_ else ""
        tls_ca_file_ = f"&tlsCAFile={MONGO_TLS_CA_KEYFILE_}" if MONGO_TLS_CA_KEYFILE_ else ""
        tls_allow_invalid_certificates_ = "&tlsAllowInvalidCertificates=true"
        retry_writes_ = "&retryWrites=true" if MONGO_RETRY_WRITES_ else "&retryWrites=false"
        timeout_ms_ = f"&timeoutMS={MONGO_TIMEOUT_MS_}"
        self.connstr = f"mongodb://{MONGO_USERNAME_}:{MONGO_PASSWORD_}@{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}/?{auth_source_}{replicaset_}{read_preference_primary_}{appname_}{tls_}{tls_certificate_key_file_}{tls_certificate_key_file_password_}{tls_ca_file_}{tls_allow_invalid_certificates_}{retry_writes_}{timeout_ms_}"
        self.client_ = MongoClient(self.connstr)
        self.db_ = self.client_[MONGO_DB_]


class Iot:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.props_ = Misc().props_
        self.xtra_props_ = Misc().xtra_props_

    def iot_query_f(self, searched_, page_):
        """
        docstring is in progress
        """
        try:
            aggregate_ = []
            limitn_ = 50
            match_ = {
                "$match": {"$or": [
                    {"ser_dnn_no": {"$regex": searched_,  "$options": "i"}},
                    {"ser_sscc_no": {"$regex": searched_,  "$options": "i"}}
                ]}
            }
            group_ = {
                "$group": {"_id": {"ser_sscc_no": "$ser_sscc_no", "ser_dnn_no": "$ser_dnn_no", "ser_line_no": "$ser_line_no", "ser_prd_no": "$ser_prd_no"},
                           "count": {"$sum": 1},
                           "ser_in_count": {"$sum": {"$cond": [{"$eq": ["$ser_is_in", True]}, 1, 0]}},
                           "ser_out_count": {"$sum": {"$cond": [{"$eq": ["$ser_is_out", True]}, 1, 0]}},
                           "ser_in_date": {"$first": "$ser_in_date"},
                           "ser_out_date": {"$first": "$ser_out_date"}
                           }
            }
            replacewith_ = {"$replaceWith": {"$mergeObjects": ["$$ROOT", "$_id"]}}
            skip_ = {"$skip": limitn_ * (page_ - 1)}
            limit_ = {"$limit": limitn_}
            sort_ = {"$sort": {"ser_in_date": -1}}
            lookup_delivery_ = {"$lookup": {
                "from": "delivery_data",
                "let": {"p_ser_dnn_no": "$ser_dnn_no", "p_ser_line_no": "$ser_line_no"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [{"$eq": ["$dnn_no", "$$p_ser_dnn_no"]}, {"$eq": ["$dnn_line_no", "$$p_ser_line_no"]}]}}},
                    {"$unset": ["_modified_count", "_created_at", "_created_by", "_modified_at", "_modified_by"]}
                ],
                "as": "delivery",
            }}
            unwind_delivery_ = {"$unwind": {"path": "$delivery", "preserveNullAndEmptyArrays": True}}
            replacewith_delivery_ = {"$replaceWith": {"$mergeObjects": ["$$ROOT", "$delivery"]}}
            unset_delivery_ = {"$unset": "delivery"}

            if searched_:
                aggregate_.append(match_)

            aggregate_.append(group_)
            aggregate_.append(replacewith_)
            aggregate_.append(sort_)
            aggregate_.append(skip_)
            aggregate_.append(limit_)
            aggregate_.append(lookup_delivery_)
            aggregate_.append(unwind_delivery_)
            aggregate_.append(replacewith_delivery_)
            aggregate_.append(unset_delivery_)

            cursor_ = Mongo().db_["serial_data"].aggregate(aggregate_)
            docs_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []

            return {"result": True, "payload": docs_, "msg": None, "status": 200}

        except APIError as exc_:
            return {"result": False, "payload": None, "msg": str(exc_), "status": 400}

        except Exception as exc_:
            return {"result": False, "payload": None, "msg": str(exc_), "status": 500}

    def barcode_scan_f(self, aut_id_):
        """
        docstring is in progress
        """
        try:
            data_ = request.json
            bar_operation_ = data_["bar_operation"] if "bar_operation" in data_ and data_["bar_operation"] is not None else None
            bar_input_ = data_["bar_input"] if "bar_input" in data_ and data_["bar_input"] is not None else None
            bar_mode_ = data_["bar_mode"] if "bar_mode" in data_ and data_["bar_mode"] in ["auto", "manual"] else "auto"

            if bar_operation_ is None or bar_input_ is None:
                raise APIError("invalid inputs")

            prefixes_ = ["1S", "1P", "P", "1K", "S", "Q", "16K", "00"]
            if bar_mode_ == "auto":
                for prfx_ in prefixes_:
                    if bar_input_.startswith(prfx_):
                        bar_input_ = bar_input_.removeprefix(prfx_)
                        break

            doc_ = {}
            doc_["bar_operation"] = bar_operation_
            doc_["bar_input"] = bar_input_
            doc_["bar_mode"] = bar_mode_
            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = aut_id_
            filter_ = {"bar_operation": bar_operation_, "bar_input": bar_input_}

            read_ = Mongo().db_["barcode_data"].find_one(filter_)
            if not read_:
                doc_["_created_at"] = doc_["_modified_at"]
                doc_["_created_by"] = doc_["_modified_by"]
                Mongo().db_["barcode_data"].insert_one(doc_)
            else:
                Mongo().db_["barcode_data"].update_one(filter_, {"$set": doc_}, upsert=True)

            data_ = {}
            payload_ = []
            total_ = total_in_ = total_out_ = 0
            find_one_ = Mongo().db_["serial_data"].find_one({"$or": [{"ser_dnn_no": bar_input_}, {"ser_sscc_no": bar_input_}]})
            if find_one_:
                ser_dnn_no_ = find_one_["ser_dnn_no"] if "ser_dnn_no" in find_one_ else None
                if ser_dnn_no_:
                    delivery_ = Mongo().db_["delivery_data"].find_one({"dnn_no": ser_dnn_no_})
                    if delivery_:
                        aggregate_ = []
                        match_ = {"$match": {"ser_dnn_no": ser_dnn_no_}}
                        group_ = {"$group": {"_id": {"ser_dnn_no": "$ser_dnn_no", "ser_sscc_no": "$ser_sscc_no"},
                                             "count": {"$sum": 1},
                                             "ser_in_count": {"$sum": {"$cond": [{"$eq": ["$ser_is_in", True]}, 1, 0]}},
                                             "ser_out_count": {"$sum": {"$cond": [{"$eq": ["$ser_is_out", True]}, 1, 0]}}
                                             }
                                  }
                        replacewith_ = {"$replaceWith": {"$mergeObjects": ["$$ROOT", "$_id"]}}
                        sort_ = {"$sort": {"ser_sscc_no": 1}}
                        aggregate_.append(match_)
                        aggregate_.append(group_)
                        aggregate_.append(replacewith_)
                        aggregate_.append(sort_)
                        cursor_ = Mongo().db_["serial_data"].aggregate(aggregate_)
                        payload_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []
                    else:
                        raise APIError(f"delivery not found {ser_dnn_no_}")
                else:
                    raise APIError(f"delivery not defined in {bar_mode_} mode")
            else:
                raise APIError(f"input not found in {bar_mode_} mode")

            for pl_ in payload_:
                total_ += pl_["count"]
                total_in_ += pl_["ser_in_count"]
                total_out_ += pl_["ser_out_count"]

            data_["payload"] = payload_
            data_["input"] = bar_input_
            data_["delivery"] = delivery_
            data_["total"] = total_
            data_["total_in"] = total_in_
            data_["total_out"] = total_out_

            return {"result": True, "data": data_, "msg": f"{bar_input_} OK", "status": 200}

        except APIError as exc_:
            return {"result": False, "payload": None, "msg": str(exc_), "status": 400}

        except Exception as exc_:
            return {"result": False, "payload": None, "msg": str(exc_), "status": 500}


class Crud:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.props_ = Misc().props_
        self.xtra_props_ = Misc().xtra_props_

    def root_schemas_f(self, schema_):
        """
        docstring is in progress
        """
        try:
            base_path_ = "/app/_template"
            filename_ = f"{schema_}.json"
            if not filename_.startswith("_"):
                raise APIError("invalid schema file")

            fullpath_ = os.path.normpath(os.path.join(base_path_, filename_))
            if not fullpath_.startswith(base_path_):
                PRINT_("!!! [schema] fullpath_", fullpath_)
                raise APIError("file not allowed [schema]")

            with open(fullpath_, "r", encoding="utf-8") as fopen_:
                res_ = json.loads(fopen_.read())

            return res_

        except APIError as exc__:
            PRINT_("!!!", exc__)

    def validate_iso8601_f(self, strv):
        """
        docstring is in progress
        """
        regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
        match_iso8601 = re.compile(regex).match
        return match_iso8601(strv) is not None

    def get_properties_f(self, collection):
        """
        docstring is in progress
        """
        try:
            cursor_ = Mongo().db_["_collection"].find_one({"col_id": collection}) if collection[:1] != "_" else self.root_schemas_f(f"{collection}")
            if not cursor_:
                raise APIError("collection not found for properties")
            if "col_structure" not in cursor_:
                raise APIError("structure not found")

            structure_ = cursor_["col_structure"] if collection[:1] != "_" else cursor_
            if "properties" not in structure_:
                raise APIError("properties not found in structure")
            properties_ = structure_["properties"]

            return {"result": True, "properties": properties_}

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def inner_collection_f(self, cid_):
        """
        docstring is in progress
        """
        try:
            is_crud_ = cid_[:1] != "_"
            collection_ = Mongo().db_["_collection"].find_one({"col_id": cid_}) if is_crud_ else self.root_schemas_f(f"{cid_}")
            if not collection_:
                raise APIError(f"collection not found to root: {cid_}")

            return {"result": True, "collection": collection_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def decode_crud_doc_f(self, doc_, properties_):
        """
        docstring is in progress
        """
        try:
            document_ = doc_
            for k in properties_:
                property_ = properties_[k]
                if "bsonType" in property_:
                    if k in doc_.keys():
                        if property_["bsonType"] == "date":
                            ln_ = 10 if doc_[k] and len(doc_[k]) == 10 else 19
                            rgx_ = "%Y-%m-%d" if doc_[k] and ln_ == 10 else "%Y-%m-%dT%H:%M:%S"
                            if (doc_[k] and isinstance(doc_[k], str) and self.validate_iso8601_f(doc_[k])):
                                document_[k] = datetime.strptime(doc_[k][:ln_], rgx_)
                            else:
                                document_[k] = datetime.strptime(doc_[k][:ln_], rgx_) if doc_[k] is not None else None
                        elif property_["bsonType"] == "string":
                            document_[k] = str(doc_[k]) if doc_[k] is not None else doc_[k]
                        elif property_["bsonType"] in [
                            "number",
                            "int",
                            "float",
                            "double",
                        ]:
                            document_[k] = doc_[k] * 1 if document_[k] is not None else document_[k]
                        elif property_["bsonType"] == "decimal":
                            document_[k] = doc_[k] * 1.00 if document_[k] is not None else document_[k]
                        elif property_["bsonType"] == "bool":
                            document_[k] = document_[k] and document_[k] in [True, "true", "True", "TRUE"]
                    else:
                        if property_["bsonType"] == "bool":
                            document_[k] = False

            return {"result": True, "doc": document_}

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def decode_crud_input_f(self, input_):
        """
        docstring is in progress
        """
        try:
            collection_id_ = input_["collection"]
            is_crud_ = collection_id_[:1] != "_"
            doc_ = input_["doc"]

            col_check_ = self.inner_collection_f(collection_id_)
            if not col_check_["result"]:
                raise APIError(col_check_["msg"])
            collection__ = col_check_["collection"] if "collection" in col_check_ else None

            structure_ = collection__["col_structure"] if is_crud_ else collection__
            if "properties" not in structure_:
                raise APIError("properties not found in the structure")
            properties_ = structure_["properties"]

            decode_crud_doc_f_ = self.decode_crud_doc_f(doc_, properties_)
            if not decode_crud_doc_f_["result"]:
                raise APIError(decode_crud_doc_f_["msg"])

            return {"result": True, "doc": decode_crud_doc_f_["doc"]}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def frame_convert_bool_f(self, data_):
        """
        docstring is in progress
        """
        return str(data_).strip().lower() == "true"

    def frame_convert_datetime_f(self, data_):
        """
        docstring is in progress
        """
        date_ = str(data_).strip()
        return datetime.fromisoformat(date_) if date_ not in [" ", "0", "0.0", "NaT", "NaN", "nat", "nan", np.nan, np.double, None] else None

    def frame_convert_string_f(self, data_):
        """
        docstring is in progress
        """
        str_ = str(data_).replace(r"\W", "").strip()
        return str_ if str_ not in ["", None] else None

    def frame_convert_number_f(self, data_):
        """
        docstring is in progress
        """
        str_ = str(data_).replace(r"\D", "").strip()
        return float(str_) if str_ not in ["", None] else None

    def frame_convert_int_f(self, data_):
        """
        docstring is in progress
        """
        str_ = str(data_).replace(r"\D", "").strip()
        return int(str_) if str_ not in ["", None] else None

    def frame_convert_objectid_f(self, data_):
        """
        docstring is in progress
        """
        str_ = str(data_).strip()
        return ObjectId(str_)

    def copykey_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_ = obj["collection"]
            properties_ = obj["properties"]
            key_ = obj["key"]
            match_ = obj["match"] if "match" in obj and obj["match"] != [] else []
            sweeped_ = obj["sweeped"] if "sweeped" in obj and obj["sweeped"] != [] else []

            get_filtered_ = {}
            if len(match_) > 0:
                get_filtered_ = self.get_filtered_f({"match": match_, "properties": properties_ if properties_ else None})

            ids_ = []
            for _id in sweeped_:
                ids_.append(ObjectId(_id))
            if len(ids_) > 0:
                get_filtered_ = {"$and": [get_filtered_, {"_id": {"$in": ids_}}]}

            distinct_ = ""
            cursora_ = Mongo().db_[f"{collection_}_data"].distinct(key_, get_filtered_)
            if cursora_ and len(cursora_) > 0:
                distinct_ = "\n".join(map(str, cursora_[:1024]))

            return {"result": True, "copied": distinct_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def convert_column_name_f(self, str_):
        """
        docstring is in progress
        """
        cleantags_ = re.compile(r"<[^>]+>")
        cleanptrn_ = re.compile(r"[!'\"#$%&()*+/.,;<>?@[\]^\-`{|}~\\]")
        exceptions_ = {
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "ş": "s",
            "ü": "u",
            "ö": "o",
            "Ç": "c",
            "Ğ": "g",
            "İ": "i",
            "Ş": "s",
            "Ü": "u",
            "Ö": "o",
            " ": "_",
        }
        str_ = str_.replace("\t", " ")
        str_ = re.sub(cleantags_, "", str_)
        str_ = re.sub(cleanptrn_, "", str_)
        str_ = str_[:32]
        str_ = re.sub(" +", " ", str_)
        str_ = re.sub(".", lambda char_: exceptions_.get(char_.group(), char_.group()), str_)
        return str_.lower().strip().encode("ascii", "ignore").decode("ascii")

    def import_f(self, obj):
        """
        docstring is in progress
        """
        content_, stats_, res_, details_, files_, filename_, upsertable_ = "", "", None, {}, [], "", False
        try:
            form_ = obj["form"]
            file_ = obj["file"]
            collection_ = obj["collection"]
            upserted_ = "process" in obj and obj["process"] == "update"
            email_ = form_["email"]
            mimetype_ = file_.content_type

            collection__ = f"{collection_}_data"
            find_one_ = Mongo().db_["_collection"].find_one({"col_id": collection_})
            if not find_one_:
                raise APIError(f"collection not found {collection_}")

            col_structure_ = find_one_["col_structure"] if "col_structure" in find_one_ else None
            if not col_structure_:
                raise APIError(f"no structure found {collection_}")

            get_properties_ = self.get_properties_f(collection_)
            if not get_properties_["result"]:
                raise APIError(get_properties_["msg"])
            properties_ = get_properties_["properties"]

            defaults_ = {}
            required_ = col_structure_["required"] if "required" in col_structure_ and len(col_structure_["required"]) > 0 else []
            if required_:
                for req_ in required_:
                    if req_ in properties_ and "default" in properties_[req_] and properties_[req_]["default"] is not None:
                        defaults_[req_] = properties_[req_]["default"]

            import_ = col_structure_["import"] if "import" in col_structure_ else None
            if not import_:
                raise APIError(f"no import rules defined for {collection_}")
            ignored_ = import_["ignored"] if "ignored" in import_ and len(import_["ignored"]) > 0 else []
            upsertable_ = "upsertable" in import_ and import_["upsertable"] is True
            upsertables_ = import_["upsertables"] if "upsertables" in import_ and len(import_["upsertables"]) > 0 else []

            if mimetype_ in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
                filesize_ = file_.tell()
                if filesize_ > API_UPLOAD_LIMIT_BYTES_:
                    raise APIError(f"invalid file size {API_UPLOAD_LIMIT_BYTES_} bytes")
                file_.seek(0, os.SEEK_END)
                df_ = pd.read_excel(file_, sheet_name=collection_, header=0, engine="openpyxl", dtype="object")
            elif mimetype_ == "text/csv":
                decoded_ = file_.read().decode("utf-8")
                filesize_ = file_.content_length
                if filesize_ > API_UPLOAD_LIMIT_BYTES_:
                    raise APIError(f"invalid file size {API_UPLOAD_LIMIT_BYTES_} bytes")
                if mimetype_ == "text/csv":
                    df_ = pd.read_csv(io.StringIO(decoded_), header=0, dtype="object")
            else:
                raise APIError("file type is not supported")

            df_ = df_.rename(lambda column_: self.convert_column_name_f(column_), axis="columns")

            columns_tobe_deleted_ = []
            for column_ in df_.columns:
                if column_ in properties_:
                    property_ = properties_[column_]
                    if "bsonType" in property_:
                        if property_["bsonType"] == "date":
                            df_[column_] = df_[column_].apply(self.frame_convert_datetime_f)
                        elif property_["bsonType"] == "bool":
                            df_[column_] = df_[column_].apply(self.frame_convert_bool_f)
                        elif property_["bsonType"] == "string":
                            df_[column_] = df_[column_].apply(self.frame_convert_string_f)
                            if "replacement" in property_ and len(property_["replacement"]) > 0:
                                for repl_ in property_["replacement"]:
                                    find_ = repl_["find"] if "find" in repl_ and repl_["find"] is not None else None
                                    replace_ = repl_["replace"] if "replace" in repl_ and repl_["replace"] is not None else ""
                                    if find_ and replace_ is not None:
                                        df_[column_] = df_[column_].str.replace(find_, replace_, regex=True)
                        elif property_["bsonType"] == "int":
                            df_[column_] = df_[column_].apply(self.frame_convert_int_f)
                        elif property_["bsonType"] in ["number", "decimal"]:
                            df_[column_] = df_[column_].apply(self.frame_convert_number_f)
                    else:
                        columns_tobe_deleted_.append(column_)
                else:
                    if column_ != "_id":
                        columns_tobe_deleted_.append(column_)
                    else:
                        df_[column_] = df_[column_].apply(self.frame_convert_objectid_f)

            if defaults_:
                for key_, value_ in defaults_.items():
                    if key_ not in df_.columns:
                        df_[key_] = value_

            if ignored_:
                for ignored__ in ignored_:
                    if ignored__ in df_.columns:
                        df_[ignored__] = None

            if "_structure" in df_.columns:
                columns_tobe_deleted_.append("_structure")

            if len(columns_tobe_deleted_) > 0:
                df_.drop(columns_tobe_deleted_, axis=1, inplace=True)

            uniques_ = []
            unique_ = col_structure_["unique"] if "unique" in col_structure_ and len(col_structure_["unique"]) > 0 else []
            for uq_ in unique_:
                uql_, uqlz_ = len(uq_), 0
                for uq__ in uq_:
                    if uq__ in df_.columns:
                        uqlz_ += 1
                        uniques_.append(uq__)
                if uql_ == uqlz_:
                    break

            df_ = df_.groupby(list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns), as_index=False, dropna=False).sum()
            df_.replace([np.nan, pd.NaT, "nan", "NaN", "nat", "NaT"], None, inplace=True)
            df_["_created_at"] = df_["_modified_at"] = Misc().get_now_f()
            df_["_created_by"] = df_["_modified_by"] = email_
            df_["_modified_count"] = 0
            payload_ = df_.to_dict("records")

            wrote_, count_ = [], 0
            if "_id" in df_.columns:
                wrote_ = [pymongo.UpdateOne({"_id": ObjectId(doc_["_id"])}, {"$set": doc_}, upsert=True) for doc_ in payload_]
            elif upserted_ and upsertable_ and uniques_:
                fieldsgiven_ = False
                for doc_ in payload_:
                    filter_, set_ = {}, {}
                    for uniques__ in uniques_:
                        filter_[uniques__] = doc_[uniques__]
                    for upsertables__ in upsertables_:
                        if upsertables__ in doc_:
                            fieldsgiven_ = True
                            set_[upsertables__] = doc_[upsertables__]
                    set_["_modified_at"] = Misc().get_now_f()
                    set_["_modified_by"] = email_
                    wrote_.append(pymongo.UpdateOne(filter_, {"$set": set_}, upsert=True))
                if not fieldsgiven_:
                    raise APIError("no upsertable fields provided")
            else:
                wrote_ = [pymongo.InsertOne(doc_) for doc_ in payload_]

            bulk_write_ = Mongo().db_[collection__].bulk_write(wrote_, ordered=False)
            details_, content_ = bulk_write_.bulk_api_result, ""

            res_ = {"result": True, "count": count_, "msg": "file was imported successfully"}

        except pymongo.errors.PyMongoError as exc__:
            res_ = Misc().mongo_error_f(exc__)
            details_ = res_["msg"]
            if "writeErrors" in details_:
                for werrs_ in details_["writeErrors"]:
                    content_ += ">>> "
                    if "errmsg" in werrs_:
                        content_ += f"{str(werrs_['errmsg'])}. "
                    if "errInfo" in werrs_:
                        content_ += f"{str(werrs_['errInfo'])}"
                    content_ += "\n"
                stats_ += f"<br />FAILED: {str(len(details_['writeErrors']))}<br />"
            res_["msg"] = "please find the error details in the email we've just sent you"

        except APIError as exc__:
            content_, details_ = str(exc__), {}
            res_ = Misc().notify_exception_f(exc__)

        except Exception as exc__:
            content_, details_ = str(exc__), {}
            res_ = Misc().notify_exception_f(exc__)

        finally:
            stats_ += f"<br />ROW COUNT: {str(len(df_))}<br />"
            stats_ += f"<br />INSERTED: {str(details_['nInserted'])}" if "nInserted" in details_ else ""
            stats_ += f"<br />UPSERTED: {str(details_['nUpserted'])}" if "nUpserted" in details_ else ""
            stats_ += f"<br />MATCHED: {str(details_['nMatched'])}" if "nMatched" in details_ else ""
            stats_ += f"<br />MODIFIED: {str(details_['nModified'])}" if "nModified" in details_ else ""
            stats_ += f"<br />REMOVED: {str(details_['nRemoved'])}" if "nRemoved" in details_ else ""
            filename_ = f"imported-{collection_}-{Misc().get_timestamp_f()}.txt"
            fullpath_ = os.path.normpath(os.path.join(API_TEMPFILE_PATH_, filename_))
            if not fullpath_.startswith(TEMP_PATH_):
                PRINT_("!!! [import] fullpath_", fullpath_)
                raise APIError("file not allowed [import]")
            with open(fullpath_, "w", encoding="utf-8") as file_:
                file_.write(stats_.replace("<br />", "\n") + "\n\n-----BEGIN ERROR LIST-----\n" + content_ + "-----END ERROR LIST-----")
            file_.close()
            files_.append({"name": fullpath_, "type": "txt"})
            Email().send_email_f({
                "personalizations": {"to": [{"email": email_, "name": None}]},
                "op": "importerr",
                "html": f"Hi,<br /><br />Here's the data file upload result;<br /><br />MIME TYPE: {mimetype_}<br />TARGET COLLECTION: {collection_}<br />{stats_}",
                "files": files_
            })
            return res_

    def announce_f(self, input_):
        """
        docstring is in progress
        """
        try:
            if "collection" not in input_:
                raise APIError("collection is missing")

            if "id" not in input_:
                raise APIError("id is missing")

            if "scope" not in input_:
                raise APIError("scope is missing")

            id_ = input_["id"]
            scope_ = input_["scope"]
            col_id_ = input_["collection"]

            user_ = None
            email_ = None
            if "user" in input_:
                user_ = input_["userindb"]
                email_ = user_["usr_id"]

            if scope_ not in ["test", "live"]:
                raise APIError("invalid scope")

            get_view_data_f_ = self.get_view_data_f(user_, id_, "announcement")
            if not get_view_data_f_["result"]:
                raise APIError(get_view_data_f_["msg"])

            df_ = get_view_data_f_["df"]
            df_raw_ = get_view_data_f_["dfraw"]
            pivotify_ = get_view_data_f_["pivotify"]

            view_ = get_view_data_f_["view"]
            _tags = view_["_tags"]
            vie_title_ = view_["title"]
            data_json_ = view_["data_json"]
            data_excel_ = view_["data_excel"]
            data_csv_ = view_["data_csv"]
            vie_attach_pivot_ = view_["pivot"]

            personalizations_to_ = []
            to_ = []
            users_ = Mongo().db_["_user"].find({"_tags": {"$elemMatch": {"$in": _tags}}})
            if users_:
                for member_ in users_:
                    if member_["usr_id"] not in to_:
                        to_.append(member_["usr_id"])
                        personalizations_to_.append({"email": member_["usr_id"], "name": member_["usr_name"]})
            personalizations_ = {"to": personalizations_to_}

            files_ = []
            if data_json_:
                file_json_ = f"{API_TEMPFILE_PATH_}/{id_}.json"
                file_json_raw_ = f"{API_TEMPFILE_PATH_}/{id_}-detail.json"
                df_.to_json(f"{file_json_}", orient="records", date_format="iso", force_ascii=False, date_unit="s", default_handler=None, lines=False, compression=None, index=False)
                df_raw_.to_json(f"{file_json_raw_}", orient="records", date_format="iso", force_ascii=False, date_unit="s", default_handler=None, lines=False, compression=None, index=False)
                files_.append({"name": file_json_, "type": "json"})
                files_.append({"name": file_json_raw_, "type": "json"})
            if data_csv_:
                file_csv_ = f"{API_TEMPFILE_PATH_}/{id_}.csv"
                file_csv_raw_ = f"{API_TEMPFILE_PATH_}/{id_}-detail.csv"
                df_.to_csv(f"{file_csv_}", sep=";", encoding="utf-8", header=True, decimal=".", index=False)
                df_raw_.to_csv(f"{file_csv_raw_}", sep=";", encoding="utf-8", header=True, decimal=".", index=False)
                files_.append({"name": file_csv_, "type": "csv"})
                files_.append({"name": file_csv_raw_, "type": "csv"})
            if data_excel_:
                file_excel_ = f"{API_TEMPFILE_PATH_}/{id_}.xlsx"
                file_excel_raw_ = f"{API_TEMPFILE_PATH_}/{id_}-detail.xlsx"
                df_.to_excel(f"{file_excel_}", sheet_name=col_id_, engine="xlsxwriter", header=True, index=False)
                df_raw_.to_excel(f"{file_excel_raw_}", sheet_name=col_id_, engine="xlsxwriter", header=True, index=False)
                files_.append({"name": file_excel_, "type": "xlsx"})
                files_.append({"name": file_excel_raw_, "type": "xlsx"})

            body_ = ""
            if vie_attach_pivot_:
                body_ += f"{pivotify_}"

            footer_ = f"<br />Generated at {Misc().get_now_f().strftime('%d.%m.%Y %H:%M')}"
            html_ = f'<div style="font-size: 13px;"><h1>{vie_title_}</h1><p>{body_}</p><p>{footer_}</p></div>' if scope_ == "live" else f'<div style="font-size: 13px;"><p style="color: #c00; font-weight: bold;">THIS IS A TEST MESSAGE</p><p>{vie_title_}</p><p>{body_}</p><p>{footer_}</p></div>'

            email_sent_ = Email().send_email_f({
                "personalizations": personalizations_,
                "op": "view",
                "html": html_,
                "subject": vie_title_ if scope_ == "live" else f"TEST: {vie_title_}",
                "files": files_
            })

            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            Mongo().db_["_announcement"].insert_one({
                "ano_id": f"ano-{Misc().get_timestamp_f()}",
                "ano_scope": scope_,
                "ano_vie_id": id_,
                "ano_vie_title": vie_title_,
                "ano_to": to_,
                "_tags": _tags,
                "_created_at": Misc().get_now_f(),
                "_created_by": email_ if email_ else "cronjob"
            })

            return {"result": True}

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def dump_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            op_ = obj_["op"]
            email_ = obj_["user"]["email"] if obj_ and obj_["user"] else "cronjob"

            dmp_id_ = f"dump-{MONGO_DB_}-{Misc().get_timestamp_f()}" if op_ == "dumpu" else Misc().clean_f(obj_["dumpid"])
            fn_ = f"{dmp_id_}.gz"
            type_ = "gzip"
            fullpath_ = os.path.normpath(os.path.join(API_MONGODUMP_PATH_, fn_))
            if not fullpath_.startswith(DUMP_PATH_):
                PRINT_("!!! [dump] fullpath_", fullpath_)
                raise APIError("file not allowed [restore]")

            if op_ == "dumpu":
                subprocess.call(["mongodump"] + Misc().commands_f("mongodump", {"type": type_, "loc": fullpath_}))
                size_ = os.path.getsize(fullpath_)
                Mongo().db_["_dump"].insert_one({
                    "dmp_id": dmp_id_, "dmp_type": type_, "dmp_size": size_, "_created_at": Misc().get_now_f(), "_created_by": email_, "_modified_at": Misc().get_now_f(), "_modified_by": email_
                })

            boto_s3_f_ = Misc().boto_s3_f({
                "op": op_,
                "origin": fullpath_,
                "object": fn_
            })
            if not boto_s3_f_["result"]:
                raise APIError(boto_s3_f_["msg"])

            size_ = os.path.getsize(fullpath_)

            if op_ == "dumpu" and os.path.exists(fullpath_):
                os.remove(fullpath_)

            if op_ == "dumpr":
                subprocess.call(["mongorestore"] + Misc().commands_f("mongorestore", {"type": type_, "loc": fullpath_}))

            return {"result": True, "id": dmp_id_, "file": fn_, "type": type_, "size": size_}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def link_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            source_ = obj_["source"] if "source" in obj_ else None
            _id = obj_["_id"] if "_id" in obj_ else None
            link_ = obj_["link"] if "link" in obj_ else None
            data_ = obj_["data"] if "data" in obj_ else None
            linked_ = obj_["linked"] if "linked" in obj_ and len(obj_["linked"]) > 0 else None
            user_ = obj_["user"] if "user" in obj_ else None
            col_id_ = link_["collection"] if "collection" in link_ else None
            get_ = link_["get"] if "get" in link_ else None
            set_ = link_["set"] if "set" in link_ and len(link_["set"]) > 0 else None
            match_ = link_["match"] if "match" in link_ and len(link_["match"]) > 0 else None
            usr_id_ = user_["usr_id"] if "usr_id" in user_ else None
            tags_ = link_["_tags"] if "_tags" in link_ and len(link_["_tags"]) > 0 else None

            if not source_:
                raise APIError("source collection is missing")

            if not _id:
                raise APIError("source document id is missing")

            if link_ is None:
                raise APIError("link info is missing")

            if linked_ is None:
                raise APIError("linked data is missing")

            if data_ is None:
                raise APIError("master data is missing")

            if user_ is None:
                raise APIError("user is missing")

            if not tags_:
                raise AppException("no link tags found")

            if col_id_ is None:
                raise APIError("linked collection is missing")

            if get_ is None:
                raise APIError("link get is missing")

            if set_ is None:
                raise APIError("link set is missing")

            if not match_:
                raise APIError("link match is missing")

            if usr_id_ is None:
                raise APIError("link user id is missing")

            get_properties_ = self.get_properties_f(col_id_)
            if not get_properties_["result"]:
                raise APIError("collection properties is missing")
            target_properties_ = get_properties_["properties"]

            collection_ = f"{col_id_}_data"
            source_id_ = f"_{source_}_id"
            setc_ = {}
            setc_[source_id_] = _id

            for set__ in set_:
                if "key" in set__ and "value" in set__:
                    targetkey__ = set__["key"]
                    setto__ = set__["value"]
                    if targetkey__ and setto__:
                        val_ = Misc().set_value_f(targetkey__, setto__, target_properties_, data_)
                        if val_:
                            setc_[targetkey__] = val_
                            setc_["_modified_at"] = Misc().get_now_f()
                            setc_["_modified_by"] = usr_id_

            if not setc_:
                raise APIError(f"no assignments to set {collection_}")

            filter0_ = {}
            filter0_[get_] = {"$in": linked_}
            filter1_ = self.get_filtered_f({"match": match_, "properties": target_properties_, "data": data_})
            filter_ = {"$and": [filter0_, filter1_]}

            update_many_ = Mongo().db_[collection_].update_many(filter_, {"$set": setc_})
            count_ = update_many_.matched_count
            if count_ == 0:
                raise AppException("no record found to get linked")

            notification_ = link_["notification"] if "notification" in link_ else None
            notify_ = notification_ and "notify" in notification_ and notification_["notify"] is True
            attachment_ = notification_ and "attachment" in notification_ and notification_["attachment"] is True
            files_ = []

            if notify_:
                subject_ = notification_["subject"] if "subject" in notification_ else "Link Completed"
                body_ = notification_["body"] if "body" in notification_ else "<p>Hi,</p><p>Link completed successfully.</p><p><h1></h1></p>"
                if attachment_:
                    fields_ = str(notification_["fields"].replace(" ", "")) if "fields" in notification_ else None
                    if not fields_:
                        raise AppException("no fields field found in link")
                    type_ = "csv"
                    file_ = f"{API_TEMPFILE_PATH_}/link-{Misc().get_timestamp_f()}.{type_}"
                    query_ = json.dumps(filter0_, default=json_util.default, sort_keys=False)
                    cmd_ = ["mongoexport"] + Misc().commands_f("mongoexport", {"query": query_, "fields": fields_, "type": type_, "file": file_, "collection": collection_})
                    subprocess.call(cmd_)
                    files_ = [{"name": file_, "type": type_}] if attachment_ else []
                    email_sent_ = Email().send_email_f({"op": "link", "tags": tags_, "subject": subject_, "html": body_, "files": files_})
                    if not email_sent_["result"]:
                        raise APIError(email_sent_["msg"])

            return {"result": True, "data": setc_, "count": count_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AppException as exc:
            return Misc().app_exception_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def get_filtered_f(self, obj):
        """
        docstring is in progress
        """
        try:
            match_ = obj["match"]
            properties_ = obj["properties"] if "properties" in obj else None
            data_ = obj["data"] if "data" in obj else None
            fand_ = []
            filtered_ = {}
            for mat_ in match_:
                key_ = mat_["key"]
                op_ = mat_["op"]
                value_ = mat_["value"]
                if key_ and op_ and key_ in properties_:
                    fres_ = None
                    typ = properties_[key_]["bsonType"] if key_ in properties_ else "string"
                    if data_ and value_ in data_ and data_[value_] is not None:
                        value_ = data_[value_]
                    if op_ == "null" or (op_ == "eq" and value_ is None):
                        op_ = "null"
                        array_, array1_, array2_ = [], {}, {}
                        array1_[key_] = {"$eq": None}
                        array2_[key_] = {"$exists": False}
                        array_.append(array1_)
                        array_.append(array2_)
                    elif op_ == "nnull" or (op_ == "ne" and value_ is None):
                        op_ = "nnull"
                        array_, array1_, array2_ = [], {}, {}
                        array1_[key_] = {"$ne": None}
                        array2_[key_] = {"$exists": True}
                        array_.append(array1_)
                        array_.append(array2_)
                    elif op_ == "contains":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = float(value_)
                        elif typ == "int":
                            fres_ = int(value_)
                        elif typ == "bool":
                            fres_ = bool(value_)
                        elif typ == "date":
                            fres_ = datetime.strptime(value_[:10], "%Y-%m-%d")
                        else:
                            fres_ = {"$regex": value_, "$options": "i"} if value_ else {"$regex": "", "$options": "i"}
                    elif op_ == "eq":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = float(value_)
                        elif typ == "int":
                            fres_ = int(value_)
                        elif typ == "bool":
                            fres_ = bool(value_)
                        elif typ == "date":
                            fres_ = datetime.strptime(value_[:10], "%Y-%m-%d")
                        else:
                            fres_ = {"$eq": value_}
                    elif op_ in ["ne", "nc"]:
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$not": {"$eq": float(value_)}}
                        elif typ == "int":
                            fres_ = {"$not": {"$eq": int(value_)}}
                        elif typ == "bool":
                            fres_ = {"$not": {"$eq": bool(value_)}}
                        elif typ == "date":
                            fres_ = {"$not": {"$eq": datetime.strptime(value_[:10], "%Y-%m-%d")}}
                        else:
                            fres_ = {"$not": {"$regex": value_, "$options": "i"}} if value_ else {"$not": {"$regex": "", "$options": "i"}}
                    elif op_ in ["in", "nin"]:
                        separated_ = re.split(",", value_)
                        list_ = [s.strip() for s in separated_] if key_ != "_id" else [ObjectId(s.strip()) for s in separated_]
                        if op_ == "in":
                            fres_ = {"$in": list_ if typ != "number" else list(map(float, list_))}
                        else:
                            fres_ = {"$nin": list_ if typ != "number" else list(map(float, list_))}
                    elif op_ == "gt":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$gt": float(value_)}
                        elif typ == "int":
                            fres_ = {"$gt": int(value_)}
                        elif typ == "date":
                            fres_ = {"$gt": datetime.strptime(value_[:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$gt": value_}
                    elif op_ == "gte":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$gte": float(value_)}
                        elif typ == "int":
                            fres_ = {"$gte": int(value_)}
                        elif typ == "date":
                            fres_ = {"$gte": datetime.strptime(value_[:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$gte": value_}
                    elif op_ == "lt":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$lt": float(value_)}
                        elif typ == "int":
                            fres_ = {"$lt": int(value_)}
                        elif typ == "date":
                            fres_ = {"$lt": datetime.strptime(value_[:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$lt": value_}
                    elif op_ == "lte":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$lte": float(value_)}
                        elif typ == "int":
                            fres_ = {"$lte": int(value_)}
                        elif typ == "date":
                            fres_ = {"$lte": datetime.strptime(value_[:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$lte": value_}
                    elif op_ == "true":
                        fres_ = {"$nin": [False, None]}
                    elif op_ == "false":
                        fres_ = {"$ne": True}

                    fpart_ = {}
                    if op_ == "null":
                        fpart_["$or"] = array_
                    if op_ == "nnull":
                        fpart_["$and"] = array_
                    else:
                        fpart_[key_] = fres_

                    fand_.append(fpart_)

                filtered_ = {"$and": fand_} if fand_ and len(fand_) > 0 else {}

            return filtered_

        except Exception as exc_:
            PRINT_("!!! get filtered exception", exc_)
            return None

    def get_view_data_f(self, user_, view_id_, scope_):
        """
        docstring is in progress
        """
        try:
            filter_ = {}
            filter_[f"col_structure.views.{view_id_}.enabled"] = True
            if user_:
                filter_[f"col_structure.views.{view_id_}._tags"] = {"$elemMatch": {"$in": user_["_tags"]}}
            collection_ = Mongo().db_["_collection"].find_one(filter_)
            if not collection_:
                return {"result": True, "skip": True}
            collection_id_ = f"{collection_['col_id']}_data"
            view_ = collection_["col_structure"]["views"][view_id_]
            col_structure_ = collection_["col_structure"]
            properties_ = col_structure_["properties"]
            properties_master_ = {}
            for property_ in properties_:
                properties_property_ = properties_[property_]
                properties_master_[property_] = properties_property_
                bson_type_ = properties_property_["bsonType"] if "bsonType" in properties_property_ else None
                if bson_type_ == "array":
                    if "items" in properties_property_:
                        items_ = properties_property_["items"]
                        if "properties" in items_:
                            item_properties_ = items_["properties"]
                            for item_property_ in item_properties_:
                                properties_master_[item_property_] = item_properties_[item_property_]

            parents_ = []
            if "parents" in col_structure_:
                parents_ = col_structure_["parents"]

            pipe_ = []
            vie_filter_ = view_["data_filter"] if "data_filter" in view_ else []
            if len(vie_filter_) > 0:
                get_filtered_ = self.get_filtered_f({"match": vie_filter_, "properties": properties_master_ if properties_master_ else None})
                pipe_.append({"$match": get_filtered_})

            unset_ = []
            unset_.append("_modified_by")
            unset_.append("_modified_at")
            unset_.append("_modified_count")
            unset_.append("_resume_token")
            unset_.append("_created_at")
            unset_.append("_created_by")
            unset_.append("_structure")
            unset_.append("_tags")
            unset_.append("_id")

            for properties_master__ in properties_master_:
                if (properties_master__[:1] == "_" and properties_master__ not in Misc().get_except_underdashes()):
                    unset_.append(properties_master__)

            for parent_ in parents_:
                if "match" in parent_ and "collection" in parent_:
                    parent_collection_ = parent_["collection"]
                    find_one_ = Mongo().db_["_collection"].find_one({"col_id": parent_collection_})
                    if (find_one_ and "col_structure" in find_one_ and "properties" in find_one_["col_structure"]):
                        for property_ in find_one_["col_structure"]["properties"]:
                            properties_master_[property_] = find_one_["col_structure"]["properties"][property_]
                        match_ = parent_["match"]
                        pipeline__ = []
                        let_ = {}
                        for match__ in match_:
                            if "exclude" in match__ and match__["exclude"] is True:
                                continue
                            if match__["key"] and match__["value"]:
                                key_ = match__["key"]
                                value_ = match__["value"]
                                let_[f"{key_}"] = f"${key_}"
                                if key_:
                                    pipeline__.append({"$eq": [f"$${key_}", f"${value_}"]})

                        pipeline_ = [{"$match": {"$expr": {"$and": pipeline__}}}]
                        lookup_ = {"from": f"{parent_collection_}_data", "let": let_, "pipeline": pipeline_, "as": parent_collection_}
                        unwind_ = {"path": f"${parent_collection_}", "preserveNullAndEmptyArrays": True}
                        replace_with_ = {"$mergeObjects": ["$$ROOT", f"${parent_collection_}"]}
                        pipe_.append({"$lookup": lookup_})
                        pipe_.append({"$unwind": unwind_})
                        pipe_.append({"$replaceWith": replace_with_})
                        unset_.append(parent_collection_)

            if unset_ and len(unset_) > 0:
                unset_ = list(dict.fromkeys(unset_))
                pipe_.append({"$unset": unset_})

            set_ = {"$set": {"_ID": {"$toObjectId": "$_id"}}}
            pipe_.append(set_)

            records_ = json.loads(JSONEncoder().encode(list(Mongo().db_[collection_id_].aggregate(pipe_))))

            count_ = len(records_) if records_ else 0
            df_ = pd.DataFrame(records_).fillna("#N/A")
            df_raw_ = pd.DataFrame(records_).fillna("")
            vie_visual_style_ = view_["chart_type"] if "chart_type" in view_ else "Vertical Bar"
            data_index_0_ = view_["data_index"][0] if "data_index" in view_ and len(view_["data_index"]) > 0 else None
            data_values_0_k_ = view_["data_values"][0]["key"] if "data_values" in view_ and len(view_["data_values"]) > 0 and "key" in view_["data_values"][0] else None
            data_values_0_v_ = view_["data_values"][0]["value"] if "data_values" in view_ and len(view_["data_values"]) > 0 and "value" in view_["data_values"][0] else "sum"
            data_columns_0_ = view_["data_columns"][0] if "data_columns" in view_ and len(view_["data_columns"]) > 0 else None
            pivot_totals_ = view_["pivot_totals"] if "pivot_totals" in view_ else False
            data_values_ = view_["data_values"] if "data_values" in view_ and len(["data_values"]) > 0 else None
            dropped_ = []

            if data_index_0_ in df_.columns:
                dropped_.append(data_index_0_)

            if data_values_0_k_ in df_.columns:
                dropped_.append(data_values_0_k_)

            if data_columns_0_ in df_.columns:
                dropped_.append(data_columns_0_)

            groupby_ = []

            if vie_visual_style_ == "Line":
                if data_columns_0_ and data_columns_0_ in df_.columns:
                    groupby_.append(data_columns_0_)
                if data_index_0_ and data_index_0_ in df_.columns:
                    groupby_.append(data_index_0_)
            else:
                if data_index_0_ and data_index_0_ in df_.columns:
                    groupby_.append(data_index_0_)
                if data_columns_0_ and data_columns_0_ in df_.columns:
                    groupby_.append(data_columns_0_)

            df_ = df_.drop([x for x in df_.columns if x not in dropped_], axis=1)
            dtypes_ = list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns)
            df_grp_ = df_.groupby(dtypes_, as_index=False).sum() if len(dtypes_) > 0 else None

            count_ = None
            sum_ = None
            unique_ = None
            mean_ = None
            stdev_ = None
            var_ = None

            if df_ is not None:
                count_ = len(df_)
                if count_ > 0 and data_values_0_k_ in df_.columns:
                    count_ = int(len(df_[data_values_0_k_]))
                    sum_ = float(pd.to_numeric(df_[data_values_0_k_], errors="coerce").sum())
                    unique_ = float(pd.to_numeric(df_[data_values_0_k_], errors="coerce").nunique())
                    mean_ = float(pd.to_numeric(df_[data_values_0_k_], errors="coerce").mean())
                    stdev_ = float(pd.to_numeric(df_[data_values_0_k_], errors="coerce").std())
                    var_ = float(pd.to_numeric(df_[data_values_0_k_], errors="coerce").var())

                if len(groupby_) > 0:
                    df_ = df_.groupby(groupby_, as_index=False).sum() if data_values_0_v_ == "sum" else df_.groupby(groupby_, as_index=False).count()

            dfj_ = json.loads(df_.to_json(orient="records"))

            series_ = []
            series_sub_ = []
            xaxis_ = None
            legend_ = None

            if data_index_0_ and data_values_0_k_ in df_.columns:
                if vie_visual_style_ in ["Pie", "Vertical Bar", "Horizontal Bar"]:
                    for idx_, item_ in enumerate(dfj_):
                        xaxis_ = item_[data_index_0_] if data_index_0_ in item_ else None
                        yaxis_ = item_[data_values_0_k_] if data_values_0_k_ in item_ else None
                        if xaxis_ and yaxis_:
                            series_.append({"name": xaxis_, "value": yaxis_})
                elif vie_visual_style_ == "Line":
                    for idx_, item_ in enumerate(dfj_):
                        if idx_ > 0 and item_[data_columns_0_] != legend_:
                            series_.append({"name": legend_, "series": series_sub_})
                            series_sub_ = []
                        series_sub_.append({"name": item_[data_index_0_], "value": item_[data_values_0_k_]})
                        legend_ = item_[data_columns_0_] if data_columns_0_ in item_ else None
                    if legend_:
                        series_.append({"name": legend_, "series": series_sub_})
                else:
                    for idx_, item_ in enumerate(dfj_):
                        if idx_ > 0 and item_[data_index_0_] != xaxis_:
                            series_.append({"name": xaxis_, "series": series_sub_})
                            series_sub_ = []
                        if data_columns_0_ in item_ and item_[data_columns_0_] is not None:
                            series_sub_.append({"name": item_[data_columns_0_], "value": item_[data_values_0_k_]})
                        xaxis_ = item_[data_index_0_] if data_index_0_ in item_ else None
                    if xaxis_:
                        series_.append({"name": xaxis_, "series": series_sub_})

            pvs_ = []
            aggfunc_ = {}

            for idx_, kv_ in enumerate(data_values_):
                if "key" in kv_ and "value" in kv_:
                    key_ = kv_["key"]
                    value_ = kv_["value"]
                    if key_ in df_.columns and value_ in ["count", "size", "sum", "mean", "average", "stdev", "var", "max", "min", "unique"]:
                        prfx_ = " " * idx_
                        nc_ = f"{prfx_}{key_} [{value_}]"
                        df_[nc_] = df_[key_]
                        pvs_.append(nc_)
                        df_[nc_] = pd.to_numeric(df_[nc_], errors="coerce")
                        if value_ == "count":
                            aggfunc_[nc_] = "count"
                        elif value_ == "size":
                            aggfunc_[nc_] = np.size
                        elif value_ == "sum":
                            aggfunc_[nc_] = np.sum
                        elif value_ == "mean":
                            aggfunc_[nc_] = np.mean
                        elif value_ == "average":
                            aggfunc_[nc_] = np.average
                        elif value_ == "stdev":
                            aggfunc_[nc_] = np.std
                        elif value_ == "var":
                            aggfunc_[nc_] = np.var
                        elif value_ == "unique":
                            aggfunc_[nc_] = lambda x: len(x.unique())
                        elif value_ == "max":
                            aggfunc_[nc_] = np.max
                        elif value_ == "min":
                            aggfunc_[nc_] = np.min
                        else:
                            aggfunc_[nc_] = "count"

            pivot_html_ = ""
            pivotify_html_ = ""

            if pvs_ and data_index_0_ and data_columns_0_ and aggfunc_ and pivot_totals_:
                pivot_table_ = pd.pivot_table(
                    df_,
                    values=pvs_,
                    index=data_index_0_,
                    columns=data_columns_0_,
                    aggfunc=aggfunc_,
                    margins=pivot_totals_,
                    margins_name="Total",
                    fill_value=0
                )

                background_ = "#eee"
                padding_ = 8
                padding_r_ = 2 * padding_
                font_size_table_ = 13
                styles_ = [
                    {"selector": "th", "props": [
                        ("background", f"{background_}"),
                        ("padding", f"{padding_}px {padding_r_}px"),
                        ("font-size", f"{font_size_table_}px"),
                    ]},
                    {"selector": "td", "props": [
                        ("background", f"{background_}"),
                        ("padding", f"{padding_}px {padding_r_}px"),
                        ("text-align", "right"),
                        ("font-size", f"{font_size_table_}px"),
                    ]},
                    {"selector": "table", "props": [("font-size", f"{font_size_table_}px")]},
                    {"selector": "caption", "props": [("caption-side", "top")]}
                ]

                pivot_html_ = pivot_table_.to_html().replace('border="1"', "")
                pivot_table_ = pivot_table_.style.set_table_styles(styles_)
                pivotify_html_ = pivot_table_.to_html().replace('border="1"', "")

            return {
                "result": True,
                "series": series_,
                "data": records_ if scope_ == "external" else [] if scope_ == "propsonly" else records_[:PREVIEW_ROWS_],
                "properties": properties_master_,
                "pivot": pivot_html_,
                "pivotify": pivotify_html_,
                "df": df_ if scope_ == "announcement" else None,
                "dfgrp": df_grp_ if scope_ == "announcement" else None,
                "dfraw": df_raw_ if scope_ == "announcement" else None,
                "view": view_,
                "stats": {
                    "count": count_ if count_ else 0,
                    "sum": sum_ if sum_ and sum_ > 0 else 0,
                    "unique": unique_ if unique_ and unique_ > 0 else 0,
                    "mean": mean_ if mean_ and mean_ > 0 else 0,
                    "stdev": stdev_ if stdev_ and stdev_ > 0 else 0,
                    "var": var_ if var_ and var_ > 0 else 0
                }
            }

        except pymongo.errors.PyMongoError as exc_:
            return Misc().mongo_error_f(exc_)

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def charts_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["userindb"]
            source_ = input_["source"]
            if source_ not in ["internal", "external", "propsonly"]:
                raise APIError("invalid source")

            collections_ = list(Mongo().db_["_collection"].aggregate([
                {
                    "$project": {
                        "col_id": 1,
                        "col_structure": 1,
                        "views": {"$objectToArray": "$col_structure.views"}
                    }
                }, {
                    "$match": {
                        "views": {
                            "$elemMatch": {
                                "v.enabled": True,
                                "v.flashcard": {"$ne": True},
                                "v._tags": {
                                    "$elemMatch": {"$in": user_["_tags"]}
                                }
                            }
                        }
                    }
                }
            ]))

            returned_views_ = []
            for collection_ in collections_:
                views_ = collection_["views"] if "views" in collection_ and len(collection_["views"]) > 0 else []
                for view_ in views_:
                    id__ = view_["k"]
                    view__ = view_["v"]

                    if "enabled" not in view__ or not view__["enabled"]:
                        continue

                    if "flashcard" in view__ and view__["flashcard"] is True:
                        continue

                    if not any(tag_ in user_["_tags"] for tag_ in view__["_tags"]):
                        continue

                    get_view_data_f_ = self.get_view_data_f(user_, id__, source_)

                    if "skip" in get_view_data_f_ and get_view_data_f_["skip"] is True:
                        continue

                    if not get_view_data_f_["result"]:
                        continue

                    returned_views_.append({
                        "id": id__,
                        "collection": collection_["col_id"],
                        "properties": get_view_data_f_["properties"],
                        "view": view__,
                        "data": get_view_data_f_["data"],
                        "series": get_view_data_f_["series"],
                        "pivot": get_view_data_f_["pivot"],
                        "stats": get_view_data_f_["stats"],
                        "priority": view__["priority"] if "priority" in view__ and view__["priority"] > 0 else 9999
                    })

            returned_views_.sort(key=operator.itemgetter("priority", "id"), reverse=False)

            return {"result": True, "views": returned_views_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def announcements_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["userindb"]
            data_ = list(Mongo().db_["_announcement"].find({"_tags": {"$elemMatch": {"$in": user_["_tags"]}}}).limit(20))
            announcements_ = json.loads(JSONEncoder().encode(data_))

            return {"result": True, "data": announcements_}

        except pymongo.errors.PyMongoError as exc_:
            return Misc().mongo_error_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def views_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["userindb"]

            collections_ = list(Mongo().db_["_collection"].aggregate([
                {
                    "$project": {
                        "col_id": 1,
                        "col_structure": 1,
                        "views": {"$objectToArray": "$col_structure.views"}
                    }
                }, {
                    "$match": {
                        "views": {
                            "$elemMatch": {
                                "v.enabled": True,
                                "v._tags": {
                                    "$elemMatch": {"$in": user_["_tags"]}
                                }
                            }
                        }
                    }
                }
            ]))

            returned_views_ = []
            for collection_ in collections_:
                cid_ = collection_["col_id"]
                col_structure_ = collection_["col_structure"]
                properties_ = col_structure_["properties"]
                views_ = collection_["views"] if "views" in collection_ and len(collection_["views"]) > 0 else []
                for view_ in views_:
                    id__ = view_["k"]
                    view__ = view_["v"]

                    if "enabled" not in view__ or not view__["enabled"]:
                        continue

                    if not any(tag_ in user_["_tags"] for tag_ in view__["_tags"]):
                        continue

                    count_ = 0
                    filter_ = view__["data_filter"] if "data_filter" in view__ else []
                    if len(filter_) > 0:
                        get_filtered_ = self.get_filtered_f({"match": filter_, "properties": properties_ if properties_ else None})
                        count_ = Mongo().db_[f"{cid_}_data"].count_documents(get_filtered_)

                    returned_views_.append({
                        "id": id__,
                        "collection": collection_["col_id"],
                        "view": view__,
                        "priority": view__["priority"] if "priority" in view__ and view__["priority"] > 0 else 9999,
                        "count": count_
                    })

            returned_views_.sort(key=operator.itemgetter("priority", "id"), reverse=False)

            return {"result": True, "views": returned_views_}

        except pymongo.errors.PyMongoError as exc_:
            return Misc().mongo_error_f(exc_)

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def collections_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"]
            structure_ = self.root_schemas_f("_collection")
            usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
            collections_ = list(Mongo().db_["_collection"].find(filter={}, sort=[("col_priority", 1), ("col_title", 1)]))

            if Auth().is_manager_f(user_) or Auth().is_admin_f(user_):
                data_ = collections_
            else:
                data__ = []
                for coll_ in collections_:
                    for usr_tag_ in usr_tags_:
                        filter_ = {
                            "per_collection_id": coll_["col_id"],
                            "per_tag": usr_tag_,
                            "$or": [
                                {"per_read": True},
                                {"per_insert": True},
                                {"per_update": True},
                                {"per_delete": True}
                            ]
                        }
                        permission_ = Mongo().db_["_permission"].find_one(filter_)
                        if permission_:
                            data__.append(coll_)
                            break
                data_ = data__

            return {"result": True, "data": json.loads(JSONEncoder().encode(data_)), "structure": structure_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def collection_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"]
            col_id_ = obj["collection"]
            data_ = {}
            usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []

            if col_id_ == "_query" or Auth().is_manager_f(user_) or Auth().is_admin_f(user_):
                permitted_ = True
            else:
                permitted_ = False
                for usr_tag_ in usr_tags_:
                    permissions_ = Mongo().db_["_permission"].find_one({
                        "per_collection_id": col_id_,
                        "per_tag": usr_tag_,
                        "$or": [
                            {"per_insert": True},
                            {"per_read": True},
                            {"per_update": True},
                            {"per_delete": True},
                            {"per_action": True}
                        ],
                    })
                    if permissions_:
                        permitted_ = True
                        break

            if permitted_:
                data_ = Mongo().db_["_collection"].find_one({"col_id": col_id_})
            else:
                raise AuthError(f"no collection permission {col_id_}")

            return {"result": True, "data": data_}

        except AuthError as exc_:
            return Misc().auth_error_f(exc_)

        except pymongo.errors.PyMongoError as exc_:
            return Misc().mongo_error_f(exc_)

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)

    def query_f(self, obj_):
        """
        docstring is in progress
        """
        schema_, query_, data_, fields_, count_, permitted_, aggregate_base_, err_ = {}, {}, [], [], 0, False, [], None
        files_, personalizations_to_, to_, orig_ = [], [], [], None
        init_res_ = {"result": True, "query": query_, "data": data_, "count": count_, "fields": fields_, "err": err_}
        try:
            que_id_ = obj_["id"] if "id" in obj_ else None
            if not que_id_:
                raise APIError("no query id defined")

            schema_ = self.root_schemas_f("_query")
            if not schema_:
                raise APIError("query schema not found")

            sched_ = "sched" in obj_ and obj_["sched"] is True
            key_ = obj_["key"] if "key" in obj_ and obj_["key"] is not None else None

            if not request:
                if key_ and key_ == SMTP_PASSWORD_:
                    orig_ = "sched"
                else:
                    raise APIError("no request detected")
            else:
                orig_ = request.base_url.replace(request.host_url, "")
                if orig_ not in ["api/crud", f"api/get/query/{que_id_}"]:
                    raise AuthError("request is not authenticated")

            query_ = Mongo().db_["_query"].find_one({"que_id": que_id_})
            if not query_:
                raise APIError("query not found")
            que_type_ = query_["que_type"] if "que_type" in query_ else "query"

            approved_ = "_approved" in query_ and query_["_approved"] is True
            if que_type_ != "query" and not approved_:
                err_ = "query needs to be approved by the administrators"
                raise PassException(err_)

            if orig_ == "api/crud":
                user_ = obj_["userindb"] if "userindb" in obj_ else None
                if not user_:
                    raise APIError(f"no user defined for {que_id_}")
                usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
                if Auth().is_manager_f(user_) or Auth().is_admin_f(user_):
                    permitted_ = True
                else:
                    for usr_tag_ in usr_tags_:
                        if usr_tag_ in query_["_tags"]:
                            permitted_ = True
                            break
                if not permitted_:
                    raise AuthError("user is not a subscriber")

            que_collection_id_ = query_["que_collection_id"] if "que_collection_id" in query_ else None
            if not que_collection_id_:
                raise APIError("query collection not defined")

            collection_ = Mongo().db_["_collection"].find_one({"col_id": que_collection_id_})
            if not collection_:
                raise APIError("query collection not found")

            structure_ = collection_["col_structure"] if "col_structure" in collection_ else None
            if not structure_:
                raise APIError("collection structure not found")

            properties_ = structure_["properties"] if "properties" in structure_ else None
            if not properties_:
                raise APIError("properties not found in structure")

            que_aggregate_ = query_["que_aggregate"] if "que_aggregate" in query_ and len(query_["que_aggregate"]) > 0 else None
            if not que_aggregate_:
                raise APIError("aggregation not found")

            queries_ = structure_["queries"] if "queries" in structure_ else None
            if not queries_:
                err_ = "queries not defined in the structure"
                raise PassException(err_)

            query_allowed_ = "query" in queries_ and queries_["query"] is True
            if not query_allowed_:
                err_ = "query not allowed for the collection"
                raise PassException(err_)

            update_allowed_ = "cronjob" in queries_ and queries_["cronjob"] is True
            updatables_ = queries_["updatables"] if "updatables" in queries_ and len(queries_["updatables"]) > 0 else None

            que_type_ = query_["que_type"] if "que_type" in query_ else "query"

            match_exists_, set_ = False, None
            for agg_ in que_aggregate_:
                if "$limit" in agg_ or "$skip" in agg_:
                    continue
                if "$match" in agg_:
                    match_exists_ = True
                if "$set" in agg_:
                    set_ = agg_["$set"]
                if "$project" in agg_:
                    for prj_ in agg_["$project"]:
                        fields_.append(prj_)
                aggregate_base_.append(agg_)

            aggregate_ = aggregate_base_.copy()

            if que_type_ == "job":
                if not update_allowed_:
                    err_ = "update queries not allowed for the collection"
                    raise PassException(err_)
                if not updatables_:
                    err_ = "no updatable fields defined in the collection structure"
                    raise PassException(err_)
                if not match_exists_:
                    err_ = "no match found in the update query"
                    raise PassException(err_)
                if not set_:
                    err_ = "no set found in the update query"
                    raise PassException(err_)
                set__ = {}
                for item_ in set_:
                    if item_ not in properties_:
                        continue
                    if item_ not in updatables_:
                        continue
                    value_ = set_[item_]
                    if str(value_).lower() == "$current_date":
                        value_ = Misc().get_now_f()
                    set__[item_] = value_
                if not set__:
                    err_ = "no valid set fields found in the update query"
                    raise PassException(err_)
                aggregate_update_ = []
                for agg_ in que_aggregate_:
                    if "$project" in agg_ or "$set" in agg_ or "$unset" in agg_:
                        continue
                    aggregate_update_.append(agg_)
                aggregate_update_.append({"$project": {"_id": "$_id"}})
                cursor_ = Mongo().db_[f"{que_collection_id_}_data"].aggregate(aggregate_update_)
                if not cursor_:
                    err_ = "no record found to update"
                    raise PassException(err_)
                data_ = json.loads(JSONEncoder().encode(list(cursor_)))
                ids_ = [ObjectId(doc_["_id"]) for doc_ in data_]
                if ids_:
                    set__["_modified_at"] = Misc().get_now_f()
                    update_many_ = Mongo().db_[f"{que_collection_id_}_data"].update_many({"_id": {"$in": ids_}}, {"$set": set__})
                    count_ = update_many_.matched_count
                return {"result": True, "query": query_, "data": [], "count": count_, "fields": [], "schema": schema_, "err": err_}

            aggregate_base_.append({"$count": "count"})

            if orig_ == "api/crud":
                page_ = obj_["page"] if "page" in obj_ and obj_["page"] > 0 else 1
                limit_ = obj_["limit"] if "limit" in obj_ and obj_["limit"] > 0 else API_QUERY_PAGE_SIZE_
                aggregate_.append({"$skip": limit_ * (page_ - 1)})
                aggregate_.append({"$limit": limit_})
            else:
                aggregate_.append({"$limit": API_DEFAULT_AGGREGATION_LIMIT_})

            cursor_ = Mongo().db_[f"{que_collection_id_}_data"].aggregate(aggregate_)
            data_ = json.loads(JSONEncoder().encode(list(cursor_)))
            count_ = len(data_)

            if sched_ and orig_ == "sched":
                _tags = query_["_tags"] if "_tags" in query_ and len(query_["_tags"]) > 0 else API_PERMISSIVE_TAGS_
                que_title_ = query_["que_title"] if "que_title" in query_ else que_id_
                que_message_body_ = query_["que_message_body"] if "que_message_body" in query_ and query_["que_message_body"] is not None else ""
                users_ = Mongo().db_["_user"].find({"_tags": {"$elemMatch": {"$in": _tags}}})
                for member_ in users_:
                    if member_["usr_id"] not in to_:
                        to_.append(member_["usr_id"])
                        personalizations_to_.append({"email": member_["usr_id"], "name": member_["usr_name"]})
                personalizations_ = {"to": personalizations_to_}
                df_raw_ = pd.DataFrame(data_).fillna("")
                file_excel_ = f"{API_TEMPFILE_PATH_}/query-{que_id_}-{Misc().get_timestamp_f()}.xlsx"
                df_raw_.to_excel(file_excel_, sheet_name=que_id_, engine="xlsxwriter", header=True, index=False)
                files_.append({"name": file_excel_, "type": "xlsx"})
                count_ = len(df_raw_.index)
                if count_ > 0:
                    email_sent_ = Email().send_email_f({
                        "personalizations": personalizations_,
                        "html": que_message_body_,
                        "subject": que_title_,
                        "files": files_
                    })
                    if not email_sent_["result"]:
                        raise APIError(email_sent_["msg"])

            return {"result": True, "query": query_, "data": data_, "count": count_, "fields": fields_, "schema": schema_, "err": err_}

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except pymongo.errors.PyMongoError as exc__:
            init_res_["result"] = False
            init_res_["schema"] = {}
            init_res_["query"], init_res_["fields"] = [], []
            init_res_["err"] = str(exc__)
            return init_res_

        except PassException as exc__:
            init_res_["schema"] = schema_
            init_res_["query"] = query_
            init_res_["err"] = str(exc__)
            return init_res_

        except Exception as exc__:
            init_res_["result"] = False
            init_res_["schema"] = {}
            init_res_["query"] = query_
            init_res_["err"] = str(exc__)
            return init_res_

    def read_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["user"]
            limit_ = input_["limit"]
            page_ = input_["page"]
            collection_id_ = input_["collection"]
            projection_ = input_["projection"]
            group_ = "group" in input_ and input_["group"] is True
            skip_ = limit_ * (page_ - 1)
            match_ = input_["match"] if "match" in input_ and len(input_["match"]) > 0 else []
            allowed_cols_ = ["_collection", "_query"]
            is_crud_ = collection_id_[:1] != "_"

            if collection_id_ not in allowed_cols_ and not Auth().is_manager_f(user_) and not Auth().is_admin_f(user_) and not is_crud_:
                raise AuthError(f"collection is not allowed to read: {collection_id_}")

            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            collation_ = {"locale": user_["locale"]} if user_ and "locale" in user_ else {"locale": "tr"}
            cursor_ = Mongo().db_["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemas_f(f"{collection_id_}")
            if not cursor_:
                raise APIError(f"collection not found to read: {collection_id_}")

            structure_ = cursor_["col_structure"] if is_crud_ else cursor_
            reconfig_ = cursor_["_reconfig_req"] if "_reconfig_req" in cursor_ and cursor_["_reconfig_req"] is True else False
            get_filtered_ = self.get_filtered_f({"match": match_, "properties": structure_["properties"] if "properties" in structure_ else None})

            if collection_id_ == "_query" and not (Auth().is_manager_f(user_) or Auth().is_admin_f(user_)):
                get_filtered_["_tags"] = {"$elemMatch": {"$in": user_["_tags"]}}

            sort_ = list(input_["sort"].items()) if "sort" in input_ and input_["sort"] else list(structure_["sort"].items()) if "sort" in structure_ and structure_["sort"] else [("_modified_at", -1)]

            if group_:
                group__ = {"_id": {}}
                project__ = {"_id": 0}
                sort__ = {}
                for item_ in projection_:
                    group__["_id"][item_] = f"${item_}"
                    project__[item_] = f"$_id.{item_}"
                    sort__[item_] = 1
                sort__ = input_["sort"] if "sort" in input_ else {"_modified_at": -1}
                group__["count"] = {"$sum": 1}
                project__["count"] = "$count"
                cursor_ = Mongo().db_[collection_].aggregate([{"$match": get_filtered_}, {"$sort": sort__}, {"$limit": limit_}, {"$group": group__}, {"$project": project__}])
            else:
                sort__ = {"_modified_at": -1}
                cursor_ = Mongo().db_[collection_].find(filter=get_filtered_, projection=projection_, sort=sort_, collation=collation_).skip(skip_).limit(limit_)

            docs_ = json.loads(JSONEncoder().encode(list(cursor_)))[:limit_] if cursor_ else []
            count_ = Mongo().db_[collection_].count_documents(get_filtered_)

            return {
                "result": True,
                "data": docs_,
                "count": count_,
                "structure": structure_,
                "reconfig": reconfig_
            }

        except AuthError as exc_:
            return Misc().auth_error_f(exc_)

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def crudschema_validate_f(self, obj):
        """
        docstring is in progress
        """
        try:
            properties_ = {}
            required_ = []
            validator_ = {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {},
                    "required": ["_id"],
                }
            }

            structure_ = obj["structure"]
            collection_ = obj["collection"]

            if collection_ in Mongo().db_.list_collection_names() and "properties" in structure_:
                properties_ = structure_["properties"]
                properties_ = Misc().properties_cleaner_f(properties_)

                if "required" in structure_ and structure_["required"] and len(structure_["required"]) > 0:
                    break_ = False
                    err_ = None
                    for req_ in structure_["required"]:
                        if req_ not in properties_:
                            break_ = True
                            err_ = f"{req_} is required but not found in the structure"
                            break
                    if break_:
                        raise APIError(err_)
                    required_ = structure_["required"]
                else:
                    required_ = None

                if properties_:
                    validator_["$jsonSchema"].update({"properties": properties_})

                if required_:
                    validator_["$jsonSchema"].update({"required": required_})

                Mongo().db_.command({"collMod": collection_, "validator": validator_})
                Mongo().db_[collection_].drop_indexes()

                if "index" in structure_ and len(structure_["index"]) > 0:
                    break_ = False
                    err_ = None
                    for indexes_ in structure_["index"]:
                        ixs = []
                        ix_name_ = ""
                        for ix_ in indexes_:
                            if ix_ not in properties_:
                                break_ = True
                                err_ = f"{ix_} was indexed but not found in properties"
                                break
                            ixs.append((ix_, pymongo.ASCENDING))
                            ix_name_ += f"_{ix_}"
                        if break_:
                            raise APIError(err_)
                        ix_name_ = f"ix_{collection_}{ix_name_}"
                        Mongo().db_[collection_].create_index(ixs, unique=False, name=ix_name_)

                if "unique" in structure_ and len(structure_["unique"]) > 0:
                    break_ = False
                    err_ = None
                    for uniques in structure_["unique"]:
                        uqs = []
                        uq_name_ = ""
                        for uq_ in uniques:
                            if uq_ not in properties_:
                                break_ = True
                                err_ = f"{uq_} is unique but not found in properties"
                                break
                            uqs.append((uq_, pymongo.ASCENDING))
                            uq_name_ += f"_{uq_}"
                        if break_:
                            raise APIError(err_)
                        uq_name_ = f"uq_{collection_}{uq_name_}"
                        Mongo().db_[collection_].create_index(uqs, unique=True, name=uq_name_)

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def nocrudschema_validate_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_ = obj["collection"]
            structure_ = self.root_schemas_f(f"{collection_}")
            schemavalidate_ = self.crudschema_validate_f({"collection": collection_, "structure": structure_})
            if not schemavalidate_["result"]:
                raise APIError(schemavalidate_["msg"])

            return {"result": True}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def savequery_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            que_id_ = obj_["id"] if "id" in obj_ and obj_["id"] is not None else None
            aggregate_ = obj_["aggregate"] if "aggregate" in obj_ and obj_["aggregate"] is not None else None
            approved_ = "approved" in obj_ and obj_["approved"] is True
            user_ = obj_["userindb"] if "userindb" in obj_ and obj_["userindb"] is not None else None

            if not user_:
                raise AuthError("user not found", obj_)

            if not aggregate_:
                raise APIError("no aggregation provided", obj_)

            if not que_id_:
                raise APIError("query not found", obj_)

            if not Auth().is_manager_f(user_) and not Auth().is_admin_f(user_):
                raise AuthError("query is locked to get modified")

            doc_ = {
                "que_aggregate": aggregate_,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_["usr_id"],
                "_approved": False
            }

            if approved_:
                if not Auth().is_admin_f(user_):
                    raise AuthError("no permission to approve")
                doc_["_approved"] = True
                doc_["_approved_at"] = Misc().get_now_f()
                doc_["_approved_by"] = user_["usr_id"]

            Mongo().db_["_query"].update_one({"que_id": que_id_}, {"$set": doc_, "$inc": {"_modified_count": 1}})

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def saveschema_f(self, obj):
        """
        docstring is in progress
        """
        try:
            col_id_ = obj["collection"] if "collection" in obj and obj["collection"] is not None else None
            structure_ = obj["structure"] if "structure" in obj and obj["structure"] is not None else None
            user_ = obj["user"] if "user" in obj and obj["user"] is not None else None

            if not user_:
                raise APIError("user not found")

            if not Auth().is_admin_f(user_):
                raise APIError("no permission to modify this schema")

            if not structure_:
                raise APIError("structure not found")

            if not col_id_:
                raise APIError("collection not found")

            properties_ = structure_["properties"] if "properties" in structure_ else None
            if not properties_:
                raise APIError("no properties found")

            arr_ = [str_ for str_ in structure_ if str_ not in STRUCTURE_KEYS_ and str_ not in STRUCTURE_KEYS_OPTIN_]
            if len(arr_) > 0:
                raise APIError(f"some structure keys are invalid: {','.join(arr_)}")

            arr_ = [str_ for str_ in structure_ if str_ in STRUCTURE_KEYS_]
            if len(arr_) != len(STRUCTURE_KEYS_):
                raise APIError(f"some structure keys are missing; expected: {','.join(STRUCTURE_KEYS_)}, considered: {','.join(arr_)}")

            for property_ in properties_:
                prop_ = properties_[property_]
                arr_ = [key_ for key_ in prop_ if key_ in PROP_KEYS_]
                if len(arr_) != len(PROP_KEYS_):
                    raise APIError(f"some keys are missing in property {property_}; expected: {','.join(PROP_KEYS_)}, considered: {','.join(arr_)}")

            Mongo().db_["_collection"].update_one({"col_id": col_id_}, {"$set": {
                "col_structure": structure_,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_["usr_id"]
            }, "$inc": {"_modified_count": 1}})

            func_ = self.crudschema_validate_f({"collection": f"{col_id_}_data", "structure": structure_})
            if not func_["result"]:
                raise APIError(func_["msg"])

            for property_ in properties_:
                prop_ = properties_[property_]
                if prop_["bsonType"] in ["int", "number", "float", "decimal", "string"] and "counter" in prop_ and prop_["counter"] is True:
                    counter_name_ = f"{property_.upper()}_COUNTER"
                    find_one_ = Mongo().db_["_kv"].find_one({"kav_key": counter_name_})
                    if not find_one_:
                        initialno__ = "0" if prop_["bsonType"] in ["int", "number", "float", "decimal"] else ""
                        initialas__ = "string" if prop_["bsonType"] == "string" else "int"
                        doc_ = {"kav_key": counter_name_, "kav_value": initialno__, "kav_as": initialas__}
                        doc_["_created_at"] = doc_["_modified_at"] = Misc().get_now_f()
                        doc_["_created_by"] = doc_["_modified_by"] = user_["usr_id"]
                        Mongo().db_["_kv"].insert_one(doc_)

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def saveview_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"] if "userindb" in obj else None
            col_id_ = obj["collection"]
            filter_ = obj["filter"]
            title_ = obj["title"].strip().title()
            view_id_ = title_.lower().replace(" ", "-")
            email_ = user_["usr_id"] if user_ and "usr_id" in user_ else None
            _tags = user_["_tags"]

            doc_ = Mongo().db_["_collection"].find_one({"col_id": col_id_})
            if not doc_:
                raise APIError("collection not found")

            view_ = {
                "title": title_,
                "description": f"{title_} Description",
                "priority": 9999,
                "enabled": True,
                "dashboard": False,
                "data_filter": filter_,
                "data_sort": {"_modified_at": -1},
                "data_excluded": [],
                "data_index": [],
                "data_columns": [],
                "data_values": [],
                "data_json": True,
                "data_excel": True,
                "data_csv": True,
                "pivot": True,
                "pivot_totals": True,
                "chart": True,
                "flashcard": False,
                "chart_type": "Stacked Vertical Bar",
                "chart_label": True,
                "chart_gradient": True,
                "chart_grid": True,
                "chart_legend": False,
                "chart_xaxis": True,
                "chart_xaxis_label": False,
                "chart_yaxis": True,
                "chart_yaxis_label": False,
                "chart_colors": [],
                "scheduled": False,
                "scheduled_cron": "15 14,15,16 * * mon,tue",
                "_tags": [
                    "#Managers",
                    "#Administrators"
                ]
            }
            doc_["col_structure"]["views"][view_id_] = view_
            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = email_

            Mongo().db_["_collection"].update_one({"col_id": col_id_}, {"$set": doc_})

            Misc().log_f({
                "type": "Info",
                "collection": col_id_,
                "op": "saveview",
                "user": email_,
                "document": doc_
            })

            return {"result": True, "id": view_id_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def upsert_f(self, obj):
        """
        docstring is in progress
        """
        try:
            doc = obj["doc"]
            _id = ObjectId(doc["_id"]) if "_id" in doc else None
            match_ = {"_id": _id} if _id else obj["match"] if "match" in obj and obj["match"] is not None and len(obj["match"]) > 0 else obj["filter"] if "filter" in obj else None
            link_ = obj["link"] if "link" in obj and obj["link"] is not None else None
            linked_ = obj["linked"] if "linked" in obj and obj["linked"] is not None else None
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            col_check_ = self.inner_collection_f(collection_id_)

            if collection_id_ in PROTECTED_COLLS_:
                raise APIError("collection is protected")

            if not col_check_["result"]:
                raise APIError("collection not found")

            is_crud_ = collection_id_[:1] != "_"
            if not is_crud_:
                schemavalidate_ = self.nocrudschema_validate_f({"collection": collection_id_})
                if not schemavalidate_["result"]:
                    raise APIError(schemavalidate_["msg"])

            doc = Misc().set_strip_doc_f(doc)

            doc_ = {}
            for item in doc:
                if item[:1] != "_" or item in Misc().get_except_underdashes():
                    doc_[item] = doc[item] if doc[item] is not None else None

            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            if collection_id_ == "_query":
                doc_["_approved"] = False

            Mongo().db_[collection_].update_one(match_, {"$set": doc_, "$inc": {"_modified_count": 1}})

            if is_crud_ and link_ and linked_:
                link_f_ = self.link_f({
                    "source": collection_id_,
                    "_id": str(_id),
                    "link": link_,
                    "linked": linked_,
                    "data": doc_,
                    "user": user_
                })
                if not link_f_["result"]:
                    raise AppException(link_f_["msg"])

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_id_,
                "op": "update",
                "user": user_["email"] if user_ else None,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AppException as exc:
            return Misc().app_exception_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def remove_f(self, obj):
        """
        docstring is in progress
        """
        try:
            doc_ = obj["doc"]
            _id = ObjectId(doc_["_id"]) if "_id" in doc_ else None
            match_ = {"_id": _id} if _id else obj["match"]
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]

            if collection_id_ not in PROTECTED_INSDEL_EXC_COLLS_:
                if collection_id_ in PROTECTED_COLLS_:
                    raise APIError("collection is protected to delete")

            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            doc_["_removed_at"] = Misc().get_now_f()
            doc_["_removed_by"] = user_["email"] if user_ and "email" in user_ else None

            Mongo().db_[collection_].delete_one(match_)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_id_,
                "op": "remove",
                "user": user_["email"] if user_ else None,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            if collection_ == "_collection":
                col_id_ = doc_["col_id"]
                Mongo().db_[f"{col_id_}_data"].aggregate([{"$match": {}}, {"$out": f"{col_id_}_data_removed"}])
                Mongo().db_[f"{col_id_}_data"].drop()

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def multiple_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_id_ = obj["collection"]
            user_ = obj["user"] if "user" in obj else None
            match_ = obj["match"] if "match" in obj else None

            op_ = obj["op"]
            if op_ not in ["clone", "delete"]:
                raise APIError("operation not supported")

            if op_ != "delete" or collection_id_ not in PROTECTED_INSDEL_EXC_COLLS_:
                if collection_id_ in PROTECTED_COLLS_:
                    raise APIError("collection is protected for bulk processes")

            if op_ == "delete" and collection_id_ == "_user":
                raise APIError("user collection is protected to delete")

            ids_ = []
            for _id in match_:
                ids_.append(ObjectId(_id))

            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            structure__ = Mongo().db_["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemas_f(f"{collection_id_}")
            if structure__:
                structure_ = structure__["col_structure"] if is_crud_ else structure__
            else:
                raise APIError(f"collection structure not found: {collection_id_}")
            if not structure_:
                raise APIError("structure not found")

            if "unique" in structure_ and "properties" in structure_:
                properties = structure_["properties"]
                unique = structure_["unique"]
            else:
                if op_ == "clone":
                    raise APIError("unique in structure not found")

            cursor = Mongo().db_[collection_].find({"_id": {"$in": ids_}})
            for index, doc in enumerate(cursor, start=1):
                col_id_ = doc["col_id"] if "col_id" in doc else None
                if op_ == "clone":
                    doc["_created_at"] = Misc().get_now_f()
                    doc["_created_by"] = user_["email"] if user_ and "email" in user_ else None
                    doc["_modified_at"] = None
                    doc["_modified_by"] = None
                    doc["_modified_count"] = -1
                    doc.pop("_id", None)
                    if unique:
                        for uq_ in unique:
                            if uq_[0] in doc:
                                if "objectId" in properties[uq_[0]] and properties[uq_[0]]["objectId"] is True:
                                    doc[uq_[0]] = str(bson.objectid.ObjectId())
                                elif properties[uq_[0]]["bsonType"] == "string":
                                    doc[uq_[0]] = f"{doc[uq_[0]]}-1" if "_" in doc[uq_[0]] else f"{doc[uq_[0]]}-{index}"
                                elif properties[uq_[0]]["bsonType"] in ["number", "int", "float", "decimal"]:
                                    doc[uq_[0]] = doc[uq_[0]] + 10000
                    Mongo().db_[collection_].insert_one(doc)
                elif op_ == "delete":
                    Mongo().db_[collection_].delete_one({"_id": doc["_id"]})
                    doc["_deleted_at"] = Misc().get_now_f()
                    doc["_deleted_by"] = user_["email"] if user_ and "email" in user_ else None
                    Mongo().db_[f"{collection_id_}_bin"].insert_one(doc)
                    if collection_ == "_collection":
                        suffix_ = Misc().get_timestamp_f()
                        Mongo().db_[f"{col_id_}_data"].aggregate([{"$match": {}}, {"$out": f"{col_id_}_data_bin_{suffix_}"}])
                        Mongo().db_[f"{col_id_}_data"].drop()

                log_ = Misc().log_f({
                    "type": "Info",
                    "collection": collection_,
                    "op": f"multiple {op_}",
                    "user": user_["email"] if user_ else None,
                    "document": doc
                })
                if not log_["result"]:
                    raise APIError(log_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def action_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_id_ = obj["collection"]
            user_ = obj["userindb"] if "userindb" in obj else None
            match_ = obj["match"] if "match" in obj else None
            actionix_ = obj["actionix"] if "actionix" in obj else None
            email_ = user_["usr_id"] if user_ and "usr_id" in user_ else None
            if not email_:
                raise AppException("user is not allowed")

            doc_ = obj["doc"] if "doc" in obj else None
            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = email_

            is_crud_ = collection_id_[:1] != "_"
            if not is_crud_:
                raise AppException("operation is not allowed")

            if int(actionix_) < 0:
                raise AppException("please select an action to run")
            actionix_ = int(actionix_)

            ids_ = []
            if match_ and len(match_) > 0:
                for _id in match_:
                    ids_.append(ObjectId(_id))

            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            schema_ = Mongo().db_["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemas_f(f"{collection_id_}")
            if not schema_:
                raise AppException("schema not found")

            structure_ = schema_["col_structure"] if "col_structure" in schema_ else None
            if not structure_:
                raise AppException(f"structure not found {collection_id_}")

            properties_ = structure_["properties"] if "properties" in structure_ else None
            if not properties_:
                raise AppException(f"properties not found {collection_id_}")

            action_ = structure_["actions"][actionix_] if "actions" in structure_ and len(structure_["actions"]) > 0 and structure_["actions"][actionix_] else None
            if not action_:
                raise AppException("action not found")

            action_id_ = action_["id"] if "id" in action_ and action_["id"] is not None else "action"
            tags_ = action_["_tags"] if "_tags" in action_ and len(action_["_tags"]) > 0 else None
            if not tags_:
                raise AppException("no tags found in action")

            apis_ = action_["apis"] if "apis" in action_ and len(action_["apis"]) > 0 else []
            set_ = action_["set"] if "set" in action_ else None
            uniqueness_ = "uniqueness" in action_ and action_["uniqueness"] is True
            unique_ = action_["unique"] if "unique" in action_ and len(action_["unique"]) > 0 else None

            if not set_ and not apis_:
                raise AppException("no set or apis provided in action")

            notification_ = action_["notification"] if "notification" in action_ else None
            notify_ = notification_ and notification_["notify"] is True
            filter_ = notification_["filter"] if notification_ and "filter" in notification_ and len(notification_["filter"]) > 0 else None
            get_notification_filtered_ = None

            if notify_ and filter_:
                get_notification_filtered_ = self.get_filtered_f({"match": filter_, "properties": properties_, "data": doc_})

            match_ = action_["match"] if "match" in action_ and len(action_["match"]) > 0 else {}
            get_filtered_ = self.get_filtered_f({"match": match_, "properties": properties_})

            if ids_ and len(ids_) > 0:
                get_filtered_ = {"$and": [get_filtered_, {"_id": {"$in": ids_}}]}
                if get_notification_filtered_:
                    get_notification_filtered_ = {"$and": [get_notification_filtered_, {"_id": {"$in": ids_}}]}
            else:
                if apis_:
                    raise AppException("no selection was made")

            if uniqueness_ and unique_:
                unique_ = set(unique_)
                group_ = {}
                for uq_ in unique_:
                    group_[uq_] = f"${uq_}"
                uniques_ = list(Mongo().db_[collection_].aggregate([{"$match": get_filtered_}, {"$group": {"_id": group_, "count": {"$sum": 1}}}]))
                if uniques_ and len(uniques_) > 1:
                    raise AppException(f"{(','.join(unique_))} must be unique in selection")

            count_ = 0
            if set_:
                set_ = {"$set": doc_, "$inc": {"_modified_count": 1}}
                update_many_ = Mongo().db_[collection_].update_many(get_filtered_, set_)
                count_ = update_many_.matched_count if update_many_.matched_count > 0 else 0
                if count_ == 0:
                    raise PassException("no rows affected due to the match criteria")

            files_ = []
            for api_ in apis_:
                id_ = api_["id"] if "id" in api_ and api_["id"] is not None else None
                if not id_:
                    PRINT_("!!! no action api id found")
                    continue
                enabled_ = "enabled" in api_ and api_["enabled"] is True
                if not enabled_:
                    PRINT_(f"!!! action api not enabled: {id_}")
                    continue
                url_ = api_["url"] if "url" in api_ and api_["url"][:4] in ["http", "https"] else None
                if not url_:
                    PRINT_(f"!!! invalid url in action api: {id_}")
                    continue
                headers_ = api_["headers"] if "headers" in api_ else None
                if not headers_:
                    PRINT_(f"!!! invalid headers in action api: {id_}")
                    continue
                method_ = api_["method"] if "method" in api_ and api_["method"].lower() in ["get", "post"] else None
                if not method_:
                    PRINT_(f"!!! invalid method in action api: {id_}")
                    continue
                map_ = api_["map"] if "map" in api_ else None
                if not map_:
                    PRINT_(f"!!! no map found: {id_}")
                    continue

                json_ = {}
                for _, value_ in map_.items():
                    if value_ in doc_:
                        json_["key"] = value_
                        json_["value"] = doc_[value_]
                if not json_:
                    PRINT_(f"!!! no mapping values found: {id_}")
                    continue
                json_["ids"] = []
                if ids_ and len(ids_) > 0:
                    json_["ids"] = ids_
                json_["map"] = map_
                json_["email"] = email_

                response_ = requests.post(url_, json=json.loads(JSONEncoder().encode(json_)), headers=headers_, timeout=60)
                res_ = json.loads(response_.content)
                res_content_ = res_["content"] if "content" in res_ else ""
                res_files_ = res_["files"] if "files" in res_ and len(res_["files"]) > 0 else None
                if response_.status_code != 200:
                    raise AppException(f"{res_content_}")

                if res_files_:
                    files_ += res_files_

            if notify_:
                notify_collection_ = f"{notification_['collection']}_data" if "collection" in notification_ else collection_
                if notify_collection_ != collection_:
                    get_properties_ = self.get_properties_f(notification_["collection"])
                    if not get_properties_["result"]:
                        raise AppException(get_properties_["msg"])
                    properties_ = get_properties_["properties"]
                    get_notification_filtered_ = self.get_filtered_f({"match": filter_, "properties": properties_, "data": doc_})
                attachment_ = "attachment" in notification_ and notification_["attachment"] is True
                subject_ = notification_["subject"] if "subject" in notification_ else "Action Completed"
                body_ = notification_["body"] if "body" in notification_ else "<p>Hi,</p><p>Action completed successfully.</p><p><h1></h1></p>"
                fields_ = str(",".join(notification_["fields"])) if "fields" in notification_ and str(type(notification_["fields"])) == "<class 'list'>" and len(
                    notification_["fields"]) > 0 else notification_["fields"].replace(" ", "") if notification_ and "fields" in notification_ else None

                if get_notification_filtered_ and fields_ and attachment_:
                    type_ = "csv"
                    file_ = f"{API_TEMPFILE_PATH_}/{action_id_}-{Misc().get_timestamp_f()}.{type_}"
                    query_ = json.dumps(get_notification_filtered_, default=json_util.default, sort_keys=False)
                    subprocess.call(["mongoexport"] + Misc().commands_f("mongoexport", {"query": query_, "fields": fields_, "type": type_, "file": file_, "collection": notify_collection_}))
                    files_ += [{"name": file_, "type": type_}]

                email_sent_ = Email().send_email_f({"op": "action", "tags": tags_, "subject": subject_, "html": body_, "files": files_})
                if not email_sent_["result"]:
                    raise APIError(email_sent_["msg"])

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_,
                "op": "action",
                "user": email_,
                "document": {"doc": doc_, "match": match_}
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "count": count_, "content": "OK"}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AppException as exc__:
            return Misc().app_exception_f(exc__)

        except PassException as exc__:
            return Misc().pass_exception_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def insert_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            doc_ = obj["doc"]
            link_ = obj["link"] if "link" in obj and obj["link"] is not None else None
            linked_ = obj["linked"] if "linked" in obj and obj["linked"] is not None else None

            if collection_id_ not in PROTECTED_INSDEL_EXC_COLLS_:
                if collection_id_ in PROTECTED_COLLS_:
                    raise APIError("collection is protected to add")

            if "_id" in doc_:
                doc_.pop("_id", None)

            if "_structure" in doc_:
                doc_.pop("_structure", None)

            inserted_ = None
            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            doc_["_created_at"] = doc_["_modified_at"] = Misc().get_now_f()
            doc_["_created_by"] = doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None

            if collection_id_ == "_collection":
                file_ = "_template.json"
                prefix_ = doc_["col_prefix"] if "col_prefix" in doc_ else "zzz"
                path_ = f"/app/_template/{file_}"
                if os.path.isfile(path_):
                    with open(path_, "r", encoding="utf-8") as fopen_:
                        jtxt_ = fopen_.read()
                        jtxt_ = jtxt_.replace("zzz_", f"{prefix_}_")
                        structure_ = json.loads(jtxt_)
                doc_["col_structure"] = structure_
            elif collection_id_ == "_token":
                tkn_lifetime_ = int(doc_["tkn_lifetime"]) if "tkn_lifetime" in doc_ and int(doc_["tkn_lifetime"]) > 0 else 1440
                secret_ = pyotp.random_base32()
                token_finder_ = pyotp.random_base32()
                jwt_proc_f_ = Misc().jwt_proc_f("encode", None, secret_, {
                    "iss": "Technoplatz",
                    "aud": "api",
                    "sub": "bi",
                    "exp": Misc().get_now_f() + timedelta(minutes=tkn_lifetime_),
                    "iat": Misc().get_now_f()
                }, {"finder": token_finder_})
                if not jwt_proc_f_["result"]:
                    raise AuthError(jwt_proc_f_["msg"])
                doc_["tkn_copy_count"] = 0
                doc_["tkn_token"] = inserted_ = jwt_proc_f_["jwt"]
                doc_["tkn_secret"] = secret_
                doc_["tkn_finder"] = token_finder_

            doc_ = Misc().set_strip_doc_f(doc_)

            insert_one_ = Mongo().db_[collection_].insert_one(doc_)
            _id = insert_one_.inserted_id

            if collection_id_ == "_collection":
                col_id_ = doc_["col_id"] if "col_id" in doc_ else None
                col_structure_ = doc_["col_structure"] if "col_structure" in doc_ else None
                datac_ = f"{col_id_}_data"
                if col_structure_ and col_structure_ != {} and datac_ not in Mongo().db_.list_collection_names():
                    Mongo().db_[datac_].insert_one({})
                    schemavalidate_ = self.crudschema_validate_f({"collection": datac_, "structure": col_structure_})
                    if not schemavalidate_["result"]:
                        raise APIError(schemavalidate_["msg"])
                    Mongo().db_[datac_].delete_one({})

            if is_crud_:
                get_properties_ = self.get_properties_f(collection_id_)
                if not get_properties_["result"]:
                    raise APIError(get_properties_["msg"])
                properties_ = get_properties_["properties"]
                for property_ in properties_:
                    prop_ = properties_[property_]
                    if "counter" in prop_ and prop_["counter"] is True and prop_["bsonType"] in ["int", "number", "float", "decimal", "string"]:
                        if prop_["bsonType"] in ["int", "number", "float", "decimal"]:
                            counter_name_ = f"{property_.upper()}_COUNTER"
                            counter_ = doc_[property_]
                        else:
                            counter_ = doc_[property_]
                        Mongo().db_["_kv"].update_one({"kav_key": counter_name_}, {"$set": {"kav_value": str(counter_)}})

                if link_ and linked_:
                    link_f_ = self.link_f({
                        "source": collection_id_,
                        "_id": str(_id),
                        "link": link_,
                        "linked": linked_,
                        "data": doc_,
                        "user": user_
                    })
                    if not link_f_["result"]:
                        raise APIError(link_f_["msg"])

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_id_,
                "op": "insert",
                "user": user_["email"] if user_ else None,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "token": inserted_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AuthError as exc_:
            return Misc().auth_error_f(exc_)

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)


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
            html_ = f"{msg['html']} {EMAIL_DISCLAIMER_HTML_}" if "html" in msg else EMAIL_DISCLAIMER_HTML_
            tags_ = msg["tags"] if "tags" in msg and len(msg["tags"]) > 0 else None
            personalizations_ = msg["personalizations"] if "personalizations" in msg else None
            subject_ = msg["subject"] if "subject" in msg else None

            if subject_ is None:
                subject_ = (
                    EMAIL_UPLOADERR_SUBJECT_
                    if op_ in ["uploaderr", "importerr"]
                    else EMAIL_SIGNIN_SUBJECT_
                    if op_ == "signin"
                    else EMAIL_TFA_SUBJECT_
                    if op_ == "tfa"
                    else EMAIL_SIGNUP_SUBJECT_
                    if op_ == "signup"
                    else msg["subject"]
                    if msg["subject"]
                    else EMAIL_DEFAULT_SUBJECT_
                )

            if subject_ is None:
                raise APIError("subject is missing")

            if html_ is None or html_ == "":
                raise APIError("email message is missing")

            if tags_:
                get_users_from_tags_f_ = Misc().get_users_from_tags_f(tags_)
                if not get_users_from_tags_f_["result"]:
                    raise APIError(f"personalizations error {get_users_from_tags_f_['msg']}")
                personalizations_ = get_users_from_tags_f_ if "to" in get_users_from_tags_f_ else None

            if personalizations_ is None:
                raise APIError("email personalizations is missing")

            if "to" not in personalizations_ or len(personalizations_["to"]) == 0:
                raise APIError("to list is missing")

            email_from_ = f"{COMPANY_NAME_} <{FROM_EMAIL_}>"
            server_ = smtplib.SMTP_SSL(SMTP_SERVER_, SMTP_PORT_)
            server_.ehlo()
            server_.login(SMTP_USERID_, SMTP_PASSWORD_)

            message_ = MIMEMultipart()
            message_["From"] = email_from_
            message_["Subject"] = subject_
            message_.attach(MIMEText(html_, "html"))

            for file_ in files_:
                filename_ = file_["name"].replace(f"{API_TEMPFILE_PATH_}/", "") if "name" in file_ else None
                if not filename_:
                    raise APIError("file not defined")
                fullpath_ = os.path.normpath(os.path.join(API_TEMPFILE_PATH_, filename_))
                if not fullpath_.startswith(TEMP_PATH_):
                    PRINT_("!!! [email] fullpath_", fullpath_)
                    raise APIError("file not allowed [email]")
                with open(fullpath_, "rb") as attachment_:
                    part_ = MIMEBase("application", "octet-stream")
                    part_.set_payload(attachment_.read())
                encoders.encode_base64(part_)
                part_.add_header("Content-Disposition", f"attachment; filename= {filename_}")
                message_.attach(part_)

            recipients_ = []
            recipients_str_ = ""
            for recipient_ in personalizations_["to"]:
                email_to_ = f"{recipient_['name']} <{recipient_['email']}>" if recipient_["name"] and "name" in recipient_ else recipient_["email"]
                recipients_str_ += email_to_ if recipients_str_ == "" else f", {email_to_}"
                recipients_.append(recipient_["email"])

            message_["To"] = recipients_str_
            server_.sendmail(email_from_, recipients_, message_.as_string())
            server_.close()

            return {"result": True}

        except smtplib.SMTPResponseException as exc_:
            return Misc().notify_exception_f(f"smtp error: {exc_.smtp_error}")

        except smtplib.SMTPServerDisconnected as exc_:
            return {"result": True, "exc": str(exc_)}

        except APIError as exc_:
            return Misc().notify_exception_f(exc_)

        except Exception as exc_:
            return Misc().notify_exception_f(exc_)


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

            Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_otp_secret": aut_otp_secret_,
                "aut_otp_validated": False,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": email_,
                "_otp_secret_modified_at": Misc().get_now_f(),
                "_otp_secret_modified_by": email_,
            }, "$inc": {"_modified_count": 1}
            })

            return {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

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
                Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                    "aut_otp_validated": validated_,
                    "_otp_validated_at": Misc().get_now_f(),
                    "_otp_validated_by": email_,
                    "_otp_validated_ip": Misc().get_client_ip_f(),
                }, "$inc": {"_modified_count": 1}
                })
            else:
                Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                    "aut_otp_validated": validated_,
                    "_otp_not_validated_at": Misc().get_now_f(),
                    "_otp_not_validated_by": email_,
                    "_otp_not_validated_ip": Misc().get_client_ip_f()
                }, "$inc": {"_modified_count": 1}
                })
                raise AuthError("invalid otp")

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_auth",
                "op": "validate-otp",
                "user": email_,
                "document": {
                    "otp": otp_,
                    "success": validated_,
                    "ip": Misc().get_client_ip_f(),
                    "_modified_at": Misc().get_now_f(),
                    "_modified_by": email_,
                }})
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
            user_ = Mongo().db_["_user"].find_one({"usr_id": email_, "usr_enabled": True, "usr_scope": {"$in": ["Internal", "Administrator"]}})
            if not user_ or user_ is None:
                raise APIError("user not found")

            usr_id_ = user_["usr_id"]
            name_ = user_["usr_name"]
            tfac_ = randint(100001, 999999)
            Mongo().db_["_auth"].update_one({"aut_id": usr_id_}, {"$set": {"aut_tfac": tfac_, "_tfac_modified_at": Misc().get_now_f()}, "$inc": {"_modified_count": 1}})
            email_sent_ = Email().send_email_f({
                "op": "tfa",
                "personalizations": {"to": [{"email": usr_id_, "name": name_}]},
                "html": f"<p>Hi {name_},</p><p>Here's your backup two-factor access code so that you can validate your account;</p><p><h1>{tfac_}</h1></p>"
            })
            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)


class Auth:
    """
    docstring is in progress
    """

    def is_admin_f(self, user_):
        """
        docstring is in progress
        """
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        in_admin_tags_ = any(tag_ in tags_ for tag_ in API_ADMIN_TAGS_)
        in_admin_ips_ = Misc().in_admin_ips_f()
        return in_admin_tags_ and in_admin_ips_

    def is_manager_f(self, user_):
        """
        docstring is in progress
        """
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        in_permissive_tags_ = any(tag_ in tags_ for tag_ in API_PERMISSIVE_TAGS_)
        in_admin_ips_ = Misc().in_admin_ips_f()
        return in_permissive_tags_ and in_admin_ips_

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

            find_ = Mongo().db_["_token"].find_one({"tkn_finder": token_finder_, "tkn_is_active": True})
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

            if qid_ and "tkn_allowed_queries" in find_ and len(find_["tkn_allowed_queries"]) > 0:
                if qid_ not in find_["tkn_allowed_queries"]:
                    raise AuthError(f"token is not allowed to read {qid_}")

            if not ("tkn_allowed_ips" in find_ and len(find_["tkn_allowed_ips"]) > 0 and
                    (ip_ in find_["tkn_allowed_ips"] or "0.0.0.0" in find_["tkn_allowed_ips"])):
                raise AuthError(f"IP is not allowed to do {operation_}")

            return {"result": True}

        except AuthError as exc_:
            return ({"result": False, "msg": str(exc_)})

        except jwt.ExpiredSignatureError as exc_:
            return ({"result": False, "msg": str(exc_)})

        except jwt.JWTClaimsError as exc_:
            return ({"result": False, "msg": str(exc_)})

        except jwt.JWTError as exc_:
            return ({"result": False, "msg": str(exc_)})

        except Exception as exc_:
            return ({"result": False, "msg": str(exc_)})

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

            if str(aut_tfac_) != str(tfac_):
                if aut_otp_secret_:
                    validate_qr_f_ = OTP().validate_qr_f(email_, {"otp": tfac_})
                    if not validate_qr_f_["result"]:
                        raise AuthError("invalid otp")
                else:
                    raise AuthError("invalid otp")

            Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_tfac": None,
                "aut_tfac_ex": aut_tfac_,
                "_modified_at": Misc().get_now_f()
            }, "$inc": {"_modified_count": 1}
            })

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": "_auth",
                "op": op_,
                "user": email_,
                "document": {
                    "otp_entered": tfac_,
                    "otp_expected": aut_tfac_,
                    "exception": str(exc),
                    "_modified_at": Misc().get_now_f(),
                    "_modified_by": email_,
                }
            })
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

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
            pat = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*.-_?&]{8,32}$")
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
            Mongo().db_["_auth"].update_one({"aut_id": aut_id_}, {"$set": {
                "aut_jwt_secret": None,
                "aut_jwt_token": None,
                "aut_tfac": None,
                "_signed_out_at": Misc().get_now_f()}, "$inc": {"_modified_count": 1}
            })
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
            adminops_ = ["dumpu", "dumpr", "dumpd"]
            read_permissive_colls_ = ["_collection", "_query", "_announcement"]
            read_permissive_ops_ = ["read", "query", "queries", "charts", "views", "collection", "collections", "announcements"]
            insert_permissive_ops_ = ["clone"]
            update_permissive_ops_ = ["savequery"]
            is_crud_ = collection_id_ and collection_id_[:1] != "_"
            allowmatch_ = []

            if not op_:
                raise APIError("no operation provided")

            if not user_id_:
                raise APIError(f"no user defined: {user_id_}")

            if Auth().is_admin_f(user_):
                return {"result": True}

            if op_ in adminops_:
                raise AuthError(f"{op_} is not allowed")

            if Auth().is_manager_f(user_):
                return {"result": True}

            if not collection_id_:
                raise AuthError(f"no collection provided: {op_}")

            if op_ in read_permissive_ops_:
                op_ = "read"

            if op_ in insert_permissive_ops_:
                op_ = "insert"

            if op_ in update_permissive_ops_:
                op_ = "update"

            if op_ in read_permissive_ops_ and collection_id_ in read_permissive_colls_:
                return {"result": True}

            if not is_crud_:
                raise AuthError(f"{collection_id_} is not allowed to {op_}")

            permit_ = False
            for usr_tag_ in usr_tags_:
                permission_ = Mongo().db_["_permission"].find_one({"per_collection_id": collection_id_, "per_tag": usr_tag_})
                if permission_:
                    per_insert_ = "per_insert" in permission_ and permission_["per_insert"] is True
                    per_read_ = "per_read" in permission_ and permission_["per_read"] is True
                    per_update_ = "per_update" in permission_ and permission_["per_update"] is True
                    per_delete_ = "per_delete" in permission_ and permission_["per_delete"] is True
                    per_action_ = "per_action" in permission_ and permission_["per_action"] is True
                    if (op_ == "read" and per_read_) or \
                        (op_ == "insert" and per_insert_ and per_read_) or \
                        (op_ == "import" and per_insert_ and per_read_) or \
                        (op_ == "upsert" and per_insert_ and per_update_ and per_read_) or \
                        (op_ == "update" and per_update_ and per_read_) or \
                        (op_ == "action" and per_action_ and per_read_) or \
                        (op_ == "clone" and per_insert_ and per_read_) or \
                            (op_ == "delete" and per_read_ and per_delete_):
                        permit_ = True
                        per_match_ = permission_["per_match"] if "per_match" in permission_ and len(permission_["per_match"]) > 0 else None
                        if per_match_:
                            allowmatch_ = per_match_
                        break

            if not permit_:
                raise AuthError(f"user is not allowed to {op_} {collection_id_}")

            return {"result": True, "allowmatch": allowmatch_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def firewall_f(self, user_):
        """
        docstring is in progress
        """
        try:
            ip_ = Misc().get_client_ip_f()
            tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
            allowed_ = Mongo().db_["_firewall"].find_one({
                "$or": [
                    {"fwa_tag": {"$in": tags_}, "fwa_source_ip": ip_, "fwa_enabled": True},
                    {"fwa_tag": {"$in": tags_}, "fwa_source_ip": "0.0.0.0", "fwa_enabled": True}
                ]
            })
            if not allowed_:
                raise AuthError(f"connection is not allowed from IP address {ip_}")

            return {"result": True}

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": "_firewall",
                "op": "block",
                "user": user_["usr_id"],
                "document": {
                    "ip": ip_,
                    "exception": str(exc),
                    "_modified_at": Misc().get_now_f(),
                    "_modified_by": user_["usr_id"],
                }
            })
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def account_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["user"] if "user" in input_ else None
            auth_ = input_["auth"] if "auth" in input_ else None
            email_ = user_["email"] if "email" in user_ else None
            op_ = input_["op"]

            response_ = {}
            api_key_ = None

            if op_ == "apikeygen":
                api_key_ = secrets.token_hex(16)
                Mongo().db_["_auth"].update_one(
                    {"aut_id": email_}, {"$set": {
                        "aut_api_key": api_key_,
                        "_api_key_modified_at": Misc().get_now_f(),
                        "_api_key_modified_by": email_
                    }, "$inc": {"_api_key_modified_count": 1}})
                response_ = {"api_key": api_key_, "_modified_at": Misc().get_now_f()}
            elif op_ == "apikeyget":
                api_key_modified_at_ = auth_["_api_key_modified_at"] if "_api_key_modified_at" in auth_ else None
                api_key_ = auth_["aut_api_key"] if "aut_api_key" in auth_ else None
                response_ = {"api_key": api_key_, "api_key_modified_at": api_key_modified_at_}
            else:
                raise APIError("operation not supported " + op_)

            return {"result": True, "user": response_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

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
            if not auth_:
                raise AuthError("account not found")

            otp_send_ = OTP().request_otp_f(email_)
            if not otp_send_["result"]:
                raise APIError(otp_send_["msg"])

            return {"result": True, "user": None}

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
            email_ = escape(input_["email"])
            password_ = escape(input_["password"])
            tfac_ = escape(input_["tfac"])

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

            Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_salt": salt_,
                "aut_key": key_,
                "aut_tfac": None,
                "aut_expires": 0,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": email_,
            }, "$inc": {"_modified_count": 1}})

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
            email_ = escape(input_["email"])
            password_ = escape(input_["password"])
            tfac_ = escape(input_["tfac"])

            user_validate_ = self.user_validate_by_basic_auth_f({"userid": email_, "password": password_})
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])
            user_ = user_validate_["user"] if "user" in user_validate_ else None
            auth_ = user_validate_["auth"] if "auth" in user_validate_ else None

            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, "signin")
            if not verify_otp_f_["result"]:
                raise AuthError(verify_otp_f_["msg"])

            usr_name_ = user_["usr_name"]
            perm_ = Auth().is_manager_f(user_) or Auth().is_admin_f(user_)
            perma_ = Auth().is_admin_f(user_)
            payload_ = {
                "iss": "Technoplatz",
                "aud": "api",
                "sub": "bi",
                "exp": Misc().get_now_f() + timedelta(minutes=int(API_SESSION_EXP_MINUTES_)),
                "iat": Misc().get_now_f(),
                "id": email_,
                "name": usr_name_,
                "perm": perm_,
                "perma": perma_
            }
            secret_ = pyotp.random_base32()
            jwt_proc_f_ = Misc().jwt_proc_f("encode", None, secret_, payload_, None)
            if not jwt_proc_f_["result"]:
                raise AuthError(jwt_proc_f_["msg"])
            token_ = jwt_proc_f_["jwt"]

            api_key_ = auth_["aut_api_key"] if "aut_api_key" in auth_ and auth_["aut_api_key"] is not None else None
            if api_key_ is None:
                api_key_ = secrets.token_hex(16)

            Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_jwt_secret": secret_,
                "aut_jwt_token": token_,
                "aut_tfac": None,
                "aut_api_key": api_key_,
                "_modified_at": Misc().get_now_f(),
                "_jwt_at": Misc().get_now_f()},
                "$inc": {"_modified_count": 1}
            })

            ip_ = Misc().get_client_ip_f()
            user_payload_ = {"token": token_, "name": usr_name_, "email": email_, "perm": perm_, "perma": perma_, "api_key": api_key_, "ip": ip_}

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_auth",
                "op": "signin",
                "user": email_,
                "document": {"_signedin_at": Misc().get_now_f(), "ip": ip_, "perm": perm_}
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            if "_otp_validated_ip" in auth_ and auth_["_otp_validated_ip"] is not None and auth_["_otp_validated_ip"] != ip_:
                email_sent_ = Email().send_email_f({
                    "op": "signin",
                    "personalizations": {"to": [{"email": email_, "name": usr_name_}]},
                    "html": f"<p>Hi {usr_name_},<br /><br />You have now signed-in from {ip_}.</p>",
                })
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

            jwt_secret_ = auth_["aut_jwt_secret"] if "aut_jwt_secret" in auth_ and auth_["aut_jwt_secret"] is not None else None

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

            user_ = Mongo().db_["_user"].find_one({"usr_id": aut_id_, "usr_enabled": True, "usr_scope": {"$in": ["Internal", "Administrator"]}})
            if not user_:
                raise AuthError("user not found")

            user_["email"] = user_["usr_id"]
            user_["api_key"] = auth_["aut_api_key"]

            return ({"result": True, "user": user_, "auth": auth_})

        except PassException as exc_:
            return Misc().pass_exception_f(exc_)

        except AuthError as exc_:
            return Misc().auth_error_f(exc_)

        except Exception as exc_:
            return ({"result": False, "msg": "invalid session", "exc": str(exc_)})

    def user_validate_by_basic_auth_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_id_ = Misc().clean_f(input_["userid"]) if "userid" in input_ else None
            password_ = Misc().clean_f(input_["password"]) if "password" in input_ else None

            if not user_id_:
                raise APIError("email must be provided")

            pat = re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
            if not re.search(pat, user_id_):
                raise APIError("invalid user id")

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": user_id_})
            if not auth_:
                raise AuthError("account not found")

            if "aut_salt" not in auth_ or auth_["aut_salt"] is None:
                raise AuthError("please set a new password")
            if "aut_key" not in auth_ or auth_["aut_key"] is None:
                raise AuthError("you need to set a new password")

            user_ = Mongo().db_["_user"].find_one({"usr_id": user_id_, "usr_enabled": True, "usr_scope": {"$in": ["Internal", "Administrator"]}})
            if not user_:
                raise AuthError("user not found for validate")
            user_["aut_api_key"] = auth_["aut_api_key"] if "aut_api_key" in auth_ and auth_["aut_api_key"] is not None else None

            if not password_:
                raise AuthError("no credentials provided")

            salt_ = auth_["aut_salt"]
            key_ = auth_["aut_key"]
            hash_f_ = self.password_hash_f(password_, salt_)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])
            new_key_ = hash_f_["key"]
            if new_key_ != key_:
                raise AuthError("invalid email or password")

            firewall_ = self.firewall_f(user_)
            if not firewall_["result"]:
                raise AuthError(firewall_["msg"])

            return {"result": True, "user": user_, "auth": auth_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def user_validate_by_api_key_f(self, input_):
        """
        docstring is in progress
        """
        try:
            api_key_ = Misc().clean_f(input_["api_key"]) if "api_key" in input_ else None
            if not api_key_ or api_key_ is None:
                raise AuthError("api key must be provided")

            auth_ = Mongo().db_["_auth"].find_one({"aut_api_key": api_key_})
            if not auth_:
                raise AuthError("user is not authenticated")
            user_id_ = auth_["aut_id"]

            user_ = Mongo().db_["_user"].find_one({"usr_id": user_id_, "usr_enabled": True, "usr_scope": {"$in": ["Internal", "Administrator"]}})
            if not user_:
                raise APIError("user not found to validate")

            firewall_ = self.firewall_f(user_)
            if not firewall_["result"]:
                raise APIError(firewall_["msg"])

            return {"result": True, "user": user_, "auth": auth_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def signin_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            email_ = escape(input_["email"])
            password_ = escape(input_["password"])

            user_validate_ = self.user_validate_by_basic_auth_f({"userid": email_, "password": password_})
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])

            otp_send_ = OTP().request_otp_f(email_)
            if not otp_send_["result"]:
                raise APIError(otp_send_["msg"])

            return {"result": True, "msg": "2FA required", "user": None}

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

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
            password_ = Misc().clean_f(input_["password"])

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": user_id_})
            if auth_:
                raise AuthError("account already exists")

            user_ = Mongo().db_["_user"].find_one({"usr_id": user_id_, "usr_enabled": True, "usr_scope": {"$in": ["Internal", "Administrator"]}})
            if not user_:
                raise AuthError("user not found")

            usr_scope_ = user_["usr_scope"] if "usr_scope" in user_ else None
            if not usr_scope_ or usr_scope_ not in ["Internal", "Administrator"]:
                raise AuthError("invalid signup request")

            hash_f_ = self.password_hash_f(password_, None)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])

            salt_ = hash_f_["salt"]
            key_ = hash_f_["key"]

            aut_otp_secret_ = pyotp.random_base32()
            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=user_id_, issuer_name="Technoplatz-BI")
            api_key_ = secrets.token_hex(16)

            Mongo().db_["_auth"].insert_one({
                "aut_id": user_id_,
                "aut_salt": salt_,
                "aut_key": key_,
                "aut_api_key": api_key_,
                "aut_tfac": None,
                "aut_expires": 0,
                "aut_otp_secret": aut_otp_secret_,
                "aut_otp_validated": False,
                "_qr_modified_at": Misc().get_now_f(),
                "_qr_modified_by": user_id_,
                "_qr_modified_count": 0,
                "_created_at": Misc().get_now_f(),
                "_created_by": user_id_,
                "_created_ip": Misc().get_client_ip_f(),
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_id_,
            })

            return {"result": True, "qr": qr_, "user": None}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)


DOMAIN_ = os.environ.get("DOMAIN") if os.environ.get("DOMAIN") else "localhost"
API_OUTPUT_ROWS_LIMIT_ = os.environ.get("API_OUTPUT_ROWS_LIMIT")
NOTIFICATION_SLACK_HOOK_URL_ = os.environ.get("NOTIFICATION_SLACK_HOOK_URL")
COMPANY_NAME_ = os.environ.get("COMPANY_NAME") if os.environ.get("COMPANY_NAME") else "Technoplatz BI"
SMTP_SERVER_ = os.environ.get("SMTP_SERVER")
SMTP_PORT_ = os.environ.get("SMTP_PORT")
SMTP_USERID_ = os.environ.get("SMTP_USERID")
SMTP_PASSWORD_ = os.environ.get("SMTP_PASSWORD")
FROM_EMAIL_ = os.environ.get("FROM_EMAIL")
EMAIL_DISCLAIMER_HTML_ = os.environ.get("EMAIL_DISCLAIMER_HTML")
EMAIL_TFA_SUBJECT_ = "Your Backup OTP"
EMAIL_SIGNUP_SUBJECT_ = "Welcome"
EMAIL_SIGNIN_SUBJECT_ = "New Sign-in"
EMAIL_UPLOADERR_SUBJECT_ = "File Upload Result"
EMAIL_DEFAULT_SUBJECT_ = "Hello"
API_SCHEDULE_INTERVAL_MIN_ = os.environ.get("API_SCHEDULE_INTERVAL_MIN")
MONGO_DUMP_HOURS_ = os.environ.get("MONGO_DUMP_HOURS") if os.environ.get("MONGO_DUMP_HOURS") else "23"
API_UPLOAD_LIMIT_BYTES_ = int(os.environ.get("API_UPLOAD_LIMIT_BYTES"))
API_MAX_CONTENT_LENGTH_MB_ = int(os.environ.get("API_MAX_CONTENT_LENGTH_MB"))
API_DEFAULT_AGGREGATION_LIMIT_ = int(os.environ.get("API_DEFAULT_AGGREGATION_LIMIT"))
API_QUERY_PAGE_SIZE_ = int(os.environ.get("API_QUERY_PAGE_SIZE"))
API_SESSION_EXP_MINUTES_ = os.environ.get("API_SESSION_EXP_MINUTES")
API_TEMPFILE_PATH_ = os.environ.get('API_TEMPFILE_PATH')
API_MONGODUMP_PATH_ = os.environ.get('API_MONGODUMP_PATH')
API_CORS_ORIGINS_ = os.environ.get('API_CORS_ORIGINS').strip().split(",")
API_S3_ACTIVE_ = os.environ.get("API_S3_ACTIVE") in [True, "true", "True", "TRUE"]
API_S3_REGION_ = os.environ.get("API_S3_REGION")
API_S3_ENDPOINT_URL_ = os.environ.get("API_S3_ENDPOINT_URL")
API_S3_ACCESS_ID_ = os.environ.get("API_S3_ACCESS_ID")
API_S3_SECRET_KEY_ = os.environ.get("API_S3_SECRET_KEY")
API_S3_BUCKET_NAME_ = os.environ.get("API_S3_BUCKET_NAME")
API_PERMISSIVE_TAGS_ = os.environ.get("API_PERMISSIVE_TAGS").replace(" ", "").split(",")
API_ADMIN_TAGS_ = os.environ.get("API_ADMIN_TAGS").replace(" ", "").split(",")
API_ADMIN_IPS_ = get_docker_secret("admin_ips", default="").replace(" ", "").split(",")
MONGO_RS_ = os.environ.get("MONGO_RS")
MONGO_HOST0_ = os.environ.get("MONGO_HOST0")
MONGO_HOST1_ = os.environ.get("MONGO_HOST1")
MONGO_HOST2_ = os.environ.get("MONGO_HOST2")
MONGO_PORT0_ = int(os.environ.get("MONGO_PORT0"))
MONGO_PORT1_ = int(os.environ.get("MONGO_PORT1"))
MONGO_PORT2_ = int(os.environ.get("MONGO_PORT2"))
MONGO_DB_ = os.environ.get("MONGO_DB")
MONGO_AUTH_DB_ = os.environ.get("MONGO_AUTH_DB")
MONGO_USERNAME_ = get_docker_secret("mongo_username", default="")
MONGO_PASSWORD_ = get_docker_secret("mongo_password", default="")
MONGO_TLS_CERT_KEYFILE_PASSWORD_ = get_docker_secret("mongo_tls_keyfile_password", default="")
MONGO_TLS_ = os.environ.get("MONGO_TLS") in [True, "true", "True", "TRUE"]
MONGO_TLS_CA_KEYFILE_ = os.environ.get("MONGO_TLS_CA_KEYFILE")
MONGO_TLS_CERT_KEYFILE_ = os.environ.get("MONGO_TLS_CERT_KEYFILE")
MONGO_RETRY_WRITES_ = os.environ.get("MONGO_RETRY_WRITES") in [True, "true", "True", "TRUE"]
MONGO_TIMEOUT_MS_ = int(os.environ.get("MONGO_TIMEOUT_MS")) if os.environ.get("MONGO_TIMEOUT_MS") and int(os.environ.get("MONGO_TIMEOUT_MS")) > 0 else 10000
PREVIEW_ROWS_ = int(os.environ.get("PREVIEW_ROWS")) if os.environ.get("PREVIEW_ROWS") and int(os.environ.get("PREVIEW_ROWS")) > 0 else 10
PROTECTED_COLLS_ = ["_log", "_dump", "_event", "_announcement"]
PROTECTED_INSDEL_EXC_COLLS_ = ["_token"]
STRUCTURE_KEYS_ = ["properties", "views", "unique", "index", "required", "sort", "parents", "links", "actions", "triggers", "fetchers", "import"]
STRUCTURE_KEYS_OPTIN_ = ["queries"]
PROP_KEYS_ = ["bsonType", "title", "description"]
TEMP_PATH_ = "/temp"
DUMP_PATH_ = "/mongodump"
PRINT_ = partial(print, flush=True)
TFAC_OPS_ = ["announce"]

app = Flask(__name__)
app.config["CORS_ORIGINS"] = API_CORS_ORIGINS_
app.config["CORS_HEADERS"] = ["Content-Type", "Origin", "Authorization", "X-Requested-With", "Accept", "x-auth"]
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
app.config["MAX_CONTENT_LENGTH"] = API_MAX_CONTENT_LENGTH_MB_ * 1024 * 1024
app.config["UPLOAD_EXTENSIONS"] = ["pdf", "png", "jpg", "jpeg", "xlsx", "xls", "doc", "docx", "csv", "txt"]
app.config["UPLOAD_FOLDER"] = API_TEMPFILE_PATH_
app.json_encoder = JSONEncoder
CORS(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@ app.route("/api/import", methods=["POST"], endpoint="import")
def storage_f():
    """
    docstring is in progress
    """
    try:
        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError({"result": False, "msg": jwt_validate_f_["msg"]})

        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "user session not found"})

        form_ = request.form.to_dict(flat=True)
        if not form_:
            raise APIError("form not found")

        file_ = request.files["file"]
        if not file_:
            raise APIError("no file received")

        process_ = form_["process"] if "process" in form_ and form_["process"] in ["insert", "update"] else "insert"
        collection_ = form_["collection"]
        col_check_ = Crud().inner_collection_f(collection_)
        if not col_check_["result"]:
            raise APIError(col_check_["msg"])

        permission_f_ = Auth().permission_f({
            "user": jwt_validate_f_["user"],
            "auth": jwt_validate_f_["auth"],
            "collection": collection_,
            "op": process_
        })
        if not permission_f_["result"]:
            raise AuthError(permission_f_["msg"])

        prefix_ = col_check_["collection"]["col_prefix"]

        import_f_ = Crud().import_f({
            "form": form_,
            "file": file_,
            "collection": collection_,
            "process": process_,
            "user": user_,
            "prefix": prefix_,
        })

        if not import_f_["result"]:
            raise APIError(import_f_["msg"])

        count_ = import_f_["count"] if "count" in import_f_ and import_f_["count"] > 0 else 0
        msg_ = import_f_["msg"] if "msg" in import_f_ else None

        hdr_ = {"Content-Type": "application/json; charset=utf-8"}
        return json.dumps({"result": import_f_["result"], "count": count_, "msg": msg_}, default=json_util.default, sort_keys=False), 200, hdr_

    except AuthError as exc_:
        return {"msg": str(exc_), "status": 401}

    except APIError as exc_:
        return {"msg": str(exc_), "status": 400}

    except Exception as exc_:
        return {"msg": str(exc_), "status": 500}


@ app.route("/api/crud", methods=["POST"])
def crud_f():
    """
    docstring is in progress
    """
    sc__, res_ = 200, {}
    try:
        input_ = request.json
        if "op" not in input_:
            raise APIError({"result": False, "msg": "no operation found"})
        op_ = escape(input_["op"])

        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError({"result": False, "msg": jwt_validate_f_["msg"]})

        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "user session ended"})

        input_["user"] = user_
        input_["userindb"] = user_
        collection_ = input_["collection"] if "collection" in input_ else None
        match_ = input_["match"] if "match" in input_ and input_["match"] is not None and len(input_["match"]) > 0 else []
        allowmatch_ = []

        permission_f_ = Auth().permission_f({
            "user": jwt_validate_f_["user"],
            "auth": jwt_validate_f_["auth"],
            "collection": collection_,
            "op": op_
        })
        if not permission_f_["result"]:
            raise AuthError(permission_f_)

        allowmatch_ = permission_f_["allowmatch"] if "allowmatch" in permission_f_ and len(permission_f_["allowmatch"]) > 0 else []
        if op_ in ["read", "update", "upsert", "delete", "action"]:
            match_ += allowmatch_
            input_["match"] = match_

        if op_ in ["update", "upsert", "insert", "action"]:
            if "doc" not in input_:
                raise APIError({"result": False, "msg": "no document included"})
            decode_ = Crud().decode_crud_input_f(input_)
            if not decode_["result"]:
                raise APIError(decode_)
            input_["doc"] = decode_["doc"]
        elif op_ in ["remove", "clone", "delete"]:
            col_check_ = Crud().inner_collection_f(input_["collection"])
            if not col_check_["result"]:
                raise APIError(col_check_)

        if op_ in TFAC_OPS_:
            tfac_ = input_["tfac"]
            email_ = user_["usr_id"] if "usr_id" in user_ else None
            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, op_)
            if not verify_otp_f_["result"]:
                raise APIError(verify_otp_f_)

        if op_ == "read":
            res_ = Crud().read_f(input_)
        elif op_ == "update":
            res_ = Crud().upsert_f(input_)
        elif op_ == "insert":
            res_ = Crud().insert_f(input_)
        elif op_ in ["clone", "delete"]:
            res_ = Crud().multiple_f(input_)
        elif op_ == "action":
            res_ = Crud().action_f(input_)
        elif op_ == "remove":
            res_ = Crud().remove_f(input_)
        elif op_ == "copykey":
            res_ = Crud().copykey_f(input_)
        elif op_ == "charts":
            res_ = Crud().charts_f(input_)
        elif op_ == "views":
            res_ = Crud().views_f(input_)
        elif op_ == "announcements":
            res_ = Crud().announcements_f(input_)
        elif op_ == "announce":
            res_ = Crud().announce_f(input_)
        elif op_ == "collections":
            res_ = Crud().collections_f(input_)
        elif op_ == "collection":
            res_ = Crud().collection_f(input_)
        elif op_ == "query":
            res_ = Crud().query_f(input_)
        elif op_ in ["dumpu", "dumpd", "dumpr"]:
            res_ = Crud().dump_f(input_)
        elif op_ == "saveschema":
            res_ = Crud().saveschema_f(input_)
        elif op_ == "savequery":
            res_ = Crud().savequery_f(input_)
        elif op_ == "saveview":
            res_ = Crud().saveview_f(input_)
        else:
            raise APIError(f"invalid operation: {op_}")

        if not res_["result"]:
            raise APIError(res_)

    except APIError as exc__:
        sc__, res_ = 400, ast.literal_eval(str(exc__))

    except AuthError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except SessionError as exc__:
        sc__, res_ = 403, ast.literal_eval(str(exc__))

    except Exception as exc__:
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        if res_["result"] and op_ == "dumpd":
            hdr_ = {"Content-Type": "application/json; charset=utf-8"}
            return send_from_directory(directory=API_MONGODUMP_PATH_, path=res_["file"], as_attachment=True), 200, hdr_

        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@ app.route("/api/otp", methods=["POST"])
def otp_f():
    """
    docstring is in progress
    """
    sc__, res_ = 200, {}
    try:
        input_ = request.json
        if not input_:
            res_ = {"result": False, "msg": "input is missing"}
            raise APIError(res_)

        request_ = input_["request"] if "request" in input_ else None
        if not request_:
            res_ = {"result": False, "msg": "no request provided"}
            raise APIError(res_)

        if "op" not in request_:
            res_ = {"result": False, "msg": "no operation found"}
            raise APIError(res_)

        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError({"result": False, "msg": jwt_validate_f_["msg"]})

        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "user session not found"})
        email_ = user_["email"] if "email" in user_ else None

        op_ = escape(request_["op"])

        if op_ == "reset":
            res_ = OTP().reset_otp_f(email_)
        elif op_ == "show":
            res_ = OTP().show_otp_f(email_)
        elif op_ == "request":
            res_ = OTP().request_otp_f(email_)
        elif op_ == "validate":
            res_ = OTP().validate_qr_f(email_, request_)
        else:
            raise APIError(f"invalid operation: {op_}")

        if not res_["result"]:
            raise APIError(res_)

    except SessionError as exc__:
        sc__, res_ = 403, ast.literal_eval(str(exc__))

    except APIError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except Exception as exc__:
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@ app.route("/api/auth", methods=["POST"], endpoint="auth")
def auth_f():
    """
    docstring is in progress
    """
    sc__, res_ = 200, {}
    try:
        input_ = request.json
        if not input_:
            raise APIError({"result": False, "msg": "input missing"})
        if "op" not in input_:
            raise APIError({"result": False, "msg": "no operation found"})
        op_ = input_["op"]

        user_, auth_ = None, None

        if op_ in ["signout", "apikeygen", "apikeyget"]:
            jwt_validate_f_ = Auth().jwt_validate_f()
            if not jwt_validate_f_["result"]:
                raise SessionError(jwt_validate_f_["msg"])
            auth_ = jwt_validate_f_["auth"] if "auth" in jwt_validate_f_ else None
            user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
            if not auth_:
                raise SessionError({"result": False, "msg": "no authentication"})

        if op_ == "signup":
            res_ = Auth().signup_f()
        elif op_ == "signin":
            res_ = Auth().signin_f()
        elif op_ == "tfac":
            res_ = Auth().tfac_f()
        elif op_ == "signout":
            res_ = Auth().signout_f(auth_)
        elif op_ == "forgot":
            res_ = Auth().forgot_f()
        elif op_ == "reset":
            res_ = Auth().reset_f()
        elif op_ in ["apikeygen", "apikeyget"]:
            input_["user"] = user_
            input_["auth"] = auth_
            res_ = Auth().account_f(input_)
        else:
            raise APIError({"result": False, "msg": f"operation not supported: {op_}"})

        if not res_["result"]:
            raise AuthError(res_)

    except APIError as exc__:
        sc__, res_ = 400, ast.literal_eval(str(exc__))

    except SessionError as exc__:
        sc__, res_ = 403, ast.literal_eval(str(exc__))

    except AuthError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except Exception as exc__:
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@ app.route("/api/iot", methods=["POST"])
def iot_post_f():
    """
    docstring is in progress
    """
    sc__, res_ = 200, {}
    try:
        if not request.headers:
            raise AuthError({"result": False, "msg": "no headers provided"})

        if not request.json:
            raise APIError({"result": False, "msg": "no data provided"})

        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise AuthError({"result": False, "msg": jwt_validate_f_["msg"]})

        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise AuthError({"result": False, "msg": "user session ended"})
        aut_id_ = user_["email"]

        requestj_ = request.json
        process_ = requestj_["process"] if "process" in requestj_ else None
        if not process_:
            raise APIError({"result": False, "msg": "no process provided"})

        if process_ == "scan":
            res_ = Iot().barcode_scan_f(aut_id_)
        elif process_ == "query":
            searched_ = requestj_["searched"] if "searched" in requestj_ else None
            page_ = requestj_["page"] if "page" in requestj_ else 1
            res_ = Iot().iot_query_f(searched_, page_)

    except AuthError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except APIError as exc__:
        sc__, res_ = 400, ast.literal_eval(str(exc__))

    except Exception as exc__:
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@ app.route("/api/post", methods=["POST"])
def post_f():
    """
    docstring is in progress
    """
    try:
        if not request.headers:
            raise AuthError("no headers provided")

        content_type_ = request.headers.get("Content-Type", None) if "Content-Type" in request.headers else None
        if not content_type_:
            raise APIError("no content type provided")

        operation_ = request.headers.get("operation", None).lower() if "operation" in request.headers else None
        if not operation_:
            raise APIError("no operation provided in header")

        rh_collection_ = request.headers.get("collection", None).lower() if "collection" in request.headers else None
        if not rh_collection_:
            raise APIError("no collection provided in header")

        if operation_ not in ["read", "insert", "update", "upsert", "delete"]:
            raise APIError("invalid operation")

        x_api_token_ = request.headers["Authorization"] if "Authorization" in request.headers else None
        if not x_api_token_:
            raise AuthError("no authorization provided")

        split_ = re.split(" ", x_api_token_)
        if not split_ or len(split_) != 2 or split_[0].lower() != "bearer":
            raise AuthError("invalid authorization bearer")

        access_validate_by_api_token_f_ = Auth().access_validate_by_api_token_f(x_api_token_, operation_, None)
        if not access_validate_by_api_token_f_["result"]:
            raise AuthError(access_validate_by_api_token_f_["msg"])

        if not request.json:
            raise APIError("no json data provided")

        if not API_OUTPUT_ROWS_LIMIT_:
            raise APIError("no api rows limit defined")

        collection_f_ = Crud().inner_collection_f(rh_collection_)
        if not collection_f_["result"]:
            raise APIError(collection_f_["msg"])

        collection_ = collection_f_["collection"] if "collection" in collection_f_ else None
        if not collection_:
            raise APIError("collection not found")

        structure_ = collection_["col_structure"] if "col_structure" in collection_ else None
        if not structure_:
            raise APIError(f"no structure found: {collection_}")

        properties_ = structure_["properties"] if "properties" in structure_ else None
        if not properties_:
            raise APIError(f"no properties found: {collection_}")

        unique_ = structure_["unique"] if "unique" in structure_ else []
        is_crud_ = rh_collection_[:1] != "_"
        collection_data_ = f"{rh_collection_}_data" if is_crud_ else rh_collection_
        body_ = request.json
        type_ = str(type(body_))

        if type_ != "<class 'list'>":
            if operation_ == "read":
                body_ = [body_]
            else:
                raise APIError("post data must be provided in an array")

        output_ = []
        count_ = 0

        session_client_ = MongoClient(Mongo().connstr)
        session_db_ = session_client_[MONGO_DB_]
        session_ = session_client_.start_session()
        session_.start_transaction()

        if operation_ == "read":
            for item_ in body_:
                cursor_ = session_db_[collection_data_].find(item_)
                docs_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []
                for doc_ in docs_:
                    output_.append(doc_)
                    count_ += 1
                    if count_ >= int(API_OUTPUT_ROWS_LIMIT_):
                        break
        elif operation_ in ["insert", "update", "upsert", "delete"]:
            filter_ = {}
            if operation_ in ["update", "upsert", "delete"]:
                if len(unique_) > 0:
                    for uq_ in unique_:
                        for uq__ in uq_:
                            filter_[uq__] = None
                else:
                    raise APIError(f"at least one unique field must be provided for {operation_}")
            for ix_, item_ in enumerate(body_):
                filter__ = {}
                if operation_ in ["update", "upsert", "delete"]:
                    for key_ in filter_:
                        if key_ in item_ and item_[key_] is not None:
                            filter__[key_] = item_[key_]
                    if not filter__:
                        raise APIError(f"at least one unique field must be provided for {operation_} index {ix_}")
                decode_crud_doc_f_ = Crud().decode_crud_doc_f(item_, properties_)
                if not decode_crud_doc_f_["result"]:
                    raise APIError(decode_crud_doc_f_["msg"])
                doc__ = decode_crud_doc_f_["doc"]
                doc__["_modified_at"] = Misc().get_now_f()
                doc__["_modified_by"] = "API"
                if operation_ in ["insert", "upsert"]:
                    doc__["_created_at"] = Misc().get_now_f()
                    doc__["_created_by"] = "API"
                if operation_ == "upsert":
                    session_db_[collection_data_].update_many(filter__, {"$set": doc__, "$inc": {"_modified_count": 1}}, upsert=True, session=session_)
                if operation_ == "update":
                    session_db_[collection_data_].update_many(filter__, {"$set": doc__, "$inc": {"_modified_count": 1}}, session=session_)
                elif operation_ == "insert":
                    session_db_[collection_data_].insert_one(doc__, session=session_)
                elif operation_ == "delete":
                    session_db_[collection_data_].delete_many(filter__, session=session_)
                count_ += 1
                if count_ >= int(API_OUTPUT_ROWS_LIMIT_):
                    break
                output_.append(item_)

        log_ = Misc().log_f({
            "type": "Info",
            "collection": rh_collection_,
            "op": f"API {operation_}",
            "user": "API",
            "document": body_
        })
        if not log_["result"]:
            raise APIError(log_["msg"])

        session_.commit_transaction()
        session_client_.close()

        res_ = {
            "result": True,
            "operation": operation_,
            "count": count_,
            "output": output_
        }
        response_ = make_response(json.dumps(res_, default=json_util.default, ensure_ascii=False, sort_keys=False))
        response_.status_code = 200
        response_.mimetype = "application/json"
        return response_

    except AuthError as exc_:
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 401
        response_.mimetype = "application/json"
        return response_

    except APIError as exc_:
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 400
        response_.mimetype = "application/json"
        return response_

    except Exception as exc_:
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 500
        response_.mimetype = "application/json"
        return response_


@ app.route("/api/get/query/<string:id_>", methods=["GET"])
def api_get_query(id_):
    """
    docstring is in progress
    """
    status_code_ = 200
    res_ = None
    id_ = Misc().clean_f(id_)
    try:
        if not request.headers:
            raise AuthError({"result": False, "msg": "no header provided"})

        x_api_token_ = request.headers["X-Api-Token"] if "X-Api-Token" in request.headers and request.headers["X-Api-Token"] is not None else None
        if not x_api_token_:
            raise AuthError({"result": False, "msg": "missing token"})

        func_ = Auth().access_validate_by_api_token_f(x_api_token_, "read", id_)
        if not func_["result"]:
            raise AuthError(func_)

        query_f_ = Crud().query_f({"id": id_})
        if not query_f_["result"]:
            raise APIError(query_f_)

        res_ = query_f_["data"] if "data" in query_f_ else []
        if not res_:
            raise APIError(f"no data generated at /api/get/query/{id_}")

    except AuthError as exc__:
        Misc().notify_exception_f(exc__)
        res_ = ast.literal_eval(str(exc__))
        status_code_ = 401

    except APIError as exc__:
        Misc().notify_exception_f(exc__)
        res_ = ast.literal_eval(str(exc__))
        status_code_ = 500

    except Exception as exc__:
        Misc().notify_exception_f(exc__)
        res_ = ast.literal_eval(str(exc__))
        status_code_ = 500

    finally:
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = status_code_
        response_.mimetype = "application/json"
        return response_


@ app.route("/api/get/view/<string:id_>", methods=["GET"])
def get_data_f(id_):
    """
    docstring is in progress
    """
    status_code_ = 200
    res_ = None
    try:
        if not request.headers:
            raise AuthError({"result": False, "msg": "no header provided"})
        id_ = Misc().clean_f(id_)
        user_ = None
        api_token_ = request.headers["X-Api-Token"] if "X-Api-Token" in request.headers and request.headers["X-Api-Token"] is not None else None
        if api_token_:
            access_validate_by_api_token_f_ = Auth().access_validate_by_api_token_f(api_token_, "read", id_)
            if not access_validate_by_api_token_f_["result"]:
                raise AuthError(access_validate_by_api_token_f_)
        else:
            PRINT_("!!! missing token", id_)
            raise AuthError({"result": False, "msg": "missing token"})

        generate_view_data_f_ = Crud().get_view_data_f(user_, id_, "external")
        if not generate_view_data_f_["result"]:
            raise APIError(generate_view_data_f_)

        res_ = generate_view_data_f_["data"] if generate_view_data_f_ and "data" in generate_view_data_f_ else []

    except AuthError as exc_:
        res_ = ast.literal_eval(str(exc_))
        status_code_ = 401

    except APIError as exc_:
        res_ = ast.literal_eval(str(exc_))
        status_code_ = 500

    except Exception as exc_:
        res_ = ast.literal_eval(str(exc_))
        status_code_ = 500

    finally:
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = status_code_
        response_.mimetype = "application/json"
        return response_


if __name__ == "__main__":
    Schedular().main_f()
    app.run(host="0.0.0.0", port=80, debug=False)
