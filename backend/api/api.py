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
import base64
import re
import secrets
import json
import operator
import smtplib
import urllib
import hashlib
import ast
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial
from subprocess import call
from random import randint
from datetime import datetime, timedelta
import pytz
from pymongo import MongoClient
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
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from croniter import croniter


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


class JSONEncoder(json.JSONEncoder):
    """
    docstring is in progress
    """

    def default(self, o):
        """
        docstring is in progress
        """
        if isinstance(o, ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


class Schedular:
    """
    docstring is in progress
    """

    def cron_looker_f(self, view_):
        """
        docstring is in progress
        """
        scheduled_ = view_["scheduled"] if "scheduled" in view_ else None
        scheduled_cron_ = view_["scheduled_cron"] if "scheduled_cron" in view_ else None
        scheduled_tz_ = view_["scheduled_tz"] if "scheduled_tz" in view_ else "Europe/Berlin"
        if not (scheduled_ and scheduled_cron_ and scheduled_tz_):
            return {"result": False, "msg": "not scheduled"}
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
        return {"result": True, "minute": str(minute_), "hour": str(hour_), "day": str(day_), "month": str(month_), "day_of_week": str(day_of_week_), "tz": str(scheduled_tz_)}

    def schedule_views_f(self, sched_):
        """
        docstring is in progress
        """
        try:
            print("*** scheduled views started", Misc().get_now_f())
            collections_ = list(Mongo().db_["_collection"].aggregate([{
                "$project": {
                    "col_id": 1,
                    "col_structure": 1,
                    "views": {"$objectToArray": "$col_structure.views"}
                }}, {
                "$match": {
                    "views": {
                        "$elemMatch": {
                            "$and": [{"v.enabled": True}, {"v.scheduled": True}]
                        }
                    }
                }
            }]))

            if not collections_:
                return {"result": True}

            for collection_ in collections_:
                views_ = collection_["views"] if "views" in collection_ and len(collection_["views"]) > 0 else None
                if not views_:
                    print(f"!!! no view found to schedule for {collection_['col_id']}")
                    continue
                for view_ in views_:
                    id__ = view_["k"]
                    view__ = view_["v"]
                    cron_looker_f_ = self.cron_looker_f(view__)
                    if not cron_looker_f_["result"]:
                        continue
                    args_ = [{
                        "collection": collection_["col_id"],
                        "id": id__,
                        "scope": "live"
                    }]
                    sched_.add_job(Crud().announce_f, "cron", minute=cron_looker_f_["minute"], hour=cron_looker_f_["hour"], day=cron_looker_f_["day"], month=cron_looker_f_[
                                   "month"], day_of_week=cron_looker_f_["day_of_week"], id=id__, timezone=cron_looker_f_["tz"], replace_existing=True, args=args_)
                    print("scheduled", id__)

            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def main_f(self):
        """
        docstring is in progress
        """
        try:
            sched_ = BackgroundScheduler(timezone=TZ_, daemon=True)
            sched_.remove_all_jobs()

            schedule_views_f_ = self.schedule_views_f(sched_)
            if not schedule_views_f_["result"]:
                raise APIError(schedule_views_f_["msg"])

            args_ = {"user": {"email": "cron"}, "op": "backup"}
            sched_.add_job(Crud().dump_f, "cron", day_of_week="*", hour=f"{API_DUMP_HOURS_}", minute="0", id="schedule_dump", timezone=TZ_, replace_existing=True, args=[args_])
            sched_.add_job(self.schedule_views_f, "cron", day_of_week="*", hour="*", minute=f"*/{API_SCHEDULE_INTERVAL_MIN_}", id="schedule_views", timezone=TZ_, replace_existing=True, args=[sched_])
            sched_.start()
            return True

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)


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
            "barcoded",
            "replacement",
            "placeholder",
        ]

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

    def post_notification(self, exc):
        """
        docstring is in progress
        """
        if NOTIFICATION_SLACK_HOOK_URL_:
            ip_ = self.get_user_ip_f()
            exc_type_, exc_obj_, exc_tb_ = sys.exc_info()
            file_ = os.path.split(exc_tb_.tb_frame.f_code.co_filename)[1]
            line_ = exc_tb_.tb_lineno
            exception_ = str(exc)
            notification_ = f"IP: {ip_}, DOMAIN: {DOMAIN_}, TYPE: {exc_type_}, FILE: {file_}, OBJ: {exc_obj_}, LINE: {line_}, EXCEPTION: {exception_}"
            resp_ = requests.post(NOTIFICATION_SLACK_HOOK_URL_, json.dumps({"text": str(notification_)}), timeout=10)
            if resp_.status_code != 200:
                print("*** notification error", resp_)

        return True

    def exception_f(self, exc_):
        """
        docstring is in progress
        """
        res_ = str(exc_)
        self.post_notification(res_)
        return {"result": False, "msg": res_}

    def api_error_f(self, exc_):
        """
        docstring is in progress
        """
        res_ = str(exc_)
        self.post_notification(res_)
        return {"result": False, "msg": res_}

    def app_exception_f(self, exc_):
        """
        docstring is in progress
        """
        res_ = str(exc_)
        self.post_notification(res_)
        return {"result": False, "msg": res_}

    def auth_error_f(self, exc_):
        """
        docstring is in progress
        """
        res_ = str(exc_)
        self.post_notification(res_)
        return {"result": False, "msg": res_}

    def mongo_error_f(self, exc_):
        """
        docstring is in progress
        """
        splt_ = str(exc_).split(", full error: ")
        splt0_ = splt_[0] if splt_ and len(splt_) > 0 else None
        splt1_ = splt_[1] if splt_ and len(splt_) > 1 else None
        jerror_ = splt1_ if splt1_ else splt0_ if splt0_ else str(exc_)
        self.post_notification(jerror_)
        return {"result": False, "msg": jerror_, "notify": False, "count": 0}

    def log_f(self, obj):
        """
        docstring is in progress
        """
        try:
            doc_ = {
                "log_type": obj["type"],
                "log_date": self.get_now_f(),
                "log_user_id": obj["user"],
                "log_ip": Misc().get_user_ip_f(),
                "log_collection_id": obj["collection"] if "collection" in obj else None,
                "log_operation": obj["op"] if "op" in obj else None,
                "log_document": str(obj["document"]) if "document" in obj else None,
                "_created_at": self.get_now_f(),
                "_created_by": obj["user"],
            }

            Mongo().db_["_log"].insert_one(doc_)
            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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

    def get_jdate_f(self):
        """
        docstring is in progress
        """
        return int(datetime.today().timestamp())

    def get_now_f(self):
        """
        docstring is in progress
        """
        return datetime.now(pytz.timezone(TZ_))

    def allowed_file(self, filename):
        """
        docstring is in progress
        """
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["UPLOAD_EXTENSIONS"]

    def get_user_ip_f(self):
        """
        docstring is in progress
        """
        return request.headers["cf-connecting-ip"] if "cf-connecting-ip" in request.headers else bleach.clean(request.access_route[-1])

    def get_user_host_f(self):
        """
        docstring is in progress
        """
        return request.headers["cf-connecting-ip"] if "cf-connecting-ip" in request.headers else bleach.clean(request.access_route[-1])

    def get_except_underdashes(self):
        """
        docstring is in progress
        """
        return ["_tags"]

    def make_array_unique_f(self, array_):
        """
        docstring is in progress
        """
        temp_ = set()
        return [x for x in array_ if x not in temp_ and not temp_.add(x)]

    def user_token_validate_f(self, token_, operation_):
        """
        docstring is in progress
        """
        try:
            find_ = Mongo().db_["_token"].find_one({"_id": ObjectId(base64.b64decode(token_).decode())})
            if not find_:
                raise APIError(f"token not found {token_}")

            grant_ = f"tkn_grant_{operation_}"
            if not find_[grant_]:
                raise APIError(f"token is not permitted to {operation_}")

            return {"result": True, "data": find_}

        except APIError as exc_:
            return Misc().exception_f(exc_)

    def api_token_validate_f(self, bearer_):
        """
        docstring is in progress
        """
        try:
            token__ = re.split(" ", bearer_)
            token_ = token__[1] if token__ and len(token__) > 0 and token__[0].lower() == "bearer" else None
            if not token_:
                raise AuthError("token not found at one")

            header_ = jwt.get_unverified_header(token_)
            finder_ = header_["finder"] if "finder" in header_ and header_["finder"] != "" and header_["finder"] is not None else None
            if not finder_:
                raise AuthError("finder is not valid please use an api token")

            find_ = Mongo().db_["_token"].find_one({"tkn_finder": finder_, "tkn_is_active": True})
            if not find_:
                raise AuthError("token not found")
            jwt_secret_ = find_["tkn_secret"]

            options_ = {"iss": "Technoplatz", "aud": "api", "sub": "bi"}
            jwt_proc_f_ = Misc().jwt_proc_f("decode", token_, jwt_secret_, options_, None)

            if not jwt_proc_f_["result"]:
                raise AuthError(jwt_proc_f_["msg"])

            tkn_grant_read_ = find_["tkn_grant_read"] if "tkn_grant_read" in find_ and find_["tkn_grant_read"] is True else False

            if not tkn_grant_read_:
                raise APIError("token is not permitted to read")

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

    def permitted_user_f(self, user_):
        """
        docstring is in progress
        """
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        return any(i in tags_ for i in PERMISSIVE_TAGS_)

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
                        dict_[field_] = [properties_property_[field_], "null"]
                    else:
                        dict_[field_] = properties_property_[field_]
            properties_new_[property_] = dict_
        return properties_new_

    def string_to_formula_f(self, set_, rec_, properties_):
        """
        docstring is in progress
        """
        key_ = set_["key"]
        value_ = set_["value"]
        if value_[:1] == "$":
            forward_ = value_[1:]
            value_ = rec_[forward_] if forward_ in rec_ else None
        elif value_[:1] == "=":
            formula_ = str(value_[1:]).replace(" ", "")
            parts_ = re.split("([+-/*()])", formula_)
            for part_ in parts_:
                if part_[:1] == "$":
                    forward_ = part_[1:]
                    if forward_ in rec_:
                        if rec_[forward_] in [None, ""]:
                            rec_[forward_] = 0
                        formula_ = formula_.replace(part_, str(rec_[forward_]))
                    else:
                        formula_ = formula_.replace(part_, "")

            value_ = str(ne.evaluate(formula_))
            value_ = float(value_) if properties_[key_]["bsonType"] in ["number", "decimal", "double"] else int(value_) if properties_[key_]["bsonType"] == "int" else None

        return value_

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
                        personalizations_.append(
                            {"email": member_["usr_id"], "name": member_["usr_name"]}
                        )

            return {"result": True, "to": personalizations_}

        except Exception as exc:
            return Misc().exception_f(exc)


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
        replicaset_ = f"&replicaSet={MONGO_RS_}" if MONGO_RS_ and MONGO_RS_ != "" else ""
        read_preference_primary_ = f"&readPreference={self.mongo_readpref_primary_}" if self.mongo_readpref_primary_ else ""
        appname_ = f"&appname={self.mongo_appname_}" if self.mongo_appname_ else ""
        tls_ = "&tls=true" if MONGO_TLS_ else "&tls=false"
        tls_certificate_key_file_ = f"&tlsCertificateKeyFile={MONGO_TLS_CERT_KEYFILE_}" if MONGO_TLS_CERT_KEYFILE_ else ""
        tls_certificate_key_file_password_ = f"&tlsCertificateKeyFilePassword={MONGO_TLS_CERT_KEY_PASSWORD_}" if MONGO_TLS_CERT_KEY_PASSWORD_ else ""
        tls_ca_file_ = f"&tlsCAFile={MONGO_TLS_CA_KEYFILE_}" if MONGO_TLS_CA_KEYFILE_ else ""
        tls_allow_invalid_certificates_ = "&tlsAllowInvalidCertificates=true"
        retry_writes_ = "&retryWrites=true" if MONGO_RETRY_WRITES_ else "&retryWrites=false"
        self.connstr = f"mongodb://{MONGO_USERNAME_}:{MONGO_PASSWORD_}@{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}/?{auth_source_}{replicaset_}{read_preference_primary_}{appname_}{tls_}{tls_certificate_key_file_}{tls_certificate_key_file_password_}{tls_ca_file_}{tls_allow_invalid_certificates_}{retry_writes_}"
        self.client_ = MongoClient(self.connstr)
        self.db_ = self.client_[MONGO_DB_]

    def backup_f(self):
        """
        docstring is in progress
        """
        try:
            ts_ = Misc().get_timestamp_f()
            id_ = f"dump-{MONGO_DB_}-{ts_}"
            file_ = f"{id_}.gz"
            loc_ = f"/dump/{file_}"
            type_ = "gzip"
            command_ = f'mongodump --host "{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}" --db {MONGO_DB_} --authenticationDatabase {MONGO_AUTH_DB_} --username {MONGO_USERNAME_} --password "{MONGO_PASSWORD_}" --ssl --sslPEMKeyFile {MONGO_TLS_CERT_KEYFILE_} --sslCAFile {MONGO_TLS_CA_KEYFILE_} --sslPEMKeyPassword {MONGO_TLS_CERT_KEY_PASSWORD_} --tlsInsecure --{type_} --archive={loc_}'
            os.system(command_)
            size_ = os.path.getsize(loc_)
            return {"result": True, "id": id_, "type": type_, "size": size_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def restore_f(self, obj):
        """
        docstring is in progress
        """
        try:
            id_ = obj["id"]
            file_ = f"{id_}.gz"
            loc_ = f"/dump/{file_}"
            type_ = "gzip"

            command_ = f'mongorestore --host "{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}" --db {MONGO_DB_} --authenticationDatabase {MONGO_AUTH_DB_} --username {MONGO_USERNAME_} --password "{MONGO_PASSWORD_}" --ssl --sslPEMKeyFile {MONGO_TLS_CERT_KEYFILE_} --sslCAFile {MONGO_TLS_CA_KEYFILE_} --sslPEMKeyPassword {MONGO_TLS_CERT_KEY_PASSWORD_} --tlsInsecure --{type_} --archive={loc_} --nsExclude="{MONGO_DB_}._backup" --nsExclude="{MONGO_DB_}._auth" --nsExclude="{MONGO_DB_}._user" --nsExclude="{MONGO_DB_}._log" --drop --quiet'
            os.system(command_)

            size_ = os.path.getsize(loc_)
            return {"result": True, "id": id_, "type": type_, "size": size_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)


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

    def root_schemas_f(self, schema):
        """
        docstring is in progress
        """
        return json.loads(open(f"/app/_schema/{schema}.json", "r", encoding="utf-8").read())

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

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def template_f(self, input_):
        """
        docstring is in progress
        """
        try:
            proc_ = input_["proc"] if "proc" in input_ else None
            if proc_ not in ["list", "install"]:
                raise APIError("invalid template request")

            user_ = input_["user"] if "user" in input_ else None
            if not user_:
                raise APIError("user not provided")
            email_ = user_["usr_id"]

            userindb_ = input_["userindb"] if "userindb" in input_ else None
            if not userindb_:
                raise APIError("user not found")

            data_ = None
            path_ = "/app/_template/templates.json"
            if not os.path.isfile(path_):
                raise APIError("no templates found")

            with open(path_, "r", encoding="utf-8") as fopen_:
                data_ = json.loads(fopen_.read())

            if proc_ == "list":
                data_ = [item_ for item_ in data_]
                data_.sort(key=operator.itemgetter("sort"), reverse=False)
            elif proc_ == "install":
                suffix_ = Misc().get_timestamp_f()
                template_ = input_["template"] if "template" in input_ else None
                if not template_:
                    raise APIError("invalid template requested")

                col_id_ = f"{template_['collection']}-{suffix_}"
                col_title_ = f"{template_['title']}-{suffix_}"
                file_ = template_["file"]
                collection__ = f"{col_id_}_data"
                prefix_ = template_["prefix"] if "prefix" in template_ else "zzz"
                description_ = template_["description"] if "description" in template_ else None

                find_one_ = Mongo().db_["_collection"].find_one({"col_id": col_id_})
                if find_one_:
                    raise APIError("collection name already exists")
                if col_id_ in Mongo().db_.list_collection_names():
                    raise APIError("collection data already exists")

                find_one_ = Mongo().db_["_collection"].find_one({"col_prefix": prefix_})
                if find_one_:
                    raise APIError(f"collection prefix already exists: {prefix_}")

                path_ = f"/app/_template/{file_}"
                if os.path.isfile(path_):
                    with open(path_, "r", encoding="utf-8") as fopen_:
                        jtxt_ = fopen_.read()
                        jtxt_ = jtxt_.replace("zzz_", f"{prefix_}_")
                        structure_ = json.loads(jtxt_)

                Mongo().db_["_collection"].insert_one({
                    "col_id": col_id_,
                    "col_title": col_title_,
                    "col_description": description_,
                    "col_prefix": prefix_,
                    "col_structure": structure_,
                    "_created_at": Misc().get_now_f(),
                    "_created_by": email_,
                    "_modified_at": Misc().get_now_f(),
                    "_modified_by": email_,
                    "_modified_count": 0
                })

                schemavalidate_ = self.crudschema_validate_f(
                    {"collection": collection__, "structure": structure_}
                )
                if not schemavalidate_["result"]:
                    raise APIError(schemavalidate_["msg"])

            return {"result": True, "data": data_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
                            rgx_ = (
                                "%Y-%m-%d"
                                if doc_[k] and ln_ == 10
                                else "%Y-%m-%dT%H:%M:%S"
                            )
                            if (
                                doc_[k]
                                and isinstance(doc_[k], str)
                                and self.validate_iso8601_f(doc_[k])
                            ):
                                document_[k] = datetime.strptime(doc_[k][:ln_], rgx_)
                            else:
                                document_[k] = (
                                    datetime.strptime(doc_[k][:ln_], rgx_)
                                    if doc_[k] is not None
                                    else None
                                )
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
                            document_[k] = (
                                True
                                if document_[k] and document_[k] in [True, "true", "True", "TRUE"]
                                else False
                            )
                    else:
                        if property_["bsonType"] == "bool":
                            document_[k] = False

            return {"result": True, "doc": document_}

        except Exception as exc:
            return Misc().exception_f(exc)

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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def frame_convert_datetime_f(self, data_):
        """
        docstring is in progress
        """
        str_ = str(data_).strip()
        return datetime.fromisoformat(str_) if str_ not in [" ", "0", "0.0", "NaT", "NaN", "nat", "nan", np.nan, np.double, None] else None

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

    def purge_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_id_ = obj["collection"]
            user_ = obj["user"] if "user" in obj else None
            email_ = user_["email"] if user_ and "email" in user_ else None
            match_ = obj["match"]
            tfac_ = obj["tfac"] if "tfac" in obj and obj["tfac"] else None

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise APIError(f"user auth not found {email_}")

            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, "purge")
            if not verify_otp_f_["result"]:
                raise APIError(verify_otp_f_["msg"])

            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            cursor_ = (
                Mongo().db_["_collection"].find_one({"col_id": collection_id_})
                if is_crud_
                else self.root_schemas_f(f"{collection_}")
            )
            if not cursor_:
                raise APIError(f"collection not found to purge: {collection_}")

            structure_ = cursor_["col_structure"] if is_crud_ else cursor_

            get_filtered_ = self.get_filtered_f(
                {
                    "match": match_,
                    "properties": structure_["properties"]
                    if "properties" in structure_
                    else None,
                }
            )

            ts_ = Misc().get_timestamp_f()
            bin_ = f"{collection_id_}_bin_{ts_}"
            Mongo().db_[bin_].insert_many(Mongo().db_[collection_].find(get_filtered_))
            Mongo().db_[collection_].delete_many(get_filtered_)

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": collection_,
                    "op": "purge",
                    "user": email_,
                    "document": get_filtered_,
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f(
                {
                    "type": "Error",
                    "collection": collection_,
                    "op": "purge",
                    "user": email_,
                    "document": str(exc),
                }
            )
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def copykey_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_ = obj["collection"]
            properties_ = obj["properties"]
            key_ = obj["key"]
            match_ = obj["match"] if "match" in obj and obj["match"] != [] else []

            get_filtered_ = {}
            if len(match_) > 0:
                get_filtered_ = self.get_filtered_f({
                    "match": match_,
                    "properties": properties_ if properties_ else None
                })

            distinct_ = ""
            cursora_ = Mongo().db_[f"{collection_}_data"].distinct(key_, get_filtered_)
            if cursora_ and len(cursora_) > 0:
                distinct_ = "\n".join(map(str, cursora_))

            return {"result": True, "copied": distinct_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
        try:
            # INPUTS
            form_ = obj["form"]
            file_ = obj["file"]
            collection_ = obj["collection"]
            email_ = form_["email"]
            mimetype_ = file_.content_type

            # GETTING COLLECTION PROPERTIES
            collection__ = f"{collection_}_data"
            find_one_ = Mongo().db_["_collection"].find_one({"col_id": collection_})
            if not find_one_:
                raise APIError(f"collection not found {collection_}")
            get_properties_ = self.get_properties_f(collection_)
            if not get_properties_["result"]:
                raise APIError(get_properties_["msg"])
            properties_ = get_properties_["properties"]

            # CREATE A DATAFRAME
            if mimetype_ in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
                filesize_ = file_.tell()
                if filesize_ > API_UPLOAD_LIMIT_BYTES_:
                    raise APIError(f"invalid file size {API_UPLOAD_LIMIT_BYTES_} bytes")
                file_.seek(0, os.SEEK_END)
                df_ = pd.read_excel(file_, sheet_name=collection_, header=0, engine="openpyxl", dtype="object")
            elif mimetype_ == "text/csv":
                content_ = file_.read().decode("utf-8")
                filesize_ = file_.content_length
                if filesize_ > API_UPLOAD_LIMIT_BYTES_:
                    raise APIError(f"invalid file size {API_UPLOAD_LIMIT_BYTES_} bytes")
                if mimetype_ == "text/csv":
                    df_ = pd.read_csv(io.StringIO(content_), header=0, dtype="object")
            else:
                raise APIError("file type is not supported")

            # MAKING COLUMN NAMES PRETTY
            df_ = df_.rename(lambda column_: self.convert_column_name_f(column_), axis="columns")

            # CONVERTING DATASET COLUMNS
            columns_tobe_deleted_ = []
            for column_ in df_.columns:
                if column_ in properties_:
                    property_ = properties_[column_]
                    if "bsonType" in property_:
                        if property_["bsonType"] == "date":
                            df_[column_] = df_[column_].apply(self.frame_convert_datetime_f)
                        elif property_["bsonType"] == "string":
                            df_[column_] = df_[column_].apply(self.frame_convert_string_f)
                            if "replacement" in property_ and len(property_["replacement"]) > 0:
                                for repl_ in property_["replacement"]:
                                    find_ = repl_["find"] if "find" in repl_ and repl_["find"] is not None else None
                                    replace_ = repl_["replace"] if "replace" in repl_ and repl_["replace"] is not None else ""
                                    if find_ and replace_ is not None:
                                        df_[column_] = df_[column_].str.replace(find_, replace_, regex=True)
                        elif property_["bsonType"] in ["number", "int", "decimal"]:
                            df_[column_] = df_[column_].apply(self.frame_convert_number_f)
                    else:
                        columns_tobe_deleted_.append(column_)
                else:
                    columns_tobe_deleted_.append(column_)

            # REMOVING UNNECESSRY COLUMNS
            if "_structure" in df_.columns:
                columns_tobe_deleted_.append("_structure")
            if len(columns_tobe_deleted_) > 0:
                df_.drop(columns_tobe_deleted_, axis=1, inplace=True)

            # SUM OF ALL NUMERICS BY COMBINING DUPLICATE ITEMS
            # ITS OBVIOUS BUT TRUE :)
            df_ = df_.groupby(list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns), as_index=False, dropna=False).sum()

            # REMOVING NANS
            df_.replace(
                [np.nan, pd.NaT, "nan", "NaN", "nat", "NaT"], None, inplace=True
            )

            # SETTING THE DEFAULTS
            df_["_created_at"] = Misc().get_now_f()
            df_["_created_by"] = email_
            df_["_modified_at"] = None
            df_["_modified_by"] = None
            df_["_modified_count"] = 0

            # BULK INSERT DF INTO DATABASE
            payload_ = df_.to_dict("records")

            session_client_ = MongoClient(Mongo().connstr)
            session_db_ = session_client_[MONGO_DB_]
            session_ = session_client_.start_session()
            session_.start_transaction()
            insert_many_ = session_db_[collection__].insert_many(payload_, ordered=False, session=session_)
            session_.commit_transaction()
            count_ = len(insert_many_.inserted_ids)
            session_client_.close()

            return {"result": True, "count": count_, "msg": "file was imported successfully"}

        except pymongo.errors.PyMongoError as exc:
            exc_type_, exc_obj_, exc_tb_ = sys.exc_info()
            session_.abort_transaction()
            res_ = Misc().mongo_error_f(exc)
            email_sent_ = Email().sendEmail_f({
                "personalizations": {"to": [{"email": email_, "name": None}]},
                "op": "importerr",
                "html": f"Hi,<br /><br />Here's the data upload result about file that you've just tried to upload;<br /><br />MIME TYPE: {mimetype_}<br />FILE SIZE: {filesize_} bytes<br />COLLECTION: {collection_}<br />ROW COUNT: {len(df_)}<br /><br />ERRORS:<br />{str(exc_obj_)}"
            })
            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            res_["msg"] = "file upload error! we have just sent an email with the error details."
            return res_

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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

            self_ = get_view_data_f_["self"]
            _tags = self_["_tags"]
            vie_title_ = self_["title"]
            data_json_ = self_["data_json"]
            data_excel_ = self_["data_excel"]
            data_csv_ = self_["data_csv"]
            vie_attach_pivot_ = self_["pivot"]

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
                file_json_ = f"{id_}.json"
                file_json_raw_ = f"{id_}-detail.json"
                df_.to_json(f"/cron/{file_json_}", orient="records", date_format="iso", force_ascii=False, date_unit="s", default_handler=None, lines=False, compression=None, index=True)
                df_raw_.to_json(f"/cron/{file_json_raw_}", orient="records", date_format="iso", force_ascii=False, date_unit="s", default_handler=None, lines=False, compression=None, index=True)
                files_.append({"filename": file_json_, "filetype": "json"})
                files_.append({"filename": file_json_raw_, "filetype": "json"})
            if data_csv_:
                file_csv_ = f"{id_}.csv"
                file_csv_raw_ = f"{id_}-detail.csv"
                df_.to_csv(f"/cron/{file_csv_}", sep=";", encoding="utf-8", header=True, decimal=".", index=False)
                df_raw_.to_csv(f"/cron/{file_csv_raw_}", sep=";", encoding="utf-8", header=True, decimal=".", index=False)
                files_.append({"filename": file_csv_, "filetype": "csv"})
                files_.append({"filename": file_csv_raw_, "filetype": "csv"})
            if data_excel_:
                file_excel_ = f"{id_}.xlsx"
                file_excel_raw_ = f"{id_}-detail.xlsx"
                df_.to_excel(f"/cron/{file_excel_}", sheet_name=col_id_, engine="xlsxwriter", header=True, index=False)
                df_raw_.to_excel(f"/cron/{file_excel_raw_}", sheet_name=col_id_, engine="xlsxwriter", header=True, index=False)
                files_.append({"filename": file_excel_, "filetype": "xlsx"})
                files_.append({"filename": file_excel_raw_, "filetype": "xlsx"})

            body_ = ""
            if vie_attach_pivot_:
                body_ += f"{pivotify_}"

            footer_ = f"<br />Generated at {Misc().get_now_f().strftime('%d.%m.%Y %H:%M')}"
            html_ = f'<div style="font-size: 13px;"><h1>{vie_title_}</h1><p>{body_}</p><p>{footer_}</p></div>' if scope_ == "live" else f'<div style="font-size: 13px;"><p style="color: #c00; font-weight: bold;">THIS IS A TEST MESSAGE</p><p>{vie_title_}</p><p>{body_}</p><p>{footer_}</p></div>'

            email_sent_ = Email().sendEmail_f({
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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def dump_f(self, obj):
        """
        docstring is in progress
        """
        try:
            op_ = obj["op"] if "op" in obj else None

            dump_f_ = Mongo().backup_f() if op_ == "backup" else Mongo().restore_f(obj)
            if not dump_f_["result"]:
                raise APIError(dump_f_["msg"])

            id_ = dump_f_["id"]
            type_ = dump_f_["type"]
            size_ = dump_f_["size"]
            op_ = obj["op"] if "op" in obj else None
            email_ = obj["user"]["email"] if obj and obj["user"] else "cron"
            description_ = "On Demand" if op_ == "backup" else "Automatic"

            doc_ = {
                "bak_id": id_,
                "bak_type": type_,
                "bak_size": size_,
                "bak_description": description_,
                "bak_process": op_,
                "_created_at": Misc().get_now_f(),
                "_created_by": email_,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": email_,
            }

            Mongo().db_["_backup"].insert_one(doc_)

            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def parent_f(self, obji):
        """
        docstring is in progress
        """
        try:
            collection_ = obji["collection"]
            fields_ = obji["fields"]

            data_collection_ = f"{collection_}_data"
            projection_ = {}
            for field_ in fields_:
                projection_[field_] = 1

            cursor_ = (
                Mongo()
                .db_[data_collection_]
                .find(filter={}, projection=projection_)
                .limit(1000)
            )
            docs_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []

            return {"result": True, "data": docs_}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def set_akey(self, key_, setto_, properties_, data_):
        """
        docstring is in progress
        """
        try:
            if key_ not in properties_:
                raise APIError(f"{key_} was set but not found in collection properties")

            setto__ = None

            if setto_[:1] == "$":
                kvk_ = setto_[1:]
                kav_ = Mongo().db_["_kv"].find_one({"kav_key": kvk_})
                if kav_:
                    kav_key_ = kav_["kav_key"] if "kav_key" in kav_ and kav_["kav_key"] is not None else None
                    kav_as_ = kav_["kav_as"] if "kav_as" in kav_ and kav_["kav_as"] is not None else None
                    kav_value_ = kav_["kav_value"] if "kav_value" in kav_ and kav_["kav_value"] is not None else None
                    if kav_key_ and kav_value_ and kav_as_:
                        setto__ = datetime.strptime(kav_value_[:10], "%Y-%m-%d") if kav_as_ == "date" else bool(kav_value_) if kav_as_ == "bool" else float(kav_value_) if kav_as_ in ["float",
                                                                                                                                                                                       "number"] else int(kav_value_) if kav_as_ == "int" else str(kav_value_) if kav_as_ == "string" else str(kav_value_)
                else:
                    raise APIError(f"no key value pair provided for {setto_}")
            else:
                setto__ = data_[setto_] if setto_ in data_ and data_[setto_] is not None else setto_

            if not setto__:
                raise APIError(f"no link value provided for {setto_}; please consider to define a key-value pair for it")

            return {"result": True, "value": setto__}

        except APIError as exc:
            return Misc().api_error_f(exc)

    def link_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            link_ = obj_["link"] if "link" in obj_ else None
            data_ = obj_["data"] if "data" in obj_ else None
            linked_ = obj_["linked"] if "linked" in obj_ and len(obj_["linked"]) > 0 else None
            user_ = obj_["user"] if "user" in obj_ else None

            if link_ is None:
                raise APIError("link info is missing")
            if linked_ is None:
                raise APIError("linked data is missing")
            if data_ is None:
                raise APIError("master data is missing")
            if user_ is None:
                raise APIError("user data is missing")

            collection_ = link_["collection"] if "collection" in link_ else None
            get_ = link_["get"] if "get" in link_ else None
            set_ = link_["set"] if "set" in link_ and len(link_["set"]) > 0 else None
            usr_id_ = user_["usr_id"] if "usr_id" in user_ else None

            if collection_ is None:
                raise APIError("link collection is missing")
            if get_ is None:
                raise APIError("link get is missing")
            if set_ is None:
                raise APIError("link set is missing")
            if usr_id_ is None:
                raise APIError("user id is missing")

            get_properties_ = self.get_properties_f(collection_)
            if not get_properties_["result"]:
                raise APIError("collection properties is missing")
            target_properties_ = get_properties_["properties"]

            data_collection_ = f"{collection_}_data"
            setc_ = {}

            for set__ in set_:
                if "key" in set__ and "value" in set__:
                    targetkey__ = set__["key"]
                    setto__ = set__["value"]
                    if targetkey__ and setto__:
                        set_akey_ = self.set_akey(targetkey__, setto__, target_properties_, data_)
                        if not set_akey_["result"]:
                            raise APIError(set_akey_["msg"])
                        val_ = set_akey_["value"]
                        if val_:
                            setc_[targetkey__] = val_
                            setc_["_modified_at"] = Misc().get_now_f()
                            setc_["_modified_by"] = usr_id_

            if not setc_:
                raise APIError(f"no assignments to set {data_collection_}")

            filter_ = {}
            filter_[get_] = {"$in": linked_}
            update_many_ = Mongo().db_[data_collection_].update_many(filter_, {"$set": setc_})
            count_ = update_many_.matched_count

            return {"result": True, "data": setc_, "count": count_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def get_filtered_f(self, obj):
        """
        docstring is in progress
        """
        try:
            match_ = obj["match"]
            properties_ = obj["properties"] if "properties" in obj else None
            fand_ = []
            filtered_ = {}
            if properties_:
                for mat_ in match_:
                    if mat_["key"] and mat_["op"] and mat_["key"] in properties_:
                        fres_ = None
                        typ = (
                            properties_[mat_["key"]]["bsonType"]
                            if mat_["key"] in properties_
                            else "string"
                        )
                        if mat_["op"] in ["eq", "contains"]:
                            if typ in ["number", "int", "decimal"]:
                                fres_ = float(mat_["value"])
                            elif typ == "bool":
                                fres_ = bool(mat_["value"])
                            elif typ == "date":
                                fres_ = datetime.strptime(mat_["value"][:10], "%Y-%m-%d")
                            else:
                                fres_ = {"$regex": mat_["value"], "$options": "i"} if mat_["value"] else {"$regex": "", "$options": "i"}
                        elif mat_["op"] in ["ne", "nc"]:
                            if typ in ["number", "decimal"]:
                                fres_ = {"$not": {"$eq": float(mat_["value"])}}
                            elif typ == "bool":
                                fres_ = {"$not": {"$eq": bool(mat_["value"])}}
                            elif typ == "date":
                                fres_ = {
                                    "$not": {
                                        "$eq": datetime.strptime(
                                            mat_["value"][:10], "%Y-%m-%d"
                                        )
                                    }
                                }
                            else:
                                fres_ = (
                                    {"$not": {"$regex": mat_["value"], "$options": "i"}}
                                    if mat_["value"]
                                    else {"$not": {"$regex": "", "$options": "i"}}
                                )
                        elif mat_["op"] in ["in", "nin"]:
                            separated_ = re.split(",", mat_["value"])
                            list_ = (
                                [s.strip() for s in separated_]
                                if mat_["key"] != "_id"
                                else [ObjectId(s.strip()) for s in separated_]
                            )
                            if mat_["op"] == "in":
                                fres_ = {"$in": list_ if typ != "number" else list(map(float, list_))}
                            else:
                                fres_ = {
                                    "$nin": list_
                                    if typ != "number"
                                    else list(map(float, list_))
                                }
                        elif mat_["op"] == "gt":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$gt": float(mat_["value"])}
                            elif typ == "date":
                                fres_ = {
                                    "$gt": datetime.strptime(mat_["value"][:10], "%Y-%m-%d")
                                }
                            else:
                                fres_ = {"$gt": mat_["value"]}
                        elif mat_["op"] == "gte":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$gte": float(mat_["value"])}
                            elif typ == "date":
                                fres_ = {
                                    "$gte": datetime.strptime(mat_["value"][:10], "%Y-%m-%d")
                                }
                            else:
                                fres_ = {"$gte": mat_["value"]}
                        elif mat_["op"] == "lt":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$lt": float(mat_["value"])}
                            elif typ == "date":
                                fres_ = {
                                    "$lt": datetime.strptime(mat_["value"][:10], "%Y-%m-%d")
                                }
                            else:
                                fres_ = {"$lt": mat_["value"]}
                        elif mat_["op"] == "lte":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$lte": float(mat_["value"])}
                            elif typ == "date":
                                fres_ = {
                                    "$lte": datetime.strptime(mat_["value"][:10], "%Y-%m-%d")
                                }
                            else:
                                fres_ = {"$lte": mat_["value"]}
                        elif mat_["op"] == "true":
                            fres_ = {"$eq": True}
                        elif mat_["op"] == "false":
                            fres_ = {"$eq": False}
                        elif mat_["op"] == "nnull":
                            array_ = []
                            array1_ = {}
                            array2_ = {}
                            array1_[mat_["key"]] = {"$ne": None}
                            array2_[mat_["key"]] = {"$exists": True}
                            array_.append(array1_)
                            array_.append(array2_)
                        elif mat_["op"] == "null":
                            array_ = []
                            array1_ = {}
                            array2_ = {}
                            array1_[mat_["key"]] = {"$eq": None}
                            array2_[mat_["key"]] = {"$exists": False}
                            array_.append(array1_)
                            array_.append(array2_)

                        fpart_ = {}
                        if mat_["op"] in ["null", "nnull"]:
                            fpart_["$or"] = array_
                        else:
                            fpart_[mat_["key"]] = fres_

                        fand_.append(fpart_)

                filtered_ = {"$and": fand_} if fand_ and len(fand_) > 0 else {}

            return filtered_

        except Exception as exc_:
            print("!!! exc_", exc_)
            return None

    def get_view_data_f(self, user_, view_id_, scope_):
        """
        docstring is in progress
        """
        try:
            filter_ = {}
            filter_[f"col_structure.views.{view_id_}.enabled"] = True
            if user_:
                filter_[f"col_structure.views.{view_id_}._tags"] = {
                    "$elemMatch": {"$in": user_["_tags"]}
                }
            collection_ = Mongo().db_["_collection"].find_one(filter_)
            if not collection_:
                return {
                    "result": True,
                    "skip": True
                }
            collection_id_ = f"{collection_['col_id']}_data"
            view_ = collection_["col_structure"]["views"][view_id_]
            col_structure_ = collection_["col_structure"]
            properties_ = col_structure_["properties"]
            properties_master_ = {}
            for property_ in properties_:
                properties_property_ = properties_[property_]
                properties_master_[property_] = properties_property_
                bson_type_ = (
                    properties_property_["bsonType"]
                    if "bsonType" in properties_property_
                    else None
                )
                if bson_type_ == "array":
                    if "items" in properties_property_:
                        items_ = properties_property_["items"]
                        if "properties" in items_:
                            item_properties_ = items_["properties"]
                            for item_property_ in item_properties_:
                                properties_master_[item_property_] = item_properties_[
                                    item_property_
                                ]

            parents_ = []
            if "parents" in col_structure_:
                parents_ = col_structure_["parents"]

            pipe_ = []
            set_ = {"$set": {"_ID": {"$toObjectId": "$_id"}}}
            pipe_.append(set_)

            unset_ = []
            unset_.append("_modified_by")
            unset_.append("_modified_at")
            unset_.append("_modified_count")
            unset_.append("_resume_token")
            unset_.append("_created_at")
            unset_.append("_created_by")
            unset_.append("_structure")
            unset_.append("_tags")
            unset_.append("_ID")

            for properties_master__ in properties_master_:
                if (
                    properties_master__[:1] == "_"
                    and properties_master__ not in Misc().get_except_underdashes()
                ):
                    unset_.append(properties_master__)

            for parent_ in parents_:
                if "match" in parent_ and "collection" in parent_:
                    parent_collection_ = parent_["collection"]
                    find_one_ = (
                        Mongo()
                        .db_["_collection"]
                        .find_one({"col_id": parent_collection_})
                    )
                    if (
                        find_one_
                        and "col_structure" in find_one_
                        and "properties" in find_one_["col_structure"]
                    ):
                        for property_ in find_one_["col_structure"]["properties"]:
                            properties_master_[property_] = find_one_["col_structure"][
                                "properties"
                            ][property_]
                        match_ = parent_["match"]
                        pipeline__ = []
                        let_ = {}
                        for match__ in match_:
                            if match__["key"] and match__["value"]:
                                key_ = match__["key"]
                                value_ = match__["value"]
                                let_[f"{key_}"] = f"${key_}"
                                if key_:
                                    pipeline__.append({"$eq": [f"$${key_}", f"${value_}"]})

                        pipeline_ = [{"$match": {"$expr": {"$and": pipeline__}}}]
                        lookup_ = {
                            "from": f"{parent_collection_}_data",
                            "let": let_,
                            "pipeline": pipeline_,
                            "as": parent_collection_,
                        }
                        unwind_ = {
                            "path": f"${parent_collection_}",
                            "preserveNullAndEmptyArrays": True
                        }
                        replace_with_ = {
                            "$mergeObjects": ["$$ROOT", f"${parent_collection_}"]
                        }
                        pipe_.append({"$lookup": lookup_})
                        pipe_.append({"$unwind": unwind_})
                        pipe_.append({"$replaceWith": replace_with_})
                        unset_.append(parent_collection_)

            vie_filter_ = view_["data_filter"] if "data_filter" in view_ else []
            if len(vie_filter_) > 0:
                get_filtered_ = self.get_filtered_f({
                    "match": vie_filter_,
                    "properties": properties_master_ if properties_master_ else None
                })
                pipe_.append({"$match": get_filtered_})

            if unset_ and len(unset_) > 0:
                unset_ = list(dict.fromkeys(unset_))
                pipe_.append({"$unset": unset_})

            records_ = json.loads(JSONEncoder().encode(list(Mongo().db_[collection_id_].aggregate(pipe_))))
            count_ = len(records_) if records_ else 0

            df_ = pd.DataFrame(records_).fillna("#N/A")
            df_raw_ = pd.DataFrame(records_).fillna("")

            vie_visual_style_ = view_["chart_type"] if "chart_type" in view_ else "Vertical Bar"
            data_index_0_ = (
                view_["data_index"][0]
                if "data_index" in view_ and len(view_["data_index"]) > 0
                else None
            )
            data_values_0_k_ = (
                view_["data_values"][0]["key"]
                if "data_values" in view_
                and len(view_["data_values"]) > 0
                and "key" in view_["data_values"][0]
                else None
            )
            data_values_0_v_ = (
                view_["data_values"][0]["value"]
                if "data_values" in view_
                and len(view_["data_values"]) > 0
                and "value" in view_["data_values"][0]
                else "sum"
            )
            data_columns_0_ = (
                view_["data_columns"][0]
                if "data_columns" in view_ and len(view_["data_columns"]) > 0
                else None
            )

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
                if data_columns_0_ in df_.columns:
                    groupby_.append(data_columns_0_)
                if data_index_0_ in df_.columns:
                    groupby_.append(data_index_0_)
            else:
                if data_index_0_ in df_.columns:
                    groupby_.append(data_index_0_)
                if data_columns_0_ in df_.columns:
                    groupby_.append(data_columns_0_)

            df_ = df_.drop([x for x in df_.columns if x not in dropped_], axis=1)
            df_grp_ = df_.groupby(list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns), as_index=False).sum()

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
                    sum_ = float(
                        pd.to_numeric(df_[data_values_0_k_], errors="coerce").sum()
                    )
                    unique_ = float(
                        pd.to_numeric(df_[data_values_0_k_], errors="coerce").nunique()
                    )
                    mean_ = float(
                        pd.to_numeric(df_[data_values_0_k_], errors="coerce").mean()
                    )
                    stdev_ = float(
                        pd.to_numeric(df_[data_values_0_k_], errors="coerce").std()
                    )
                    var_ = float(
                        pd.to_numeric(df_[data_values_0_k_], errors="coerce").var()
                    )

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
                    dict(
                        selector="th",
                        props=[
                            ("background", f"{background_}"),
                            ("padding", f"{padding_}px {padding_r_}px"),
                            ("font-size", f"{font_size_table_}px"),
                        ],
                    ),
                    dict(
                        selector="td",
                        props=[
                            ("background", f"{background_}"),
                            ("padding", f"{padding_}px {padding_r_}px"),
                            ("text-align", "right"),
                            ("font-size", f"{font_size_table_}px"),
                        ],
                    ),
                    dict(selector="table", props=[("font-size", f"{font_size_table_}px")]),
                    dict(selector="caption", props=[("caption-side", "top")]),
                ]

                pivot_html_ = pivot_table_.to_html().replace('border="1"', "")
                pivot_table_ = pivot_table_.style.set_table_styles(styles_)
                pivotify_html_ = pivot_table_.to_html().replace('border="1"', "")

            return {
                "result": True,
                "series": series_,
                "data": records_ if scope_ == "external" else [] if scope_ == "propsonly" else records_[:50],
                "properties": properties_master_,
                "pivot": pivot_html_,
                "pivotify": pivotify_html_,
                "df": df_ if scope_ == "announcement" else None,
                "dfgrp": df_grp_ if scope_ == "announcement" else None,
                "dfraw": df_raw_ if scope_ == "announcement" else None,
                "self": view_,
                "stats": {
                    "count": count_ if count_ else 0,
                    "sum": sum_ if sum_ and sum_ > 0 else 0,
                    "unique": unique_ if unique_ and unique_ > 0 else 0,
                    "mean": mean_ if mean_ and mean_ > 0 else 0,
                    "stdev": stdev_ if stdev_ and stdev_ > 0 else 0,
                    "var": var_ if var_ and var_ > 0 else 0
                }
            }

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
                views_ = collection_["views"] if "views" in collection_ and len(collection_["views"]) > 0 else None
                if views_:
                    for view_ in views_:
                        id__ = view_["k"]
                        view__ = view_["v"]
                        get_view_data_f_ = self.get_view_data_f(user_, id__, source_)
                        if "skip" in get_view_data_f_ and get_view_data_f_["skip"] is True:
                            continue
                        if not get_view_data_f_["result"]:
                            continue
                            # raise APIError(f"get view data error {get_view_data_f_['msg']}")
                        returned_views_.append({
                            "id": id__,
                            "collection": collection_["col_id"],
                            "properties": get_view_data_f_["properties"],
                            "self": view__,
                            "data": get_view_data_f_["data"],
                            "series": get_view_data_f_["series"],
                            "pivot": get_view_data_f_["pivot"],
                            "stats": get_view_data_f_["stats"]
                        })

            return {"result": True, "views": returned_views_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def collections_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"]
            data_ = []
            structure_ = self.root_schemas_f("_collection")

            if Misc().permitted_user_f(user_):
                data_ = list(
                    Mongo()
                    .db_["_collection"]
                    .find(filter={}, sort=[("_updated_at", -1)])
                )
            else:
                usr_tags_ = (
                    user_["_tags"]
                    if "_tags" in user_ and len(user_["_tags"]) > 0
                    else []
                )
                for usr_tag_ in usr_tags_:
                    filter_ = {
                        "per_tag": usr_tag_,
                        "$or": [
                            {"per_insert": True},
                            {"per_read": True},
                            {"per_update": True},
                            {"per_delete": True},
                        ],
                    }
                    permissions_ = Mongo().db_["_permission"].find(filter=filter_, sort=[("per_collection_id", 1)])
                    for permission_ in permissions_:
                        collection_ = Mongo().db_["_collection"].find_one({"col_id": permission_["per_collection_id"]})
                        data_.append(collection_)

            return {
                "result": True,
                "data": json.loads(JSONEncoder().encode(data_)),
                "structure": structure_,
            }

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def collection_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"]
            col_id_ = obj["collection"]
            data_ = {}
            usr_tags_ = (
                user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
            )

            if Misc().permitted_user_f(user_):
                permitted_ = True
            else:
                permitted_ = False
                for usr_tag_ in usr_tags_:
                    permissions_ = (
                        Mongo()
                        .db_["_permission"]
                        .find_one(
                            {
                                "per_collection_id": col_id_,
                                "per_tag": usr_tag_,
                                "$or": [
                                    {"per_insert": True},
                                    {"per_read": True},
                                    {"per_update": True},
                                    {"per_delete": True},
                                ],
                            }
                        )
                    )
                    if permissions_:
                        permitted_ = True
                        break

            if permitted_:
                data_ = Mongo().db_["_collection"].find_one({"col_id": col_id_})
            else:
                raise APIError(f"no permission for {col_id_}")

            return {"result": True, "data": data_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def read_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["user"]
            limit_ = input_["limit"]
            page = input_["page"]
            collection_id_ = input_["collection"]
            projection_ = input_["projection"]
            skip_ = limit_ * (page - 1)
            match_ = input_["match"] if "match" in input_ and len(input_["match"]) > 0 else []
            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            collation_ = {"locale": user_["locale"]} if user_ and "locale" in user_ else {"locale": "tr"}
            cursor_ = Mongo().db_["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemas_f(f"{collection_id_}")
            if not cursor_:
                raise APIError(f"collection not found to read: {collection_id_}")

            structure_ = cursor_["col_structure"] if is_crud_ else cursor_
            reconfig_ = cursor_["_reconfig_req"] if "_reconfig_req" in cursor_ and cursor_["_reconfig_req"] is True else False

            get_filtered_ = self.get_filtered_f({
                "match": match_,
                "properties": structure_["properties"] if "properties" in structure_ else None
            })

            sort_ = list(input_["sort"].items()) if "sort" in input_ and input_["sort"] else list(structure_["sort"].items()) if "sort" in structure_ and structure_["sort"] else [("_modified_at", -1)]

            cursor_ = Mongo().db_[collection_].find(filter=get_filtered_, projection=projection_, sort=sort_, collation=collation_).skip(skip_).limit(limit_)
            docs_ = json.loads(JSONEncoder().encode(list(cursor_)))[:limit_] if cursor_ else []
            count_ = Mongo().db_[collection_].count_documents(get_filtered_)

            return {
                "result": True,
                "data": docs_,
                "count": count_,
                "structure": structure_,
                "reconfig": reconfig_,
            }

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f(
                {
                    "type": "Error",
                    "collection": collection_,
                    "op": "read",
                    "user": user_["email"] if user_ else None,
                    "document": str(exc),
                }
            )
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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

            if (
                collection_ in Mongo().db_.list_collection_names()
                and "properties" in structure_
            ):
                properties_ = structure_["properties"]
                properties_ = Misc().properties_cleaner_f(properties_)

                if (
                    "required" in structure_
                    and structure_["required"]
                    and len(structure_["required"]) > 0
                ):
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

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def schema_ext_validate_f(self, structure_, _id):
        """
        docstring is in progress
        """
        try:

            views_ = structure_["views"] if structure_ and "views" in structure_ else None
            if not views_:
                raise APIError("no views found")

            errstr_ = ""
            for vie_ in views_:
                if _id is not None and vie_ != _id:
                    continue
                view_ = views_[vie_]
                title_ = view_["title"] if "title" in view_ and view_["title"] != "" else None
                description_ = view_["description"] if "description" in view_ and view_["description"] != "" else None
                priority_ = view_["priority"] if "priority" in view_ and isinstance(view_["priority"], int) else None
                enabled_ = view_["enabled"] if "enabled" in view_ and view_["enabled"] in [True, False] else None
                dashboard_ = view_["dashboard"] if "dashboard" in view_ and view_["dashboard"] in [True, False] else None
                data_json_ = view_["data_json"] if "data_json" in view_ and view_["data_json"] in [True, False] else None
                data_excel_ = view_["data_excel"] if "data_excel" in view_ and view_["data_excel"] in [True, False] else None
                data_csv_ = view_["data_csv"] if "data_csv" in view_ and view_["data_csv"] in [True, False] else None
                pivot_ = view_["pivot"] if "pivot" in view_ and view_["pivot"] in [True, False] else None
                pivot_totals_ = view_["pivot_totals"] if "pivot_totals" in view_ and view_["pivot_totals"] in [True, False] else None
                chart_ = view_["chart"] if "chart" in view_ and view_["chart"] in [True, False] else None
                chart_type_ = view_["chart_type"] if "chart_type" in view_ and view_["chart_type"] in ["Flashcard", "Vertical Bar", "Normalized Vertical Bar", "Stacked Vertical Bar",
                                                                                                       "Grouped Vertical Bar", "Horizontal Bar", "Normalized Horizontal Bar", "Stacked Horizontal Bar", "Grouped Horizontal Bar", "Line", "Pie", "Doughnut"] else None
                chart_label_ = view_["chart_label"] if "chart_label" in view_ and view_["chart_label"] in [True, False] else None
                chart_gradient_ = view_["chart_gradient"] if "chart_gradient" in view_ and view_["chart_gradient"] in [True, False] else None
                chart_grid_ = view_["chart_grid"] if "chart_grid" in view_ and view_["chart_grid"] in [True, False] else None
                chart_legend_ = view_["chart_legend"] if "chart_legend" in view_ and view_["chart_legend"] in [True, False] else None
                chart_xaxis_ = view_["chart_xaxis"] if "chart_xaxis" in view_ and view_["chart_xaxis"] in [True, False] else None
                chart_xaxis_label_ = view_["chart_xaxis_label"] if "chart_xaxis_label" in view_ and view_["chart_xaxis_label"] in [True, False] else None
                chart_yaxis_ = view_["chart_yaxis"] if "chart_yaxis" in view_ and view_["chart_yaxis"] in [True, False] else None
                chart_yaxis_label_ = view_["chart_yaxis_label"] if "chart_yaxis_label" in view_ and view_["chart_yaxis_label"] in [True, False] else None
                chart_colors_ = view_["chart_colors"] if "chart_colors" in view_ else None
                scheduled_ = view_["scheduled"] if "scheduled" in view_ and view_["scheduled"] in [True, False] else None
                scheduled_cron_ = view_["scheduled_cron"] if "scheduled_cron" in view_ else None
                scheduled_tz_ = view_["scheduled_tz"] if "scheduled_tz" in view_ else None
                data_filter_ = view_["data_filter"] if "data_filter" in view_ else None
                data_sort_ = view_["data_sort"] if "data_sort" in view_ else None
                data_excluded = view_["data_excluded"] if "data_excluded" in view_ else None
                data_index_ = view_["data_index"] if "data_index" in view_ and len(view_["data_index"]) > 0 else None
                data_columns_ = view_["data_columns"] if "data_columns" in view_ and len(view_["data_columns"]) > 0 else None
                data_values_ = view_["data_values"] if "data_values" in view_ and len(view_["data_values"]) > 0 else None

                errarr_ = []
                errarr_.append("title is missing") if title_ is None else _Noop()
                errarr_.append("description is missing") if description_ is None else _Noop()
                errarr_.append("priority is missing") if priority_ is None else _Noop()
                errarr_.append("enabled is missing") if enabled_ is None else _Noop()
                errarr_.append("dashboard is missing") if dashboard_ is None else _Noop()
                errarr_.append("data_json is missing") if data_json_ is None else _Noop()
                errarr_.append("data_excel is missing") if data_excel_ is None else _Noop()
                errarr_.append("data_csv is missing") if data_csv_ is None else _Noop()
                errarr_.append("pivot is missing") if pivot_ is None else _Noop()
                errarr_.append("pivot_totals is missing") if pivot_totals_ is None else _Noop()
                errarr_.append("chart is missing") if chart_ is None else _Noop()
                errarr_.append("chart_type is missing") if chart_type_ is None else _Noop()
                errarr_.append("chart_label is missing") if chart_label_ is None else _Noop()
                errarr_.append("chart_gradient is missing") if chart_gradient_ is None else _Noop()
                errarr_.append("chart_grid is missing") if chart_grid_ is None else _Noop()
                errarr_.append("chart_legend is missing") if chart_legend_ is None else _Noop()
                errarr_.append("chart_xaxis is missing") if chart_xaxis_ is None else _Noop()
                errarr_.append("chart_xaxis_label is missing") if chart_xaxis_label_ is None else _Noop()
                errarr_.append("chart_yaxis is missing") if chart_yaxis_ is None else _Noop()
                errarr_.append("chart_yaxis_label is missing") if chart_yaxis_label_ is None else _Noop()
                errarr_.append("chart_colors is missing") if chart_colors_ is None else _Noop()
                errarr_.append("scheduled is missing") if scheduled_ is None else _Noop()
                errarr_.append("scheduled_cron is missing") if scheduled_cron_ is None else _Noop()
                errarr_.append("scheduled_tz is missing") if scheduled_tz_ is None else _Noop()
                errarr_.append("data_filter is missing") if data_filter_ is None else _Noop()
                errarr_.append("data_sort is missing") if data_sort_ is None else _Noop()
                errarr_.append("data_excluded is missing") if data_excluded is None else _Noop()
                errarr_.append("data_values is missing") if data_values_ is None else _Noop()
                errarr_.append("data_columns is missing") if data_columns_ is None and chart_type_ not in ["Flashcard", "Pie"] else _Noop()
                errarr_.append("data_index is missing") if data_index_ is None and chart_type_ not in ["Flashcard"] else _Noop()

                if len(errarr_) > 0:
                    errstr_ += f"{vie_}: "
                    errstr_ += ", ".join(errarr_) + " "

            if errstr_ != "":
                errstr_ = f"!!! view schema error: {errstr_}"
                raise APIError(errstr_)

            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

    def saveschema_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_id_ = obj["collection"]
            structure_ = obj["structure"]
            user_ = obj["user"]

            Mongo().db_["_collection"].update_one({"col_id": collection_id_}, {"$set": {
                "col_structure": structure_,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_["usr_id"]
            },
                "$inc": {"_modified_count": 1}
            })

            func_ = self.crudschema_validate_f({"collection": f"{collection_id_}_data", "structure": structure_})
            if not func_["result"]:
                raise APIError(func_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def saveview_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"] if "userindb" in obj else None
            col_id_ = obj["collection"]
            view_ = obj["view"]
            view_id_ = obj["id"]
            email_ = user_["usr_id"] if user_ and "usr_id" in user_ else None
            _tags = user_["_tags"]

            if not Misc().permitted_user_f(user_):
                permission_ = Mongo().db_["_permission"].find_one({
                    "per_collection_id": col_id_,
                    "per_tag": {"$in": _tags},
                    "per_schema": True
                })
                if not permission_:
                    raise APIError("no permission")

            doc_ = Mongo().db_["_collection"].find_one({"col_id": col_id_})
            if not doc_:
                raise APIError("collection not found")
            doc_["col_structure"]["views"][view_id_] = view_
            structure_ = doc_["col_structure"]

            schema_ext_validate_f_ = self.schema_ext_validate_f(structure_, view_id_)
            if not schema_ext_validate_f_["result"]:
                raise APIError(schema_ext_validate_f_["msg"])

            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = email_

            Mongo().db_["_collection"].update_one({"col_id": col_id_}, {"$set": doc_})

            func_ = self.crudschema_validate_f({"collection": f"{col_id_}_data", "structure": structure_})
            if not func_["result"]:
                raise APIError(func_["msg"])

            Misc().log_f({
                "type": "Info",
                "collection": col_id_,
                "op": "saveview",
                "user": email_,
                "document": doc_
            })

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": col_id_,
                "op": "saveview",
                "user": email_,
                "document": str(exc)
            })

            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def upsert_f(self, obj):
        """
        docstring is in progress
        """
        try:
            doc = obj["doc"]
            _id = ObjectId(doc["_id"]) if "_id" in doc else None
            match_ = (
                {"_id": _id}
                if _id
                else obj["match"]
                if "match" in obj and obj["match"] is not None and len(obj["match"]) > 0
                else obj["filter"]
                if "filter" in obj
                else None
            )

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

            doc_ = {}
            for item in doc:
                if item[:1] != "_" or item in Misc().get_except_underdashes():
                    doc_[item] = doc[item] if doc[item] != "" else None

            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            Mongo().db_[collection_].update_one(match_, {"$set": doc_, "$inc": {"_modified_count": 1}})

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
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "update",
                "user": user_["email"] if user_ else None,
                "document": str(exc)
            })
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "remove",
                "user": user_["email"] if user_ else None,
                "document": str(exc)
            })
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
                raise APIError("user collection is protected to be deleted")

            ids_ = []
            for _id in match_:
                ids_.append(ObjectId(_id))

            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            structure__ = (
                Mongo().db_["_collection"].find_one({"col_id": collection_id_})
                if is_crud_
                else self.root_schemas_f(f"{collection_id_}")
            )
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
                if op_ == "clone":
                    doc["_created_at"] = doc["_modified_at"] = Misc().get_now_f()
                    doc["_created_by"] = doc["_modified_by"] = (
                        user_["email"] if user_ and "email" in user_ else None
                    )
                    doc["_modified_count"] = 0
                    doc.pop("_id", None)
                    if unique:
                        for uq in unique:
                            if uq[0] in doc:
                                if "objectId" in properties[uq[0]] and properties[uq[0]]["objectId"] is True:
                                    doc[uq[0]] = str(bson.objectid.ObjectId())
                                elif properties[uq[0]]["bsonType"] == "string":
                                    doc[uq[0]] = (
                                        f"{doc[uq[0]]}-1"
                                        if "_" in doc[uq[0]]
                                        else f"{doc[uq[0]]}-{index}"
                                    )
                    Mongo().db_[collection_].insert_one(doc)

                elif op_ == "delete":
                    Mongo().db_[collection_].delete_one({"_id": doc["_id"]})
                    doc["_deleted_at"] = Misc().get_now_f()
                    doc["_deleted_by"] = user_["email"] if user_ and "email" in user_ else None
                    Mongo().db_[f"{collection_id_}_bin"].insert_one(doc)

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
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": f"multiple {op_}",
                "user": user_["email"] if user_ else None,
                "document": str(exc)
            })
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def action_f(self, obj):
        """
        docstring is in progress
        """
        try:
            collection_id_ = obj["collection"]
            user_ = obj["userindb"] if "userindb" in obj else None
            match_ = obj["match"] if "match" in obj else None
            actionix_ = obj["actionix"] if "actionix" in obj else None
            doc_ = obj["doc"] if "doc" in obj else None

            email_ = user_["usr_id"] if user_ and "usr_id" in user_ else None
            if not email_:
                raise AppException("user is not allowed")

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

            action_ = (
                structure_["actions"][actionix_]
                if "actions" in structure_
                and len(structure_["actions"]) > 0
                and structure_["actions"][actionix_]
                else None
            )
            if not action_:
                raise AppException("action not found")

            tags_ = (
                action_["_tags"]
                if "_tags" in action_ and len(action_["_tags"]) > 0
                else None
            )
            if not tags_:
                raise AppException("no tags found in action")

            notify_ = False
            notification_ = (
                action_["notification"] if "notification" in action_ else None
            )

            if notification_:
                if "notify" not in notification_:
                    raise AppException("no notify field found in notification")
                notify_ = notification_["notify"] is True
                subject_ = (
                    notification_["subject"]
                    if "subject" in notification_
                    else "Action Completed"
                )
                if not subject_:
                    raise AppException("no subject field found in notification")
                body_ = (
                    notification_["body"]
                    if "body" in notification_
                    else "<p>Hi,</p><p>Action completed successfully.</p><p><h1></h1></p>"
                )
                if not body_:
                    raise AppException("no body field found in notification")
                fields_ = (
                    notification_["fields"].replace(" ", "")
                    if "fields" in notification_
                    else None
                )
                if not fields_:
                    raise AppException("no fields field found in notification")
                filter_ = (
                    notification_["filter"]
                    if "filter" in notification_ and len(notification_["filter"]) > 0
                    else None
                )
                if not filter_:
                    raise AppException("no filter array found in notification")
                get_notification_filtered_ = self.get_filtered_f(
                    {
                        "match": filter_,
                        "properties": structure_["properties"]
                        if "properties" in structure_
                        else None,
                    }
                )

            match_ = (
                action_["match"]
                if "match" in action_ and len(action_["match"]) > 0
                else {}
            )

            get_filtered_ = self.get_filtered_f(
                {
                    "match": match_,
                    "properties": structure_["properties"]
                    if "properties" in structure_
                    else None,
                }
            )

            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = email_

            if ids_ and len(ids_) > 0:
                get_filtered_ = {"$and": [get_filtered_, {"_id": {"$in": ids_}}]}
                if notify_:
                    get_notification_filtered_ = {
                        "$and": [get_notification_filtered_, {"_id": {"$in": ids_}}]
                    }

            # DO ACTION ON DATABASE
            session_client_ = MongoClient(Mongo().connstr)
            session_db_ = session_client_[MONGO_DB_]
            session_ = session_client_.start_session()
            session_.start_transaction()
            set_ = {"$set": doc_, "$inc": {"_modified_count": 1}}
            update_many_ = session_db_[collection_].update_many(
                get_filtered_, set_, session=session_
            )

            if update_many_.matched_count:
                session_.commit_transaction()
                if notify_:
                    type_ = "csv"
                    file_ = f"action-{Misc().get_timestamp_f()}.{type_}"
                    loc_ = f"/cron/{file_}"
                    query_ = (
                        "'"
                        + json.dumps(
                            get_notification_filtered_,
                            default=json_util.default,
                            sort_keys=False,
                        )
                        + "'"
                    )
                    command_ = f"mongoexport --quiet --uri='mongodb://{MONGO_USERNAME_}:{MONGO_PASSWORD_}@{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}/?authSource={MONGO_AUTH_DB_}' --ssl --collection={collection_} --out={loc_} --tlsInsecure --sslCAFile={MONGO_TLS_CA_KEYFILE_} --sslPEMKeyFile={MONGO_TLS_CERT_KEYFILE_} --sslPEMKeyPassword={MONGO_TLS_CERT_KEY_PASSWORD_} --tlsInsecure --db={MONGO_DB_} --type={type_} --fields={fields_} --query={query_}"
                    call(command_, shell=True)
                    files_ = [{"filename": file_, "filetype": type_}]
                    email_sent_ = Email().sendEmail_f(
                        {
                            "op": "action",
                            "tags": tags_,
                            "subject": subject_,
                            "html": body_,
                            "files": files_,
                        }
                    )
                    if not email_sent_["result"]:
                        raise APIError(email_sent_["msg"])
            else:
                raise AppException("no rows affected due to the match criteria")

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": collection_,
                    "op": "action",
                    "user": email_,
                    "document": {"doc": doc_, "match": match_},
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "count": update_many_.matched_count}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f(
                {
                    "type": "Error",
                    "collection": collection_id_,
                    "op": "action",
                    "user": email_,
                    "document": str(exc),
                }
            )

            return Misc().mongo_error_f(exc)

        except AppException as exc:
            return Misc().app_exception_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

        finally:
            session_: session_.abort_transaction()

    def insert_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            doc_ = obj["doc"]

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
                file_ = "template-elementary.json"
                prefix_ = doc_["col_prefix"] if "col_prefix" in doc_ else "zzz"
                path_ = f"/app/_template/{file_}"
                if os.path.isfile(path_):
                    with open(path_, "r", encoding="utf-8") as fopen_:
                        jtxt_ = fopen_.read()
                        jtxt_ = jtxt_.replace("zzz_", f"{prefix_}_")
                        structure_ = json.loads(jtxt_)
                doc_["col_structure"] = structure_
            elif collection_id_ == "_token":
                tkn_lifetime_ = doc_["tkn_lifetime"] if "tkn_lifetime" in doc_ and doc_["tkn_lifetime"] > 0 else 1440
                secret_ = pyotp.random_base32()
                finder_ = pyotp.random_base32()
                jwt_proc_f_ = Misc().jwt_proc_f("encode", None, secret_, {
                    "iss": "Technoplatz",
                    "aud": "api",
                    "sub": "bi",
                    "exp": Misc().get_now_f() + timedelta(minutes=tkn_lifetime_),
                    "iat": Misc().get_now_f()
                }, {"finder": finder_})
                if not jwt_proc_f_["result"]:
                    raise AuthError(jwt_proc_f_["msg"])
                doc_["tkn_copy_count"] = 0
                doc_["tkn_token"] = inserted_ = jwt_proc_f_["jwt"]
                doc_["tkn_secret"] = secret_
                doc_["tkn_finder"] = finder_

            Mongo().db_[collection_].insert_one(doc_)

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

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_id_,
                "op": "insert",
                "user": user_["email"] if user_ else None,
                "document": doc_,
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "token": inserted_}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "insert",
                "user": user_["email"] if user_ else None,
                "document": str(exc)
            })
            return Misc().mongo_error_f(exc)

        except AuthError as exc_:
            return Misc().auth_error_f(exc_)

        except APIError as exc_:
            return Misc().api_error_f(exc_)

        except Exception as exc_:
            return Misc().exception_f(exc_)


