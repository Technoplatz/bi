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
along with this program. If not, see https://www.gnu.org/licenses.

If your software can interact with users remotely through a computer
network, you should also make sure that it provides a way for users to
get its source.  For example, if your program is a web application, its
interface could display a "collection" link that leads users to an archive
of the code.  There are many ways you could offer source, and different
solutions will be better for different programs; see section 13 for the
specific requirements.

You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU AGPL, see
https://www.gnu.org/licenses.
"""

import os
import sys
import re
import asyncio
import smtplib
import json
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from functools import partial
from subprocess import call
from bson.objectid import ObjectId
from get_docker_secret import get_docker_secret
import pytz
import pymongo
import requests


class AppException(BaseException):
    """
    docstring is in progress
    """


class PassException(BaseException):
    """
    docstring is in progress
    """


class Trigger():
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        print_(">>> init started")
        self.operations_ = ["insert", "update", "replace", "delete"]
        self.pipeline_ = [{"$match": {"operationType": {"$in": self.operations_}}}]
        self.numerics_ = ["number", "int", "float", "decimal"]
        self.groupbys_ = ["sum", "count", "mean", "std", "var"]
        self.connstr_ = f"mongodb://{mongo_username_}:{mongo_password_}@{mongo_host0_}:{mongo_port0_},{mongo_host1_}:{mongo_port1_},{mongo_host2_}:{mongo_port2_}/{mongo_db_}?authSource={mngo_auth_db_}&replicaSet={mongo_rs_}&tls={mongo_tls_}&tlsCertificateKeyFile={mongo_tls_cert_keyfile_}&tlsAllowInvalidCertificates={mongo_tls_allow_invalid_certificates_}&tlsCertificateKeyFilePassword={mongo_tls_cert_keyfile_password_}&retryWrites={mongo_retry_writes_}"
        self.client = pymongo.MongoClient(self.connstr_)
        self.db_ = self.client[mongo_db_]
        self.counter_ = 0
        self.repeater_ = 0

        refresh_properties_f_ = self.refresh_properties_f()
        if not refresh_properties_f_["result"]:
            raise AppException(refresh_properties_f_["exc"])

        refresh_triggers_f_ = self.refresh_triggers_f()
        if not refresh_triggers_f_["result"]:
            raise AppException(refresh_triggers_f_["exc"])

        refresh_fetchers_f_ = self.refresh_fetchers_f()
        if not refresh_fetchers_f_["result"]:
            raise AppException(refresh_fetchers_f_["exc"])

        print_(">>> init ended")

    def exception_passed_f(self):
        """
        docstring is in progress
        """
        return True

    def exception_printed_f(self, exc_):
        """
        docstring is in progress
        """
        line_no_ = exc_.__traceback__.tb_lineno if hasattr(exc_, "__traceback__") and hasattr(exc_.__traceback__, "tb_lineno") else None
        name_ = type(exc_).__name__ if hasattr(type(exc_), "__name__") else "Exception"
        print_(f"!!! worker exception type: {name_}, line: {line_no_}:", str(exc_))
        return True

    def exception_reported_f(self, exc_):
        """
        docstring is in progress
        """
        line_no_ = exc_.__traceback__.tb_lineno if hasattr(exc_, "__traceback__") and hasattr(exc_.__traceback__, "tb_lineno") else None
        name_ = type(exc_).__name__ if hasattr(type(exc_), "__name__") else "Exception"
        print_(f"!!! worker error type: {name_}, line: {line_no_}:", str(exc_))
        if notification_slack_hook_url_:
            exc_type_, exc_obj_, exc_tb_ = sys.exc_info()
            file_ = os.path.split(exc_tb_.tb_frame.f_code.co_filename)[1]
            line_ = exc_tb_.tb_lineno
            exception_ = str(exc_)
            notification_str_ = f"TYPE: {exc_type_}, FILE: {file_}, OBJ: {exc_obj_}, LINE: {line_}, EXCEPTION: {exception_}"
            resp_ = requests.post(notification_slack_hook_url_, json.dumps({"text": str(notification_str_)}), timeout=10)
            if resp_.status_code != 200:
                print_("*** notification error", resp_)

        return True

    def get_now_f(self):
        """
        docstring is in progress
        """
        return datetime.now()

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

    def refresh_properties_f(self):
        """
        docstring is in progress
        """
        try:
            print_(">>> getting collections structure...")
            self.properties_ = {}
            cursor_ = self.db_["_collection"].aggregate([{
                "$match": {"$and": [{"col_structure.properties": {"$exists": True, "$ne": None}}]}
            }])
            for item_ in cursor_:
                self.properties_[item_["col_id"]] = item_["col_structure"]["properties"] if "properties" in item_["col_structure"] else None

            print_(">>> structure refreshed")

            return {"result": True}

        except pymongo.errors.PyMongoError as exc_:
            print_("!!! refresher mongo error")
            return {"result": False, "msg": str(exc_)}

        except AppException as exc_:
            print_("!!! refresher app exception")
            return {"result": False, "msg": str(exc_)}

        except Exception as exc_:
            print_("!!! refresher exception")
            return {"result": False, "msg": str(exc_)}

    def refresh_triggers_f(self):
        """
        docstring is in progress
        """
        try:
            print_(">>> getting triggers...")
            self.triggers_ = []
            cursor_ = self.db_["_collection"].aggregate([{"$match": {"col_structure.triggers": {"$elemMatch": {"enabled": True}}}}])
            for item_ in cursor_:
                for trigger_ in item_["col_structure"]["triggers"]:
                    for cluster_ in trigger_["targets"]:
                        self.triggers_.append({
                            "source": item_["col_id"],
                            "target": cluster_["collection"],
                            "operations": trigger_["operations"] if "operations" in trigger_ and len(trigger_["operations"]) > 0 else [],
                            "changes": trigger_["changes"] if "changes" in trigger_ and len(trigger_["changes"]) > 0 else [],
                            "on_changes_all": "on_changes_all" in trigger_ and trigger_["on_changes_all"] is True,
                            "match": cluster_["match"] if "match" in cluster_ and len(cluster_["match"]) > 0 else [],
                            "filter": cluster_["filter"] if "filter" in cluster_ and len(cluster_["filter"]) > 0 else [],
                            "set": cluster_["set"] if "set" in cluster_ and len(cluster_["set"]) > 0 else [],
                            "upsert": "upsert" in cluster_ and cluster_["upsert"] is True,
                            "notification": cluster_["notification"] if "notification" in cluster_ else None,
                        })

            if not self.triggers_:
                raise PassException("!!! no trigger found - passed")

            print_(">>> triggers refreshed")

            return {"result": True}

        except PassException as exc_:
            self.exception_passed_f()
            return {"result": True, "msg": str(exc_)}

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return {"result": False, "msg": str(exc_)}

    def refresh_fetchers_f(self):
        """
        docstring is in progress
        """
        try:
            print_(">>> getting fetchers...")
            self.fetchers_ = []
            cursor_ = self.db_["_collection"].aggregate([{"$match": {"col_structure.fetchers": {"$elemMatch": {"enabled": True}}}}])
            for item_ in cursor_:
                if "col_structure" not in item_:
                    continue
                if "fetchers" not in item_["col_structure"]:
                    continue
                for fetcher_ in item_["col_structure"]["fetchers"]:
                    self.fetchers_.append({
                        "collection": fetcher_["collection"],
                        "match": fetcher_["match"],
                        "get": fetcher_["get"],
                        "set": fetcher_["set"]
                    })

            if not self.fetchers_:
                raise PassException("!!! no fetcher found - passed")

            print_(">>> fetchers refreshed", self.fetchers_)
            return {"result": True}

        except PassException as exc_:
            self.exception_passed_f()
            return {"result": True, "msg": str(exc_)}

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return {"result": False, "msg": str(exc_)}

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
            if properties_:
                for mat_ in match_:
                    if mat_["key"] and mat_["op"] and mat_["key"] in properties_:
                        fres_ = None
                        typ = properties_[mat_["key"]]["bsonType"] if mat_["key"] in properties_ else "string"

                        value_ = mat_["value"]
                        if data_ and value_ in data_ and data_[value_] is not None:
                            value_ = data_[value_]

                        if mat_["op"] in ["eq", "contains"]:
                            if typ in ["number", "int", "decimal"]:
                                fres_ = float(value_)
                            elif typ == "bool":
                                fres_ = bool(value_)
                            elif typ == "date":
                                fres_ = datetime.strptime(value_[:10], "%Y-%m-%d")
                            else:
                                fres_ = {"$regex": value_, "$options": "i"} if value_ else {"$regex": "", "$options": "i"}
                        elif mat_["op"] in ["ne", "nc"]:
                            if typ in ["number", "decimal"]:
                                fres_ = {"$not": {"$eq": float(value_)}}
                            elif typ == "bool":
                                fres_ = {"$not": {"$eq": bool(value_)}}
                            elif typ == "date":
                                fres_ = {"$not": {"$eq": datetime.strptime(value_[:10], "%Y-%m-%d")}}
                            else:
                                fres_ = {"$not": {"$regex": value_, "$options": "i"}} if value_ else {"$not": {"$regex": "", "$options": "i"}}
                        elif mat_["op"] in ["in", "nin"]:
                            separated_ = re.split(",", value_)
                            list_ = [s.strip() for s in separated_] if mat_["key"] != "_id" else [ObjectId(s.strip()) for s in separated_]
                            if mat_["op"] == "in":
                                fres_ = {"$in": list_ if typ != "number" else list(map(float, list_))}
                            else:
                                fres_ = {"$nin": list_ if typ != "number" else list(map(float, list_))}
                        elif mat_["op"] == "gt":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$gt": float(value_)}
                            elif typ == "date":
                                fres_ = {"$gt": datetime.strptime(value_[:10], "%Y-%m-%d")}
                            else:
                                fres_ = {"$gt": value_}
                        elif mat_["op"] == "gte":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$gte": float(value_)}
                            elif typ == "date":
                                fres_ = {"$gte": datetime.strptime(value_[:10], "%Y-%m-%d")}
                            else:
                                fres_ = {"$gte": value_}
                        elif mat_["op"] == "lt":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$lt": float(value_)}
                            elif typ == "date":
                                fres_ = {"$lt": datetime.strptime(value_[:10], "%Y-%m-%d")}
                            else:
                                fres_ = {"$lt": value_}
                        elif mat_["op"] == "lte":
                            if typ in ["number", "decimal"]:
                                fres_ = {"$lte": float(value_)}
                            elif typ == "date":
                                fres_ = {"$lte": datetime.strptime(value_[:10], "%Y-%m-%d")}
                            else:
                                fres_ = {"$lte": value_}
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
            self.exception_printed_f(exc_)
            return None

    def aggregater_sum_f(self, coll_, filter_, field_):
        """
        docstring is in progress
        """
        try:
            sum_ = None
            match_ = filter_ if filter_ else {}
            aggregate_ = self.db_[coll_].aggregate([{"$match": match_}, {"$group": {"_id": None, "sum": {"$sum": f"${field_}"}}}, {"$project": {"_id": 0}}])
            for doc_ in aggregate_:
                sum_ = doc_["sum"] if "sum" in doc_ else None
            return sum_

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)
            return 0

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return 0

    def aggregater_count_f(self, coll_, filter_):
        """
        docstring is in progress
        """
        try:
            count_ = None
            match_ = filter_ if filter_ else {}
            aggregate_ = self.db_[coll_].aggregate([{"$match": match_}, {"$group": {"_id": None, "count": {"$sum": 1}}}, {"$project": {"_id": 0}}])
            for doc_ in aggregate_:
                count_ = doc_["count"] if "count" in doc_ else None
            return count_

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)
            return 0

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return 0

    def prefix_remove_f(self, input_, prfxs_):
        """
        gets the collection and the fields that affected by the change stream.
        """
        prfx_ = prfxs_[0] if prfxs_ and len(prfxs_) > 0 else prfxs_
        return input_.removeprefix(prfx_)

    def get_users_from_tags_f(self, tags_):
        """
        docstring is in progress
        """
        try:
            personalizations_ = []
            to_ = []
            users_ = self.db_["_user"].find({"usr_enabled": True, "_tags": {"$elemMatch": {"$in": tags_}}})
            if users_:
                for member_ in users_:
                    if member_["usr_id"] not in to_:
                        to_.append(member_["usr_id"])
                        personalizations_.append({"email": member_["usr_id"], "name": member_["usr_name"]})

            return {"result": True, "to": personalizations_}

        except pymongo.errors.PyMongoError as exc_:
            return {"result": False, "to": personalizations_, "msg": str(exc_)}

        except Exception as exc_:
            return {"result": False, "to": personalizations_, "msg": str(exc_)}

    def send_email_smtp_f(self, msg):
        """
        docstring is in progress
        """
        try:
            company_name_ = os.environ.get("COMPANY_NAME") if os.environ.get("COMPANY_NAME") else "Technoplatz BI"
            smtp_server_ = os.environ.get("SMTP_SERVER")
            smtp_port_ = os.environ.get("SMTP_PORT")
            smtp_userid_ = os.environ.get("SMTP_USERID")
            smtp_password_ = os.environ.get("SMTP_PASSWORD")
            from_email_ = os.environ.get("FROM_EMAIL")
            disclaimer_ = f"<p>Sincerely,</p><p>{company_name_}</p><p>PLEASE DO NOT REPLY THIS EMAIL<br />--------------------------------<br />This email and its attachments transmitted with it may contain private, confidential or prohibited information. If you are not the intended recipient of this mail, you are hereby notified that storing, copying, using or forwarding of any part of the contents is strictly prohibited. Please completely delete it from your system and notify the sender. {company_name_} makes no warranty with regard to the accuracy or integrity of this mail and its transmission.</p>"
            email_from_ = f"{company_name_} <{from_email_}>"
            html_ = f"{msg['html']} {disclaimer_}"
            server_ = smtplib.SMTP_SSL(smtp_server_, smtp_port_)
            server_.ehlo()
            server_.login(smtp_userid_, smtp_password_)
            files_ = msg["files"] if "files" in msg and len(msg["files"]) > 0 else []

            message_ = MIMEMultipart()
            message_["From"] = email_from_
            message_["Subject"] = msg["subject"]
            message_.attach(MIMEText(html_, "html"))

            for file_ in files_:
                filename_ = file_["filename"]
                with open(f"{filename_}", "rb") as attachment_:
                    part_ = MIMEBase("application", "octet-stream")
                    part_.set_payload(attachment_.read())
                encoders.encode_base64(part_)
                filename_ = filename_.replace("/docs/", "").replace("/cron/", "")
                part_.add_header("Content-Disposition", f"attachment; filename= {filename_}")
                message_.attach(part_)

            recipients_ = []
            recipients_str_ = ""
            for recipient_ in msg["personalizations"]["to"]:
                email_to_ = f"{recipient_['name']} <{recipient_['email']}>" if recipient_["name"] and "name" in recipient_ else recipient_["email"]
                recipients_str_ += email_to_ if recipients_str_ == "" else f", {email_to_}"
                recipients_.append(recipient_["email"])

            message_["To"] = recipients_str_
            server_.sendmail(email_from_, recipients_, message_.as_string())
            server_.close()

            return {"result": True}

        except smtplib.SMTPResponseException as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except smtplib.SMTPServerDisconnected as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return {"result": False, "msg": str(exc_)}

    async def worker_fetchers_f(self, params_):
        """
        gets the collection and the fields that affected by the change stream.
        """
        try:
            _id = params_["id"] if "id" in params_ else None
            collection_ = params_["collection"] if "collection" in params_ else None
            changed_ = params_["changed"] if "changed" in params_ else None
            if None in [_id, collection_, changed_]:
                raise PassException("!!! no changed or _id found")

            fetchers_ = self.fetchers_ if self.fetchers_ and len(self.fetchers_) > 0 else []
            if not fetchers_:
                raise PassException("!!! no fetcher found for")

            changed_doc_ = self.db_[collection_].find_one({"_id": _id})
            if not changed_doc_:
                raise PassException(f"!!! no changed document found {_id}")

            for fetcher_ in fetchers_:
                fetcher_col_id_ = fetcher_["collection"] if "collection" in fetcher_ and fetcher_["collection"] is not None else None
                fetcher_match_ = fetcher_["match"] if "match" in fetcher_ and len(fetcher_["match"]) > 0 else None
                fetcher_get_ = fetcher_["get"] if "get" in fetcher_ and fetcher_["get"] is not None else None
                fetcher_set_ = fetcher_["set"] if "set" in fetcher_ and fetcher_["set"] is not None else None
                if None in [fetcher_col_id_, fetcher_match_, fetcher_get_, fetcher_set_]:
                    continue

                document_ = self.db_["_collection"].find_one({"col_id": fetcher_col_id_})
                if not document_:
                    print_(f"!!! no fetcher document found: {fetcher_col_id_}")
                    continue

                structure_ = document_["col_structure"] if "col_structure" in document_ else None
                if not structure_:
                    print_(f"!!! no fetcher structure found: {fetcher_col_id_}")
                    continue

                properties_ = structure_["properties"] if "properties" in structure_ else None
                if not properties_:
                    print_(f"!!! no fetcher properties found: {fetcher_col_id_}")
                    continue

                match_new_ = []
                for fm_ in fetcher_match_:
                    if fm_["value"] in changed_doc_:
                        match_new_.append({"key": fm_["key"], "op": fm_["op"], "value": changed_doc_[fm_["value"]]})

                if not match_new_:
                    continue

                get_filtered_f_ = self.get_filtered_f({
                    "match": match_new_,
                    "properties": properties_
                })

                fetcher_document_ = self.db_[f"{fetcher_col_id_}_data"].find_one(get_filtered_f_)
                if not fetcher_document_:
                    print_(f"!!! not target document found for {fetcher_col_id_}: {get_filtered_f_}")
                    continue

                get_val_ = fetcher_document_[fetcher_get_] if fetcher_get_ in fetcher_document_ else None
                if not get_val_:
                    print_(f"!!! no target value found for {fetcher_col_id_}: {get_filtered_f_}")
                    continue

                set_ = {}
                set_[fetcher_set_] = get_val_
                self.db_[collection_].update_one({"_id": _id}, {"$set": set_})

            return {"result": True}

        except PassException as exc_:
            self.exception_passed_f()
            return {"result": True, "msg": str(exc_)}

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except AppException as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return {"result": False, "msg": str(exc_)}

    async def worker_change_f(self, params_):
        """
        gets the collection and the fields that affected by the change stream.
        """
        try:
            source_collection_ = params_["collection"]
            token_ = params_["token"]
            op_ = params_["op"]
            changed_ = params_["changed"]
            source_properties_ = params_["properties"]
            _id = params_["id"]
            self.counter_ += 1
            self.repeater_ += 1
            if self.repeater_ == 100:
                print_("counter_", self.counter_, source_collection_)
                self.repeater_ = 0

            source_collection_id_ = source_collection_.replace("_data", "")
            changed_keys_ = list(changed_.keys())

            if not changed_keys_:
                raise PassException(">>> passed, no changed keys")

            trigger_targets_ = \
                [tg_ for tg_ in self.triggers_ if tg_["source"] == source_collection_id_ and op_ in tg_["operations"] and
                 [ma_ for ma_ in tg_["changes"] if ma_["key"] in changed_keys_ and (
                     (ma_["op"].lower() == "eq" and changed_[ma_["key"]] == ma_["value"]) or
                     (ma_["op"].lower() == "ne" and changed_[ma_["key"]] != ma_["value"]) or
                     (ma_["op"].lower() == "gt" and changed_[ma_["key"]] > ma_["value"]) or
                     (ma_["op"].lower() == "gte" and changed_[ma_["key"]] >= ma_["value"]) or
                     (ma_["op"].lower() == "lt" and changed_[ma_["key"]] < ma_["value"]) or
                     (ma_["op"].lower() == "lte" and changed_[ma_["key"]] <= ma_["value"]) or
                     (ma_["op"].lower() == "null" and changed_[ma_["key"]] in [None, ""]) or
                     (ma_["op"].lower() == "nnull" and changed_[ma_["key"]] not in [None, ""])
                 )]]
            if trigger_targets_ == []:
                raise PassException("!!! no trigger target found")

            print_(f"\n>>> change detected [{source_collection_id_}]", op_, changed_)

            for target_ in trigger_targets_:
                target_collection_id_ = target_["target"].lower()
                target_collection_ = f"{target_collection_id_}_data"
                target_properties_ = self.properties_[target_collection_id_] if target_collection_id_ in self.properties_ else None

                print_(">>> target found", target_collection_id_)
                if target_properties_ is None:
                    raise AppException(f"no target properties found {target_collection_id_}")

                target_changes_ = target_["changes"] if "changes" in target_ and len(target_["changes"]) > 0 else None
                if not target_changes_:
                    print_(f"no target changes defined {target_collection_id_}")
                    raise AppException(f"no target changes defined {target_collection_id_}")

                match_ = {"_id": _id}
                conditions_filter_ = self.get_filtered_f({
                    "match": target_changes_,
                    "properties": source_properties_
                })
                match_ = {**match_, **conditions_filter_}

                full_document_ = self.db_[source_collection_].find_one(match_)
                if not full_document_:
                    print_(f"full document not found ({source_collection_}): {match_}")
                    continue

                match_ = {}
                match_for_aggregate_ = {}
                target_matches_ = target_["match"]
                upsert_ = target_["upsert"]

                for item_ in target_matches_:
                    key__ = item_["key"] if "key" in item_ else None
                    value__ = item_["value"] if \
                        "value" in item_ and \
                        item_["value"] is not None and \
                        item_["value"] in full_document_ and \
                        (item_["key"] in target_properties_ or item_["value"] == "_id") \
                        else None

                    if key__ and value__:
                        match_[key__] = match_for_aggregate_[value__] = full_document_[value__]
                    else:
                        continue

                if not match_:
                    print_(f"!!! no data found with the target {target_collection_id_}", match_)
                    continue

                on_changes_all_ = target_["on_changes_all"]
                if on_changes_all_ is True:
                    changes_filter0_ = self.get_filtered_f({
                        "match": target_changes_,
                        "properties": source_properties_
                    })
                    count0_ = 0
                    aggregate0_ = self.db_[source_collection_].aggregate([
                        {"$match": changes_filter0_},
                        {"$group": {"_id": None, "count": {"$sum": 1}}},
                        {"$project": {"_id": 0}}])

                    for doc_ in aggregate0_:
                        count0_ = doc_["count"] if "count" in doc_ else 0

                    match1_ = {}
                    for item_ in target_matches_:
                        key__ = item_["key"] if "key" in item_ else None
                        value__ = item_["value"] if \
                            "value" in item_ and \
                            item_["value"] is not None and \
                            item_["value"] in full_document_ and \
                            (item_["key"] in target_properties_ or item_["value"] == "_id") \
                            else None

                        if key__ and value__:
                            match1_[key__] = full_document_[value__]
                        else:
                            continue

                        changes_filter1_ = self.get_filtered_f({
                            "match": match1_,
                            "properties": source_properties_
                        })
                        count1_ = 0
                        aggregate1_ = self.db_[source_collection_].aggregate([
                            {"$match": changes_filter1_},
                            {"$group": {"_id": None, "count": {"$sum": 1}}},
                            {"$project": {"_id": 0}}])
                        for doc_ in aggregate1_:
                            count1_ = doc_["count"] if "count" in doc_ else 0

                    if count0_ != count1_:
                        print_("!!! on changes all not completed", changes_filter0_)
                        continue

                filter_ = {}
                if "filter" in target_ and len(target_["filter"]) > 0 and not upsert_:
                    filter_ = self.get_filtered_f({
                        "match": target_["filter"],
                        "properties": target_properties_
                    })
                match_ = {**match_, **filter_}

                set_ = {}
                sets_ = target_["set"]

                for item_ in sets_:
                    target_field_ = item_["key"]
                    value_ = str(item_["value"])
                    source_bson_type_ = source_properties_[value_]["bsonType"] if value_ in source_properties_ and "bsonType" in source_properties_[value_] else None
                    target_enum_ = target_field_ in target_properties_ and "enum" in target_properties_[target_field_] and len(target_properties_[target_field_]["enum"]) > 0
                    target_bson_type_ = target_properties_[target_field_]["bsonType"] if "bsonType" in target_properties_[target_field_] else None
                    decimals_ = int(target_properties_[target_field_]["decimals"]) if "decimals" in target_properties_[target_field_] and int(target_properties_[target_field_]["decimals"]) >= 0 else None
                    parts_ = re.split("([+-/*()])", value_)
                    chkgroupbys_ = re.findall("[a-zA-Z_]+", value_)
                    chkgroup0_ = chkgroupbys_[0]

                    type_ = \
                        "sourcevalue" if value_ in source_properties_ else \
                        "targetvalue" if value_ in target_properties_ else \
                        "enum" if target_enum_ else \
                        "string" if target_bson_type_ == "string" else \
                        "formula" if len(parts_) > 1 or chkgroup0_ in self.groupbys_ else \
                        target_bson_type_

                    if type_ == "formula":
                        if target_bson_type_ in self.numerics_:
                            if chkgroup0_ in self.groupbys_:
                                chkgroup0_ = chkgroup0_.lower()
                                chkgroup1_ = chkgroupbys_[1]
                                if chkgroup0_ == "sum":
                                    set_[target_field_] = self.aggregater_sum_f(source_collection_, match_for_aggregate_, chkgroup1_)
                                elif chkgroup0_ == "count":
                                    set_[target_field_] = self.aggregater_count_f(source_collection_, match_for_aggregate_)
                                else:
                                    set_[target_field_] = full_document_[chkgroup1_]
                            else:
                                for part_ in parts_:
                                    part_ = part_.strip()
                                    if part_ in full_document_:
                                        value_ = value_.replace(part_, str(full_document_[part_]))
                                set_[target_field_] = round(eval(value_), decimals_) if decimals_ else eval(value_)
                        else:
                            set_[target_field_] = round(eval(value_), decimals_) if decimals_ else eval(value_)
                    elif type_ == "sourcevalue":
                        if full_document_ and value_ in full_document_:
                            set_[target_field_] = \
                                str(full_document_[value_]) if source_bson_type_ and source_bson_type_ == "string" else \
                                full_document_[value_] * 1 if source_bson_type_ and source_bson_type_ in self.numerics_ else \
                                full_document_[value_]
                    elif type_ == "targetvalue":
                        set_[target_field_] = f"${value_}"
                    elif type_ == "string":
                        set_[target_field_] = str(value_)
                    elif type_ == "bool":
                        set_[target_field_] = str(value_).lower() == "true"
                    elif type_ == "date":
                        if str(value_).lower() == "$current_date":
                            set_[target_field_] = self.get_now_f()
                        else:
                            ln_ = 10 if len(value_) == 10 else 19
                            rgx_ = "%Y-%m-%d" if ln_ == 10 else "%Y-%m-%dT%H:%M:%S"
                            set_[target_field_] = datetime.strptime(value_[:ln_], rgx_)
                    elif type_ == "number":
                        set_[target_field_] = float(value_) * 1
                    elif type_ == "enum":
                        set_[target_field_] = value_
                    else:
                        set_[target_field_] = value_

                set_["_modified_at"] = self.get_now_f()
                set_["_modified_by"] = "_automation"
                if upsert_ is True:
                    set_["_created_at"] = set_["_modified_at"]
                    set_["_created_by"] = set_["_modified_by"]

                set_["_resume_token"] = token_
                update_many_ = self.db_[target_collection_].update_many(match_, {"$set": set_}, upsert=upsert_)
                count_ = update_many_.matched_count
                print_(">>> updated :)", {"coll": target_collection_, "match": match_, "set": set_, "count": count_})

                notification_ = target_["notification"] if "notification" in target_ else None
                if notification_:
                    notify_ = "notify" in notification_ and notification_["notify"] is True
                    attachment_ = "attachment" in notification_ and notification_["attachment"] is True
                    subject_ = notification_["subject"] if "subject" in notification_ and notification_["subject"] != "" else None
                    body_ = notification_["body"] if "body" in notification_ and notification_["body"] != "" else None
                    ncollection_ = notification_['collection'] if "collection" in notification_ and notification_["collection"] != "" else None
                    fields_ = notification_["fields"].replace(" ", "") if "fields" in notification_ and notification_["fields"] != "" else None
                    nkey_ = notification_["key"] if "key" in notification_ and notification_["key"] != "" else None
                    nfilter_ = notification_["filter"] if "filter" in notification_ and len(notification_["filter"]) > 0 else None
                    tags_ = notification_["_tags"] if "_tags" in notification_ and len(notification_["_tags"]) > 0 else None
                    if not (notify_ and subject_ and body_ and ncollection_ and fields_ and nfilter_ and nkey_ and tags_):
                        continue
                    keyf_ = full_document_[nkey_]
                    get_users_from_tags_f_ = self.get_users_from_tags_f(tags_)
                    if not get_users_from_tags_f_["result"]:
                        print_("!!! error get_users_from_tags_f_:", get_users_from_tags_f_["msg"])
                        continue
                    to_ = get_users_from_tags_f_["to"] if "to" in get_users_from_tags_f_ and len(get_users_from_tags_f_["to"]) > 0 else None
                    if not to_:
                        print_("!!! _tags to not found")
                        continue

                    personalizations_ = {"to": get_users_from_tags_f_["to"]}
                    files_ = []
                    subject_ += f" - {keyf_}"
                    type_ = "csv"

                    ndocument_ = self.db_["_collection"].find_one({"col_id": ncollection_})
                    if not ndocument_:
                        print_("!!! notification collection not found", ncollection_)
                        continue

                    nproperties_ = ndocument_["col_structure"]["properties"] if "col_structure" in ndocument_ and "properties" in ndocument_["col_structure"] else None
                    if not nproperties_:
                        continue

                    if attachment_:
                        query_ = json.dumps(self.get_filtered_f({
                            "match": nfilter_,
                            "properties": nproperties_,
                            "data": full_document_
                        }))
                        file_ = f"/docs/stream-{self.get_timestamp_f()}.{type_}"
                        ncollection_ += "_data"
                        command_ = f"mongoexport --quiet --uri=\"mongodb://{mongo_username_}:{mongo_password_}@{mongo_host0_}:{mongo_port0_},{mongo_host1_}:{mongo_port1_},{mongo_host2_}:{mongo_port2_}/?authSource={mongo_auth_db_}\" --ssl --collection={ncollection_} --out={file_} --sslCAFile={mongo_tls_ca_keyfile_} --sslPEMKeyFile={mongo_tls_cert_keyfile_} --sslPEMKeyPassword={mongo_tls_cert_keyfile_password_} --tlsInsecure --db={mongo_db_} --type={type_} --fields='{fields_}' --query='{query_}'"

                        call(command_, shell=True)
                        files_ = [{"filename": file_, "filetype": type_}]

                    msg_ = {
                        "files": files_,
                        "personalizations": personalizations_,
                        "subject": subject_,
                        "html": body_
                    }
                    email_sent_ = self.send_email_smtp_f(msg_)
                    if not email_sent_["result"]:
                        raise PassException(email_sent_["msg"])

            return {"result": True}

        except PassException as exc_:
            self.exception_passed_f()
            return {"result": True, "msg": str(exc_)}

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except AppException as exc_:
            self.exception_reported_f(exc_)
            return {"result": False, "msg": str(exc_)}

        except Exception as exc_:
            self.exception_printed_f(exc_)
            return {"result": False, "msg": str(exc_)}

    async def starter_fetchers_f(self, params_):
        """
        docstring is in progress
        """
        return await self.worker_fetchers_f(params_)

    async def starter_changes_f(self, params_):
        """
        docstring is in progress
        """
        return await self.worker_change_f(params_)

    async def changes_stream_f(self):
        """
        creates a pipeline to run async works in a loop
        """
        try:
            print_(">>> change stream started")
            resume_token_ = None

            with self.db_.watch(self.pipeline_) as changes_stream_:
                for event_ in changes_stream_:

                    source_collection_ = event_["ns"]["coll"] if "ns" in event_ and "coll" in event_["ns"] else None
                    if source_collection_ is None:
                        print_("!!! no collection provided")
                        continue
                    source_collection_id_ = source_collection_.replace("_data", "")

                    if source_collection_ == "_collection":
                        refresh_properties_f_ = self.refresh_properties_f()
                        if not refresh_properties_f_["result"]:
                            print_(">>> properties refresh error", refresh_properties_f_["exc"])
                            continue
                        refresh_triggers_f_ = self.refresh_triggers_f()
                        if not refresh_triggers_f_["result"]:
                            print_(">>> triggers refresh error", refresh_triggers_f_["exc"])
                            continue
                        refresh_fetchers_f_ = self.refresh_fetchers_f()
                        if not refresh_fetchers_f_["result"]:
                            print_(">>> fetchers refresh error", refresh_fetchers_f_["exc"])
                            continue
                        print_(">>> _collection updated and refreshed")

                    source_properties_ = self.properties_[source_collection_id_] if source_collection_id_ in self.properties_ else None
                    if source_properties_ is None:
                        continue

                    op_ = event_["operationType"] if "operationType" in event_ and event_["operationType"] in self.operations_ else None
                    if op_ is None:
                        print_("!!! no operation provided")
                        continue

                    changed_ = event_["updateDescription"]["updatedFields"] if "updateDescription" in event_ and "updatedFields" in event_["updateDescription"] and op_ in ["update", "replace"] else None
                    if changed_ is None:
                        changed_ = event_["fullDocument"] if "fullDocument" in event_ and op_ == "insert" else None
                        if changed_ is None:
                            print_("!!! no changed fields provided")
                            continue

                    if source_collection_[:1] == "_":
                        print_(f">>> system collection passed {source_collection_}")
                        continue

                    resume_token_ = changes_stream_.resume_token
                    token_ = resume_token_["_data"] if "_data" in resume_token_ and resume_token_["_data"] is not None else None
                    _id = event_["documentKey"]["_id"] if "documentKey" in event_ and "_id" in event_["documentKey"] else None

                    if _id is None:
                        continue

                    params_ = {"collection": source_collection_, "properties": source_properties_, "id": _id, "token": token_, "op": op_, "changed": changed_}
                    await asyncio.create_task(self.starter_changes_f(params_))
                    await asyncio.create_task(self.starter_fetchers_f(params_))

            current_task_ = asyncio.current_task()
            running_tasks_ = [task for task in asyncio.all_tasks() if task is not current_task_]
            await asyncio.wait(running_tasks_)

        except pymongo.errors.PyMongoError as exc_:
            self.exception_reported_f(exc_)

        except AppException as exc_:
            self.exception_reported_f(exc_)

        except Exception as exc_:
            self.exception_printed_f(exc_)


mongo_rs_ = os.environ.get("MONGO_RS")
mongo_host0_ = os.environ.get("MONGO_HOST0")
mongo_host1_ = os.environ.get("MONGO_HOST1")
mongo_host2_ = os.environ.get("MONGO_HOST2")
mongo_port0_ = int(os.environ.get("MONGO_PORT0"))
mongo_port1_ = int(os.environ.get("MONGO_PORT1"))
mongo_port2_ = int(os.environ.get("MONGO_PORT2"))
mongo_db_ = os.environ.get("MONGO_DB")
mngo_auth_db_ = os.environ.get("MONGO_AUTH_DB")
mongo_username_ = get_docker_secret("mongo_username", default="")
mongo_password_ = get_docker_secret("mongo_password", default="")
mongo_tls_cert_keyfile_password_ = get_docker_secret("mongo_tls_keyfile_password", default="")
mongo_tls_ = os.environ.get("MONGO_TLS")
mongo_tls_cert_keyfile_ = os.environ.get("MONGO_TLS_CERT_KEYFILE")
mongo_tls_allow_invalid_certificates_ = os.environ.get("MONGO_TLS_ALLOW_INVALID_CERTIFICATES")
mongo_retry_writes_ = os.environ.get("MONGO_RETRY_WRITES")
mongo_auth_db_ = os.environ.get("MONGO_AUTH_DB")
mongo_tls_ca_keyfile_ = os.environ.get("MONGO_TLS_CA_KEYFILE")
notification_slack_hook_url_ = os.environ.get("NOTIFICATION_SLACK_HOOK_URL")

if __name__ == "__main__":
    print_ = partial(print, flush=True)
    asyncio.run(Trigger().changes_stream_f())
