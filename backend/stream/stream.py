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
import re
import asyncio
import urllib
from datetime import datetime
from functools import partial
from bson.objectid import ObjectId
import pymongo


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
        print(">>> init started")
        mongo_rs_ = os.environ.get("MONGO_RS")
        mongo_host0_ = os.environ.get("MONGO_HOST0")
        mongo_host1_ = os.environ.get("MONGO_HOST1")
        mongo_host2_ = os.environ.get("MONGO_HOST2")
        mongo_port0_ = int(os.environ.get("MONGO_PORT0"))
        mongo_port1_ = int(os.environ.get("MONGO_PORT1"))
        mongo_port2_ = int(os.environ.get("MONGO_PORT2"))
        mongo_db_ = os.environ.get("MONGO_DB")
        mngo_auth_db_ = os.environ.get("MONGO_AUTH_DB")
        mongo_username_ = urllib.parse.quote_plus(os.environ.get("MONGO_USERNAME"))
        mongo_password_ = urllib.parse.quote_plus(os.environ.get("MONGO_PASSWORD"))
        mongo_tls_ = os.environ.get("MONGO_TLS")
        mongo_tls_cert_key_password_ = urllib.parse.quote_plus(os.environ.get("MONGO_TLS_CERT_KEY_PASSWORD"))
        mongo_tls_cert_keyfile_ = os.environ.get('MONGO_TLS_CERT_KEYFILE')
        mongo_tls_allow_invalid_certificates_ = os.environ.get("MONGO_TLS_ALLOW_INVALID_CERTIFICATES")
        mongo_retry_writes_ = os.environ.get("MONGO_RETRY_WRITES")

        self.operations_ = ["insert", "update", "replace", "delete"]
        self.pipeline_ = [{"$match": {"operationType": {"$in": self.operations_}}}]
        self.numerics_ = ["number", "int", "float", "decimal"]
        self.groupbys_ = ["sum", "count", "mean", "std", "var"]
        self.connstr_ = f"mongodb://{mongo_username_}:{mongo_password_}@{mongo_host0_}:{mongo_port0_},{mongo_host1_}:{mongo_port1_},{mongo_host2_}:{mongo_port2_}/{mongo_db_}?authSource={mngo_auth_db_}&replicaSet={mongo_rs_}&tls={mongo_tls_}&tlsCertificateKeyFile={mongo_tls_cert_keyfile_}&tlsAllowInvalidCertificates={mongo_tls_allow_invalid_certificates_}&tlsCertificateKeyFilePassword={mongo_tls_cert_key_password_}&retryWrites={mongo_retry_writes_}"
        self.client = pymongo.MongoClient(self.connstr_)
        self.db_ = self.client[mongo_db_]

        refresh_f_ = self.refresh_f()
        if not refresh_f_["result"]:
            raise AppException(refresh_f_["exc"])

        print(">>> init ended")

    def exception_show_f(self, exc):
        """
        docstring is in progress
        """
        line_no_ = exc.__traceback__.tb_lineno if hasattr(exc, "__traceback__") and hasattr(exc.__traceback__, "tb_lineno") else None
        name_ = type(exc).__name__ if hasattr(type(exc), "__name__") else "Exception"
        print(f"!!! worker exception type {name_} at line {line_no_}:", str(exc))
        return True

    def refresh_f(self):
        """
        docstring is in progress
        """
        try:
            print(">>> getting triggers...")
            self.triggers_ = []
            cursor_ = self.db_["_collection"].aggregate([{
                "$match": {
                    "col_structure.triggers": {
                        "$elemMatch": {
                            "enabled": True
                        }
                    }
                }
            }])
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
                            "prefixes": cluster_["prefixes"] if "prefixes" in cluster_ and len(cluster_["prefixes"]) > 0 else []
                        })

            if not self.triggers_:
                raise PassException("!!! no trigger found and passed")

            print(">>> getting properties...")
            self.properties_ = {}
            cursor_ = self.db_["_collection"].aggregate([{
                "$match": {"$and": [{"col_structure.properties": {"$exists": True, "$ne": None}}]}
            }])
            for item_ in cursor_:
                self.properties_[item_["col_id"]] = item_["col_structure"]["properties"]
            if not self.properties_:
                raise AppException("!!! no properties found")
            print(">>> properties collected")

            return {"result": True}

        except PassException as exc_:
            return {"result": True, "exc": exc_}

        except pymongo.errors.PyMongoError as exc_:
            print("!!! refresher mongo error")
            return {"result": False, "exc": exc_}

        except AppException as exc_:
            print("!!! refresher app exception")
            return {"result": False, "exc": exc_}

        except Exception as exc_:
            print("!!! refresher exception")
            return {"result": False, "exc": exc_}

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

    def aggregater_sum_f(self, coll_, filter_, field_):
        """
        docstring is in progress
        """
        try:
            sum_ = None
            match_ = filter_ if filter_ else {}
            aggregate_ = self.db_[coll_].aggregate([
                {"$match": match_},
                {"$group": {"_id": None, "sum": {"$sum": f"${field_}"}}},
                {"$project": {"_id": 0}}])

            for doc_ in aggregate_:
                sum_ = doc_["sum"] if "sum" in doc_ else None

            return sum_

        except pymongo.errors.PyMongoError as exc_:
            print("!!! sum mongo error", str(exc_))
            return 0

        except Exception as exc_:
            print("!!! sum exception", str(exc_))
            return 0

    def aggregater_count_f(self, coll_, filter_):
        """
        docstring is in progress
        """
        try:
            count_ = None
            match_ = filter_ if filter_ else {}
            aggregate_ = self.db_[coll_].aggregate([
                {"$match": match_},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
                {"$project": {"_id": 0}}])

            for doc_ in aggregate_:
                count_ = doc_["count"] if "count" in doc_ else None

            return count_

        except pymongo.errors.PyMongoError as exc_:
            print("!!! count mongo error", str(exc_))
            return 0

        except Exception as exc_:
            print("!!! count exception", str(exc_))
            return 0

    async def worker_f(self, event_, resume_token_):
        """
        gets the collection and the fields that affected by the change stream.
        """
        try:
            source_collection_ = event_["ns"]["coll"] if "ns" in event_ and "coll" in event_["ns"] else None
            if source_collection_ is None:
                raise AppException("no collection provided")

            if source_collection_ == "_collection":
                refresh_f_ = self.refresh_f()
                if not refresh_f_["result"]:
                    raise AppException(refresh_f_["exc"])
                raise PassException(">>> _collection updated")

            source_collection_id_ = source_collection_.replace("_data", "")

            _id = event_["documentKey"]["_id"]
            if _id is None:
                raise AppException(f"!!! missing document _id {event_}")

            token_ = resume_token_["_data"] if "_data" in resume_token_ else None
            if token_ is None:
                raise AppException(f"no resume token provided: {resume_token_}")

            source_properties_ = self.properties_[source_collection_id_] if source_collection_id_ in self.properties_ else None
            if source_properties_ is None:
                raise PassException(f"no source properties defined for '{source_collection_id_}'")

            op_ = event_["operationType"] if "operationType" in event_ and event_["operationType"] in self.operations_ else None
            if op_ is None:
                raise AppException(f"invalid operation type '{op_}'")

            changed_ = event_["updateDescription"]["updatedFields"] if "updateDescription" in event_ and "updatedFields" in event_["updateDescription"] and op_ in ["update", "replace"] else None
            if changed_ is None:
                changed_ = event_["fullDocument"] if "fullDocument" in event_ and op_ == "insert" else None
                if changed_ is None:
                    raise AppException(f"updated fields is missing '{op_}'")
            changed_keys_ = list(changed_.keys())

            print(f"\nİİİ change detected [{source_collection_id_}]", op_, changed_keys_, changed_)

            trigger_targets_ = [tg_ for tg_ in self.triggers_ if tg_["source"] == source_collection_id_ and op_ in tg_["operations"] and [ma_ for ma_ in tg_["changes"] if ma_["key"] in changed_keys_ and (
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
                raise PassException("!!! no trigger condition found")

            for target_ in trigger_targets_:
                target_collection_id_ = target_["target"]
                target_collection_ = f"{target_collection_id_}_data"
                target_properties_ = self.properties_[target_collection_id_] if target_collection_id_ in self.properties_ else None
                print(">>> target found", target_collection_id_)
                if target_properties_ is None:
                    raise AppException(f"no target properties found {target_collection_id_}")

                target_changes_ = target_["changes"] if "changes" in target_ and len(target_["changes"]) > 0 else None
                if not target_changes_:
                    raise AppException(f"no target changes found {target_collection_id_}")

                match_ = {"_id": _id}
                conditions_filter_ = self.get_filtered_f({
                    "match": target_changes_,
                    "properties": source_properties_
                })
                match_ = {**match_, **conditions_filter_}

                full_document_ = self.db_[source_collection_].find_one(match_)
                if not full_document_:
                    continue

                match_ = {}
                match_for_aggregate_ = {}
                target_matches_ = target_["match"]
                for item_ in target_matches_:
                    if "value" in item_ and item_["value"] in full_document_ and full_document_[item_["value"]] is not None:
                        match_[item_["key"]] = full_document_[item_["value"]]
                        match_for_aggregate_[item_["value"]] = full_document_[item_["value"]]
                    else:
                        continue
                if not match_:
                    print(f"\n!!! no data found with the target {target_collection_id_}", match_)
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
                        if "value" in item_ and item_["value"] in full_document_ and full_document_[item_["value"]] is not None:
                            match1_[item_["value"]] = full_document_[item_["value"]]
                        else:
                            continue
                        if not match1_:
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
                        print("!!! on changes all not completed", changes_filter0_)
                        continue

                filter_ = {}
                target_filters_ = target_["filter"] if "filter" in target_ and len(target_["filter"]) > 0 else None
                if target_filters_:
                    filter_ = self.get_filtered_f({
                        "match": target_filters_,
                        "properties": target_properties_
                    })
                match_ = {**match_, **filter_}

                # if "_id" in match_ and ObjectId.is_valid(match_["_id"]):
                #     pass
                # else:
                #     match_ = {**match_, **filter_}

                set_ = {}
                sets_ = target_["set"]
                upsert_ = "upsert" in target_ and target_["upsert"] is True
                for item_ in sets_:
                    target_field_ = item_["key"]
                    value_ = str(item_["value"])
                    source_bson_type_ = source_properties_[value_]["bsonType"] if value_ in source_properties_ and "bsonType" in source_properties_[value_] else None
                    target_enum_ = target_field_ in target_properties_ and "enum" in target_properties_[target_field_] and len(target_properties_[target_field_]["enum"]) > 0
                    target_bson_type_ = target_properties_[target_field_]["bsonType"] if "bsonType" in target_properties_[target_field_] else None
                    parts_ = re.split("([+-/*()])", value_)
                    chkgroupbys_ = re.findall("[a-zA-Z_]+", value_)
                    chkgroup0_ = chkgroupbys_[0]
                    type_ = "enum" if target_enum_ else "sourcevalue" if value_ in source_properties_ else "targetvalue" if value_ in target_properties_ else "string" if target_bson_type_ == "string" else "formula" if len(
                        parts_) > 1 or chkgroup0_ in self.groupbys_ else target_bson_type_
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
                                set_[target_field_] = eval(value_)
                        else:
                            set_[target_field_] = eval(value_)
                    elif type_ == "sourcevalue":
                        set_[target_field_] = str(full_document_[value_]) if source_bson_type_ and source_bson_type_ == "string" else full_document_[
                            value_] * 1 if source_bson_type_ and source_bson_type_ in self.numerics_ else full_document_[value_]
                    elif type_ == "targetvalue":
                        set_[target_field_] = f"${value_}"
                    elif type_ == "string":
                        set_[target_field_] = str(value_)
                    elif type_ == "bool":
                        set_[target_field_] = str(value_).lower() == "true"
                    elif type_ == "date":
                        if str(value_).lower() == "$current_date":
                            set_[target_field_] = datetime.now()
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

                set_["_modified_at"] = datetime.now()
                set_["_modified_by"] = "_automation"
                set_["_resume_token"] = token_

                print(f">>> updating... {set_}")
                update_many_ = self.db_[target_collection_].update_many(match_, {"$set": set_}, upsert=upsert_)
                count_ = update_many_.matched_count
                print(">>> updated :)", {"coll": target_collection_, "match": match_, "set": set_, "count": count_})

            return True

        except pymongo.errors.PyMongoError as exc_:
            self.exception_show_f(exc_)

        except PassException as exc_:
            self.exception_show_f(exc_)

        except AppException as exc_:
            self.exception_show_f(exc_)

        except Exception as exc_:
            self.exception_show_f(exc_)

    def backlog_stream_f(self):
        """
        backlog stream is in progress
        """
        print(">>> backlog stream started")
        print(">>> backlog stream ended")
        return True

    async def starter_f(self, event_, resume_token_):
        """
        docstring is in progress
        """
        return await self.worker_f(event_, resume_token_)

    async def changes_stream(self):
        """
        creates a pipeline to run async works in a loop
        """
        try:
            print(">>> change stream started")
            resume_token_ = None
            backlog_stream_ = self.backlog_stream_f()
            if not backlog_stream_:
                raise AppException("backlog trace error")

            with self.db_.watch(self.pipeline_) as changes_stream_:
                for event_ in changes_stream_:
                    resume_token_ = changes_stream_.resume_token
                    starter_f_ = asyncio.create_task(self.starter_f(event_, resume_token_))
                    await starter_f_

            current_task_ = asyncio.current_task()
            running_tasks_ = [task for task in asyncio.all_tasks() if task is not current_task_]
            await asyncio.wait(running_tasks_)

        except pymongo.errors.PyMongoError as exc_:
            self.exception_show_f(exc_)

        except AppException as exc_:
            self.exception_show_f(exc_)

        except Exception as exc_:
            self.exception_show_f(exc_)


if __name__ == "__main__":
    print = partial(print, flush=True)
    asyncio.run(Trigger().changes_stream())