class _Noop:
    def __init__(self, level=0):
        self.level = level

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Email:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.disclaimer_ = f"<p>Sincerely,</p><p>{COMPANY_NAME_}</p><p>PLEASE DO NOT REPLY THIS EMAIL<br />--------------------------------<br />This email and its attachments transmitted with it may contain private, confidential or prohibited information. If you are not the intended recipient of this mail, you are hereby notified that storing, copying, using or forwarding of any part of the contents is strictly prohibited. Please completely delete it from your system and notify the sender. {COMPANY_NAME_} makes no warranty with regard to the accuracy or integrity of this mail and its transmission.</p>"
        self.disclaimer_text_ = f"\n\nSincerely,\n\n{COMPANY_NAME_}\n\nPLEASE DO NOT REPLY THIS EMAIL\n--------------------------------\nThis email and its attachments transmitted with it may contain private, confidential or prohibited information. If you are not the intended recipient of this mail, you are hereby notified that storing, copying, using or forwarding of any part of the contents is strictly prohibited. Please completely delete it from your system and notify the sender. {COMPANY_NAME_} makes no warranty with regard to the accuracy or integrity of this mail and its transmission."

    def send_email_smtp_f(self, msg):
        """
        docstring is in progress
        """
        try:
            email_from_ = f"{COMPANY_NAME_} <{FROM_EMAIL_}>"
            html_ = f"{msg['html']} {self.disclaimer_}"
            server_ = smtplib.SMTP_SSL(SMTP_SERVER_, SMTP_PORT_)
            server_.ehlo()
            server_.login(SMTP_USERID_, SMTP_PASSWORD_)

            message_ = MIMEMultipart()
            message_["From"] = email_from_
            message_["Subject"] = msg["subject"]
            message_.attach(MIMEText(html_, "html"))

            for file_ in msg["files"]:
                filename_ = file_["filename"]
                with open(f"/cron/{filename_}", "rb") as attachment_:
                    part_ = MIMEBase("application", "octet-stream")
                    part_.set_payload(attachment_.read())
                encoders.encode_base64(part_)
                part_.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename_}",
                )
                message_.attach(part_)

            recipients_ = []
            recipients_str_ = ""
            for recipient_ in msg["personalizations"]["to"]:
                email_to_ = (
                    f"{recipient_['name']} <{recipient_['email']}>"
                    if recipient_["name"] and "name" in recipient_
                    else recipient_["email"]
                )
                recipients_str_ += (
                    email_to_ if recipients_str_ == "" else f", {email_to_}"
                )
                recipients_.append(recipient_["email"])

            message_["To"] = recipients_str_
            server_.sendmail(email_from_, recipients_, message_.as_string())
            server_.close()

            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def sendEmail_f(self, msg):
        """
        docstring is in progress
        """
        try:
            op_ = msg["op"] if "op" in msg else None
            files_ = msg["files"] if "files" in msg and len(msg["files"]) > 0 else []
            html_ = f"{msg['html']}" if "html" in msg else None
            tags_ = msg["tags"] if "tags" in msg and len(msg["tags"]) > 0 else None
            personalizations_ = (
                msg["personalizations"] if "personalizations" in msg else None
            )
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

            if op_ is None or op_ == "":
                raise APIError("email operation is missing")

            if html_ is None or html_ == "":
                raise APIError("email message is missing")

            if tags_:
                f_ = Misc().get_users_from_tags_f(tags_)
                if not f_["result"]:
                    raise APIError(f"personalizations error {f_['msg']}")
                personalizations_ = f_ if "to" in f_ else None

            if personalizations_ is None:
                raise APIError("email personalizations is missing")

            if "to" not in personalizations_ or len(personalizations_["to"]) == 0:
                raise APIError("to list is missing")

            msg_ = {
                "op": op_,
                "files": files_,
                "personalizations": personalizations_,
                "subject": subject_,
                "html": html_
            }

            email_sent_ = self.send_email_smtp_f(msg_)

            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)


