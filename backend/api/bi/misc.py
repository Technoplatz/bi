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

Helpers: client ip resolution, logging, notifications, formula and pipeline validation.
"""

import os
import secrets
import sys
import re
import json
import ipaddress
from datetime import datetime
import boto3
import botocore
import pymongo
import bleach
import jwt
import numexpr as ne
from flask import request
from markupsafe import escape
import requests

from bi import config as cfg
from bi.db import Mongo
from bi.errors import APIError


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
            "caseType",
            "query",
            "selection",
            "reminder",
            "note",
            "masked",
        ]

    def get_now_f(self):
        """
        docstring is in progress
        """
        return datetime.now()

    def s3_f(self, input_):
        """
        docstring is in progress
        """
        try:
            if not cfg.API_S3_ACTIVE_:
                return {"result": True}

            op_ = input_["op"]
            localfile_ = input_["localfile"]
            object_ = input_["object"]
            s3_ = boto3.client(
                "s3",
                region_name=cfg.API_S3_REGION_,
                aws_access_key_id=cfg.API_S3_KEY_ID_,
                aws_secret_access_key=cfg.API_S3_KEY_,
            )
            try:
                (
                    s3_.download_file(cfg.API_S3_BUCKET_NAME_, object_, localfile_)
                    if op_
                    in [
                        "dumpr",
                        "dumpd",
                    ]
                    else s3_.upload_file(localfile_, cfg.API_S3_BUCKET_NAME_, object_)
                )
            except botocore.exceptions.ClientError as exc__:
                msg_ = str(exc__)
                if exc__.response["Error"]["Code"] == "404":
                    msg_ = "object does not exist"
                return {"result": False, "msg": msg_}

            s3_.close()
            return {"result": True}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return {"result": False, "msg": str(exc__)}

    def tools_config_f(self):
        """
        writes the credentials for mongodump and mongorestore into a private config file so that
        neither the connection string nor the certificate key password appears on a command line;
        the caller removes the file with tools_config_remove_f when the tool has finished
        """
        connstr_ = f"mongodb://{cfg.MONGO_USERNAME_}:{cfg.MONGO_PASSWORD_}@{cfg.MONGO_HOST0_}:{cfg.MONGO_PORT0_},{cfg.MONGO_HOST1_}:{cfg.MONGO_PORT1_},{cfg.MONGO_HOST2_}:{cfg.MONGO_PORT2_}"
        path_ = os.path.join(cfg.API_TEMPFILE_PATH_, f".mongotools-{secrets.token_hex(8)}.yml")
        with open(os.open(path_, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as fh_:
            fh_.write(f"uri: {json.dumps(connstr_)}\n")
            if cfg.MONGO_TLS_CERT_KEYFILE_PASSWORD_:
                fh_.write(f"sslPEMKeyPassword: {json.dumps(cfg.MONGO_TLS_CERT_KEYFILE_PASSWORD_)}\n")
        return path_

    def tools_config_remove_f(self, path_):
        """
        removes a config file written by tools_config_f
        """
        try:
            if path_ and os.path.exists(path_):
                os.remove(path_)
        except OSError:
            pass

    def commands_f(self, command_, input_):
        """
        argument lists for mongodump and mongorestore; secrets come from the config file
        """
        type_ = input_["type"] if "type" in input_ else None
        loc_ = input_["loc"] if "loc" in input_ else None
        config_ = input_["config"] if "config" in input_ else None
        common_ = [
            f"--config={config_}",
            f"--db={cfg.MONGO_DB_}",
            f"--authenticationDatabase={cfg.MONGO_AUTH_DB_}",
            "--ssl",
            f"--sslPEMKeyFile={cfg.MONGO_TLS_CERT_KEYFILE_}",
            f"--sslCAFile={cfg.MONGO_TLS_CA_KEYFILE_}",
        ] + (["--tlsInsecure"] if cfg.MONGO_TLS_ALLOW_INVALID_CERTIFICATES_ else []) + [
            f"--{type_}",
            f"--archive={loc_}",
            "--quiet",
        ]
        commands_ = {
            "mongorestore": common_ + ["--drop"],
            "mongodump": common_,
        }
        return commands_[command_] if command_ in commands_ else []

    def jwt_proc_f(self, endecode_, token_, jwt_secret_, payload_, header_):
        """
        docstring is in progress
        """
        try:
            alg_ = "HS256"
            if endecode_ == "decode":
                if not jwt_secret_:
                    raise jwt.InvalidTokenError("no session secret")
                # expected claims are literals, never taken from the token itself
                claims_ = jwt.decode(
                    token_,
                    jwt_secret_,
                    algorithms=[alg_],
                    audience=cfg.JWT_AUDIENCE_,
                    issuer=cfg.JWT_ISSUER_,
                    options={"require": ["exp"]},
                )
                if claims_.get("sub") != cfg.JWT_SUBJECT_:
                    raise jwt.InvalidTokenError("invalid subject")
            elif endecode_ == "encode":
                # time claims are produced as naive local datetimes; make them timezone-aware so the
                # encoded epoch seconds are correct utc (otherwise iat sits in the future and exp drifts)
                payload_ = dict(payload_)
                for claim_ in ("exp", "iat", "nbf"):
                    value_ = payload_.get(claim_)
                    if isinstance(value_, datetime) and value_.tzinfo is None:
                        payload_[claim_] = value_.astimezone()
                claims_ = jwt.encode(
                    payload_, jwt_secret_, algorithm=alg_, headers=header_
                )

            return {"result": True, "jwt": claims_}

        except jwt.ExpiredSignatureError as exc__:
            return {"result": False, "msg": str(exc__), "exc": str(exc__)}

        except jwt.InvalidTokenError as exc__:
            return {"result": False, "msg": str(exc__), "exc": str(exc__)}

        except Exception as exc__:
            return {"result": False, "msg": str(exc__), "exc": str(exc__)}

    def post_notification_f(self, notification_):
        """
        docstring is in progress
        """
        res_ = None
        try:
            ip_ = self.get_client_ip_f()
            exc_type_, exc_obj_, exc_tb_ = sys.exc_info()
            file_ = os.path.split(exc_tb_.tb_frame.f_code.co_filename)[1]
            line_ = exc_tb_.tb_lineno
            notification_str_ = f"IP: {ip_}, DOMAIN: {cfg.DOMAIN_}, DATE: {self.get_now_f()}, FILE: {file_}, LINE: {line_}, OBJ: {str(exc_obj_)}, EXCEPTION: {notification_}"
            res_ = notification_str_
            if cfg.NOTIFICATION_PUSH_URL_:
                response_ = requests.post(
                    cfg.NOTIFICATION_PUSH_URL_,
                    json.dumps({"text": str(notification_str_)}),
                    timeout=10,
                )
                if response_.status_code != 200:
                    res_ = response_.content
                    cfg.PRINT_("!!! TBACK", res_)

        except Exception as exc__:
            res_ = str(exc__)

        finally:
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

        self.post_notification_f(msg_)
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

    def ip_in_networks_f(self, ip_, networks_):
        """
        true when ip_ belongs to one of the cidr networks in networks_
        """
        try:
            addr_ = ipaddress.ip_address(str(ip_).strip())
        except ValueError:
            return False
        for net_ in networks_:
            try:
                if addr_ in ipaddress.ip_network(str(net_).strip(), strict=False):
                    return True
            except ValueError:
                continue
        return False

    def get_client_ip_f(self):
        """
        resolves the real client ip
        walks the X-Forwarded-For chain from the right, skipping trusted local proxies (traefik),
        and honours cf-connecting-ip only when the peer that reached the proxy is a cloudflare edge
        """
        if not request:
            return "0.0.0.0"
        remote_ = request.remote_addr or "0.0.0.0"
        forwarded_ = request.headers.get("X-Forwarded-For", "") or ""
        chain_ = [ip_.strip() for ip_ in forwarded_.split(",") if ip_.strip()] + [remote_]
        peer_ = chain_[0]
        for hop_ in reversed(chain_):
            if not self.ip_in_networks_f(hop_, cfg.API_TRUSTED_PROXIES_):
                peer_ = hop_
                break
        cf_ip_ = request.headers.get("cf-connecting-ip", None)
        if cf_ip_ and self.ip_in_networks_f(peer_, cfg.API_CLOUDFLARE_IPS_):
            try:
                return str(ipaddress.ip_address(cf_ip_.strip()))
            except ValueError:
                return peer_
        return peer_

    def age_minutes_f(self, dt_):
        """
        minutes elapsed since dt_ (tolerates tz-aware values read back from mongo)
        """
        if dt_ is None:
            return None
        if getattr(dt_, "tzinfo", None) is not None:
            dt_ = dt_.replace(tzinfo=None)
        return (datetime.now() - dt_).total_seconds() / 60

    def regex_fragment_f(self, value_):
        """
        M-2: client values used inside $regex are escaped and length-capped so they can neither
        change the pattern nor build catastrophic expressions
        """
        return re.escape(str(value_)[:cfg.API_FILTER_VALUE_MAX_LEN_])

    def neutralize_cells_f(self, frame_):
        """
        M-3: spreadsheet clients interpret cells starting with = + - @ or a tab/cr as formulas;
        returns a copy of the frame where such text cells are prefixed with an apostrophe
        """
        out_ = frame_.copy()
        for column_ in out_.columns:
            if out_[column_].dtype == object:
                out_[column_] = out_[column_].map(
                    lambda v_: ("'" + v_) if isinstance(v_, str) and v_[:1] in ("=", "+", "-", "@", "\t", "\r") else v_
                )
        return out_

    def scan_forbidden_ops_f(self, node_):
        """
        returns the first forbidden mongodb operator found anywhere in node_, else None
        """
        if isinstance(node_, dict):
            for key_, value_ in node_.items():
                if isinstance(key_, str) and key_ in cfg.FORBIDDEN_AGG_OPS_:
                    return key_
                found_ = self.scan_forbidden_ops_f(value_)
                if found_:
                    return found_
        elif isinstance(node_, (list, tuple)):
            for item_ in node_:
                found_ = self.scan_forbidden_ops_f(item_)
                if found_:
                    return found_
        return None

    def validate_pipeline_f(self, pipeline_):
        """
        validates a user or admin supplied aggregation pipeline against the stage allowlist
        """
        if not isinstance(pipeline_, list):
            return {"result": False, "msg": "aggregation must be a list of stages"}
        for ix_, stage_ in enumerate(pipeline_):
            if not isinstance(stage_, dict) or len(stage_) != 1:
                return {"result": False, "msg": f"invalid aggregation stage at index {ix_}"}
            name_ = list(stage_.keys())[0]
            if name_ not in cfg.ALLOWED_AGG_STAGES_:
                return {"result": False, "msg": f"aggregation stage is not allowed: {name_}"}
        found_ = self.scan_forbidden_ops_f(pipeline_)
        if found_:
            return {"result": False, "msg": f"aggregation operator is not allowed: {found_}"}
        return {"result": True}

    def get_except_underdashes(self):
        """
        docstring is in progress
        """
        return ["_tags"]

    def in_admin_ips_f(self):
        """
        docstring is in progress
        """
        ip_ = str(Misc().get_client_ip_f())
        return ip_ in cfg.API_ADMIN_IPS_

    def properties_cleaner_f(self, properties_, required_):
        """
        docstring is in progress
        """
        properties_new_ = {}
        for property_ in properties_:
            dict_ = {}
            properties_property_ = properties_[property_]
            for field_ in properties_property_:
                if field_ not in self.xtra_props_:
                    if field_ == "items":
                        items_ = properties_property_["items"]
                        if "properties" in items_:
                            items_properties_ = items_["properties"]
                            properties_new__ = self.properties_cleaner_f(items_properties_, required_)
                            properties_property_["items"]["properties"] = properties_new__
                    if field_ == "bsonType":
                        if required_ and property_ in required_:
                            dict_[field_] = properties_property_[field_]
                        else:
                            if properties_property_[field_] == "object":
                                dict_[field_] = [properties_property_[field_], "array", "null"]
                            elif properties_property_[field_] == "string":
                                if ("minLength" in properties_property_ and properties_property_["minLength"] == 0) or \
                                        ("pattern" in properties_property_ and "{0," in properties_property_["pattern"]):
                                    dict_[field_] = ["string", "null"]
                                else:
                                    dict_[field_] = properties_property_[field_]
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
            personalizations_, to_ = [], []
            users_ = (
                Mongo()
                .db_["_user"]
                .find({"usr_enabled": True, "_tags": {"$elemMatch": {"$in": tags_}}})
            )
            for member_ in users_:
                if member_["usr_id"] not in to_:
                    to_.append(member_["usr_id"])
                    personalizations_.append(
                        {"email": member_["usr_id"],
                            "name": member_["usr_name"]}
                    )

            return {"result": True, "personalizations": personalizations_}

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
                kav_key_ = (
                    kav_["kav_key"]
                    if "kav_key" in kav_ and kav_["kav_key"] is not None
                    else None
                )
                kav_as_ = (
                    kav_["kav_as"]
                    if "kav_as" in kav_ and kav_["kav_as"] is not None
                    else None
                )
                kav_value_ = (
                    kav_["kav_value"]
                    if "kav_value" in kav_ and kav_["kav_value"] is not None
                    else None
                )
                if not kav_key_ or not kav_value_ or not kav_as_:
                    raise APIError("missing kv keys")
                setto__ = (
                    datetime.strptime(kav_value_[:10], "%Y-%m-%d")
                    if kav_as_ == "date"
                    else (
                        bool(kav_value_)
                        if kav_as_ == "bool"
                        else (
                            float(kav_value_)
                            if kav_as_ in ["float", "number", "decimal"]
                            else (
                                int(kav_value_)
                                if kav_as_ == "int"
                                else (
                                    str(kav_value_)
                                    if kav_as_ == "string"
                                    else str(kav_value_)
                                )
                            )
                        )
                    )
                )
            elif setto_[:1] == "=":
                decimals_ = (
                    int(properties_[key_]["decimals"])
                    if "decimals" in properties_[key_]
                    and int(properties_[key_]["decimals"]) >= 0
                    else None
                )
                forward_ = setto_[1:]
                if not forward_:
                    raise APIError("missing = value")
                formula_ = str(forward_).replace(" ", "")
                formula_parts_ = re.split("([+-/*()])", formula_)
                for part_ in formula_parts_:
                    val_ = self.set_value_f(key_, part_, properties_, data_)
                    formula_ = formula_.replace(part_, val_)
                setto__ = (
                    round(ne.evaluate(formula_), decimals_)
                    if decimals_
                    else ne.evaluate(formula_)
                )
            else:
                setto__ = setto_

            return setto__

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def clean_f(self, data_):
        """
        docstring is in progress
        """
        try:
            if not data_:
                return None

            if isinstance(data_, str):
                data_ = escape(data_.strip())

            return bleach.clean(data_)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)
