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

Collections, documents, queries, jobs, links, actions, imports and dumps.
"""

import os
import io
import re
import json
import subprocess
from datetime import datetime, timedelta
import pymongo
import bson
from bson import json_util
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
import pyotp
from flask import request
import requests
from werkzeug.utils import secure_filename

from bi import config as cfg
from bi.auth import Auth
from bi.db import Mongo
from bi.encoder import JSONEncoder
from bi.errors import APIError, AppException, AuthError, PassException
from bi.mailer import Email
from bi.misc import Misc


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
                raise APIError(f"file not allowed [schema] {fullpath_}")

            with open(fullpath_, "r", encoding="utf-8") as fopen_:
                res_ = json.loads(fopen_.read())

            return res_

        except APIError as exc__:
            cfg.PRINT_("!!!", exc__)

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
            cursor_ = (
                Mongo().db_["_collection"].find_one({"col_id": collection})
                if collection[:1] != "_"
                else self.root_schemas_f(f"{collection}")
            )
            if not cursor_:
                raise APIError("collection not found for properties")
            if "col_structure" not in cursor_:
                raise APIError("structure not found")

            structure_ = cursor_[
                "col_structure"] if collection[:1] != "_" else cursor_
            if "properties" not in structure_:
                raise APIError("properties not found in structure")
            properties_ = structure_["properties"]

            return {"result": True, "properties": properties_}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def inner_collection_f(self, cid_):
        """
        docstring is in progress
        """
        try:
            is_crud_ = cid_[:1] != "_"
            collection_ = (
                Mongo().db_["_collection"].find_one({"col_id": cid_})
                if is_crud_
                else self.root_schemas_f(f"{cid_}")
            )
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
                                document_[k] = datetime.strptime(
                                    doc_[k][:ln_], rgx_)
                            else:
                                document_[k] = (
                                    datetime.strptime(doc_[k][:ln_], rgx_)
                                    if doc_[k] is not None
                                    else None
                                )
                        elif property_["bsonType"] == "string":
                            document_[k] = (
                                str(doc_[k]) if doc_[
                                    k] is not None else doc_[k]
                            )
                        elif property_["bsonType"] in [
                            "number",
                            "int",
                            "float",
                            "double",
                        ]:
                            document_[k] = (
                                doc_[k] * 1
                                if document_[k] is not None
                                else document_[k]
                            )
                        elif property_["bsonType"] == "decimal":
                            document_[k] = (
                                doc_[k] * 1.00
                                if document_[k] is not None
                                else document_[k]
                            )
                        elif property_["bsonType"] == "bool":
                            document_[k] = document_[k] and document_[k] in [
                                True,
                                "true",
                                "True",
                                "TRUE",
                            ]
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
            collection__ = (
                col_check_[
                    "collection"] if "collection" in col_check_ else None
            )

            structure_ = collection__[
                "col_structure"] if is_crud_ else collection__
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
        return (
            datetime.fromisoformat(date_)
            if date_
            not in [
                " ",
                "0",
                "0.0",
                "NaT",
                "NaN",
                "nat",
                "nan",
                np.nan,
                np.double,
                None,
            ]
            else None
        )

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
            sweeped_ = (
                obj["sweeped"] if "sweeped" in obj and obj["sweeped"] != [] else []
            )

            get_filtered_ = {}
            if len(match_) > 0:
                get_filtered_ = self.get_filtered_f(
                    {
                        "match": match_,
                        "properties": properties_ if properties_ else None,
                    }
                )

            ids_ = []
            for _id in sweeped_:
                ids_.append(ObjectId(_id))
            if len(ids_) > 0:
                get_filtered_ = {
                    "$and": [get_filtered_, {"_id": {"$in": ids_}}]}

            distinct_ = ""
            cursora_ = Mongo().db_[f"{collection_}_data"].distinct(
                key_, get_filtered_)
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
        str_ = str_.strip().replace("\t", " ")
        str_ = re.sub(cleantags_, "", str_)
        str_ = re.sub(cleanptrn_, "", str_)
        str_ = str_[:32]
        str_ = re.sub(" +", " ", str_)
        str_ = re.sub(
            ".", lambda char_: exceptions_.get(
                char_.group(), char_.group()), str_
        )
        return str_.lower().strip().encode("ascii", "ignore").decode("ascii")

    def import_f(self, obj):
        """
        docstring is in progress
        """
        content_, stats_, res_, details_, files_, filename_, filetype_, upsertable_, df_, name_ = (
            "", "", None, {}, [], "", "xlsx", False, None, "")
        try:
            form_ = obj["form"]
            file_ = obj["file"]
            collection_ = obj["collection"]
            method_ = obj["process"] if "process" in obj and obj["process"] is not None else "insert"
            upserted_ = False
            updated_ = method_ == "update"
            # H-8: the acting user comes from the session, never from the form
            session_user_ = obj["user"] if "user" in obj and obj["user"] else {}
            email_ = session_user_["usr_id"] if "usr_id" in session_user_ else None
            if not email_:
                raise APIError("user session not found")
            mimetype_ = file_.content_type
            original_name_ = secure_filename(file_.filename or "")
            extension_ = original_name_.rsplit(".", 1)[-1].lower() if "." in original_name_ else ""
            if extension_ not in cfg.UPLOAD_EXTENSIONS_:
                raise APIError("file extension is not allowed")
            file_.seek(0, os.SEEK_END)
            filesize_ = file_.tell()
            file_.seek(0)
            if filesize_ > cfg.API_UPLOAD_LIMIT_BYTES_:
                raise APIError(f"invalid file size, limit is {cfg.API_UPLOAD_LIMIT_BYTES_} bytes")

            user_ = Mongo().db_["_user"].find_one({"usr_id": email_})
            if not user_:
                raise APIError("user not found")
            name_ = user_["usr_name"]

            collection__ = f"{collection_}_data"
            find_one_ = Mongo().db_["_collection"].find_one({"col_id": collection_})
            if not find_one_:
                raise APIError(f"collection not found {collection_}")

            col_structure_ = find_one_["col_structure"] if "col_structure" in find_one_ else None
            if not col_structure_:
                raise APIError("no structure found")

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
            purge_ = "purge" in import_ and import_["purge"] is True
            enabled_ = "enabled" in import_ and import_["enabled"] is True
            sumnum_ = "sumnum" in import_ and import_["sumnum"] is True
            upsertables_ = import_["upsertables"] if "upsertables" in import_ and len(import_["upsertables"]) > 0 else []

            if not enabled_:
                raise APIError("collection is not enabled to import")

            dferr_ = ""
            try:
                if mimetype_ in [
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "application/vnd.ms-excel",
                ]:
                    df_ = pd.read_excel(file_, sheet_name=collection_, header=0, engine="openpyxl", dtype="object")
                elif mimetype_ == "text/csv":
                    filetype_ = "txt"
                    decoded_ = file_.read().decode("utf-8")
                    df_ = pd.read_csv(io.StringIO(decoded_), header=0, dtype="object")
                else:
                    raise APIError("file type is not supported")

            except ValueError as exc__:
                dferr_ = str(exc__)

            if dferr_ != "":
                df_ = None
                raise APIError(dferr_)

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
                            if ("replacement" in property_ and len(property_["replacement"]) > 0):
                                for repl_ in property_["replacement"]:
                                    find_ = (repl_["find"] if "find" in repl_ and repl_["find"] is not None else None)
                                    replace_ = (repl_["replace"] if "replace" in repl_ and repl_["replace"] is not None else "")
                                    if find_ and replace_ is not None:
                                        df_[column_] = df_[column_].str.replace(find_, replace_, regex=True)
                        elif property_["bsonType"] == "int":
                            df_[column_] = df_[column_].apply(self.frame_convert_int_f)
                        elif property_["bsonType"] in ["number", "decimal"]:
                            df_[column_] = df_[column_].apply(self.frame_convert_number_f)
                    else:
                        columns_tobe_deleted_.append(column_)
                else:
                    # H-8: an _id column may only drive updates when the update permission was checked
                    if column_ == "_id" and updated_:
                        df_[column_] = df_[column_].apply(self.frame_convert_objectid_f)
                    else:
                        columns_tobe_deleted_.append(column_)

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
            unique_ = (col_structure_["unique"] if "unique" in col_structure_ and len(col_structure_["unique"]) > 0 else [])
            for uq_ in unique_:
                uql_, uqlz_ = len(uq_), 0
                for uq__ in uq_:
                    if uq__ in df_.columns:
                        uqlz_ += 1
                        uniques_.append(uq__)
                if uql_ == uqlz_:
                    break

            if sumnum_:
                df_ = df_.groupby(
                    list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns),
                    as_index=False,
                    dropna=False,
                ).sum()

            df_.replace([np.nan, pd.NaT, "nan", "NaN", "nat", "NaT"], None, inplace=True)
            df_["_created_at"] = df_["_modified_at"] = Misc().get_now_f()
            df_["_created_by"] = df_["_modified_by"] = email_
            df_["_modified_count"] = 0
            payload_ = df_.to_dict("records")

            wrote_, count_ = [], 0
            if "_id" in df_.columns:
                wrote_ = [
                    pymongo.UpdateOne(
                        {"_id": ObjectId(doc_["_id"])}, {"$set": doc_}, upsert=False
                    )
                    for doc_ in payload_
                ]
            elif (upserted_ or updated_) and upsertable_ and uniques_:
                fieldsgiven_ = False
                get_now_f_ = Misc().get_now_f()
                for doc_ in payload_:
                    filter_, set_ = {}, {}
                    for uniques__ in uniques_:
                        if uniques__ in doc_ and doc_[uniques__] is not None:
                            filter_[uniques__] = doc_[uniques__]
                    if not filter_:
                        continue
                    for upsertable__ in upsertables_:
                        if upsertable__ in doc_ and doc_[upsertable__] is not None:
                            fieldsgiven_ = True
                            set_[upsertable__] = doc_[upsertable__]
                    if not set_:
                        continue
                    set_["_modified_at"] = get_now_f_
                    set_["_modified_by"] = email_
                    wrote_.append(pymongo.UpdateOne(filter_, {"$set": set_}, upsert=upserted_))

                if not fieldsgiven_:
                    raise APIError("no upsertable fields provided")
            else:
                wrote_ = [pymongo.InsertOne(doc_) for doc_ in payload_]

            if purge_:
                suffix_ = Misc().get_timestamp_f()
                Mongo().db_[collection__].aggregate(
                    [{"$match": {}}, {"$out": f"{collection__}_bin_{suffix_}"}]
                )
                Mongo().db_[collection__].delete_many({})

            bulk_write_ = Mongo().db_[collection__].bulk_write(wrote_, ordered=False)
            details_, content_ = bulk_write_.bulk_api_result, ""

            res_ = {"result": True, "count": count_, "msg": "file was imported successfully", }

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
            res_["msg"] = (
                "Sorry! We have just e-mailed you the error details about this upload."
            )

        except APIError as exc__:
            content_, details_ = str(exc__), {}
            res_ = Misc().notify_exception_f(exc__)

        except Exception as exc__:
            content_, details_ = str(exc__), {}
            res_ = Misc().notify_exception_f(exc__)

        finally:
            if df_ is not None:
                stats_ += f"<br /><br />ROW COUNT: {str(len(df_))}<br />"
                stats_ += (f"<br />INSERTED: {str(details_['nInserted'])}" if "nInserted" in details_ else "")
                stats_ += (f"<br />UPSERTED: {str(details_['nUpserted'])}" if "nUpserted" in details_ else "")
                stats_ += (f"<br />MATCHED: {str(details_['nMatched'])}" if "nMatched" in details_ else "")
                stats_ += (f"<br />MODIFIED: {str(details_['nModified'])}" if "nModified" in details_ else "")
                stats_ += (f"<br />REMOVED: {str(details_['nRemoved'])}" if "nRemoved" in details_ else "")
                filename_ = f"imported-{collection_}-{Misc().get_timestamp_f()}.txt"
                fullpath_ = os.path.normpath(os.path.join(cfg.API_TEMPFILE_PATH_, filename_))
                if not fullpath_.startswith(cfg.TEMP_PATH_):
                    raise APIError(f"file not allowed [import] {fullpath_}")
                with open(fullpath_, "w", encoding="utf-8") as logfile_:
                    logfile_.write(
                        stats_.replace("<br />", "\n")
                        + "\n\n-----BEGIN ERROR LIST-----\n"
                        + content_
                        + "-----END ERROR LIST-----"
                    )
                logfile_.close()
                files_.append({"name": fullpath_, "type": "txt"})
                file_.seek(0)
                fullpathf_ = os.path.normpath(os.path.join(cfg.API_TEMPFILE_PATH_, secure_filename(file_.filename)))
                file_.save(fullpathf_)
                files_.append({"name": fullpathf_, "type": filetype_})
            else:
                stats_ += f"<br /><br />{dferr_}.<br />" if dferr_ != "" else ""

            Email().send_email_f({
                "personalizations": [{"email": email_, "name": name_}, {"email": cfg.ADMIN_EMAIL_, "name": cfg.ADMIN_NAME_}],
                "op": "importerr",
                "flag": True,
                "html":
                f"Hi,<br /><br />Here's the data file upload result;<br /><br />MIME TYPE: {mimetype_}<br />TARGET COLLECTION: {collection_}<br />METHOD: {method_}{stats_}",
                "subject": "Management [Data Upload Result]",
                "files": files_
            })

            return res_

    def dump_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            op_ = obj_["op"]
            email_ = obj_["user"]["email"] if obj_ and obj_["user"] else "cronjob"
            dmp_id_ = (f"dump-{cfg.MONGO_DB_}-{Misc().get_timestamp_f()}" if op_ == "dumpu" else Misc().clean_f(obj_["dumpid"]))
            fn_ = f"{dmp_id_}.gz"
            type_ = "gzip"
            fullpath_ = os.path.normpath(os.path.join(cfg.API_MONGODUMP_PATH_, fn_))
            if not fullpath_.startswith(cfg.DUMP_PATH_):
                raise APIError(f"file not allowed [restore] {fullpath_}")

            if op_ == "dumpu":
                subprocess.call(["mongodump"] + Misc().commands_f("mongodump", {"type": type_, "loc": fullpath_}))
                size_ = os.path.getsize(fullpath_)
                Mongo().db_["_dump"].insert_one(
                    {
                        "dmp_id": dmp_id_,
                        "dmp_type": type_,
                        "dmp_size": size_,
                        "_created_at": Misc().get_now_f(),
                        "_created_by": email_,
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": email_,
                    }
                )

            s3_f_ = Misc().s3_f(
                {"op": op_, "localfile": fullpath_, "object": f"mongodump/{fn_}"}
            )
            if not s3_f_["result"]:
                raise APIError(s3_f_["msg"])

            size_ = os.path.getsize(fullpath_)

            if op_ == "dumpu" and os.path.exists(fullpath_):
                os.remove(fullpath_)

            if op_ == "dumpr":
                subprocess.call(
                    ["mongorestore"]
                    + Misc().commands_f(
                        "mongorestore", {"type": type_, "loc": fullpath_}
                    )
                )

            files_ = [{"name": fullpath_, "type": type_}]

            return {
                "result": True,
                "id": dmp_id_,
                "files": files_,
                "type": type_,
                "size": size_,
            }

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

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
                value_ = (mat_["value"] if "value" in mat_ and mat_["value"] is not None else None)
                if key_ and op_ and key_ in properties_:
                    fres_ = None
                    typ = (properties_[key_]["bsonType"] if key_ in properties_ else "string")
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
                    elif op_ == "like":
                        if typ == "string":
                            fres_ = {"$regex": f"^{value_}", "$options": "i"}
                    elif op_ == "contains":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = float(value_)
                        elif typ == "int":
                            fres_ = int(value_)
                        elif typ == "bool":
                            fres_ = bool(value_)
                        elif typ == "date":
                            fres_ = {
                                "$gte": datetime.strptime(
                                    f"{value_[:10]}T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                ),
                                "$lte": datetime.strptime(
                                    f"{value_[:10]}T23:59:59", "%Y-%m-%dT%H:%M:%S"
                                ),
                            }
                        else:
                            multilines_ = value_.split(
                                "\n") if value_ else None
                            if multilines_ and len(multilines_) > 1:
                                fres_ = {"$in": multilines_[:32]}
                            else:
                                fres_ = (
                                    {"$regex": value_, "$options": "i"}
                                    if value_
                                    else {"$regex": "", "$options": "i"}
                                )
                    elif op_ == "eq":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = float(value_)
                        elif typ == "int":
                            fres_ = int(value_)
                        elif typ == "bool":
                            fres_ = bool(value_)
                        elif typ == "date":
                            fres_ = {
                                "$gte": datetime.strptime(
                                    f"{value_[:10]}T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                ),
                                "$lte": datetime.strptime(
                                    f"{value_[:10]}T23:59:59", "%Y-%m-%dT%H:%M:%S"
                                ),
                            }
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
                            fres_ = {
                                "$not": {
                                    "$eq": datetime.strptime(value_[:10], "%Y-%m-%d")
                                }
                            }
                        else:
                            fres_ = (
                                {"$not": {"$regex": value_, "$options": "i"}}
                                if value_
                                else {"$not": {"$regex": "", "$options": "i"}}
                            )
                    elif op_ in ["in", "nin"]:
                        separated_ = re.split(",", value_)
                        list_ = (
                            [s.strip() for s in separated_]
                            if key_ != "_id"
                            else [ObjectId(s.strip()) for s in separated_]
                        )
                        if op_ == "in":
                            fres_ = {
                                "$in": (
                                    list_
                                    if typ != "number"
                                    else list(map(float, list_))
                                )
                            }
                        else:
                            fres_ = {
                                "$nin": (
                                    list_
                                    if typ != "number"
                                    else list(map(float, list_))
                                )
                            }
                    elif op_ == "gt":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$gt": float(value_)}
                        elif typ == "int":
                            fres_ = {"$gt": int(value_)}
                        elif typ == "date":
                            fres_ = {
                                "$gt": datetime.strptime(
                                    f"{value_[:10]}T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                )
                            }
                        else:
                            fres_ = {"$gt": value_}
                    elif op_ == "gte":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$gte": float(value_)}
                        elif typ == "int":
                            fres_ = {"$gte": int(value_)}
                        elif typ == "date":
                            fres_ = {
                                "$gte": datetime.strptime(
                                    f"{value_[:10]}T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                )
                            }
                        else:
                            fres_ = {"$gte": value_}
                    elif op_ == "lt":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$lt": float(value_)}
                        elif typ == "int":
                            fres_ = {"$lt": int(value_)}
                        elif typ == "date":
                            fres_ = {
                                "$lt": datetime.strptime(
                                    f"{value_[:10]}T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                )
                            }
                        else:
                            fres_ = {"$lt": value_}
                    elif op_ == "lte":
                        if typ in ["number", "decimal", "float"]:
                            fres_ = {"$lte": float(value_)}
                        elif typ == "int":
                            fres_ = {"$lte": int(value_)}
                        elif typ == "date":
                            fres_ = {
                                "$lte": datetime.strptime(
                                    f"{value_[:10]}T00:00:00", "%Y-%m-%dT%H:%M:%S"
                                )
                            }
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

        except Exception as exc__:
            cfg.PRINT_("!!! get filtered exception", exc__)
            return None

    def announcements_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["userindb"]
            data_ = list(
                Mongo()
                .db_["_announcement"]
                .find(
                    filter={"_tags": {"$elemMatch": {"$in": user_["_tags"]}}},
                    sort=[("ano_date", -1)],
                )
                .limit(50)
            )
            announcements_ = json.loads(JSONEncoder().encode(data_))

            return {"result": True, "data": announcements_}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def collections_f(self, obj):
        """
        docstring is in progress
        """
        try:
            user_ = obj["userindb"]
            structure_ = self.root_schemas_f("_collection")
            usr_tags_ = (
                user_["_tags"] if "_tags" in user_ and len(
                    user_["_tags"]) > 0 else []
            )
            collections_ = list(
                Mongo()
                .db_["_collection"]
                .find(filter={}, sort=[("col_priority", 1), ("col_title", 1)])
            )

            if Auth().is_manager_f(user_) or Auth().is_admin_f(user_):
                data_ = collections_
            else:
                data__ = []
                for coll_ in collections_:
                    for usr_tag_ in usr_tags_:
                        permission_ = (
                            Mongo()
                            .db_["_permission"]
                            .find_one(
                                {
                                    "per_collection_id": coll_["col_id"],
                                    "per_is_active": True,
                                    "per_tag": usr_tag_,
                                    "$or": [
                                        {"per_read": True},
                                        {"per_insert": True},
                                        {"per_update": True},
                                        {"per_delete": True},
                                    ],
                                }
                            )
                        )
                        if permission_:
                            data__.append(coll_)
                            break
                data_ = data__

            return {
                "result": True,
                "data": json.loads(JSONEncoder().encode(data_)),
                "structure": structure_,
            }

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
            usr_tags_ = (
                user_["_tags"] if "_tags" in user_ and len(
                    user_["_tags"]) > 0 else []
            )

            if (
                col_id_ == "_query"
                or Auth().is_manager_f(user_)
                or Auth().is_admin_f(user_)
            ):
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
                                "per_is_active": True,
                                "per_tag": usr_tag_,
                                "$or": [
                                    {"per_insert": True},
                                    {"per_read": True},
                                    {"per_update": True},
                                    {"per_delete": True},
                                    {"per_action": True},
                                ],
                            }
                        )
                    )
                    if permissions_:
                        permitted_ = True
                        break

            if permitted_:
                data_ = Mongo().db_["_collection"].find_one(
                    {"col_id": col_id_})
            else:
                raise AuthError(f"no collection permission {col_id_}")

            return {"result": True, "data": data_}

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def visuals_f(self, obj_):
        """
        docstring is in progress
        """
        res_ = {}
        try:
            user_ = obj_["userindb"]
            visuals_ = []
            cursor_ = (
                Mongo()
                .db_["_query"]
                .find(
                    filter={
                        "que_in_dashboard": True,
                        "_approved": True,
                        "_tags": {"$elemMatch": {"$in": user_["_tags"]}},
                    },
                    sort={"que_priority": 1, "_modified_at": -1},
                )
                .limit(16)
            )
            docs_ = json.loads(JSONEncoder().encode(
                list(cursor_))) if cursor_ else []
            for item_ in docs_:
                visuals_.append(
                    {
                        "id": item_["_id"],
                        "title": item_["que_title"],
                        "collection": item_["que_collection_id"],
                        "size": (
                            item_["que_flashcard_size"]
                            if "que_flashcard_size" in item_
                            else "M"
                        ),
                    }
                )

            res_ = {"result": True, "visuals": visuals_}

        except pymongo.errors.PyMongoError as exc__:
            res_ = Misc().notify_exception_f(exc__)

        except Exception as exc__:
            res_ = Misc().notify_exception_f(exc__)

        finally:
            return res_

    def visual_f(self, obj_):
        """
        docstring is in progress
        """
        res_, visual_ = {}, {}
        try:
            user_ = obj_["userindb"]
            id_ = ObjectId(obj_["id"])
            cursor_ = (
                Mongo()
                .db_["_query"]
                .find_one(
                    {
                        "_id": id_,
                        "_approved": True,
                        "_tags": {"$elemMatch": {"$in": user_["_tags"]}},
                    }
                )
            )

            if not cursor_:
                raise APIError(f"visual not found {id_}")

            query_f_ = self.query_f(
                {"id": id_, "key": "visual", "userindb": user_})
            if not query_f_["result"]:
                raise APIError(query_f_["msg"])

            visual_ = {
                "id": id_,
                "title": cursor_["que_title"],
                "collection": cursor_["que_collection_id"],
                "size": (
                    cursor_["que_flashcard_size"]
                    if "que_flashcard_size" in cursor_
                    else "M"
                ),
                "count": query_f_["count"],
                "data": query_f_["data"],
                "fields": query_f_["fields"],
                "schema": query_f_["schema"],
            }

            res_ = {"result": True, "visual": visual_}

        except pymongo.errors.PyMongoError as exc__:
            res_ = Misc().notify_exception_f(exc__)

        except APIError as exc__:
            res_ = Misc().notify_exception_f(exc__)

        except Exception as exc__:
            res_ = Misc().notify_exception_f(exc__)

        finally:
            return res_

    def query_f(self, obj_):
        """
        docstring is in progress
        """
        schema_, query_, data_, fields_, pivot_html_, count_, permitted_, err_ = (
            {},
            {},
            [],
            [],
            "",
            0,
            False,
            None,
        )
        files_, personalizations_, to_, orig_ = [], [], [], None
        init_res_ = {
            "result": True,
            "query": query_,
            "data": data_,
            "pivot": pivot_html_,
            "count": count_,
            "fields": fields_,
            "err": err_,
        }
        try:
            _id = obj_["id"] if "id" in obj_ else None
            if not _id:
                raise APIError("no query id defined")

            schema_ = self.root_schemas_f("_query")
            if not schema_:
                raise APIError("query schema not found")

            sched_ = "sched" in obj_ and obj_["sched"] is True
            key_ = obj_["key"] if "key" in obj_ and obj_[
                "key"] is not None else None

            type_ = (
                obj_["type"]
                if "type" in obj_ and obj_["type"] in ["live", "test"]
                else "live"
            )

            if not request:
                if key_ and key_ == cfg.SMTP_PASSWORD_:
                    orig_ = "sched"
                else:
                    raise APIError("no request detected")
            else:
                if key_ and key_ == "visual":
                    orig_ = "visual"
                elif key_ and key_ == "announce":
                    orig_ = "sched"
                else:
                    orig_ = request.base_url.replace(request.host_url, "")
                    if orig_ not in ["api/crud", f"api/get/query/{_id}"]:
                        raise AuthError("request is not authenticated")

            query_ = Mongo().db_["_query"].find_one({"_id": ObjectId(_id)})
            if not query_:
                raise APIError("query not found")

            enabled_ = "que_enabled" in query_ and query_[
                "que_enabled"] is True
            if not enabled_:
                err_ = "query is not enabled"
                raise PassException(err_)

            approved_ = "_approved" in query_ and query_["_approved"] is True
            if not approved_:
                err_ = "query needs to be approved by administrators"
                raise PassException(err_)

            que_id_ = (
                query_["que_id"]
                if "que_id" in query_ and query_["que_id"] is not None
                else None
            )
            if not que_id_:
                err_ = "query id was not defined"
                raise PassException(err_)

            _tags = (
                cfg.API_PERMISSIVE_TAGS_
                if key_ == "announce" and type_ == "test"
                else (
                    query_["_tags"]
                    if "_tags" in query_ and len(query_["_tags"]) > 0
                    else cfg.API_PERMISSIVE_TAGS_
                )
            )

            if orig_ in ["api/crud", "visual"]:
                user_ = obj_["userindb"] if "userindb" in obj_ else None
                if not user_:
                    raise APIError(f"no user defined for the query")
                usr_tags_ = (
                    user_["_tags"]
                    if "_tags" in user_ and len(user_["_tags"]) > 0
                    else []
                )
                if Auth().is_manager_f(user_) or Auth().is_admin_f(user_):
                    permitted_ = True
                else:
                    for usr_tag_ in usr_tags_:
                        if usr_tag_ in query_["_tags"]:
                            permitted_ = True
                            break
                if not permitted_:
                    raise AuthError("user is not a subscriber")

            que_collection_id_ = (
                query_["que_collection_id"] if "que_collection_id" in query_ else None
            )
            if not que_collection_id_:
                raise APIError("query collection not defined")

            collection_ = (
                Mongo().db_["_collection"].find_one(
                    {"col_id": que_collection_id_})
            )
            if not collection_:
                raise APIError("query collection not found")

            structure_ = (
                collection_[
                    "col_structure"] if "col_structure" in collection_ else None
            )
            if not structure_:
                raise APIError("collection structure not found")

            properties_ = (
                structure_[
                    "properties"] if "properties" in structure_ else None
            )
            if not properties_:
                raise APIError("properties not found in structure")

            que_aggregate_ = (
                query_["que_aggregate"]
                if "que_aggregate" in query_ and len(query_["que_aggregate"]) > 0
                else None
            )
            if not que_aggregate_:
                raise PassException("no query defined yet")

            queries_ = structure_[
                "queries"] if "queries" in structure_ else None
            if not queries_:
                err_ = "queries not defined in the structure"
                raise PassException(err_)

            query_allowed_ = "query" in queries_ and queries_["query"] is True
            if not query_allowed_:
                err_ = "query not allowed for the collection"
                raise PassException(err_)

            update_allowed_ = "cronjob" in queries_ and queries_[
                "cronjob"] is True

            updatables_ = (
                queries_["updatables"]
                if "updatables" in queries_ and len(queries_["updatables"]) > 0
                else None
            )

            # H-4: re-validate at run time so pipelines stored before the allowlist cannot run
            validate_ = Misc().validate_pipeline_f(que_aggregate_)
            if not validate_["result"]:
                raise APIError(validate_["msg"])

            match_exists_, set_, aggregate_ = False, None, []
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
                aggregate_.append(agg_)

            attach_excel_ = True
            attach_json_ = set_ and "json" in set_ and set_["json"] is True
            attach_csv_ = set_ and "csv" in set_ and set_["csv"] is True
            attach_html_ = set_ and "html" in set_ and set_["html"] is True
            attach_pivots_ = set_ and "pivot" in set_ and set_["pivot"] and len(set_["pivot"]) > 0

            if orig_ == "api/crud":
                limit_ = obj_["limit"] if "limit" in obj_ and obj_["limit"] > 0 else cfg.API_QUERY_PAGE_SIZE_
                aggregate_.append({"$limit": limit_})
            elif orig_ == "visual":
                aggregate_.append({"$limit": cfg.API_DEFAULT_VISUAL_LIMIT_})
            else:
                aggregate_.append({"$limit": cfg.API_DEFAULT_AGGREGATION_LIMIT_})

            pd.options.display.float_format = "{:,.2f}".format

            # PRIMARY FETCH
            cursor_ = Mongo().db_[f"{que_collection_id_}_data"].aggregate(aggregate_)

            # SECONDARY FETCH OPTIONAL
            # collection_secondary_ = Mongo().db_.get_collection(f"{que_collection_id_}_data", read_preference=pymongo.ReadPreference.SECONDARY, read_concern=ReadConcern("majority"))
            # cursor_ = collection_secondary_.aggregate(aggregate_)

            data_ = json.loads(JSONEncoder().encode(list(cursor_)))

            count_ = len(data_)
            df_raw_ = pd.DataFrame(data_).fillna("") if data_ else None

            if df_raw_ is None or count_ == 0:
                err_ = "no records were matched with the query"
                raise PassException(err_)

            html_ = "<style>\
                .etable { border-spacing: 0; border-collapse: collapse;} \
                .etable td,th { padding: 7px; border: 1px solid #999;} \
                .pivot-class { max-width: 90%; margin-top: 16px; border-collapse: collapse;} \
                .pivot-class td, .pivot-class th { padding: 5px; padding-left: 10px; padding-right: 10px; border: 1px solid #aaa; text-align: center;} \
                .pivot-class th:first-child { text-align: left !important;} \
                </style>"

            html_ += (
                query_["que_message_body"]
                if "que_message_body" in query_
                and query_["que_message_body"] is not None
                else ""
            )

            if attach_pivots_:
                pivots_ = set_["pivot"]
                for pivot_ in pivots_:
                    if not ("enabled" in pivot_ and pivot_["enabled"] is True):
                        continue

                    pivot_values_ = (
                        pivot_["values"]
                        if "values" in pivot_ and len(pivot_["values"]) > 0
                        else []
                    )
                    pivot_index_ = (
                        pivot_["index"]
                        if "index" in pivot_ and len(pivot_["index"]) > 0
                        else []
                    )
                    pivot_columns_ = (
                        pivot_["columns"]
                        if "columns" in pivot_ and len(pivot_["columns"]) > 0
                        else []
                    )
                    pivot_aggfunc_ = pivot_[
                        "aggfunc"] if "aggfunc" in pivot_ else None
                    pivot_stack_ = "stack" in pivot_ and pivot_[
                        "stack"] is True
                    pivot_margins_ = "margins" in pivot_ and pivot_[
                        "margins"] is True

                    if not (pivot_values_ and pivot_index_ and pivot_columns_ and pivot_aggfunc_):
                        continue

                    pivot_table_ = pd.pivot_table(
                        df_raw_,
                        values=pivot_values_,
                        index=pivot_index_,
                        columns=pivot_columns_,
                        aggfunc=pivot_aggfunc_,
                        fill_value=0,
                        margins=pivot_margins_,
                        margins_name="Total",
                        dropna=False,
                    )

                    if pivot_stack_:
                        pivot_table_ = pivot_table_.stack()

                    phtml_ = (
                        pivot_table_.to_html(
                            table_id="pivot-table", classes="pivot-class")
                        .replace(".0<", "<")
                        .replace(".00<", "<")
                    )
                    pivot_html_ += phtml_
                    html_ += f"<p>{phtml_}</p>"

            if sched_ and orig_ == "sched":
                que_title_ = query_[
                    "que_title"] if "que_title" in query_ else _id

                count_ = len(df_raw_.index)

                if attach_html_:
                    html_ += f"<p>{df_raw_.to_html(index=False, max_rows=cfg.HTML_TABLE_MAX_ROWS_, max_cols=cfg.HTML_TABLE_MAX_COLS_, border=1, justify='left', classes='etable')}</p>"
                    html_ = f"<p>{html_}</p>"

                if attach_excel_:
                    file_excel_ = f"{cfg.API_TEMPFILE_PATH_}/query-{_id}-{Misc().get_timestamp_f()}.xlsx"
                    df_raw_.to_excel(
                        file_excel_,
                        sheet_name=_id,
                        engine="xlsxwriter",
                        header=True,
                        index=False,
                    )
                    files_.append({"name": file_excel_, "type": "xlsx"})

                if attach_json_:
                    file_json_ = f"{cfg.API_TEMPFILE_PATH_}/query-{_id}-{Misc().get_timestamp_f()}.json"
                    df_raw_.to_json(
                        file_json_,
                        date_format="iso",
                        orient="records",
                        force_ascii=False,
                    )
                    files_.append({"name": file_json_, "type": "json"})

                if attach_csv_:
                    file_csv_ = f"{cfg.API_TEMPFILE_PATH_}/query-{_id}-{Misc().get_timestamp_f()}.csv"
                    df_raw_.to_csv(file_csv_, encoding="utf-8", sep=";")
                    files_.append({"name": file_csv_, "type": "csv"})

                if count_ > 0:
                    email_sent_ = Email().send_email_f(
                        {
                            "op": "query",
                            "que_id": que_id_,
                            "html": html_,
                            "subject": que_title_,
                            "files": files_,
                            "tags": _tags,
                        }
                    )
                    if not email_sent_["result"]:
                        raise APIError(email_sent_["msg"])

            return (
                {
                    "result": True,
                    "query": query_,
                    "data": data_,
                    "pivot": pivot_html_,
                    "count": count_,
                    "fields": fields_,
                    "schema": schema_,
                    "err": err_,
                }
                if key_ != "announce"
                else {
                    "result": True,
                    "err": err_,
                }
            )

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except pymongo.errors.PyMongoError as exc__:
            init_res_["result"] = False
            init_res_["schema"] = {}
            init_res_["pivot"] = ""
            init_res_["query"], init_res_["fields"] = [], []
            init_res_["err"] = str(exc__)
            return init_res_

        except PassException as exc__:
            init_res_["schema"] = schema_
            init_res_["pivot"] = ""
            init_res_["query"] = query_
            init_res_["err"] = str(exc__)
            return init_res_

        except Exception as exc__:
            init_res_["result"] = False
            init_res_["schema"] = {}
            init_res_["pivot"] = ""
            init_res_["query"] = query_
            init_res_["err"] = str(exc__)
            return init_res_

    def job_f(self, obj_):
        """
        docstring is in progress
        """
        count_, err_, job_ = 0, None, {}
        init_res_ = {"result": True, "count": count_, "err": err_}
        try:
            _id = str(obj_["id"]) if "id" in obj_ else None
            if not _id:
                raise APIError("no job defined")

            run_ = "run" in obj_ and obj_["run"] is True

            schema_ = self.root_schemas_f("_job")
            if not schema_:
                raise APIError("job schema not found")

            job_ = Mongo().db_["_job"].find_one({"_id": ObjectId(_id)})
            if not job_:
                raise APIError("job not found")

            Mongo().db_["_job"].update_one(
                {"_id": ObjectId(_id)},
                {
                    "$set": {"job_run_date": Misc().get_now_f()},
                    "$inc": {"job_run_count": 1},
                },
            )

            job_collection_id_ = (
                job_["job_collection_id"] if "job_collection_id" in job_ else None
            )
            if not job_collection_id_:
                raise APIError("job collection not defined")

            job_name_ = job_["job_name"] if "job_name" in job_ else _id

            collection_ = (
                Mongo().db_["_collection"].find_one(
                    {"col_id": job_collection_id_})
            )
            if not collection_:
                raise APIError("query collection not found")

            structure_ = (
                collection_[
                    "col_structure"] if "col_structure" in collection_ else None
            )
            if not structure_:
                raise APIError("collection structure not found")

            properties_ = (
                structure_[
                    "properties"] if "properties" in structure_ else None
            )
            if not properties_:
                raise APIError("properties not found in structure")

            queries_ = structure_[
                "queries"] if "queries" in structure_ else None
            if not queries_:
                err_ = "queries not defined in the structure"
                raise PassException(err_)

            job_allowed_ = "query" in queries_ and queries_["query"] is True
            if not job_allowed_:
                err_ = "job not allowed for the collection"
                raise PassException(err_)

            job_aggregate_ = (
                job_["job_aggregate"]
                if "job_aggregate" in job_ and len(job_["job_aggregate"]) > 0
                else None
            )
            if not job_aggregate_:
                raise PassException("no job defined yet")

            update_allowed_ = "cronjob" in queries_ and queries_[
                "cronjob"] is True
            updatables_ = (
                queries_["updatables"]
                if "updatables" in queries_ and len(queries_["updatables"]) > 0
                else None
            )

            match_exists_, set_ = False, None
            for agg_ in job_aggregate_:
                if "$limit" in agg_ or "$skip" in agg_:
                    continue
                if "$match" in agg_:
                    match_exists_ = True
                if "$set" in agg_:
                    set_ = agg_["$set"]

            if not update_allowed_:
                err_ = "update not allowed on the collection"
                raise PassException(err_)

            if not updatables_:
                err_ = "no updatable fields found in the collection structure"
                raise PassException(err_)

            if not match_exists_:
                err_ = "no match found in the update query"
                raise PassException(err_)

            if not set_:
                err_ = "no set found in the update query"
                raise PassException(err_)

            enabled_ = "job_enabled" in job_ and job_["job_enabled"] is True
            if not enabled_:
                err_ = "job is not enabled"
                raise PassException(err_)

            approved_ = "_approved" in job_ and job_["_approved"] is True
            if not approved_:
                err_ = "job needs to be approved by the administrators"
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
                err_ = "no updateable field found in set"
                raise PassException(err_)

            """
            job must be run manually
            """
            if not run_:
                raise PassException("")

            validate_ = Misc().validate_pipeline_f(job_aggregate_)
            if not validate_["result"]:
                raise APIError(validate_["msg"])

            aggregate_update_ = []
            for agg_ in job_aggregate_:
                if (
                    "$project" in agg_
                    or "$get" in agg_
                    or "$set" in agg_
                    or "$unset" in agg_
                ):
                    continue
                aggregate_update_.append(agg_)

            aggregate_update_.append({"$project": {"_id": "$_id"}})
            cursor_ = Mongo().db_[f"{job_collection_id_}_data"].aggregate(aggregate_update_)

            if not cursor_:
                raise PassException("")

            data_ = json.loads(JSONEncoder().encode(list(cursor_)))
            ids_ = [ObjectId(doc_["_id"]) for doc_ in data_]

            if len(ids_) == 0:
                raise PassException("")

            personalizations_ = []

            get_users_from_tags_f_ = Misc(
            ).get_users_from_tags_f(["#JobAdmins"])

            if not get_users_from_tags_f_["result"]:
                raise APIError(
                    f"personalizations error: {get_users_from_tags_f_['msg']}"
                )
            personalizations_ = (
                get_users_from_tags_f_["personalizations"]
                if "personalizations" in get_users_from_tags_f_
                else []
            )

            if len(ids_) > cfg.API_JOB_UPDATE_LIMIT_:
                html_ = f"<p>Hi,</p><p>The limit of the updated documents count has been exceeded for the job '{job_name_}'.<br />Possible affected number of documents: {len(ids_)} [{cfg.API_JOB_UPDATE_LIMIT_}].</p><p>Aggregation:<br />{str(aggregate_update_)}</p>"
                email_sent_ = Email().send_email_f(
                    {
                        "op": "job",
                        "personalizations": personalizations_,
                        "html": html_,
                        "subject": f"Job Alert [{job_name_}]",
                    }
                )
                if not email_sent_["result"]:
                    raise PassException(email_sent_["msg"])

                err_ = f"job update limit exceeded [{len(ids_)}]"
                raise PassException(err_)

            set__["_modified_at"] = Misc().get_now_f()
            update_many_ = (
                Mongo()
                .db_[f"{job_collection_id_}_data"]
                .update_many({"_id": {"$in": ids_}}, {"$set": set__})
            )
            count_ = update_many_.matched_count

            Mongo().db_["_job"].update_one(
                {"_id": ObjectId(_id)},
                {
                    "$set": {"job_success_date": Misc().get_now_f()},
                    "$inc": {"job_success_count": 1},
                },
            )

            Mongo().db_["_joblog"].insert_one(
                {
                    "jol_id": ObjectId(str(_id)),
                    "jol_name": job_name_,
                    "jol_run_date": Misc().get_now_f(),
                    "jol_count": count_,
                    "jol_ids": ids_,
                    "jol_set": set__,
                }
            )

            html_ = f"<p>Hi,</p><p>The job '{job_name_}' was completed successfully.<br />Affected number of documents: {len(ids_)}.</p><p>Set:<br />{str(set__)}</p>"
            email_sent_ = Email().send_email_f(
                {
                    "op": "job",
                    "personalizations": personalizations_,
                    "html": html_,
                    "subject": f"Job Done [{job_name_}]",
                }
            )
            if not email_sent_["result"]:
                raise PassException(email_sent_["msg"])

            return {
                "result": True,
                "count": count_,
                "job": job_,
                "schema": schema_,
                "err": err_,
            }

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except pymongo.errors.PyMongoError as exc__:
            init_res_["result"] = False
            init_res_["schema"] = {}
            init_res_["count"] = count_
            init_res_["job"] = job_
            init_res_["err"] = str(exc__)
            return init_res_

        except PassException as exc__:
            init_res_["result"] = True
            init_res_["count"] = count_
            init_res_["schema"] = schema_
            init_res_["job"] = job_
            init_res_["err"] = str(exc__)
            return init_res_

        except Exception as exc__:
            init_res_["result"] = False
            init_res_["schema"] = {}
            init_res_["count"] = count_
            init_res_["job"] = job_
            init_res_["err"] = str(exc__)
            return init_res_

    def read_f(self, input_):
        """
        docstring is in progress
        """
        try:
            user_ = input_["user"]
            limit_ = (
                input_["limit"] if "limit" in input_ and input_[
                    "limit"] > 0 else 50
            )
            page_ = input_["page"]
            collection_id_ = input_["collection"]
            projection_ = input_["projection"]
            group_ = "group" in input_ and input_["group"] is True
            skip_ = limit_ * (page_ - 1)
            match_ = (
                input_["match"]
                if "match" in input_ and len(input_["match"]) > 0
                else []
            )
            selections_ = (
                input_["selections"]
                if "selections" in input_ and input_["selections"] is not None
                else {}
            )
            allowed_cols_ = ["_collection", "_query"]
            is_crud_ = collection_id_[:1] != "_"
            selected_ = {}

            if (
                collection_id_ not in allowed_cols_
                and not Auth().is_manager_f(user_)
                and not Auth().is_admin_f(user_)
                and not is_crud_
            ):
                raise AuthError(
                    f"collection is not allowed to read: {collection_id_}")

            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            collation_ = (
                {"locale": user_["locale"]}
                if user_ and "locale" in user_
                else {"locale": cfg.DEFAULT_LOCALE_}
            )

            cursor_ = (
                Mongo().db_["_collection"].find_one({"col_id": collection_id_})
                if is_crud_
                else self.root_schemas_f(f"{collection_id_}")
            )
            if not cursor_:
                raise APIError(
                    f"collection not found to read: {collection_id_}")

            structure_ = cursor_["col_structure"] if is_crud_ else cursor_
            properties_ = (
                structure_[
                    "properties"] if "properties" in structure_ else None
            )
            if not properties_:
                raise AuthError(f"properties not found {collection_id_}")

            user_tags_ = (
                user_["_tags"] if "_tags" in user_ and len(
                    user_["_tags"]) > 0 else []
            )
            user_actions_ = []
            actions_ = (
                structure_["actions"]
                if "actions" in structure_ and len(structure_["actions"]) > 0
                else []
            )
            if actions_:
                for action_ in actions_:
                    action_tags_ = (
                        action_["_tags"]
                        if "_tags" in action_ and len(action_["_tags"]) > 0
                        else []
                    )
                    if action_tags_ and user_tags_:
                        found_ = [
                            item_ for item_ in action_tags_ if item_ in user_tags_
                        ]
                        if found_:
                            user_actions_.append(action_)

            reconfig_ = (
                cursor_["_reconfig_req"]
                if "_reconfig_req" in cursor_ and cursor_["_reconfig_req"] is True
                else False
            )
            get_filtered_ = self.get_filtered_f(
                {"match": match_, "properties": properties_}
            )

            if collection_id_ == "_query" and not (
                Auth().is_manager_f(user_) or Auth().is_admin_f(user_)
            ):
                get_filtered_["_tags"] = {"$elemMatch": {"$in": user_tags_}}

            for property_ in selections_:
                sel_ = []
                for item_ in selections_[property_]:
                    if item_["value"] is True:
                        sel_.append(item_["id"])
                if len(sel_) > 0:
                    get_filtered_[property_] = {"$in": sel_}

            sort_ = (
                input_["sort"]
                if "sort" in input_ and input_["sort"]
                else (
                    structure_["sort"]
                    if "sort" in structure_ and structure_["sort"]
                    else ("_modified_at", -1)
                )
            )

            if group_:
                group__ = {"_id": {}}
                project__ = {"_id": 0}
                sort__ = {}
                for item_ in projection_:
                    group__["_id"][item_] = f"${item_}"
                    project__[item_] = f"$_id.{item_}"
                    sort__[item_] = 1
                group__["count"] = {"$sum": 1}
                project__["count"] = "$count"
                cursor_ = (
                    Mongo()
                    .db_[collection_]
                    .aggregate(
                        [
                            {"$match": get_filtered_},
                            {"$sort": sort__},
                            {"$limit": limit_},
                            {"$group": group__},
                            {"$project": project__},
                        ]
                    )
                )
            else:
                aggregate_ = []
                links_ = (
                    structure_["links"]
                    if "links" in structure_ and len(structure_["links"]) > 0
                    else []
                )
                link_collections_ = []
                for link_ in links_:
                    link_listed_ = "listed" in link_ and link_[
                        "listed"] is True
                    if not link_listed_:
                        continue
                    link_collection_ = link_["collection"]
                    link_get_ = link_["get"]
                    link_sum_ = (
                        link_["sum"]
                        if "sum" in link_ and link_["sum"] is not None
                        else None
                    )
                    fo__ = (
                        Mongo()
                        .db_["_collection"]
                        .find_one({"col_id": link_collection_})
                    )
                    if not fo__:
                        continue
                    fo_structure_ = (
                        fo__["col_structure"] if "col_structure" in fo__ else None
                    )
                    if not fo_structure_:
                        continue
                    parents__ = (
                        fo_structure_["parents"]
                        if "parents" in fo_structure_
                        and len(fo_structure_["parents"]) > 0
                        else None
                    )
                    if not parents__:
                        continue
                    for parent__ in parents__:
                        pcol_ = (
                            parent__[
                                "collection"] if "collection" in parent__ else None
                        )
                        if not pcol_:
                            continue
                        if pcol_ != collection_id_:
                            continue
                        pmatches__ = (
                            parent__["match"]
                            if "match" in parent__ and len(parent__["match"]) > 0
                            else None
                        )
                        if not pmatches__:
                            continue
                        pipeline_match_ = []
                        let_ = {}
                        for pmatch__ in pmatches__:
                            let_[
                                f"p_{pmatch__['key']}"] = f"${pmatch__['value']}"
                            pipeline_match_.append(
                                {
                                    "$eq": [
                                        f"${pmatch__['key']}",
                                        f"$$p_{pmatch__['key']}",
                                    ]
                                }
                            )
                        group_id_ = {}
                        group_id_[link_get_] = f"${link_get_}"
                        if not pipeline_match_:
                            continue
                        lookup_ = {
                            "from": f"{link_collection_}_data",
                            "let": let_,
                            "pipeline": [
                                {"$match": {"$expr": {"$and": pipeline_match_}}},
                                {
                                    "$group": {
                                        "_id": group_id_,
                                        "count": {"$sum": 1},
                                        "sum": {
                                            "$sum": f"${link_sum_}" if link_sum_ else 1
                                        },
                                    }
                                },
                                {"$replaceWith": {
                                    "$mergeObjects": ["$$ROOT", "$_id"]}},
                                {"$unset": ["_id"]},
                            ],
                            "as": f"_link_{link_collection_}",
                        }
                        aggregate_.append({"$lookup": lookup_})
                        link_collections_.append(link_collection_)

                aggregate_.append({"$match": get_filtered_})
                aggregate_.append({"$sort": sort_})
                aggregate_.append({"$skip": skip_})
                aggregate_.append({"$limit": limit_})
                if projection_:
                    aggregate_.append({"$project": projection_})

                cursor_ = Mongo().db_[collection_].aggregate(aggregate_)

            docs_ = (
                json.loads(JSONEncoder().encode(list(cursor_)))[:limit_]
                if cursor_
                else []
            )
            count_ = Mongo().db_[collection_].count_documents(get_filtered_)

            for property_ in properties_:
                prop_ = properties_[property_]
                if "reminder" in prop_ and prop_["reminder"] is True:
                    for ix_, doc_ in enumerate(docs_):
                        if (
                            property_ in doc_
                            and doc_[property_] is not None
                            and len(str(doc_[property_])) > 0
                        ):
                            docs_[ix_]["_reminder"] = True
                            docs_[ix_]["_note"] = (
                                f"{docs_[ix_]['_note']}<br />{doc_[property_]}"
                                if "_note" in docs_[ix_] and docs_[ix_]["_note"] != ""
                                else doc_[property_]
                            )
                if "selection" in prop_ and prop_["selection"] is True:
                    selected_[property_] = []
                    cursor_ = (
                        Mongo()
                        .db_[collection_]
                        .aggregate(
                            [
                                {"$match": get_filtered_},
                                {
                                    "$group": {
                                        "_id": f"${property_}",
                                        "count": {"$sum": 1},
                                    }
                                },
                                {"$sort": {"_id": 1}},
                            ]
                        )
                    )
                    grps_ = (
                        json.loads(JSONEncoder().encode(list(cursor_)))[:100]
                        if cursor_
                        else []
                    )

                    for item_ in grps_:
                        value__ = False
                        if selections_ and property_ in selections_:
                            for selection_ in selections_[property_]:
                                if (
                                    selection_["id"] is not None
                                    and selection_["id"] == item_["_id"]
                                ):
                                    value__ = (
                                        "value" in selection_
                                        and selection_["value"] is True
                                    )
                                    break
                        if item_["_id"] is not None:
                            selected_[property_].append(
                                {"id": item_["_id"], "value": value__}
                            )

            return {
                "result": True,
                "data": docs_,
                "count": count_,
                "structure": structure_,
                "reconfig": reconfig_,
                "selections": selections_,
                "selected": selected_,
                "actions": user_actions_,
            }

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

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
                required_ = structure_["required"] if "required" in structure_ and len(structure_["required"]) > 0 else None
                properties_ = Misc().properties_cleaner_f(properties_, required_)

                if required_:
                    break_ = False
                    err_ = None
                    for req_ in required_:
                        if req_ not in properties_:
                            break_ = True
                            err_ = f"{req_} is required but not found in the structure"
                            break
                    if break_:
                        raise APIError(err_)

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
                            if ix_ not in properties_ and ix_ not in [
                                "_created_at",
                                "_modified_at",
                                "_created_by",
                                "_modified_by",
                                "_approved",
                            ]:
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
                        Mongo().db_[collection_].create_index(
                            uqs, unique=True, name=uq_name_
                        )

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
            schemavalidate_ = self.crudschema_validate_f(
                {"collection": collection_, "structure": structure_}
            )
            if not schemavalidate_["result"]:
                raise APIError(schemavalidate_["msg"])

            return {"result": True}

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def savejob_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            _id = obj_["id"] if "id" in obj_ and obj_[
                "id"] is not None else None
            if not _id:
                raise APIError("job not provided")

            aggregate_ = (
                obj_["aggregate"] if "aggregate" in obj_ and obj_[
                    "aggregate"] else None
            )
            if not aggregate_:
                raise APIError("no aggregation provided")

            job_ = Mongo().db_["_job"].find_one({"_id": ObjectId(_id)})
            if not job_:
                raise APIError("job not found")

            job_collection_id_ = (
                job_["job_collection_id"]
                if "job_collection_id" in job_ and job_["job_collection_id"] is not None
                else None
            )
            if not job_collection_id_:
                raise APIError("no collection provided")

            user_ = obj_["userindb"] if "userindb" in obj_ and obj_["userindb"] else None
            if not user_:
                raise AuthError("user not found")
            usr_tags_ = (
                user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else [])

            if not Auth().is_admin_f(user_):
                raise AuthError("no permission to save job")

            permission_ = (
                Mongo()
                .db_["_permission"]
                .find_one(
                    {
                        "per_collection_id": job_collection_id_,
                        "per_is_active": True,
                        "per_query": True,
                    }
                )
            )
            if not permission_:
                raise AuthError("no permission to save job")

            doc_ = {
                "job_aggregate": aggregate_,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_["usr_id"],
                "_approved": False,
            }

            approved_ = "approved" in obj_ and obj_["approved"] is True
            if approved_:
                if not Auth().is_admin_f(user_):
                    raise AuthError("no permission to approve")
                doc_["_approved"] = True
                doc_["_approved_at"] = Misc().get_now_f()
                doc_["_approved_by"] = user_["usr_id"]

            Mongo().db_["_job"].update_one(
                {"_id": ObjectId(_id)}, {"$set": doc_, "$inc": {
                    "_modified_count": 1}}
            )

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def savequery_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            _id = obj_["id"] if "id" in obj_ and obj_[
                "id"] is not None else None
            if not _id:
                raise APIError("query not found")

            query_ = Mongo().db_["_query"].find_one({"_id": ObjectId(_id)})
            if not query_:
                raise APIError("query not found")

            que_collection_id_ = (
                query_["que_collection_id"]
                if "que_collection_id" in query_
                and query_["que_collection_id"] is not None
                else None
            )
            if not que_collection_id_:
                raise APIError("no collection provided")

            aggregate_ = (
                obj_["aggregate"] if "aggregate" in obj_ and obj_[
                    "aggregate"] else None
            )
            if not aggregate_:
                raise APIError("no aggregation provided")

            user_ = (
                obj_["userindb"] if "userindb" in obj_ and obj_[
                    "userindb"] else None
            )
            if not user_:
                raise AuthError("user not found")
            usr_tags_ = (
                user_["_tags"] if "_tags" in user_ and len(
                    user_["_tags"]) > 0 else []
            )

            if not Auth().is_qadmin_f(user_):
                permission_ = (
                    Mongo()
                    .db_["_permission"]
                    .find_one(
                        {
                            "per_collection_id": que_collection_id_,
                            "per_is_active": True,
                            "per_tag": {"$in": usr_tags_},
                            "per_query": True,
                        }
                    )
                )
                if not permission_:
                    raise AuthError("no permission to save query")

            # H-4: only allowlisted stages and operators may be stored
            validate_ = Misc().validate_pipeline_f(aggregate_)
            if not validate_["result"]:
                raise APIError(validate_["msg"])

            doc_ = {
                "que_aggregate": aggregate_,
                "_modified_at": Misc().get_now_f(),
                "_modified_by": user_["usr_id"],
                "_approved": False,
            }

            approved_ = "approved" in obj_ and obj_["approved"] is True
            if approved_:
                if not Auth().is_qadmin_f(user_):
                    raise AuthError("no permission to approve query")

                doc_["_approved"] = True
                doc_["_approved_at"] = Misc().get_now_f()
                doc_["_approved_by"] = user_["usr_id"]

            Mongo().db_["_query"].update_one({"_id": ObjectId(_id)}, {"$set": doc_, "$inc": {"_modified_count": 1}})

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
            col_id_ = (
                obj["collection"]
                if "collection" in obj and obj["collection"] is not None
                else None
            )
            structure_ = (
                obj["structure"]
                if "structure" in obj and obj["structure"] is not None
                else None
            )
            user_ = obj["user"] if "user" in obj and obj["user"] is not None else None

            if not user_:
                raise APIError("user not found")

            if not Auth().is_admin_f(user_):
                raise APIError("no permission to modify this schema")

            if not structure_:
                raise APIError("structure not found")

            if not col_id_:
                raise APIError("collection not found")

            properties_ = (
                structure_[
                    "properties"] if "properties" in structure_ else None
            )
            if not properties_:
                raise APIError("no properties found")

            arr_ = [
                str_
                for str_ in structure_
                if str_ not in cfg.STRUCTURE_KEYS_ and str_ not in cfg.STRUCTURE_KEYS_OPTIN_
            ]
            if len(arr_) > 0:
                raise APIError(
                    f"some structure keys are invalid: {','.join(arr_)}")

            arr_ = [str_ for str_ in structure_ if str_ in cfg.STRUCTURE_KEYS_]
            if len(arr_) != len(cfg.STRUCTURE_KEYS_):
                raise APIError(
                    f"some structure keys are missing; expected: {','.join(cfg.STRUCTURE_KEYS_)}, considered: {','.join(arr_)}"
                )

            for property_ in properties_:
                prop_ = properties_[property_]
                arr_ = [key_ for key_ in prop_ if key_ in cfg.PROP_KEYS_]
                if len(arr_) != len(cfg.PROP_KEYS_):
                    raise APIError(
                        f"some keys are missing in property {property_}; expected: {','.join(cfg.PROP_KEYS_)}, considered: {','.join(arr_)}"
                    )

            Mongo().db_["_collection"].update_one(
                {"col_id": col_id_},
                {
                    "$set": {
                        "col_structure": structure_,
                        "_modified_at": Misc().get_now_f(),
                        "_modified_by": user_["usr_id"],
                    },
                    "$inc": {"_modified_count": 1},
                },
            )

            func_ = self.crudschema_validate_f(
                {"collection": f"{col_id_}_data", "structure": structure_}
            )
            if not func_["result"]:
                raise APIError(func_["msg"])

            for property_ in properties_:
                prop_ = properties_[property_]
                if (
                    prop_["bsonType"] in ["int", "number",
                                          "float", "decimal", "string"]
                    and "counter" in prop_
                    and prop_["counter"] is True
                ):
                    counter_name_ = f"{property_.upper()}_COUNTER"
                    find_one_ = Mongo().db_["_kv"].find_one(
                        {"kav_key": counter_name_})
                    if not find_one_:
                        initialno__ = (
                            "0"
                            if prop_["bsonType"]
                            in ["int", "number", "float", "decimal"]
                            else ""
                        )
                        initialas__ = (
                            "string" if prop_[
                                "bsonType"] == "string" else "int"
                        )
                        doc_ = {
                            "kav_key": counter_name_,
                            "kav_value": initialno__,
                            "kav_as": initialas__,
                        }
                        doc_["_created_at"] = doc_[
                            "_modified_at"] = Misc().get_now_f()
                        doc_["_created_by"] = doc_[
                            "_modified_by"] = user_["usr_id"]
                        Mongo().db_["_kv"].insert_one(doc_)

            return {"result": True}

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
            if not _id:
                raise APIError("document id is required to update")
            allowmatch_ = [
                rule_ for rule_ in (obj["match"] if "match" in obj and obj["match"] else [])
                if isinstance(rule_, dict) and "key" in rule_ and "op" in rule_
            ]
            link_ = obj["link"] if "link" in obj and obj["link"] is not None else None
            linked_ = (
                obj["linked"] if "linked" in obj and obj["linked"] is not None else None
            )
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            col_check_ = self.inner_collection_f(collection_id_)

            if collection_id_ in cfg.PROTECTED_COLLS_:
                raise APIError("collection is protected")

            if not col_check_["result"]:
                raise APIError("collection not found")

            is_crud_ = collection_id_[:1] != "_"
            if not is_crud_:
                schemavalidate_ = self.nocrudschema_validate_f(
                    {"collection": collection_id_}
                )
                if not schemavalidate_["result"]:
                    raise APIError(schemavalidate_["msg"])

            # H-5: the row filter granted by the permission must apply to id-based updates too
            match_ = {"_id": _id}
            if allowmatch_:
                props_ = self.get_properties_f(collection_id_)
                if not props_["result"]:
                    raise APIError(props_["msg"])
                filtered_ = self.get_filtered_f({"match": allowmatch_, "properties": props_["properties"], "data": doc})
                if filtered_ is None:
                    raise APIError("invalid permission filter")
                if filtered_:
                    match_ = {"$and": [{"_id": _id}, filtered_]}

            # H-7: only administrators may grant or touch administrator tags
            if collection_id_ == "_user" and not Auth().is_admin_f(user_):
                existing_ = Mongo().db_["_user"].find_one({"_id": _id})
                existing_tags_ = existing_["_tags"] if existing_ and "_tags" in existing_ and existing_["_tags"] else []
                new_tags_ = doc["_tags"] if "_tags" in doc and doc["_tags"] else []
                if any(tag_ in cfg.API_ADMIN_TAGS_ for tag_ in list(existing_tags_) + list(new_tags_)):
                    raise APIError("only administrators can manage administrator users")
                if existing_ and user_ and existing_.get("usr_id") == user_.get("usr_id") and "_tags" in doc:
                    raise APIError("users cannot change their own tags")

            doc = Misc().set_strip_doc_f(doc)

            doc_ = {}
            for item in doc:
                if item[:1] != "_" or item in Misc().get_except_underdashes():
                    doc_[item] = doc[item] if doc[item] is not None else None

            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = (
                user_["email"] if user_ and "email" in user_ else None
            )

            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            update_one_ = Mongo().db_[collection_].update_one(
                match_, {"$set": doc_, "$inc": {"_modified_count": 1}})
            if update_one_.matched_count == 0:
                raise APIError("record not found or not permitted")

            if is_crud_ and link_ and linked_:
                link_f_ = self.link_f(
                    {
                        "op": "update",
                        "source": collection_id_,
                        "_id": str(_id),
                        "link": link_,
                        "linked": linked_,
                        "data": doc_,
                        "user": user_,
                    }
                )
                if not link_f_["result"]:
                    raise AppException(link_f_["msg"])

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": collection_id_,
                    "op": "update",
                    "user": user_["email"] if user_ else None,
                    "document": doc_,
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AppException as exc__:
            return Misc().app_exception_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def remove_f(self, obj):
        """
        docstring is in progress
        """
        try:
            doc_ = obj["doc"]
            _id = ObjectId(doc_["_id"]) if "_id" in doc_ else None
            if not _id:
                raise APIError("document id is required to remove")
            allowmatch_ = [
                rule_ for rule_ in (obj["match"] if "match" in obj and obj["match"] else [])
                if isinstance(rule_, dict) and "key" in rule_ and "op" in rule_
            ]
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]

            if not cfg.API_DELETE_ALLOWED_ and not Auth().is_admin_f(user_):
                raise APIError("delete operation is not allowed")

            if collection_id_ not in cfg.PROTECTED_INSDEL_EXC_COLLS_:
                if collection_id_ in cfg.PROTECTED_COLLS_:
                    raise APIError("collection is protected to delete")

            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            # H-5: apply the permission row filter to id-based removals
            match_ = {"_id": _id}
            if allowmatch_:
                props_ = self.get_properties_f(collection_id_)
                if not props_["result"]:
                    raise APIError(props_["msg"])
                filtered_ = self.get_filtered_f({"match": allowmatch_, "properties": props_["properties"], "data": doc_})
                if filtered_ is None:
                    raise APIError("invalid permission filter")
                if filtered_:
                    match_ = {"$and": [{"_id": _id}, filtered_]}

            if collection_id_ == "_user" and not Auth().is_admin_f(user_):
                existing_ = Mongo().db_["_user"].find_one({"_id": _id})
                existing_tags_ = existing_["_tags"] if existing_ and "_tags" in existing_ and existing_["_tags"] else []
                if any(tag_ in cfg.API_ADMIN_TAGS_ for tag_ in existing_tags_):
                    raise APIError("only administrators can manage administrator users")

            doc_["_removed_at"] = Misc().get_now_f()
            doc_["_removed_by"] = user_[
                "email"] if user_ and "email" in user_ else None

            delete_one_ = Mongo().db_[collection_].delete_one(match_)
            if delete_one_.deleted_count == 0:
                raise APIError("record not found or not permitted")

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": collection_id_,
                    "op": "remove",
                    "user": user_["email"] if user_ else None,
                    "document": doc_,
                }
            )
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

            if (
                op_ == "delete"
                and not cfg.API_DELETE_ALLOWED_
                and not Auth().is_admin_f(user_)
            ):
                raise APIError("delete operation is not allowed")

            if not Auth().is_admin_f(user_):
                if op_ != "delete" or collection_id_ not in cfg.PROTECTED_INSDEL_EXC_COLLS_:
                    if collection_id_ in cfg.PROTECTED_COLLS_:
                        raise APIError(
                            "collection is protected for bulk processing")

            if op_ == "delete" and collection_id_ == "_user":
                raise APIError("user collection is protected to delete")

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
                structure_ = structure__[
                    "col_structure"] if is_crud_ else structure__
            else:
                raise APIError(
                    f"collection structure not found: {collection_id_}")
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
                    doc["_created_by"] = (
                        user_["email"] if user_ and "email" in user_ else None
                    )
                    doc["_modified_at"] = None
                    doc["_modified_by"] = None
                    doc["_modified_count"] = -1
                    doc.pop("_id", None)
                    if unique:
                        for uq_ in unique:
                            if uq_[0] in doc:
                                if (
                                    "objectId" in properties[uq_[0]]
                                    and properties[uq_[0]]["objectId"] is True
                                ):
                                    doc[uq_[0]] = str(bson.objectid.ObjectId())
                                elif properties[uq_[0]]["bsonType"] == "string":
                                    doc[uq_[0]] = (
                                        f"{doc[uq_[0]]}-1"
                                        if "_" in doc[uq_[0]]
                                        else f"{doc[uq_[0]]}-{index}"
                                    )
                                elif properties[uq_[0]]["bsonType"] in [
                                    "number",
                                    "int",
                                    "float",
                                    "decimal",
                                ]:
                                    doc[uq_[0]] = doc[uq_[0]] + 10000
                    Mongo().db_[collection_].insert_one(doc)
                elif op_ == "delete":
                    Mongo().db_[collection_].delete_one({"_id": doc["_id"]})
                    doc["_deleted_at"] = Misc().get_now_f()
                    doc["_deleted_by"] = (
                        user_["email"] if user_ and "email" in user_ else None
                    )
                    Mongo().db_[f"{collection_id_}_bin"].insert_one(doc)
                    if collection_ == "_collection":
                        suffix_ = Misc().get_timestamp_f()
                        Mongo().db_[f"{col_id_}_data"].aggregate([{"$match": {}}, {"$out": f"{col_id_}_data_bin_{suffix_}"}])
                        Mongo().db_[f"{col_id_}_data"].drop()

                log_ = Misc().log_f(
                    {
                        "type": "Info",
                        "collection": collection_,
                        "op": f"multiple {op_}",
                        "user": user_["email"] if user_ else None,
                        "document": doc,
                    }
                )
                if not log_["result"]:
                    raise APIError(log_["msg"])

            return {"result": True}

        except pymongo.errors.PyMongoError as exc:
            return Misc().mongo_error_f(exc)

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)

    def get_stored_link_f(self, source_, requested_):
        """
        resolves a link definition from the stored schema of the source collection
        the client may only choose which stored link to run, never define one
        """
        try:
            if not source_ or source_[:1] == "_":
                raise APIError("links are only available on data collections")
            if not isinstance(requested_, dict):
                raise APIError("invalid link request")
            req_collection_ = requested_["collection"] if "collection" in requested_ else None
            req_get_ = requested_["get"] if "get" in requested_ else None
            if not req_collection_ or not req_get_:
                raise APIError("link collection and get fields are required")
            col_ = Mongo().db_["_collection"].find_one({"col_id": source_})
            if not col_ or "col_structure" not in col_:
                raise APIError("source collection structure not found")
            links_ = col_["col_structure"]["links"] if "links" in col_["col_structure"] and col_["col_structure"]["links"] else []
            for stored_ in links_:
                if isinstance(stored_, dict) and stored_.get("collection") == req_collection_ and stored_.get("get") == req_get_:
                    return {"result": True, "link": json.loads(json.dumps(stored_, default=json_util.default))}
            raise APIError(f"link is not defined in the {source_} schema")

        except APIError as exc__:
            return {"result": False, "msg": str(exc__)}

        except Exception as exc__:
            return {"result": False, "msg": str(exc__)}

    def link_f(self, obj_):
        """
        docstring is in progress
        """
        try:
            source_ = obj_["source"] if "source" in obj_ else None
            _id = obj_["_id"] if "_id" in obj_ else None
            link_ = obj_["link"] if "link" in obj_ else None
            op_ = obj_["op"] if "op" in obj_ else "insert"

            # C-1: never trust the link definition sent by the client
            stored_link_ = self.get_stored_link_f(source_, link_)
            if not stored_link_["result"]:
                raise APIError(stored_link_["msg"])
            link_ = stored_link_["link"]
            data_ = obj_["data"] if "data" in obj_ else None
            linked_ = list(set(obj_["linked"])) if "linked" in obj_ and len(obj_["linked"]) > 0 else []
            linked_count_ = len(linked_)

            if not link_:
                raise APIError("no link provided")

            if op_ == "insert" and linked_count_ == 0:
                raise APIError("no linked data provided")

            user_ = obj_["user"] if "user" in obj_ else None
            col_id_ = link_["collection"] if "collection" in link_ else None
            get_ = link_["get"] if "get" in link_ else None
            set_ = link_["set"] if "set" in link_ and len(link_["set"]) > 0 else None
            match_ = link_["match"] if "match" in link_ and len(link_["match"]) > 0 else None
            usr_id_ = user_["usr_id"] if "usr_id" in user_ else None
            tags_ = link_["_tags"] if "_tags" in link_ and len(link_["_tags"]) > 0 else None
            api_ = link_["api"] if "api" in link_ and link_["api"] is not None else None
            forced_ = "forced" in link_ and link_["forced"] is True

            if not source_:
                raise APIError("source collection is missing")

            get_properties_f_ = self.get_properties_f(source_)
            if not get_properties_f_["result"]:
                raise APIError("source collection properties is missing")
            source_properties_ = get_properties_f_["properties"]

            if not _id:
                raise APIError("source document id is missing")

            if link_ is None:
                raise APIError("link info is missing")

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

            if col_id_[:1] == "_":
                raise APIError("links may only target data collections")

            # C-1: the acting user needs update permission on the target collection
            target_permission_ = Auth().permission_f({"user": user_, "auth": None, "collection": col_id_, "op": "update"})
            if not target_permission_["result"]:
                raise APIError(f"no permission to link into {col_id_}")

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
                        val_ = Misc().set_value_f(
                            targetkey__, setto__, target_properties_, data_
                        )
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

            checknum_ = len(Mongo().db_[collection_].distinct(get_, filter_))

            if linked_count_ > 0 and checknum_ != linked_count_:
                raise AppException(f"found [{checknum_}] does not match requested [{linked_count_}]")

            update_many_ = Mongo().db_[collection_].update_many(filter_, {"$set": setc_})
            count_ = update_many_.matched_count
            if count_ == 0:
                raise AppException("no record found to get linked")

            notification_ = link_["notification"] if "notification" in link_ else None
            notify_ = notification_ and "notify" in notification_ and notification_["notify"] is True
            attach_html_ = "html" in notification_ and notification_["html"] is True
            attach_json_ = "json" in notification_ and notification_["json"] is True
            attach_excel_ = "excel" in notification_ and notification_["excel"] is True
            attach_csv_ = "csv" in notification_ and notification_["csv"] is True
            files_ = []

            if api_:
                run_api_f_ = self.run_api_f(api_, data_, [_id], usr_id_)
                if not run_api_f_["result"]:
                    raise APIError(run_api_f_["msg"])
                files_ += run_api_f_["files"]

            if notify_:
                subject_ = notification_["subject"] if "subject" in notification_ else "Link"
                body_ = notification_[
                    "body"] if "body" in notification_ else "<p>Hi,</p><p>Link completed successfully.</p><p><h1></h1></p>"
                nkey_ = notification_["key"] if "key" in notification_ and notification_["key"] != "" else None
                keyf_ = data_[nkey_] if data_ and nkey_ and nkey_ in data_ else None

                if attach_html_ or attach_csv_ or attach_excel_ or attach_json_:
                    fields_ = (
                        str(notification_["fields"].replace(" ", ""))
                        if "fields" in notification_
                        else None
                    )
                    nsort_ = (
                        notification_["sort"]
                        if notification_
                        and "sort" in notification_
                        and notification_["sort"]
                        else {"_modified_at": -1}
                    )
                    topics_ = notification_["topics"].split(",") if "topics" in notification_ else []
                    if not fields_:
                        raise AppException("no fields field found in link")
                    type_ = "csv"
                    file_ = f"{cfg.API_TEMPFILE_PATH_}/link-{Misc().get_timestamp_f()}.{type_}"
                    query_ = json.dumps(filter0_, default=json_util.default, sort_keys=False)
                    cmd_ = ["mongoexport"] + Misc().commands_f(
                        "mongoexport",
                        {
                            "query": query_,
                            "fields": fields_,
                            "sort": nsort_,
                            "type": type_,
                            "file": file_,
                            "collection": collection_,
                        },
                    )
                    subprocess.call(cmd_)
                    csv_file_ = pd.read_csv(file_)

                    if attach_html_:
                        html_ = "<style>\
                            .etable { border-spacing: 0; border-collapse: collapse;} \
                            .etable td,th { padding: 7px; border: 1px solid #999;} \
                            </style>"
                        for topic_ in topics_:
                            html_ += f"{source_properties_[topic_]['title'] if topic_ in source_properties_ and 'title' in source_properties_[topic_] else topic_}: \
                                <strong>{data_[topic_] if topic_ in data_ and data_[topic_] is not None else ''}</strong>\
                                <br />"
                        html_ += f"<p>{csv_file_.to_html(index=False, max_rows=cfg.HTML_TABLE_MAX_ROWS_, max_cols=cfg.HTML_TABLE_MAX_COLS_, border=1, justify='left', classes='etable')}</p>"
                        body_ += f"<p>{html_}</p>"

                    if attach_csv_:
                        files_.append({"name": file_, "type": type_})
                    if attach_excel_:
                        file_excel_ = (
                            f"{cfg.API_TEMPFILE_PATH_}/link-{Misc().get_timestamp_f()}.xlsx"
                        )
                        csv_file_.to_excel(
                            file_excel_, index=None, sheet_name=collection_, header=True
                        )
                        files_.append({"name": file_excel_, "type": "xlsx"})
                    if attach_json_:
                        file_json_ = (
                            f"{cfg.API_TEMPFILE_PATH_}/link-{Misc().get_timestamp_f()}.json"
                        )
                        csv_file_.to_json(
                            file_json_,
                            date_format="iso",
                            orient="records",
                            force_ascii=False,
                        )
                        files_.append({"name": file_json_, "type": "json"})

                    subject_ += f" - {keyf_}" if keyf_ else ""
                    email_sent_ = Email().send_email_f(
                        {
                            "op": "link",
                            "tags": tags_,
                            "subject": subject_,
                            "html": body_,
                            "files": files_,
                        }
                    )
                    if not email_sent_["result"]:
                        raise APIError(email_sent_["msg"])

            return {"result": True, "data": setc_, "count": count_}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AppException as exc__:
            return Misc().app_exception_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def run_api_f(self, api_, doc_, ids_, email_):
        """
        docstring is in progress
        """
        files_, res_, json_ = [], {}, {}
        try:
            id_ = api_["id"] if "id" in api_ and api_[
                "id"] is not None else None
            if not id_:
                raise PassException("no action api id found")

            enabled_ = "enabled" in api_ and api_["enabled"] is True
            if not enabled_:
                raise PassException(f"action api not enabled: {id_}")

            headers_ = api_["headers"] if "headers" in api_ else None
            if not headers_:
                raise PassException(f"invalid api headers in {id_}")

            method_ = (
                api_["method"]
                if "method" in api_ and api_["method"].lower() in ["get", "post"]
                else None
            )
            if not method_:
                raise PassException(f"invalid api method in {id_}")

            map_ = api_["map"] if "map" in api_ else None
            json_["email"] = email_
            if map_:
                for _, value_ in map_.items():
                    if value_ in doc_:
                        json_["key"] = value_
                        json_["value"] = doc_[value_]
                if not json_:
                    raise PassException(
                        f"no mapping values found in api {id_}")
                json_["ids"] = []
                if ids_ and len(ids_) > 0:
                    json_["ids"] = ids_
                json_["map"] = map_
                json_["email"] = email_

            protocol_ = (
                api_["protocol"]
                if "protocol" in api_ and api_["protocol"] in ["http", "https"]
                else None
            )
            if not protocol_:
                raise PassException(f"invalid api protocol in {id_}")

            domain_ = api_["domain"] if "domain" in api_ else None
            if not domain_:
                raise PassException(f"invalid api domain in {id_}")
            subdomain_ = (
                f"{api_['subdomain']}."
                if "subdomain" in api_ and api_["subdomain"] != ""
                else ""
            )

            path_ = api_["path"] if "path" in api_ and api_[
                "path"][:1] == "/" else None
            if not path_:
                raise PassException(f"invalid api path in {id_}")

            # SSRF guard: outbound calls only to the configured integration hosts
            host_ = f"{subdomain_}{domain_}".lower()
            if host_ not in cfg.API_OUTBOUND_HOSTS_:
                raise APIError(f"api host is not allowed: {host_}")
            headers_ = dict(headers_)
            if cfg.INTEGRATION_API_KEY_:
                headers_["X-Integration-Key"] = cfg.INTEGRATION_API_KEY_

            response_ = requests.post(
                f"{protocol_}://{host_}{path_}",
                json=json.loads(JSONEncoder().encode(json_)),
                headers=headers_,
                timeout=60,
                allow_redirects=False,
            )
            res_ = json.loads(response_.content)
            msg_ = res_["msg"] if "msg" in res_ else ""

            if response_.status_code != 200 or not res_["result"]:
                raise APIError(msg_)

            files_ = (
                res_["files"] if "files" in res_ and len(
                    res_["files"]) > 0 else None
            )

            res_ = {"result": True, "files": files_, "msg": msg_}

        except pymongo.errors.PyMongoError as exc__:
            Misc().mongo_error_f(exc__)
            res_ = {"result": True, "files": files_, "msg": str(exc__)}

        except PassException as exc__:
            res_ = {"result": True, "files": files_, "msg": str(exc__)}

        except APIError as exc__:
            res_ = {"result": False, "files": files_, "msg": str(exc__)}

        except Exception as exc__:
            res_ = {"result": True, "files": files_, "msg": str(exc__)}

        finally:
            return res_

    def action_f(self, obj_):
        """
        docstring is in progress
        """
        count_, files_, msg_ = 0, [], None
        newdoc_, forex_ = {}, False
        split_id_ = Misc().get_timestamp_f()
        session_client_ = pymongo.MongoClient(Mongo().connstr)
        session_db_ = session_client_[cfg.MONGO_DB_]
        session_ = session_client_.start_session()

        try:
            collection_id_ = obj_["collection"]
            user_ = obj_["userindb"] if "userindb" in obj_ else None
            match_ = obj_["match"] if "match" in obj_ else None
            actionix_ = int(obj_["actionix"]) if "actionix" in obj_ else None
            email_ = user_["usr_id"] if user_ and "usr_id" in user_ else None
            if not email_:
                raise AppException("user is not allowed")

            doc_ = obj_["doc"] if "doc" in obj_ else None
            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = email_
            data_ = obj_["data"] if "data" in obj_ else None

            is_crud_ = collection_id_[:1] != "_"
            if not is_crud_ and collection_id_ not in ["_firewall", "_query", "_job"]:
                raise AppException("actions are not allowed")

            if actionix_ < 0:
                raise AppException("please select an action to run")

            ids_ = []
            if match_ and len(match_) > 0:
                for _id in match_:
                    ids_.append(ObjectId(str(_id)))

            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            schema_ = Mongo().db_["_collection"].find_one(
                {"col_id": collection_id_}) if is_crud_ else self.root_schemas_f(f"{collection_id_}")
            if not schema_:
                raise AppException("schema not found")

            structure_ = schema_["col_structure"] if "col_structure" in schema_ else self.root_schemas_f(
                f"{collection_id_}")
            if not structure_:
                raise AppException(f"structure not found {collection_id_}")

            properties_ = structure_["properties"] if "properties" in structure_ else None
            if not properties_:
                raise AppException(f"properties not found {collection_id_}")

            action_ = structure_["actions"][actionix_] if "actions" in structure_ and len(
                structure_["actions"]) > 0 and structure_["actions"][actionix_] else None
            if not action_:
                raise AppException("action not found")

            action_id_ = action_["id"] if "id" in action_ and action_["id"] is not None else "action"
            tags_ = action_["_tags"] if "_tags" in action_ and len(action_["_tags"]) > 0 else None
            if not tags_:
                raise AppException("no tags found in action")

            api_ = action_["api"] if "api" in action_ and action_["api"] is not None else None
            uniqueness_ = "uniqueness" in action_ and action_["uniqueness"] is True
            unique_ = action_["unique"] if "unique" in action_ and len(action_["unique"]) > 0 else None
            set_ = action_["set"] if "set" in action_ else None
            if not set_ and not api_:
                raise AppException("no set or api provided in action")

            notification_ = action_["notification"] if "notification" in action_ else None
            notify_ = notification_ and "notify" in notification_ and notification_["notify"] is True
            filter_ = notification_["filter"] if notification_ and "filter" in notification_ and len(notification_[
                                                                                                     "filter"]) > 0 else None

            get_notification_filtered_ = None
            if notify_ and filter_:
                get_notification_filtered_ = self.get_filtered_f(
                    {"match": filter_, "properties": properties_, "data": doc_})

            match_ = action_["match"] if "match" in action_ and len(action_["match"]) > 0 else {}
            download_by_ = action_["download_by"] if "download_by" in action_ and action_[
                "download_by"] in properties_ else None
            get_filtered_ = self.get_filtered_f({"match": match_, "properties": properties_}) if match_ else {}

            if ids_ and len(ids_) > 0:
                get_filtered_ = {
                    "$and": [get_filtered_, {"_id": {"$in": ids_}}]} if get_filtered_ else {
                    "_id": {"$in": ids_}}
                if get_notification_filtered_:
                    get_notification_filtered_ = {"$and": [get_notification_filtered_, {"_id": {"$in": ids_}}]}
            else:
                if is_crud_ and api_:
                    raise AppException("no selection was made")

            if uniqueness_ and unique_:
                unique_ = set(unique_)
                group_ = {}
                for uq_ in unique_:
                    group_[uq_] = f"${uq_}"
                uniques_ = list(Mongo().db_[collection_].aggregate(
                    [{"$match": get_filtered_}, {"$group": {"_id": group_, "count": {"$sum": 1}}}]))
                if uniques_ and len(uniques_) > 1:
                    raise AppException(f"{(','.join(unique_))} must be unique in selection")

            split_ = action_["split"] if "split" in action_ and action_[
                "split"] is not None and "enabled" in action_["split"] and action_["split"]["enabled"] is True else {}
            key_suffix_ = split_["key_suffix"] if "key_suffix" in split_ and split_["key_suffix"] is not None else None
            key_field_ = split_["key_field"] if "key_field" in split_ and split_["key_field"] is not None and split_[
                "key_field"] in properties_ and split_["key_field"] in data_ else None
            set_field_ = split_["set_field"] if "set_field" in split_ and split_[
                "set_field"] is not None and split_["set_field"] in properties_ else None
            set_value_ = split_["set_value"] if "set_value" in split_ and split_["set_value"] is not None else None
            ref_field_ = split_["ref_field"] if "ref_field" in split_ and split_["ref_field"] is not None and split_[
                "ref_field"] in properties_ and split_["ref_field"] in data_ and split_["ref_field"] in doc_ else None
            num_fields_ = split_["num_fields"] if "num_fields" in split_ and len(split_["num_fields"]) > 0 else None

            session_.start_transaction()

            if set_:
                if data_ and split_ and key_suffix_ and key_field_ and set_field_ and set_value_:
                    docu_ = {}
                    datanew_ = Mongo().db_[collection_].find_one({"_id": ObjectId(data_["_id"])})
                    datax_ = datanew_.copy()

                    key_value_ = datanew_[key_field_] if key_field_ in datanew_ and datanew_[key_field_] is not None else None
                    if not key_value_:
                        session_.abort_transaction()
                        raise AppException("no key value found")

                    datanew_[key_field_] = f"{datanew_[key_field_]}{key_suffix_}"

                    for doc__ in doc_:
                        datanew_[doc__] = doc_[doc__]

                    datanew_["_split_id"] = docu_["_split_id"] = split_id_
                    datanew_[set_field_] = docu_[set_field_] = set_value_
                    filter_ = {"_split_id": split_id_}
                    get_notification_filtered_ = filter_
                    get_filtered_ = {}
                    get_filtered_[key_field_] = key_value_

                    if ref_field_ and num_fields_:
                        count_ = 1
                        if doc_[ref_field_] > datax_[ref_field_]:
                            doc_[ref_field_] = datax_[ref_field_]
                        if doc_[ref_field_] < 0:
                            doc_[ref_field_] = 0

                        ration_ = doc_[ref_field_] / datax_[ref_field_]

                        datanew_.pop("_id", None)
                        datanew_["_created_at"] = docu_["_modified_at"] = (Misc().get_now_f())
                        datanew_["_created_by"] = docu_["_modified_by"] = email_
                        datanew_["_resume_token"] = None
                        datanew_["_modified_count"] = 0
                        docu_.pop("_modified_count", None)

                        for num_field_ in num_fields_:
                            dnf_ = datax_[num_field_]
                            if num_field_ == ref_field_:
                                datanew_[num_field_] = doc_[num_field_]
                                docu_[num_field_] = dnf_ - doc_[num_field_]
                            else:
                                datanew_[num_field_] = round(ration_ * dnf_, 3)
                                docu_[num_field_] = round(
                                    (1 - ration_) * dnf_, 3)

                        session_db_[collection_].insert_one(datanew_, session=session_)

                        if ration_ < 1:
                            session_db_[collection_].update_one(
                                {"_id": ObjectId(data_["_id"])}, {"$set": docu_, "$inc": {"_modified_count": 1}},
                                session=session_)
                        else:
                            session_db_[collection_].delete_one({"_id": ObjectId(data_["_id"])}, session=session_)

                    else:
                        datanew_["_modified_at"] = Misc().get_now_f()
                        datanew_["_modified_by"] = email_
                        datanew_.pop("_modified_count", None)
                        update_many_ = session_db_[collection_].update_many(
                            get_filtered_, {"$set": datanew_, "$inc": {"_modified_count": 1}}, session=session_, )
                        count_ = (update_many_.matched_count if update_many_.matched_count > 0 else 0)
                else:
                    for set__ in set_:
                        if "key" in set__ and set__["key"] in doc_:
                            newdoc_[set__["key"]] = doc_[set__["key"]]
                            forex_ = True
                    if forex_:
                        newdoc_["_modified_at"] = Misc().get_now_f()
                        newdoc_["_modified_by"] = email_
                        update_many_ = session_db_[collection_].update_many(
                            get_filtered_, {"$set": newdoc_, "$inc": {"_modified_count": 1}}, session=session_, )
                        count_ = (update_many_.matched_count if update_many_.matched_count > 0 else 0)

                if count_ == 0:
                    session_.abort_transaction()
                    raise PassException(
                        "no rows affected due to match criteria")

            if api_:
                run_api_f_ = self.run_api_f(api_, doc_, ids_, email_)
                if not run_api_f_["result"]:
                    raise APIError(run_api_f_["msg"])
                msg_ = run_api_f_["msg"] if "msg" in run_api_f_ else None
                files_ += (run_api_f_["files"] if "files" in run_api_f_ and run_api_f_["files"]
                           is not None and len(run_api_f_["files"]) > 0 else [])

            session_.commit_transaction()

            if notify_:
                notify_collection_ = (f"{notification_['collection']}_data"
                                      if "collection" in notification_ else collection_)
                if notify_collection_ != collection_:
                    get_properties_ = self.get_properties_f(notification_["collection"])
                    if not get_properties_["result"]:
                        raise AppException(get_properties_["msg"])
                    properties_ = get_properties_["properties"]
                    get_notification_filtered_ = self.get_filtered_f(
                        {"match": filter_, "properties": properties_, "data": doc_})

                subject_ = (notification_["subject"] if "subject" in notification_ else "Action Completed")
                body_ = (notification_["body"]
                         if "body" in notification_ else
                         "<p>Hi,</p><p>Action completed successfully.</p><p><h1></h1></p>")
                fields_ = (
                    str(",".join(notification_["fields"]))
                    if "fields" in notification_ and str(type(notification_["fields"])) == "<class 'list'>" and
                    len(notification_["fields"]) > 0
                    else (
                        notification_["fields"].replace(" ", "")
                        if notification_ and "fields" in notification_ else None))
                nsort_ = (notification_["sort"] if notification_ and "sort" in notification_ and notification_["sort"] else (
                    structure_["sort"] if "sort" in structure_ and structure_["sort"] else {"_modified_at": -1}))
                topics_ = notification_["topics"].split(",") if "topics" in notification_ else []
                attach_html_ = "html" in notification_ and notification_["html"] is True
                attach_json_ = "json" in notification_ and notification_["json"] is True
                attach_excel_ = "excel" in notification_ and notification_["excel"] is True
                attach_csv_ = "csv" in notification_ and notification_["csv"] is True

                if (get_notification_filtered_ and fields_ and (attach_html_ or attach_json_ or attach_excel_ or attach_csv_)):
                    type_ = "csv"
                    beasefile_ = (f"{cfg.API_TEMPFILE_PATH_}/{action_id_}-{Misc().get_timestamp_f()}")
                    file_ = f"{beasefile_}.{type_}"
                    file_excel_ = f"{beasefile_}.xlsx"
                    file_json_ = f"{beasefile_}.json"
                    query_ = json.dumps(get_notification_filtered_, default=json_util.default, sort_keys=False, )
                    subprocess.call(
                        ["mongoexport"] + Misc().commands_f(
                            "mongoexport",
                            {"query": query_, "fields": fields_, "sort": nsort_, "type": type_, "file": file_,
                             "collection": notify_collection_, },))
                    csv_file_ = pd.read_csv(file_)

                    if attach_html_:
                        html_ = "<style> .etable { border-spacing: 0; border-collapse: collapse;} .etable td,th { padding: 7px; border: 1px solid #999;} </style>"
                        for topic_ in topics_:
                            html_ += f"{properties_[topic_]['title'] if topic_ in properties_ and 'title' in properties_[topic_] else topic_}: <strong>{doc_[topic_] if topic_ in doc_ and doc_[topic_] is not None else ''}</strong><br />"
                        html_ += f"<p>{csv_file_.to_html(index=False, max_rows=cfg.HTML_TABLE_MAX_ROWS_, max_cols=cfg.HTML_TABLE_MAX_COLS_, border=1, justify='left', classes='etable')}</p>"
                        body_ += f"<p>{html_}</p>"
                    if attach_csv_:
                        files_.append({"name": file_, "type": type_})
                    if attach_excel_:
                        csv_file_.to_excel(file_excel_, index=None, sheet_name=collection_id_, header=True, )
                        files_.append({"name": file_excel_, "type": "xlsx"})
                    if attach_json_:
                        csv_file_.to_json(file_json_, date_format="iso", orient="records", force_ascii=False, )
                        files_.append({"name": file_json_, "type": "json"})

                email_sent_ = Email().send_email_f({"op": "action", "tags": tags_,
                                                    "subject": subject_, "html": body_, "files": files_, })
                if not email_sent_["result"]:
                    raise APIError(email_sent_["msg"])

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": collection_,
                    "op": "action",
                    "user": email_,
                    "document": {
                        "doc": doc_,
                        "newdoc": newdoc_ if newdoc_ else {},
                        "match": match_,
                        "filter": get_filtered_ if get_filtered_ else {},
                    },
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {
                "result": True,
                "count": count_,
                "msg": msg_ if msg_ else "action completed successfully",
                "files": files_ if download_by_ else [],
            }

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AppException as exc__:
            return Misc().notify_exception_f(exc__)

        except PassException as exc__:
            return Misc().pass_exception_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

        finally:
            session_client_.close()

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
            forced_ = link_ and "forced" in link_ and link_["forced"] is True

            if collection_id_ not in cfg.PROTECTED_INSDEL_EXC_COLLS_:
                if collection_id_ in cfg.PROTECTED_COLLS_:
                    raise APIError("collection is protected")

            if forced_ and not linked_:
                raise APIError("no linked items entered")

            if "_id" in doc_:
                doc_.pop("_id", None)

            if "_structure" in doc_:
                doc_.pop("_structure", None)

            # H-7: only administrators may create users carrying administrator tags
            if collection_id_ == "_user" and not Auth().is_admin_f(user_):
                new_tags_ = doc_["_tags"] if "_tags" in doc_ and doc_["_tags"] else []
                if any(tag_ in cfg.API_ADMIN_TAGS_ for tag_ in new_tags_):
                    raise APIError("only administrators can assign administrator tags")

            inserted_ = None
            is_crud_ = collection_id_[:1] != "_"
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            doc_["_created_at"] = doc_["_modified_at"] = Misc().get_now_f()
            doc_["_created_by"] = doc_["_modified_by"] = (user_["email"] if user_ and "email" in user_ else None)

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
                tkn_lifetime_ = (int(doc_["tkn_lifetime"]) if "tkn_lifetime" in doc_ and int(
                    doc_["tkn_lifetime"]) > 0 else 1440)
                secret_ = pyotp.random_base32()
                token_finder_ = pyotp.random_base32()
                jwt_proc_f_ = Misc().jwt_proc_f(
                    "encode",
                    None,
                    secret_,
                    {
                        "iss": "Technoplatz",
                        "aud": "api",
                        "sub": "bi",
                        "exp": Misc().get_now_f() + timedelta(minutes=tkn_lifetime_),
                        "iat": Misc().get_now_f(),
                    },
                    {"finder": token_finder_},
                )
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
                col_structure_ = (doc_["col_structure"] if "col_structure" in doc_ else None)
                datac_ = f"{col_id_}_data"
                if (
                    col_structure_
                    and col_structure_ != {}
                    and datac_ not in Mongo().db_.list_collection_names()
                ):
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
                    if (
                        "counter" in prop_
                        and prop_["counter"] is True
                        and prop_["bsonType"]
                        in ["int", "number", "float", "decimal", "string"]
                    ):
                        if prop_["bsonType"] in ["int", "number", "float", "decimal"]:
                            counter_name_ = f"{property_.upper()}_COUNTER"
                            counter_ = doc_[property_]
                        else:
                            counter_ = doc_[property_]
                        Mongo().db_["_kv"].update_one(
                            {"kav_key": counter_name_},
                            {"$set": {"kav_value": str(counter_)}},)

                if link_ and linked_:
                    link_f_ = self.link_f(
                        {
                            "op": "insert",
                            "source": collection_id_,
                            "_id": str(_id),
                            "link": link_,
                            "linked": linked_,
                            "data": doc_,
                            "user": user_,
                        }
                    )
                    if not link_f_["result"]:
                        delete_one_ = Mongo().db_[
                            collection_].delete_one({"_id": _id})
                        raise APIError(link_f_["msg"])

            log_ = Misc().log_f(
                {
                    "type": "Info",
                    "collection": collection_id_,
                    "op": "insert",
                    "user": user_["email"] if user_ else None,
                    "document": doc_,
                }
            )
            if not log_["result"]:
                raise APIError(log_["msg"])

            return {"result": True, "token": inserted_}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except AuthError as exc__:
            return Misc().auth_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)