class Security:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.origin = request.headers["Origin"].replace("https://", "").replace("http://", "").replace("/", "").split(":")[0] if request.headers and "Origin" in request.headers else None

    def validate_app_request_f(self):
        """
        docstring is in progress
        """
        try:
            if not self.origin:
                raise APIError("invalid request")

            if self.origin not in [DOMAIN_, "localhost"]:
                raise APIError(f"invalid request from {self.origin}")

            return {"result": True}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def header_simple_f(self):
        """
        docstring is in progress
        """
        return {"Content-Type": "application/json; charset=utf-8"}


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
            return Misc().api_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
                    "_otp_validated_ip": Misc().get_user_ip_f(),
                }, "$inc": {"_modified_count": 1}
                })
            else:
                Mongo().db_["_auth"].update_one({"aut_id": email_}, {"$set": {
                    "aut_otp_validated": validated_,
                    "_otp_not_validated_at": Misc().get_now_f(),
                    "_otp_not_validated_by": email_,
                    "_otp_not_validated_ip": Misc().get_user_ip_f()
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
                    "ip": Misc().get_user_ip_f(),
                    "_modified_at": Misc().get_now_f(),
                    "_modified_by": email_,
                }})
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "success": validated_, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
            return Misc().api_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def request_otp_f(self, email_):
        """
        docstring is in progress
        """
        try:
            user_ = Mongo().db_["_user"].find_one({"usr_id": email_, "usr_enabled": True})
            if not user_ or user_ is None:
                raise APIError("user not found")

            usr_id_ = user_["usr_id"]
            name_ = user_["usr_name"]
            tfac_ = randint(100001, 999999)
            Mongo().db_["_auth"].update_one({"aut_id": usr_id_}, {"$set": {"aut_tfac": tfac_, "_tfac_modified_at": Misc().get_now_f()}, "$inc": {"_modified_count": 1}})
            email_sent_ = Email().sendEmail_f({
                "op": "tfa",
                "personalizations": {"to": [{"email": usr_id_, "name": name_}]},
                "html": f"<p>Hi {name_},</p><p>Here's your backup two-factor access code so that you can validate your account;</p><p><h1>{tfac_}</h1></p>"
            })
            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)


class Auth:
    """
    docstring is in progress
    """

    def saas_f(self):
        """
        docstring is in progress
        """
        try:
            saas_ = {
                "company": COMPANY_NAME_,
                "version": "Technoplatz BI - Enterprise Edition" if SAAS_.lower() == "ee" else "Technoplatz BI - Community Edition",
            }

            return {"result": True, "user": None, "saas": saas_}

        except Exception as exc:
            return Misc().exception_f(exc)

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
            return Misc().api_error_f(exc)

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
            return Misc().exception_f(exc)

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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def password_hash_f(self, password_, salted_):
        """
        docstring is in progress
        """
        try:
            pat = re.compile(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*.-_?&]{8,32}$"
            )
            if not re.search(pat, password_):
                raise APIError("Invalid password")
            salt_ = os.urandom(32) if salted_ is None else salted_
            key_ = hashlib.pbkdf2_hmac(
                "sha512", password_.encode("utf-8"), salt_, 101010, dklen=128
            )
            return {"result": True, "salt": salt_, "key": key_}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

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
            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def permission_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["user"]
            user_id_ = user_["usr_id"] if "usr_id" in user_ else None
            usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
            collection_id_ = input_["collection"] if "collection" in input_ else None
            op_ = input_["op"] if "op" in input_ else None
            administratives_ = ["dump", "backup", "restore"]
            permissive_ = ["view", "views", "collections", "template"]
            allowmatch_ = []

            if not user_id_:
                raise APIError(f"user not found {user_id_}")

            op_ = "read" if op_ in ["collection"] else input_["op"]
            if not op_:
                raise APIError(f"operation is missing {op_}")

            if Misc().permitted_user_f(user_):
                return {"result": True, "allowmatch": allowmatch_}

            if op_ in administratives_:
                raise AuthError(f"no {op_} permission for {collection_id_}")

            if not collection_id_:
                return {"result": True, "allowmatch": allowmatch_} if op_ in permissive_ else {"result": False, "allowmatch": allowmatch_}

            if collection_id_[:1] == "_" and op_ == "read":
                return {"result": True, "allowmatch": allowmatch_}

            collection_ = Mongo().db_["_collection"].find_one({"col_id": collection_id_})
            if not collection_:
                raise APIError(f"no collection found {collection_id_}/{op_}")

            permission_ = False
            for ix_, usr_tag_ in enumerate(usr_tags_):
                permission_check_ = Mongo().db_["_permission"].find_one({"per_tag": usr_tag_, "per_collection_id": collection_id_})
                if permission_check_:
                    per_insert_ = "per_insert" in permission_check_ and permission_check_["per_insert"] is True
                    per_read_ = "per_read" in permission_check_ and permission_check_["per_read"] is True
                    per_update_ = "per_update" in permission_check_ and permission_check_["per_update"] is True
                    per_delete_ = "per_delete" in permission_check_ and permission_check_["per_delete"] is True
                    per_share_ = "per_share" in permission_check_ and permission_check_["per_share"] is True
                    per_schema_ = "per_schema" in permission_check_ and permission_check_["per_schema"] is True
                    if ((op_ == "saveschema" and per_schema_) or
                        (op_ == "announce" and per_share_) or
                        (op_ == "read" and per_read_) or
                        (op_ in ["insert", "import"] and per_insert_) or
                        (op_ == "upsert" and per_insert_ and per_update_) or
                        (op_ in ["update", "action"] and per_read_ and per_update_) or
                        (op_ == "clone" and per_read_ and per_insert_) or
                            (op_ == "delete" and per_read_ and per_delete_)):
                        if ix_ == 0:
                            allowmatch_ = permission_check_["per_match"] if "per_match" in permission_check_ and len(permission_check_["per_match"]) > 0 else []
                        permission_ = True
                        break

            if permission_ is False:
                raise AuthError(f"no {op_} permission for {collection_id_}")

            return {"result": permission_, "allowmatch": allowmatch_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def firewall_f(self, user_):
        """
        docstring is in progress
        """
        try:
            ip_ = Misc().get_user_ip_f()
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
            return Misc().api_error_f(exc)

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
            return Misc().exception_f(exc)

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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def forgot_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            if "email" not in input_ or input_["email"] is None:
                raise APIError("e-mail is missing")

            email_ = bleach.clean(input_["email"])

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            otp_send_ = OTP().request_otp_f(email_)
            if not otp_send_["result"]:
                raise APIError(otp_send_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def reset_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json

            email_ = input_["email"]
            password_ = input_["password"]
            tfac_ = input_["tfac"]

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

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def tfac_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            email_ = input_["email"]
            password_ = input_["password"]
            tfac_ = input_["tfac"]
            user_validate_ = self.user_validate_by_basic_auth_f({"userid": email_, "password": password_})
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])
            user_ = user_validate_["user"] if "user" in user_validate_ else None
            auth_ = user_validate_["auth"] if "auth" in user_validate_ else None

            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, "signin")
            if not verify_otp_f_["result"]:
                raise AuthError(verify_otp_f_["msg"])

            usr_name_ = user_["usr_name"]
            perm_ = Misc().permitted_user_f(user_)
            payload_ = {
                "iss": "Technoplatz",
                "aud": "api",
                "sub": "bi",
                "exp": Misc().get_now_f() + timedelta(minutes=int(API_SESSION_EXP_MINUTES_)),
                "iat": Misc().get_now_f(),
                "id": email_,
                "name": usr_name_,
                "perm": perm_
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

            user_payload_ = {"token": token_, "name": usr_name_, "email": email_, "perm": perm_, "api_key": api_key_}
            ip_ = Misc().get_user_ip_f()

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
                email_sent_ = Email().sendEmail_f({
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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def jwt_validate_f(self):
        """
        docstring is in progress
        """
        try:
            authorization_ = request.headers.get("Authorization", None)
            if not authorization_:
                raise AuthError("invalid authorization request")

            authb_ = "Bearer "
            ix_ = authorization_.find(authb_)
            if ix_ != 0:
                raise AuthError("no token provided")

            token_ = authorization_.replace(authb_, "")
            if not token_:
                raise AuthError("no token provided")

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
                raise AuthError(jwt_proc_f_["msg"])
            claims_ = jwt_proc_f_["jwt"]

            usr_id_ = claims_["id"] if "id" in claims_ and claims_["id"] is not None else None
            if not usr_id_:
                raise AuthError("invalid user token")
            if usr_id_ != aut_id_:
                raise AuthError("invalid user validation")

            user_ = Mongo().db_["_user"].find_one({"usr_id": aut_id_})
            if not user_:
                raise AuthError("user not found")

            user_["email"] = user_["usr_id"]
            user_["api_key"] = auth_["aut_api_key"]

            return ({"result": True, "user": user_, "auth": auth_})

        except AuthError as exc_:
            return Misc().auth_error_f(exc_)

        except Exception as exc_:
            return ({"result": False, "msg": "invalid session", "exc": str(exc_)})

    def user_validate_by_basic_auth_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_id_ = bleach.clean(input_["userid"]) if "userid" in input_ else None
            password_ = bleach.clean(input_["password"]) if "password" in input_ else None

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

            user_ = Mongo().db_["_user"].find_one({"usr_id": user_id_, "usr_enabled": True})
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
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def user_validate_by_api_key_f(self, input_):
        """
        docstring is in progress
        """
        try:
            api_key_ = bleach.clean(input_["api_key"]) if "api_key" in input_ else None
            if not api_key_ or api_key_ is None:
                raise APIError("api key must be provided")

            auth_ = Mongo().db_["_auth"].find_one({"aut_api_key": api_key_})
            if not auth_:
                raise APIError("not authenticated")
            user_id_ = auth_["aut_id"]

            user_ = Mongo().db_["_user"].find_one({"usr_id": user_id_, "usr_enabled": True})
            if not user_:
                raise APIError("user not found for api")

            firewall_ = self.firewall_f(user_)
            if not firewall_["result"]:
                raise APIError(firewall_["msg"])

            return {"result": True, "user": user_, "auth": auth_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def signin_f(self):
        """
        docstring is in progress
        """
        try:
            input_ = request.json
            email_ = input_["email"]
            password_ = input_["password"]

            user_validate_ = self.user_validate_by_basic_auth_f({"userid": email_, "password": password_})
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])

            otp_send_ = OTP().request_otp_f(email_)
            if not otp_send_["result"]:
                raise APIError(otp_send_["msg"])

            return {"result": True, "msg": "user needs to be validated by OTP"}

        except APIError as exc:
            return Misc().api_error_f(exc)

        except AuthError as exc:
            return Misc().auth_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)

    def signup_f(self):
        """
        docstring is in progress
        """
        try:
            checkup_ = self.checkup_f()
            if not checkup_["result"]:
                raise APIError(checkup_["msg"])

            input_ = request.json
            email_ = bleach.clean(input_["email"])
            password_ = bleach.clean(input_["password"])
            passcode_ = bleach.clean(input_["passcode"])

            auth_ = Mongo().db_["_auth"].find_one({"aut_id": email_})
            if auth_:
                raise APIError("account already exist")

            user_ = Mongo().db_["_user"].find_one({"usr_id": email_, "usr_enabled": True})
            if not user_ or user_ is None:
                raise APIError("user invitation not found")

            if passcode_ != str(user_["_id"]):
                raise APIError("invitation codes do not match")

            hash_f_ = self.password_hash_f(password_, None)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])

            salt_ = hash_f_["salt"]
            key_ = hash_f_["key"]

            aut_otp_secret_ = pyotp.random_base32()
            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(
                name=email_, issuer_name="Technoplatz-BI"
            )
            api_key_ = secrets.token_hex(16)

            Mongo().db_["_auth"].insert_one({
                "aut_id": email_,
                "aut_salt": salt_,
                "aut_key": key_,
                "aut_api_key": api_key_,
                "aut_tfac": None,
                "aut_expires": 0,
                "aut_otp_secret": aut_otp_secret_,
                "aut_otp_validated": False,
                "_qr_modified_at": Misc().get_now_f(),
                "_qr_modified_by": email_,
                "_qr_modified_count": 0,
                "_created_at": Misc().get_now_f(),
                "_created_by": email_,
                "_created_ip": Misc().get_user_ip_f(),
                "_modified_at": Misc().get_now_f(),
                "_modified_by": email_,
            })

            return {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().api_error_f(exc)

        except Exception as exc:
            return Misc().exception_f(exc)


TZ_ = os.environ.get("TZ") if os.environ.get("TZ") else "Europe/Berlin"
DOMAIN_ = os.environ.get("DOMAIN") if os.environ.get("DOMAIN") else "localhost"
API_OUTPUT_ROWS_LIMIT_ = os.environ.get("API_OUTPUT_ROWS_LIMIT")
NOTIFICATION_SLACK_HOOK_URL_ = os.environ.get("NOTIFICATION_SLACK_HOOK_URL")
COMPANY_NAME_ = os.environ.get("COMPANY_NAME") if os.environ.get("COMPANY_NAME") else "Technoplatz BI"
SMTP_SERVER_ = os.environ.get("SMTP_SERVER")
SMTP_PORT_ = os.environ.get("SMTP_PORT")
SMTP_USERID_ = os.environ.get("SMTP_USERID")
SMTP_PASSWORD_ = os.environ.get("SMTP_PASSWORD")
FROM_EMAIL_ = os.environ.get("FROM_EMAIL")
EMAIL_TFA_SUBJECT_ = "Your Backup OTP"
EMAIL_SIGNUP_SUBJECT_ = "Welcome"
EMAIL_SIGNIN_SUBJECT_ = "New Sign-in"
EMAIL_UPLOADERR_SUBJECT_ = "File Upload Result"
EMAIL_DEFAULT_SUBJECT_ = "Hello"
API_SCHEDULE_INTERVAL_MIN_ = os.environ.get("API_SCHEDULE_INTERVAL_MIN")
API_DUMP_HOURS_ = os.environ.get("API_DUMP_HOURS") if os.environ.get("API_DUMP_HOURS") else "23"
API_UPLOAD_LIMIT_BYTES_ = int(os.environ.get("API_UPLOAD_LIMIT_BYTES"))
API_MAX_CONTENT_LENGTH_ = int(os.environ.get("API_MAX_CONTENT_LENGTH"))
API_SESSION_EXP_MINUTES_ = os.environ.get("API_SESSION_EXP_MINUTES")
SAAS_ = os.environ.get("SAAS")
MONGO_RS_ = os.environ.get("MONGO_RS")
MONGO_HOST0_ = os.environ.get("MONGO_HOST0")
MONGO_HOST1_ = os.environ.get("MONGO_HOST1")
MONGO_HOST2_ = os.environ.get("MONGO_HOST2")
MONGO_PORT0_ = int(os.environ.get("MONGO_PORT0"))
MONGO_PORT1_ = int(os.environ.get("MONGO_PORT1"))
MONGO_PORT2_ = int(os.environ.get("MONGO_PORT2"))
MONGO_DB_ = os.environ.get("MONGO_DB")
MONGO_AUTH_DB_ = os.environ.get("MONGO_AUTH_DB")
MONGO_USERNAME_ = urllib.parse.quote_plus(os.environ.get("MONGO_USERNAME"))
MONGO_PASSWORD_ = urllib.parse.quote_plus(os.environ.get("MONGO_PASSWORD"))
MONGO_TLS_ = os.environ.get("MONGO_TLS") in [True, "true", "True", "TRUE"]
MONGO_TLS_CERT_KEY_PASSWORD_ = urllib.parse.quote_plus(os.environ.get("MONGO_TLS_CERT_KEY_PASSWORD"))
MONGO_TLS_CA_KEYFILE_ = os.environ.get("MONGO_TLS_CA_KEYFILE")
MONGO_TLS_CERT_KEYFILE_ = os.environ.get("MONGO_TLS_CERT_KEYFILE")
MONGO_RETRY_WRITES_ = os.environ.get("MONGO_RETRY_WRITES") in [True, "true", "True", "TRUE"]
PERMISSIVE_TAGS_ = ["#Managers", "#Administrators"]
PROTECTED_COLLS_ = ["_log", "_backup", "_event", "_token", "_announcement"]
PROTECTED_INSDEL_EXC_COLLS_ = ["_token"]

app = Flask(__name__)
origins_ = [f"http://{DOMAIN_}", f"https://{DOMAIN_}", f"http://{DOMAIN_}:8100", f"http://{DOMAIN_}:8101"]
app.config["CORS_ORIGINS"] = origins_
app.config["CORS_HEADERS"] = ["Content-Type", "Origin", "Authorization", "X-Requested-With", "Accept", "x-auth"]
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
app.config["MAX_CONTENT_LENGTH"] = API_MAX_CONTENT_LENGTH_
app.config["UPLOAD_EXTENSIONS"] = ["pdf", "png", "jpg", "jpeg", "xlsx", "xls", "doc", "docx", "csv", "txt"]
app.config["UPLOAD_FOLDER"] = "/vault/"
app.json_encoder = JSONEncoder
CORS(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@app.route("/import", methods=["POST"], endpoint="import")
def storage_f():
    """
    docstring is in progress
    """
    try:
        validate_request_f_ = Security().validate_app_request_f()
        if not validate_request_f_["result"]:
            raise APIError(validate_request_f_["msg"] if "msg" in validate_request_f_ else "validation error")

        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError({"result": False, "msg": jwt_validate_f_["msg"]})
        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "user session not found"})

        form_ = request.form.to_dict(flat=True)
        if not form_:
            raise APIError("no form found")

        file_ = request.files["file"]
        if not file_:
            raise APIError("no file found")

        collection__ = form_["collection"]
        col_check_ = Crud().inner_collection_f(collection__)
        if not col_check_["result"]:
            raise APIError(col_check_["msg"])

        prefix_ = col_check_["collection"]["col_prefix"]

        import_f_ = Crud().import_f({
            "form": form_,
            "file": file_,
            "collection": collection__,
            "user": user_,
            "prefix": prefix_,
        })

        if not import_f_["result"]:
            raise APIError(import_f_["msg"])

        return json.dumps({"result": import_f_["result"], "count": import_f_["count"] if "count" in import_f_ and import_f_["count"] >= 0 else 0, "msg": import_f_["msg"] if "msg" in import_f_ else None}, default=json_util.default, sort_keys=False), 200, Security().header_simple_f()

    except APIError as exc:
        return {"msg": str(exc), "status": 400}

    except Exception as exc:
        return {"msg": str(exc), "status": 500}


@app.route("/crud", methods=["POST"], endpoint="crud")
def crud_f():
    """
    docstring is in progress
    """
    try:
        input_ = request.json
        if "op" not in input_:
            raise APIError({"result": False, "msg": "no operation found"})
        op_ = input_["op"]

        validate_request_f_ = Security().validate_app_request_f()
        if not validate_request_f_["result"]:
            raise SessionError(validate_request_f_)

        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError({"result": False, "msg": jwt_validate_f_["msg"]})
        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "user session not found"})
        input_["user"] = user_
        input_["userindb"] = user_
        email_ = user_["usr_id"] if "usr_id" in user_ else None

        collection_ = input_["collection"] if "collection" in input_ else None
        match_ = input_["match"] if "match" in input_ and input_["match"] is not None and len(input_["match"]) > 0 else []
        allowmatch_ = []
        permission_f_ = Auth().permission_f({
            "user": jwt_validate_f_["user"],
            "auth": jwt_validate_f_["auth"],
            "collection": collection_,
            "op": op_,
        })
        if not permission_f_["result"]:
            raise AuthError(permission_f_)

        allowmatch_ = permission_f_["allowmatch"] if "allowmatch" in permission_f_ and len(permission_f_["allowmatch"]) > 0 else []
        if op_ in ["read", "update", "upsert", "delete", "action"]:
            match_ += allowmatch_
        input_["match"] = match_

        if op_ in ["update", "upsert", "insert", "action"]:
            if "doc" not in input_:
                raise APIError({"result": False, "msg": "document must be included in the request"})
            decode_ = Crud().decode_crud_input_f(input_)
            if not decode_["result"]:
                raise APIError(decode_)
            input_["doc"] = decode_["doc"]
        elif op_ in ["remove", "clone", "delete"]:
            col_check_ = Crud().inner_collection_f(input_["collection"])
            if not col_check_["result"]:
                raise APIError(col_check_)

        if op_ in ["announce"]:
            tfac_ = input_["tfac"]
            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, "announce")
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
        elif op_ == "purge":
            res_ = Crud().purge_f(input_)
        elif op_ == "charts":
            res_ = Crud().charts_f(input_)
        elif op_ == "announce":
            res_ = Crud().announce_f(input_)
        elif op_ == "collections":
            res_ = Crud().collections_f(input_)
        elif op_ == "collection":
            res_ = Crud().collection_f(input_)
        elif op_ == "parent":
            res_ = Crud().parent_f(input_)
        elif op_ == "link":
            res_ = Crud().link_f(input_)
        elif op_ in ["backup", "restore"]:
            res_ = Crud().dump_f(input_)
        elif op_ == "template":
            res_ = Crud().template_f(input_)
        elif op_ == "saveschema":
            res_ = Crud().saveschema_f(input_)
        elif op_ == "saveview":
            res_ = Crud().saveview_f(input_)
        else:
            raise APIError(f"{op_} is not a supported operation")

        if not res_["result"]:
            raise APIError(res_)

        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 200
        response_.mimetype = "application/json"
        return response_

    except APIError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 400
        response_.mimetype = "application/json"
        return response_

    except AuthError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 401
        response_.mimetype = "application/json"
        return response_

    except SessionError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 403
        response_.mimetype = "application/json"
        return response_

    except Exception as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 500
        response_.mimetype = "application/json"
        return response_


@app.route("/otp", methods=["POST"])
def otp_f():
    """
    docstring is in progress
    """
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

        validate_request_f_ = Security().validate_app_request_f()
        if not validate_request_f_["result"]:
            raise SessionError(validate_request_f_)

        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError({"result": False, "msg": jwt_validate_f_["msg"]})
        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "user session not found"})
        email_ = user_["email"] if "email" in user_ else None

        op_ = request_["op"]
        if op_ == "reset":
            res_ = OTP().reset_otp_f(email_)
        elif op_ == "show":
            res_ = OTP().show_otp_f(email_)
        elif op_ == "request":
            res_ = OTP().request_otp_f(email_)
        elif op_ == "validate":
            res_ = OTP().validate_qr_f(email_, request_)
        else:
            raise APIError(f"operation not supported {op_}")

        if not res_["result"]:
            raise APIError(res_)

        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 200
        response_.mimetype = "application/json"
        return response_

    except SessionError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 403
        response_.mimetype = "application/json"
        return response_

    except APIError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 401
        response_.mimetype = "application/json"
        return response_

    except Exception as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 500
        response_.mimetype = "application/json"
        return response_


@app.route("/auth", methods=["POST"], endpoint="auth")
def auth_f():
    """
    docstring is in progress
    """
    try:
        validate_ = Security().validate_app_request_f()
        if not validate_["result"]:
            raise SessionError(validate_)

        input_ = request.json
        if not input_:
            raise APIError({"result": False, "msg": "input missing"})
        if "op" not in input_:
            raise APIError({"result": False, "msg": "no operation found"})
        op_ = input_["op"]

        user_, auth_, token_ = None, None, None

        if op_ in ["signout", "apikeygen", "apikeyget"]:
            jwt_validate_f_ = Auth().jwt_validate_f()
            if not jwt_validate_f_["result"]:
                raise SessionError(jwt_validate_f_["msg"])
            auth_ = jwt_validate_f_["auth"] if "auth" in jwt_validate_f_ else None
            user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
            if not auth_:
                raise SessionError("account data not found")

        if op_ == "signup":
            res_ = Auth().signup_f()
        elif op_ == "saas":
            res_ = Auth().saas_f()
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
            raise APIError({"result": False, "msg": f"operation not supported {op_}"})

        if not res_["result"]:
            raise AuthError(res_)

        user_ = res_["user"] if res_ and "user" in res_ else None
        token_ = user_["token"] if op_ == "tfac" and "token" in user_ and user_["token"] is not None else None
        saas_ = res_["saas"] if res_ and "saas" in res_ else None
        res_ = {"result": True, "user": user_, "saas": saas_}

        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        if token_ is not None:
            response_.headers.add("A-Auth-Token", token_)
        response_.status_code = 200
        response_.mimetype = "application/json"
        return response_

    except APIError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 400
        response_.mimetype = "application/json"
        return response_

    except SessionError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 403
        response_.mimetype = "application/json"
        return response_

    except AuthError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 401
        response_.mimetype = "application/json"
        return response_

    except Exception as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 500
        response_.mimetype = "application/json"
        return response_


@app.route("/post", methods=["POST"])
def post_f():
    """
    docstring is in progress
    """
    try:
        if not request.headers:
            raise AuthError("no headers provided")

        if not request.json:
            raise APIError("no data provided")

        if not API_OUTPUT_ROWS_LIMIT_:
            raise APIError("no api rows limit defined")

        rh_api_key_ = request.headers.get("x-api-key", None) if "x-api-key" in request.headers and request.headers["x-api-key"] != "" else None
        if not rh_api_key_:
            raise AuthError("no api key provided")

        rh_authorization_ = request.headers.get("Authorization", None) if "Authorization" in request.headers and request.headers["Authorization"] != "" else None
        if not rh_authorization_:
            raise AuthError("no authorization provided")

        auth_parts_ = rh_authorization_.split()
        if len(auth_parts_) == 1:
            raise AuthError("no access token provided")
        if auth_parts_[0].lower() != "bearer":
            raise AuthError("invalid authorization format")
        rh_token_ = auth_parts_[1]

        operation_ = (
            request.headers.get("operation", None)
            if "operation" in request.headers and request.headers["operation"] != ""
            else None
        )
        if not operation_ or operation_ not in ["read", "insert", "update", "upsert", "delete"]:
            raise APIError("invalid operation")

        user_validate_ = Auth().user_validate_by_api_key_f({"api_key": rh_api_key_})
        if not user_validate_["result"]:
            raise AuthError(user_validate_["msg"])

        token_validate_f_ = Misc().user_token_validate_f(rh_token_, operation_)
        if not token_validate_f_["result"]:
            raise AuthError(f"token is not permitted to {operation_}")

        rh_collection_ = (
            request.headers.get("collection", None)
            if "collection" in request.headers and request.headers["collection"] != ""
            else None
        )
        if not rh_collection_:
            raise APIError("no collection found")
        collection_f_ = Crud().inner_collection_f(rh_collection_)
        if not collection_f_["result"]:
            raise AuthError(collection_f_["msg"])

        collection_ = (
            collection_f_["collection"] if "collection" in collection_f_ else None
        )
        if not collection_:
            raise APIError("collection not found")
        structure_ = (
            collection_["col_structure"] if "col_structure" in collection_ else None
        )
        if not collection_:
            raise APIError("structure not found")

        properties_ = structure_["properties"] if "properties" in structure_ else None
        if not properties_:
            raise APIError("properties not found")

        unique_ = structure_["unique"] if "unique" in structure_ else []

        is_crud_ = rh_collection_[:1] != "_"
        collection_data_ = f"{rh_collection_}_data" if is_crud_ else rh_collection_

        body_ = request.json
        type_ = str(type(body_))

        if type_ != "<class 'list'>":
            if operation_ == "read":
                body_ = [body_]
            else:
                raise APIError("data must be in an array")

        output_ = []
        count_ = 0

        session_client_ = MongoClient(Mongo().connstr)
        session_db_ = session_client_[MONGO_DB_]
        session_ = session_client_.start_session()
        session_.start_transaction()

        if operation_ == "read":
            for item_ in body_:
                cursor_ = session_db_[collection_data_].find(item_)
                docs_ = (
                    json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []
                )
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
                    raise APIError(f"at leat one unique field must be provided for {operation_}")
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
                if operation_ == "upsert":
                    session_db_[collection_data_].update_many(
                        filter__,
                        {"$set": doc__, "$inc": {"_modified_count": 1}},
                        upsert=True,
                        session=session_,
                    )
                if operation_ == "update":
                    session_db_[collection_data_].update_many(
                        filter__,
                        {"$set": doc__, "$inc": {"_modified_count": 1}},
                        session=session_,
                    )
                elif operation_ == "insert":
                    session_db_[collection_data_].insert_one(doc__, session=session_)
                elif operation_ == "delete":
                    session_db_[collection_data_].delete_many(
                        filter__, session=session_
                    )
                count_ += 1
                if count_ >= int(API_OUTPUT_ROWS_LIMIT_):
                    break
                output_.append(item_)

        log_ = Misc().log_f(
            {
                "type": "Info",
                "collection": rh_collection_,
                "op": f"API {operation_}",
                "user": "API",
                "document": body_,
            }
        )
        if not log_["result"]:
            raise APIError(log_["msg"])

        response_ = json.loads(
            JSONEncoder().encode(
                {
                    "collection": rh_collection_,
                    "operation": operation_,
                    "count": count_,
                    "output": output_,
                }
            )
        )

        session_.commit_transaction()
        session_client_.close()

        return (
            json.dumps(
                {"result": True, "response": response_},
                default=json_util.default,
                ensure_ascii=False,
                sort_keys=False,
            ),
            200,
            Security().header_simple_f(),
        )

    except AuthError as exc:
        return {"result": False, "response": str(exc), "status": 401}

    except APIError as exc:
        return {"result": False, "response": str(exc), "status": 400}

    except Exception as exc:
        return {"result": False, "response": str(exc), "status": 500}

    finally:
        if session_:
            session_.abort_transaction()


@app.route("/get/dump", methods=["POST"])
def get_dump_f():
    """
    docstring is in progress
    """
    try:
        validate_ = Security().validate_app_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "validation error")

        input_ = request.json
        user_ = input_["user"] if "user" in input_ else None
        if not user_:
            raise APIError("invalid credentials")

        email_ = user_["email"] if "email" in user_ else None
        token_ = user_["token"] if "token" in user_ else None
        validate_ = Auth().user_validate_by_basic_auth_f({"userid": email_, "token": token_})
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "request not validated")

        id_ = bleach.clean(input_["id"])
        if not id_:
            raise APIError("dump not selected")

        file_ = f"{id_}.gz"
        directory_ = "/dump"

        return send_from_directory(directory=directory_, path=file_, as_attachment=True), 200, Security().header_simple_f()

    except AuthError as exc:
        return {"msg": str(exc), "status": 401}

    except APIError as exc:
        return {"msg": str(exc), "status": 400}

    except Exception as exc:
        return {"msg": str(exc), "status": 500}


@app.route("/get/view/<string:id_>", methods=["GET"])
def get_data_f(id_):
    """
    docstring is in progress
    """
    try:
        if not request.headers:
            raise AuthError({"result": False, "msg": "no header provided"})

        id_ = bleach.clean(id_)

        api_token_ = request.headers["X-Api-Token"] if "X-Api-Token" in request.headers and request.headers["X-Api-Token"] != "" else None
        if api_token_:
            api_token_validate_f_ = Misc().api_token_validate_f(api_token_)
            if not api_token_validate_f_["result"]:
                raise AuthError(api_token_validate_f_)
        else:
            arg_ = request.args.get("k", default=None, type=str)
            if not arg_:
                raise AuthError({"result": False, "msg": "apikey is missing"})
            api_key_ = request.headers["X-Api-Key"] if "X-Api-Key" in request.headers and request.headers["X-Api-Key"] != "" else arg_
            user_validate_ = Auth().user_validate_by_api_key_f({"api_key": api_key_})
            if not user_validate_["result"]:
                user_validate_ = Auth().user_validate_by_api_key_f({"api_key": arg_})
                if not user_validate_["result"]:
                    raise AuthError(user_validate_)
            user_ = user_validate_["user"] if "user" in user_validate_ else None
            if not user_:
                raise AuthError({"result": False, "msg": "user not found for view"})

        generate_view_data_f_ = Crud().get_view_data_f(user_, id_, "external")
        if not generate_view_data_f_["result"]:
            raise APIError(generate_view_data_f_)

        res_ = generate_view_data_f_["data"] if generate_view_data_f_ and "data" in generate_view_data_f_ else []
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 200
        response_.mimetype = "application/json"
        return response_

    except AuthError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 401
        response_.mimetype = "application/json"
        return response_

    except APIError as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 400
        response_.mimetype = "application/json"
        return response_

    except Exception as exc_:
        res_ = ast.literal_eval(str(exc_))
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.status_code = 500
        response_.mimetype = "application/json"
        return response_


if __name__ == "__main__":
    print = partial(print, flush=True)
    Schedular().main_f()
    app.run(host="0.0.0.0", port=80, debug=False)
