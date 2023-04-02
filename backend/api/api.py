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
import sys
import pandas as pd
import numpy as np
import numexpr as ne
import openpyxl
import stat
import bson
import json
import operator
import random
import re
import secrets
import string
import pymongo
import requests
import bleach
import logging
import base64
import magic
import pyotp
import smtplib
import urllib
import hashlib
import jwt
import xlrd
import asyncio
from pickle import TRUE
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from get_docker_secret import get_docker_secret
from pymongo import MongoClient, ASCENDING
from werkzeug.utils import secure_filename
from flask import Flask, request, send_from_directory
from flask_cors import CORS, cross_origin
from random import randint
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil import tz
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from apscheduler.schedulers.background import BackgroundScheduler


class APIError(BaseException):
    pass


class AuthError(BaseException):
    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


class Schedular():
    def schedule_automation_f(self, doc_):
        try:
            aut_id_ = doc_["aut_id"] if "aut_id" in doc_ else None
            aut_source_collection_id_ = doc_["aut_source_collection_id"] if "aut_source_collection_id" in doc_ else None
            aut_source_filter_ = doc_["aut_source_filter"] if "aut_source_filter" in doc_ and len(doc_["aut_source_filter"]) > 0 else None
            aut_source_set_ = doc_["aut_source_set"] if "aut_source_set" in doc_ and len(doc_["aut_source_set"]) > 0 else None
            aut_target_set_ = doc_["aut_target_set"] if "aut_target_set" in doc_ and len(doc_["aut_target_set"]) > 0 else None
            aut_target_collection_id_ = doc_["aut_target_collection_id"] if "aut_target_collection_id" in doc_ else None
            aut_target_match_ = doc_["aut_target_match"] if "aut_target_match" in doc_ and len(doc_["aut_target_match"]) > 0 else None
            aut_target_ = doc_["aut_target"] if "aut_target" in doc_ else False
            aut_target_upsert_ = True if "aut_target_upsert" in doc_ and doc_["aut_target_upsert"] == True else False
            aut_target_prefixes_ = doc_["aut_target_prefixes"] if "aut_target_prefixes" in doc_ and len(doc_["aut_target_prefixes"]) > 0 else None

            if not aut_id_ or not aut_source_collection_id_ or not aut_source_filter_:
                raise APIError("automation info is missing")

            if aut_target_:
                if not aut_target_match_ or not aut_target_collection_id_:
                    raise APIError("match info is missing")
                if not len(aut_target_match_) > 0:
                    raise APIError("matched fields is missing")

            collection_ = Mongo().db["_collection"].find_one({"col_id": aut_source_collection_id_})
            if not collection_:
                raise APIError(f"collection not found to schedule {aut_source_collection_id_}")

            structure_ = collection_["col_structure"] if "col_structure" in collection_ else None
            if not structure_:
                raise APIError(f"structure not found: {aut_source_collection_id_}")

            properties_ = structure_["properties"] if "properties" in structure_ else None
            if not properties_:
                raise APIError(f"source properties not found: {aut_source_collection_id_}")

            get_filtered_ = Crud().get_filtered_f({
                "match": aut_source_filter_,
                "properties": structure_["properties"] if "properties" in structure_ else None
            })

            source_data_file_ = f"{aut_source_collection_id_}_data"
            if source_data_file_ not in Mongo().db.list_collection_names():
                raise APIError("collection data is missing")

            target_data_file_ = None
            target_structure_ = None

            if aut_target_:
                target_data_file_ = f"{aut_target_collection_id_}_data"
                if target_data_file_ not in Mongo().db.list_collection_names():
                    raise APIError(f"target collection data is missing {target_data_file_}")

                collection_ = Mongo().db["_collection"].find_one({"col_id": aut_target_collection_id_})
                if not collection_:
                    raise APIError(f"target collection not found to schedule: {aut_target_collection_id_}")

                target_structure_ = collection_["col_structure"] if "col_structure" in collection_ else None
                if not target_structure_:
                    raise APIError(f"target structure not found: {aut_target_collection_id_}")

                target_properties_ = target_structure_["properties"] if "properties" in target_structure_ else None
                if not target_properties_:
                    raise APIError(f"target properties not found: {aut_target_collection_id_}")

            find_ = Mongo().db[source_data_file_].find(get_filtered_)
            for rec_ in find_:
                target_match_ = {}
                id_ = rec_["_id"]
                if aut_target_ and target_structure_:
                    for m_ in aut_target_match_:
                        m_key_ = m_["key"]
                        m_value_ = m_["value"]
                        if m_value_[:1] == "$":
                            f_ = m_value_[1:]
                            m_value_ = rec_[f_]
                            if aut_target_prefixes_:
                                for prefix_ in aut_target_prefixes_:
                                    if m_value_.startswith(prefix_):
                                        m_value_ = m_value_[len(prefix_):]
                                        break
                        target_match_[m_key_] = m_value_

                    if target_match_ == {}:
                        raise APIError("The first item of the target filter must be the matching field")

                set_source_ = {}
                set_target_ = {}
                set_source_["_modified_by"] = set_target_["_modified_by"] = "Automation"
                set_source_["_modified_at"] = set_target_["_modified_at"] = datetime.now()

                if aut_source_set_ and len(aut_source_set_) > 0:
                    for aut_source_set__ in aut_source_set_:
                        key_ = aut_source_set__["key"]
                        # value_ = aut_source_set__["value"]
                        value_ = Misc().string_to_formula_f(aut_source_set__, rec_, properties_)
                        set_source_[key_] = value_
                    Mongo().db[source_data_file_].update_one({"_id": id_}, {"$set": set_source_})

                if aut_target_set_ and len(aut_target_set_) > 0:
                    for aut_target_set__ in aut_target_set_:
                        key_ = aut_target_set__["key"]
                        value_ = Misc().string_to_formula_f(aut_target_set__, rec_, target_properties_)
                        set_target_[key_] = value_

                    update_many_ = Mongo().db[target_data_file_].update_many(target_match_, {"$set": set_target_}, upsert=aut_target_upsert_)

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def announce_view_f(self, doc_, scope_, email_):
        try:
            vie_title_ = doc_["vie_title"] if "vie_title" in doc_ else "view"
            vie_id_ = doc_["vie_id"] if "vie_id" in doc_ else vie_title_
            vie_attach_pivot_ = doc_["vie_attach_pivot"] if "vie_attach_pivot" in doc_ else False
            vie_attach_csv_ = doc_["vie_attach_csv"] if "vie_attach_csv" in doc_ else False
            vie_attach_excel_ = doc_["vie_attach_excel"] if "vie_attach_excel" in doc_ else False
            user_id_ = email_ if email_ else doc_["_created_by"] if "_created_by" in doc_ else doc_["_modified_by"] if "_modified_by" in doc_ else None
            vie_tags_ = doc_["_tags"] if "_tags" in doc_ and scope_ == "live" else PERMISSIVE_TAGS_

            if not user_id_:
                raise APIError("no user provided")

            if len(vie_tags_) == 0:
                raise APIError("no subscribers found")

            user_ = Mongo().db["_user"].find_one({"usr_id": user_id_})
            if not user_:
                raise APIError(f"user not found {user_id_}")

            personalizations_to_ = []
            to_ = []

            users_ = Mongo().db["_user"].find({"_tags": {"$elemMatch": {"$in": vie_tags_}}})
            if users_:
                for member_ in users_:
                    if member_["usr_id"] not in to_:
                        to_.append(member_["usr_id"])
                        personalizations_to_.append({"email": member_["usr_id"], "name": member_["usr_name"]})

            if scope_ == "test" and user_id_ not in to_:
                to_.append(user_id_)
                personalizations_to_.append({"email": user_id_, "name": "Test"})

            _id = doc_["_id"]
            view_to_pivot_f_ = Crud().view_to_dataset_f({
                "id": _id,
                "user": user_
            })

            personalizations_ = {"to": personalizations_to_}

            if not view_to_pivot_f_["result"]:
                raise APIError(view_to_pivot_f_["msg"])

            df_pivot_ = view_to_pivot_f_["pivot"]

            file_csv_ = view_to_pivot_f_["file_csv"]
            file_excel_ = view_to_pivot_f_["file_excel"]
            file_csv_raw_ = view_to_pivot_f_["file_csv_raw"]
            file_excel_raw_ = view_to_pivot_f_["file_excel_raw"]

            # style applying to pivot
            strftime_ = datetime.now().strftime("%d.%m.%Y %H:%M")
            padding_ = 8
            padding_r_ = 2 * padding_
            font_size_body_ = 13
            font_size_table_ = 13
            background_ = "#eee"
            style_div_ = f"font-size: {font_size_body_}px;"
            header_ = f"{vie_title_}"
            styles_ = [
                dict(selector="th", props=[("background", f"{background_}"), ("padding", f"{padding_}px {padding_r_}px"), ("font-size", f"{font_size_table_}px")]),
                dict(selector="td", props=[("background", f"{background_}"), ("padding", f"{padding_}px {padding_r_}px"), ("text-align", "right"), ("font-size", f"{font_size_table_}px")]),
                dict(selector="table", props=[("font-size", f"{font_size_table_}px")]),
                dict(selector="caption", props=[("caption-side", "top")])
            ]

            files_ = []

            if df_pivot_ is not None:
                df_pivot_ = df_pivot_.style.set_table_styles(styles_)
                pivot_ = df_pivot_.to_html().replace('border="1"', "")
                if vie_attach_csv_:
                    files_.append({"filename": file_csv_, "filetype": "csv"})
                    files_.append({"filename": file_csv_raw_, "filetype": "csv"})
                if vie_attach_excel_:
                    files_.append({"filename": file_excel_, "filetype": "xlsx"})
                    files_.append({"filename": file_excel_raw_, "filetype": "xlsx"})
            else:
                pivot_ = "NO DATA FOUND MATCHING THE CRITERIA"
                raise APIError("No data found matching the criteria")

            body_ = ""
            if vie_attach_pivot_:
                body_ += f"{pivot_}"

            footer_ = f"<br />Generated at {strftime_}"
            html_ = f"<div style=\"{style_div_}\"><p>{header_}</p><p>{body_}</p><p>{footer_}</p></div>" if scope_ == "live" else f"<div style=\"{style_div_}\"><p style='color:#c00; font-weight: bold;'>THIS IS A TEST MESSAGE</p><p>{header_}</p><p>{body_}</p><p>{footer_}</p></div>"

            email_sent_ = Email().sendEmail_f({
                "personalizations": personalizations_,
                "op": "view",
                "html": html_,
                "subject": vie_title_ if scope_ == "live" else f"TEST: {vie_title_}",
                "files": files_
            })

            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            Mongo().db["_announcement"].insert_one({
                "ano_id": f"ano-{Misc().get_timestamp_f()}",
                "ano_scope": scope_,
                "ano_vie_id": vie_id_,
                "ano_vie_title": vie_title_,
                "ano_to": to_,
                "_tags": vie_tags_,
                "_created_at": datetime.now(),
                "_created_by": user_id_
            })

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def schedule_automations_f(self, backgroundscheduler_):
        try:
            print("*** schedule automations started", datetime.now(), flush=True)
            find_ = Mongo().db["_automation"].find({"aut_enabled": True})
            for doc_ in find_:
                aut_id_ = doc_["aut_id"]
                if backgroundscheduler_.get_job(aut_id_):
                    backgroundscheduler_.remove_job(aut_id_)

                backgroundscheduler_.add_job(self.schedule_automation_f, "cron", day_of_week="*", hour="*", minute="*", id=aut_id_, timezone=TZ_, replace_existing=True, args=[doc_])

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def schedule_views_f(self, sched_):
        try:
            print("*** schedule views restarted", datetime.now(), flush=True)
            view_find_ = Mongo().db["_view"].find({})
            for doc_ in view_find_:
                vie_id_ = doc_["vie_id"]
                if sched_.get_job(vie_id_):
                    sched_.remove_job(vie_id_)
                vie_scheduled_ = doc_["vie_scheduled"] if "vie_scheduled" in doc_ and doc_["vie_scheduled"] else False
                vie_pivot_values_ = doc_["vie_pivot_values"] if "vie_pivot_values" in doc_ else []
                vie_pivot_index_ = doc_["vie_pivot_index"] if "vie_pivot_index" in doc_ else []
                _tags = doc_["_tags"] if "_tags" in doc_ else []

                if vie_scheduled_ and len(vie_pivot_values_) > 0 and len(vie_pivot_index_) > 0 and len(_tags) > 0:
                    vie_sched_minutes_c_ = [str(element) for element in doc_["vie_sched_minutes"]] if "vie_sched_minutes" in doc_ and len(doc_["vie_sched_minutes"]) > 0 else ["0"]
                    vie_sched_hours_c_ = [str(element) for element in doc_["vie_sched_hours"]] if "vie_sched_hours" in doc_ and len(doc_["vie_sched_hours"]) > 0 else ["12"]
                    vie_sched_minutes_ = ",".join(vie_sched_minutes_c_)
                    vie_sched_hours_ = ",".join(vie_sched_hours_c_)
                    vie_sched_days_ = ",".join(doc_["vie_sched_days"]) if "vie_sched_days" in doc_ and len(doc_["vie_sched_days"]) > 0 else "mon"
                    sched_.add_job(self.announce_view_f, "cron", day_of_week=f"{vie_sched_days_}", hour=f"{vie_sched_hours_}", minute=f"{vie_sched_minutes_}", id=vie_id_, timezone=TZ_, replace_existing=True, args=[doc_, "live", None])
                    print(f"*** job added: {vie_id_} D[{vie_sched_days_}] H[{vie_sched_hours_}] M[{vie_sched_minutes_}]", datetime.now(), flush=True)

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def main_f(self):
        try:
            sched_ = BackgroundScheduler(timezone=TZ_, daemon=True)
            sched_.remove_all_jobs()

            # schedule automations initially
            schedule_automations_f_ = self.schedule_automations_f(sched_)
            if not schedule_automations_f_["result"]:
                raise APIError(schedule_automations_f_["msg"])

            # schedule views initially
            schedule_views_f_ = self.schedule_views_f(sched_)
            if not schedule_views_f_["result"]:
                raise APIError(schedule_views_f_["msg"])

            # reschedule views regularly
            sched_.add_job(self.schedule_automations_f, "cron", day_of_week="*", hour="*", minute=f"*/{API_SCHEDULE_INTERVAL_MIN_}", id="schedule_automations", timezone=TZ_, replace_existing=True, args=[sched_])

            # reschedule views regularly
            sched_.add_job(self.schedule_views_f, "cron", day_of_week="*", hour="*", minute=f"*/{API_SCHEDULE_INTERVAL_MIN_}", id="schedule_views", timezone=TZ_, replace_existing=True, args=[sched_])

            # schedule database dumps
            args_ = {"user": {"email": "cron"}, "op": "backup"}
            sched_.add_job(Crud().dump_f, "cron", day_of_week="*", hour=f"{API_DUMP_HOURS_}", minute="0", id="schedule_dump", timezone=TZ_, replace_existing=True, args=[args_])

            sched_.start()

            res_ = True

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_


class Misc():
    def __init__(self):
        self.props_ = ["bsonType", "title", "description", "pattern", "minimum", "maximum", "minLength", "maxLength", "enum"]
        self.xtra_props_ = ["index", "width", "required", "password", "textarea", "hashtag", "map", "hidden", "default", "secret", "token", "file", "permanent",
                            "objectId", "calc", "filter", "kv", "readonly", "color", "collection", "view", "property", "html", "object", "subscriber", "subType", "manualAdd", "barcoded"]

    def post_notification(self, exc):
        ip_ = self.get_user_ip_f()
        if NOTIFICATION_SLACK_HOOK_URL_:
            exc_ = {
                "ip": ip_,
                "domain": DOMAIN_,
                "company": COMPANY_NAME_,
                "file": __file__ if __file__ else None,
                "line": exc.__traceback__.tb_lineno if hasattr(exc, "__traceback__") and hasattr(exc.__traceback__, "tb_lineno") else None,
                "name": type(exc).__name__ if hasattr(exc, "__name__") else None,
                "details": exc.details if hasattr(exc, "details") else exc
            }
            resp_ = requests.post(NOTIFICATION_SLACK_HOOK_URL_, json.dumps({"text": str(exc_)}))
            if resp_.status_code != 200:
                print("*** notification error", resp_, flush=True)

    def exception_f(self, exc):
        print("*** exception", str(exc), type(exc).__name__, __file__, exc.__traceback__.tb_lineno, flush=True)
        return {"result": False, "msg": str(exc)}

    def api_error_f(self, exc):
        print("*** api error", str(exc), type(exc).__name__, __file__, exc.__traceback__.tb_lineno, flush=True)
        self.post_notification(exc)
        return {"result": False, "msg": str(exc)}

    def auth_error_f(self, exc):
        print("*** auth error", str(exc), type(exc).__name__, __file__, exc.__traceback__.tb_lineno, flush=True)
        return {"result": False, "msg": str(exc)}

    def mongo_error_f(self, exc):
        try:
            self.post_notification(exc)
            print("*** mongo error", str(exc.details), flush=True)
            print("*** mongo error", type(exc).__name__, flush=True)
            print("*** mongo error", __file__, flush=True)
            print("*** mongo error", exc.__traceback__.tb_lineno, flush=True)
            notify_ = False
            errhtml_ = ""
            count_ = 0
            excdetails_ = exc.details
            write_errors_ = excdetails_["writeErrors"] if excdetails_ and "writeErrors" in excdetails_ else None
            if write_errors_:
                notify_ = True
                errhtml_ += "<ul>"
                count_ = len(write_errors_)
                for error_ in write_errors_:
                    errmsg_ = str(error_["errmsg"]) if "errmsg" in error_ else ""
                    errInfo_ = str(error_["errInfo"]["details"]["schemaRulesNotSatisfied"][0]["propertiesNotSatisfied"]) if "errInfo" in error_ and "details" in error_["errInfo"] and "schemaRulesNotSatisfied" in error_[
                        "errInfo"]["details"] and error_["errInfo"]["details"]["schemaRulesNotSatisfied"][0] and "propertiesNotSatisfied" in error_["errInfo"]["details"]["schemaRulesNotSatisfied"][0] else ""
                    err_ = f"{errmsg_} {errInfo_}"
                    errhtml_ += f"<li>{err_}</li>"
                errhtml_ += "</ul>"
            else:
                errmsg_ = excdetails_["errmsg"] if "errmsg" in excdetails_ else None
                errInfo_ = excdetails_["errInfo"] if "errInfo" in excdetails_ else None
                details_ = errInfo_["details"] if errInfo_ and "details" in errInfo_ else None
                schemaRulesNotSatisfied_ = details_["schemaRulesNotSatisfied"][0] if details_ and "schemaRulesNotSatisfied" in details_ and len(details_["schemaRulesNotSatisfied"]) > 0 else None
                propertiesNotSatisfied_ = schemaRulesNotSatisfied_["propertiesNotSatisfied"][0] if schemaRulesNotSatisfied_ and "propertiesNotSatisfied" in schemaRulesNotSatisfied_ and len(schemaRulesNotSatisfied_[
                                                                                                                                                                                             "propertiesNotSatisfied"]) > 0 else None
                if propertiesNotSatisfied_:
                    err_property_name_ = propertiesNotSatisfied_["propertyName"] if "propertyName" in propertiesNotSatisfied_ else None
                    err_details_ = propertiesNotSatisfied_["details"][0] if "details" in propertiesNotSatisfied_ and len(propertiesNotSatisfied_["details"]) > 0 else None
                    err_details__ = err_details_["details"][0] if err_details_ and "details" in err_details_ and len(err_details_["details"]) > 0 else None
                    reason_ = err_details__["reason"] if err_details__ and "reason" in err_details__ else None
                    consideredValue_ = err_details__["consideredValue"] if err_details__ and "consideredValue" in err_details__ else None
                    specifiedAs_ = err_details__["specifiedAs"] if err_details__ and "specifiedAs" in err_details__ else None
                    pattern_ = specifiedAs_["pattern"] if specifiedAs_ and "pattern" in specifiedAs_ else None
                    errhtml_ = ""
                    errhtml_ += f"Error in field {err_property_name_}" if err_property_name_ else ""
                    errhtml_ += f", value: {str(consideredValue_)}" if consideredValue_ else ""
                    errhtml_ += f", reason: {str(reason_)}" if reason_ else ""
                    errhtml_ += f", pattern: {str(pattern_)}" if pattern_ else ""
                else:
                    errhtml_ = errmsg_

            res_ = {"result": False, "msg": errhtml_, "notify": notify_, "count": count_}

        except Exception as exc:
            res_ = self.exception_f(exc)

        finally:
            return res_

    def log_f(self, obj):
        try:
            doc_ = {
                "log_type": obj["type"],
                "log_date": datetime.now(),
                "log_user_id": obj["user"],
                "log_ip": Misc().get_user_ip_f(),
                "log_collection_id": obj["collection"] if "collection" in obj else None,
                "log_operation": obj["op"] if "op" in obj else None,
                "log_object_id": obj["object_id"] if "object_id" in obj else None,
                "log_document": obj["document"] if "document" in obj else None,
                "_created_at": datetime.now(),
                "_created_by": obj["user"]
            }

            Mongo().db["_log"].insert_one(doc_)
            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def get_timestamp_f(self):
        dt_ = datetime.now()
        mon_ = ("0" + str(dt_.month))[-2:]
        day_ = ("0" + str(dt_.day))[-2:]
        hou_ = ("0" + str(dt_.hour))[-2:]
        min_ = ("0" + str(dt_.minute))[-2:]
        sec_ = ("0" + str(dt_.second))[-2:]
        return f"{dt_.year}{mon_}{day_}{hou_}{min_}{sec_}"

    def get_jdate_f(self):
        return int(datetime.today().timestamp())

    def allowed_file(self, filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["UPLOAD_EXTENSIONS"]

    def get_user_ip_f(self):
        ip_ = request.headers["cf-connecting-ip"] if "cf-connecting-ip" in request.headers else bleach.clean(request.access_route[-1])
        return ip_

    def get_user_host_f(self):
        host_ = request.headers["cf-connecting-ip"] if "cf-connecting-ip" in request.headers else bleach.clean(request.access_route[-1])
        return host_

    def get_except_underdashes(self):
        return ["_tags"]

    def make_array_unique_f(self, array_):
        temp_ = set()
        return [x for x in array_ if x not in temp_ and not temp_.add(x)]

    def token_validate_f(self, token_, operation_):
        try:
            find_ = Mongo().db["_token"].find_one({
                "_id": ObjectId(base64.b64decode(token_).decode())
            })
            if not find_:
                raise Exception(f"token not found {token_}")

            grant_ = f"tkn_grant_{operation_}"
            if not find_[grant_]:
                raise Exception(f"token is not permitted to {operation_}")

            res_ = {"result": True, "data": find_}

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def permitted_user_f(self, user_):
        tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
        return True if any(i in tags_ for i in PERMISSIVE_TAGS_) else False

    def properties_cleaner_f(self, properties):
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
                    # to add null option to each bsonType
                    if field_ == "bsonType":
                        dict_[field_] = [properties_property_[field_], "null"]
                    else:
                        dict_[field_] = properties_property_[field_]
            properties_new_[property_] = dict_
        return properties_new_

    def string_to_formula_f(self, set_, rec_, properties_):
        key_ = set_["key"]
        value_ = set_["value"]
        if value_[:1] == "$":
            f_ = value_[1:]
            value_ = rec_[f_] if f_ in rec_ else None
        elif value_[:1] == "=":
            formula_ = str(value_[1:]).replace(" ", "")
            parts_ = re.split("([+-/*()])", formula_)
            for part_ in parts_:
                if part_[:1] == "$":
                    f_ = part_[1:]
                    if f_ in rec_:
                        if rec_[f_] in [None, ""]:
                            rec_[f_] = 0
                        formula_ = formula_.replace(part_, str(rec_[f_]))
                    else:
                        formula_ = formula_.replace(part_, "")

            value_ = str(ne.evaluate(formula_))
            value_ = float(value_) if properties_[key_]["bsonType"] in ["number", "decimal", "double"] else int(value_) if properties_[key_]["bsonType"] == "int" else None

        return value_


class Mongo():
    def __init__(self):
        self.mongo_appname_ = "api"
        self.mongo_readpref_primary_ = "primary"
        self.mongo_readpref_secondary_ = "secondary"
        authSource_ = f"authSource={MONGO_AUTH_DB_}" if MONGO_AUTH_DB_ else ""
        replicaset_ = f"&replicaSet={MONGO_REPLICASET_}" if MONGO_REPLICASET_ and MONGO_REPLICASET_ != "" else ""
        readPreference_primary_ = f"&readPreference={self.mongo_readpref_primary_}" if self.mongo_readpref_primary_ else ""
        readPreference_secondary_ = f"&readPreference={self.mongo_readpref_secondary_}" if self.mongo_readpref_secondary_ else ""
        appname_ = f"&appname={self.mongo_appname_}" if self.mongo_appname_ else ""
        tls_ = "&tls=true"
        tlsCertificateKeyFile_ = f"&tlsCertificateKeyFile={MONGO_TLS_CERT_KEYFILE_}" if MONGO_TLS_CERT_KEYFILE_ else ""
        tlsCertificateKeyFilePassword_ = f"&tlsCertificateKeyFilePassword={MONGO_TLS_CERT_KEY_PASSWORD_}" if MONGO_TLS_CERT_KEY_PASSWORD_ else ""
        tlsCAFile_ = f"&tlsCAFile={MONGO_TLS_CA_KEYFILE_}" if MONGO_TLS_CA_KEYFILE_ else ""
        tlsAllowInvalidCertificates_ = "&tlsAllowInvalidCertificates=true"
        retryWrites_ = "&retryWrites=true"

        # PRIMARY CONNECTION STRING
        self.connstr = f"mongodb://{MONGO_INITDB_ROOT_USERNAME_}:{MONGO_INITDB_ROOT_PASSWORD_}@{MONGO_HOST_}:{MONGO_PORT_},{MONGO_REPLICA1_HOST_}:{MONGO_PORT_},{MONGO_REPLICA2_HOST_}:{MONGO_PORT_}/?{authSource_}{replicaset_}{readPreference_primary_}{appname_}{tls_}{tlsCertificateKeyFile_}{tlsCertificateKeyFilePassword_}{tlsCAFile_}{tlsAllowInvalidCertificates_}"

        # SECONDARY CONNECTION STRING
        self.connstr_cs = f"mongodb://{MONGO_INITDB_ROOT_USERNAME_}:{MONGO_INITDB_ROOT_PASSWORD_}@{MONGO_HOST_}:{MONGO_PORT_}/?{authSource_}{readPreference_primary_}{appname_}{tls_}{tlsCertificateKeyFile_}{tlsCertificateKeyFilePassword_}{tlsCAFile_}{tlsAllowInvalidCertificates_}{retryWrites_}"

        self.session_client = MongoClient(self.connstr)
        self.client = MongoClient(self.connstr)
        self.client_cs = MongoClient(self.connstr_cs).changestream
        self.db = self.client[MONGO_DB_]

    def backup_f(self):
        try:
            ts_ = Misc().get_timestamp_f()
            id_ = f"dump-{MONGO_DB_}-{ts_}"
            file_ = f"{id_}.gz"
            loc_ = f"/dump/{file_}"
            type_ = "gzip"

            command_ = f"mongodump --host \"{MONGO_HOST_}:{MONGO_PORT_},{MONGO_REPLICA1_HOST_}:{MONGO_PORT_},{MONGO_REPLICA2_HOST_}:{MONGO_PORT_}\" --db {MONGO_DB_} --authenticationDatabase {MONGO_AUTH_DB_} --username {MONGO_INITDB_ROOT_USERNAME_} --password \"{MONGO_INITDB_ROOT_PASSWORD_}\" --ssl --sslPEMKeyFile {MONGO_TLS_CERT_KEYFILE_} --sslCAFile {MONGO_TLS_CA_KEYFILE_} --sslPEMKeyPassword {MONGO_TLS_CERT_KEY_PASSWORD_} --tlsInsecure --{type_} --archive={loc_}"
            os.system(command_)

            size_ = os.path.getsize(loc_)
            res_ = {"result": True, "id": id_, "type": type_, "size": size_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def restore_f(self, obj):
        try:
            id_ = obj["id"]
            file_ = f"{id_}.gz"
            loc_ = f"/dump/{file_}"
            type_ = "gzip"

            command_ = f"mongorestore --host \"{MONGO_HOST_}:{MONGO_PORT_},{MONGO_REPLICA1_HOST_}:{MONGO_PORT_},{MONGO_REPLICA2_HOST_}:{MONGO_PORT_}\" --db {MONGO_DB_} --authenticationDatabase {MONGO_AUTH_DB_} --username {MONGO_INITDB_ROOT_USERNAME_} --password \"{MONGO_INITDB_ROOT_PASSWORD_}\" --ssl --sslPEMKeyFile {MONGO_TLS_CERT_KEYFILE_} --sslCAFile {MONGO_TLS_CA_KEYFILE_} --sslPEMKeyPassword {MONGO_TLS_CERT_KEY_PASSWORD_} --tlsInsecure --{type_} --archive={loc_} --nsExclude=\"{MONGO_DB_}._backup\" --nsExclude=\"{MONGO_DB_}._auth\" --nsExclude=\"{MONGO_DB_}._user\" --nsExclude=\"{MONGO_DB_}._log\" --drop --quiet"
            os.system(command_)

            size_ = os.path.getsize(loc_)
            res_ = {"result": True, "id": id_, "type": type_, "size": size_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    async def async_obj_f(obj):
        await asyncio.sleep(1)


class Crud():
    def __init__(self):
        self.props_ = Misc().props_
        self.xtra_props_ = Misc().xtra_props_

    def root_schemes_f(self, scheme):
        try:
            f_ = open(f"/app/_schemes/{scheme}.json", "r")
            res_ = json.loads(f_.read())

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def validate_iso8601_f(self, strv):
        try:
            regex = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
            match_iso8601 = re.compile(regex).match
            if match_iso8601(strv) is not None:
                return True
        except:
            pass

        return False

    def get_properties_f(self, collection):
        try:
            # gets the required collection
            cursor_ = Mongo().db["_collection"].find_one({"col_id": collection}) if collection[:1] != "_" else self.root_schemes_f(f"{collection}")

            if not cursor_:
                raise APIError("collection not found for properties")

            # gets the structure and its properties
            if "col_structure" not in cursor_:
                raise APIError("structure not found")

            # gets the structure and its properties
            structure_ = cursor_["col_structure"] if collection[:1] != "_" else cursor_
            if "properties" not in structure_:
                raise APIError("properties not found in structure")

            # sets the properties
            properties_ = structure_["properties"]

            # sets response with properties
            res_ = {"result": True, "properties": properties_}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def template_f(self, input_):
        try:

            proc_ = input_["proc"] if "proc" in input_ else None
            if proc_ not in ["list", "install"]:
                raise APIError("invalid template request")

            user_ = input_["user"] if "user" in input_ else None
            if not user_:
                raise APIError("user not provided")
            email_ = user_["email"]

            userindb_ = input_["userindb"] if "userindb" in input_ else None
            if not userindb_:
                raise APIError("user not found")

            data_ = None
            path_ = f"/app/_templates/templates.json"
            if not os.path.isfile(path_):
                raise APIError("no templates found")

            f_ = open(path_, "r")
            data_ = json.loads(f_.read())

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

                prefix_ = template_["prefix"] if "prefix" in template_ else "foo"

                find_one_ = Mongo().db["_collection"].find_one({"col_id": col_id_})

                if find_one_:
                    raise APIError("collection name already exists")
                if col_id_ in Mongo().db.list_collection_names():
                    raise APIError("collection data already exists")

                find_one_ = Mongo().db["_collection"].find_one({"col_prefix": prefix_})
                if find_one_:
                    raise APIError(f"collection prefix already exists: {prefix_}")

                path_ = f"/app/_templates/{file_}"
                if os.path.isfile(path_):
                    f_ = open(path_, "r")
                    jtxt_ = f_.read()
                    jtxt_ = jtxt_.replace("foo_", f"{prefix_}_")
                    structure_ = json.loads(jtxt_)

                find_one_ = Mongo().db["_collection"].insert_one({
                    "col_id": col_id_,
                    "col_title": col_title_,
                    "col_prefix": prefix_,
                    "col_structure": structure_,
                    "_created_at": datetime.now(),
                    "_created_by": email_,
                    "_modified_at": datetime.now(),
                    "_modified_by": email_,
                    "_modified_count": 0
                })

                schemevalidate_ = self.crudscheme_validate_f({
                    "collection": collection__,
                    "structure": structure_
                })
                if not schemevalidate_["result"]:
                    raise APIError(schemevalidate_["msg"])

            res_ = {"result": True, "data": data_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def inner_collection_f(self, c):
        try:
            is_crud_ = True if c[:1] != "_" else False
            collection_ = Mongo().db["_collection"].find_one({"col_id": c}) if is_crud_ else self.root_schemes_f(f"{c}")
            if not collection_:
                raise APIError(f"collection not found to root: {c}")
            res_ = {"result": True, "collection": collection_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def decode_crud_doc_f(self, doc_, properties_):
        try:
            d = doc_
            for k in properties_:
                property_ = properties_[k]
                if "bsonType" in property_:
                    if k in doc_.keys():
                        if property_["bsonType"] == "date":
                            rgx_ = "%Y-%m-%d" if doc_[k] and len(doc_[k]) == 10 else "%Y-%m-%dT%H:%M:%S"
                            ln_ = 10 if doc_[k] and len(doc_[k]) == 10 else 19
                            if doc_[k] and isinstance(doc_[k], str) and self.validate_iso8601_f(doc_[k]):
                                d[k] = datetime.strptime(doc_[k][:ln_], rgx_)
                            else:
                                d[k] = datetime.strptime(doc_[k][:ln_], rgx_) if doc_[k] is not None else None
                        elif property_["bsonType"] == "string":
                            d[k] = str(doc_[k]) if doc_[k] is not None else doc_[k]
                        elif property_["bsonType"] in ["number", "int", "float", "double"]:
                            d[k] = doc_[k] * 1 if d[k] is not None else d[k]
                        elif property_["bsonType"] == "decimal":
                            d[k] = doc_[k] * 1.00 if d[k] is not None else d[k]
                        elif property_["bsonType"] == "bool":
                            d[k] = True if d[k] and d[k] in [True, "true", "True", "TRUE"] else False
                    else:
                        if property_["bsonType"] == "bool":
                            d[k] = False

            res_ = {"result": True, "doc": d}

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def decode_crud_input_f(self, input):
        try:
            # gets the required varaibles
            collection_id_ = input["collection"]
            is_crud_ = True if collection_id_[:1] != "_" else False
            doc_ = input["doc"]

            # retrieves the collection structure and properties
            col_check_ = self.inner_collection_f(collection_id_)
            if not col_check_["result"]:
                raise APIError(col_check_["msg"])

            collection__ = col_check_["collection"] if "collection" in col_check_ else None
            structure_ = collection__["col_structure"] if is_crud_ else collection__

            # gets the properties
            if "properties" not in structure_:
                raise APIError("properties not found in the structure")
            properties_ = structure_["properties"]

            decode_crud_doc_f_ = self.decode_crud_doc_f(doc_, properties_)
            if not decode_crud_doc_f_["result"]:
                raise APIError(decode_crud_doc_f_["msg"])

            d_ = decode_crud_doc_f_["doc"]

            res_ = {"result": True, "doc": d_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def frame_convert_datetime_f(self, data_):
        try:
            str_ = str(data_).strip()
            return datetime.fromisoformat(str_) if str_ not in [" ", "0", "0.0", "NaT", "NaN", "nat", "nan", np.nan, np.double, None] else None
        except ValueError as exc:
            raise APIError(str(exc))

    def frame_convert_string_f(self, c):
        str_ = str(c).strip()
        return str_ if c is not None else c

    def frame_convert_number_f(self, c):
        return c * 1 if c is not None else c

    def frame_convert_decimal_f(self, c):
        return c * 1.00 if c is not None else c

    def purge_f(self, obj):
        try:
            collection_id_ = obj["collection"]
            user_ = obj["user"] if "user" in obj else None
            email_ = user_["email"] if user_ and "email" in user_ else None
            match_ = obj["match"]
            tfac_ = obj["tfac"] if "tfac" in obj and obj["tfac"] else None

            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise APIError(f"user auth not found {email_}")

            verify_2fa_f_ = Auth().verify_otp_f(email_, tfac_, "purge")
            if not verify_2fa_f_["result"]:
                raise APIError(verify_2fa_f_["msg"])

            is_crud_ = True if collection_id_[:1] != "_" else False
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            cursor_ = Mongo().db["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemes_f(f"{collection_}")
            if not cursor_:
                raise APIError(f"collection not found to purge: {collection_}")

            structure_ = cursor_["col_structure"] if is_crud_ else cursor_

            get_filtered_ = self.get_filtered_f({
                "match": match_,
                "properties": structure_["properties"] if "properties" in structure_ else None
            })

            ts_ = Misc().get_timestamp_f()
            bin_ = f"{collection_id_}_bin_{ts_}"
            binned_ = Mongo().db[collection_].find(get_filtered_)
            Mongo().db[bin_].insert_many(binned_)

            Mongo().db[collection_].delete_many(get_filtered_)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_,
                "op": "purge",
                "user": email_,
                "document": get_filtered_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_,
                "op": "purge",
                "user": email_,
                "document": exc.details
            })
            res = Misc().mongo_error_f(exc)

        except APIError as exc:
            res = Misc().api_error_f(exc)

        except Exception as exc:
            res = Misc().exception_f(exc)

        finally:
            return res

    def saveasview_f(self, obj):
        try:
            collection_ = obj["collection"]
            user_ = obj["user"] if "user" in obj else None
            email_ = user_["email"] if user_ and "email" in user_ else None
            match_ = obj["match"] if "match" in obj and obj["match"] != [] else []

            userindb_ = Mongo().db["_user"].find_one({"usr_id": email_})
            if not userindb_:
                raise APIError(f"no owner user found")

            _tags = userindb_["_tags"] if userindb_ and "_tags" in userindb_ else []

            aggregate_ = Mongo().db["_view"].aggregate([
                {"$match": {"vie_collection_id": collection_}},
                {"$group": {"_id": None, "count": {"$sum": 1}}},
                {"$project": {"_id": 0}}])

            json_ = json.loads(JSONEncoder().encode(list(aggregate_)))

            if json_ and "count" in json_[0]:
                next_ = int(json_[0]["count"]) + 1
            else:
                next_ = 1

            ts_ = Misc().get_timestamp_f()
            id_ = f"vie-{collection_}-{ts_}"
            vie_title_ = f"{collection_.title()} View {next_}"

            doc_ = {
                "vie_id": id_,
                "vie_collection_id": collection_,
                "vie_title": vie_title_,
                "vie_priority": 1000,
                "vie_dashboard": False,
                "vie_filter": match_,
                "vie_sched_timezone": TZ_,
                "vie_scheduled": False,
                "vie_attach_pivot": True,
                "vie_attach_csv": True,
                "vie_attach_excel": True,
                "vie_pivot_totals": False,
                "_tags": _tags
            }
            doc_["_created_at"] = doc_["_modified_at"] = datetime.now()
            doc_["_created_by"] = doc_["_modified_by"] = email_
            doc_["_modified_count"] = 0

            Mongo().db["_view"].insert_one(doc_)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_view",
                "op": "insert",
                "user": email_,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res = {"result": True, "id": id_, "view": doc_}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": "_query",
                "op": "insert",
                "user": email_,
                "document": exc.details
            })
            res = Misc().mongo_error_f(exc)

        except APIError as exc:
            res = Misc().api_error_f(exc)

        except Exception as exc:
            res = Misc().exception_f(exc)

        finally:
            return res

    def convert_cname_f(self, str_):
        CLEANTAGS = re.compile(r"<[^>]+>")
        CLEANPTRN = re.compile(r"[!'\"#$%&()*+/.,;<>?@[\]^\-`{|}~\\]")
        exceptions_ = {"ç": "c", "ğ": "g", "ı": "i", "ş": "s", "ü": "u", "ö": "o", "ü": "u", "Ç": "c", "Ğ": "g", "İ": "i", "Ş": "s", "Ü": "u", "Ö": "o", "Ü": "u", " ": "_"}
        str_ = str_.replace("\t", " ")
        str_ = re.sub(CLEANTAGS, "", str_)
        str_ = re.sub(CLEANPTRN, "", str_)
        str_ = str_[:32]
        str_ = re.sub(" +", " ", str_)
        str_ = re.sub(".", lambda char_: exceptions_.get(char_.group(), char_.group()), str_)
        str_ = str_.lower().strip().encode("ascii", "ignore").decode("ascii")
        return str_

    def save_file_f(self, obj):
        try:
            form_ = obj["form"]
            file_ = obj["file"]
            email_ = form_["email"]

            filename_ = file_.filename
            if file_ and Misc().allowed_file(filename_):
                file_.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_))
                secure_filename_ = secure_filename(filename_).lower()
                os.rename(app.config["UPLOAD_FOLDER"] + filename_, app.config["UPLOAD_FOLDER"] + secure_filename_)
                mime_ = magic.from_file(app.config["UPLOAD_FOLDER"] + secure_filename_, mime=True)
            else:
                raise APIError(f"file type not supported {filename_}")

            res_ = {
                "result": True,
                "filename": secure_filename_,
                "mime": mime_
            }

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": "_query",
                "op": "insert",
                "user": email_,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def import_f(self, obj):
        try:
            # INPUTS
            form_ = obj["form"]
            file_ = obj["file"]
            collection_ = obj["collection"]
            email_ = form_["email"]
            mimetype_ = file_.content_type

            # CREATE A DATAFRAME
            if mimetype_ in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "application/vnd.ms-excel"]:
                filetype_ = "excel"
                file_.seek(0, os.SEEK_END)
                filesize_ = file_.tell()
                if filesize_ == 0:
                    raise APIError("file is empty")
                if filesize_ > API_UPLOAD_LIMIT_BYTES_:
                    raise APIError(f"file size is greater than {API_UPLOAD_LIMIT_BYTES_} bytes")
                df_ = pd.read_excel(file_, sheet_name=collection_, header=0, engine="openpyxl")
            elif mimetype_ == "text/csv":
                filetype_ = "csv"
                filesize_ = file_.content_length
                content_ = file_.read().decode("utf-8")
                if filesize_ > API_UPLOAD_LIMIT_BYTES_ or len(content_) > API_UPLOAD_LIMIT_BYTES_:
                    raise APIError(f"file size is greater than {API_UPLOAD_LIMIT_BYTES_} bytes")
                df_ = pd.read_csv(file_, encoding="utf-8", header=0)
            else:
                raise APIError("file type is not supported")

            # TO MAKE THE COLUMNS CLEAN
            df_ = df_.rename(lambda column_: self.convert_cname_f(column_), axis="columns")

            # GET COLLECTION PROPERTIES
            collection__ = f"{collection_}_data"
            find_one_ = Mongo().db["_collection"].find_one({"col_id": collection_})
            if not find_one_:
                raise APIError(f"collection not found {collection_}")
            structure_ = find_one_["col_structure"]

            get_properties_ = self.get_properties_f(collection_)
            if not get_properties_["result"]:
                raise APIError(get_properties_["msg"])
            properties_ = get_properties_["properties"]

            # CONVERT DATASET COLUMNS
            columns_tobe_deleted_ = []
            for column_ in df_.columns:
                if column_ in properties_:
                    property_ = properties_[column_]
                    if "bsonType" in property_:
                        if property_["bsonType"] == "date":
                            try:
                                df_[column_] = df_[column_].apply(self.frame_convert_datetime_f)
                            except:
                                if "required" in structure_ and len(structure_["required"]) > 0 and column_ in structure_["required"]:
                                    raise Exception(f"invalid or empty date in {column_} column")
                        elif property_["bsonType"] == "string":
                            df_[column_] = df_[column_].apply(self.frame_convert_string_f)
                        elif property_["bsonType"] in ["number", "int"]:
                            df_[column_] = df_[column_].apply(self.frame_convert_number_f)
                        elif property_["bsonType"] in ["decimal"]:
                            df_[column_] = df_[column_].apply(self.frame_convert_decimal_f)
                    else:
                        columns_tobe_deleted_.append(column_)
                else:
                    columns_tobe_deleted_.append(column_)

            # REMOVING UNNECESSRY COLUMNS
            if "_structure" in df_.columns:
                columns_tobe_deleted_.append("_structure")
            if len(columns_tobe_deleted_) > 0:
                df_ = df_.drop(columns_tobe_deleted_, axis=1)

            # SUM OF ALL NUMERICS BY COMBINING DUPLICATE ITEMS
            # ITS OBVIOUS BUT TRUE :)
            df_ = df_.groupby(list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns), as_index=False, dropna=False).sum()

            # REMOVING NANS
            df_.replace([np.nan, pd.NaT, 'nan', 'NaN', 'nat', 'NaT'], None, inplace=True)

            # SETTING THE DEFAULTS
            df_["_created_at"] = datetime.now()
            df_["_created_by"] = email_
            df_["_modified_at"] = None
            df_["_modified_by"] = None
            df_["_modified_count"] = 0
            df_["_upload_id"] = datetime.today().strftime("%Y%m%d%H%M%S")

            # BULK INSERT DF INTO DATABASE
            payload_ = df_.to_dict("records")
            session_client_ = Mongo().session_client
            session_db_ = session_client_[MONGO_DB_]
            with session_client_.start_session(causal_consistency=True, default_transaction_options=None, snapshot=False) as session_:
                with session_.start_transaction():
                    insert_many_ = session_db_[collection__].insert_many(payload_, ordered=False, session=session_)
                    session_.commit_transaction()
                    count_ = len(insert_many_.inserted_ids)

            res_ = {"result": True, "count": count_}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_,
                "op": "import",
                "user": email_,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

            if "notify" in res_ and res_["notify"]:
                email_sent_ = Email().sendEmail_f({
                    "personalizations": {"to": [{"email": email_, "name": None}]},
                    "op": "importerr",
                    "html": f"Hi,<br /><br />Here's the data upload result about file that you've just tried to upload;<br /><br />FILE TYPE: {filetype_}<br />FILE SIZE: {filesize_} bytes<br />COLLECTION: {collection_}<br />ROW COUNT: {len(df_)}<br /><br />ERRORS:<br />{res_['msg']}"
                })
                if not email_sent_["result"]:
                    raise APIError(email_sent_["msg"])

                res_["msg"] = "please check your inbox to get the error details."

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def view_f(self, input_):
        try:
            email_ = input_["email"] if "email" in input_ else None
            if not email_:
                raise APIError("email not found in the object")

            user_ = Mongo().db["_user"].find_one({"usr_id": email_})
            if not user_ or user_ is None:
                raise APIError("user not found for view")

            user_tags_ = user_["_tags"]

            vie_structure_ = self.root_schemes_f("_view")
            if not vie_structure_:
                raise APIError("view structure not found")

            _id = None
            vie_id_ = None

            if "_id" in input_:
                _id = input_["_id"]

            if "vie_id" in input_:
                vie_id_ = input_["vie_id"]

            source_ = input_["source"]
            if source_ not in ["internal", "external", "propsonly"]:
                raise APIError("invalid source")

            if _id not in [None, ""]:
                view_ = Mongo().db["_view"].find_one({"_id": ObjectId(_id)})
            else:
                if vie_id_ is not None:
                    view_ = Mongo().db["_view"].find_one({"vie_id": vie_id_})
                else:
                    raise APIError(f"view is not recognized")

            if not view_:
                raise APIError(f"view not found {vie_id_}")

            if "vie_collection_id" not in view_:
                raise APIError("collection not found")

            vie_collection_id_ = view_["vie_collection_id"]

            if not "_tags" in view_:
                raise APIError("no tags found")

            view_tags_ = view_["_tags"]
            if not view_tags_ or view_tags_ == []:
                raise APIError("no subscriber found")

            matches_ = [key for key, val in enumerate(user_tags_) if val in view_tags_]

            if len(matches_) == 0:
                raise APIError("user is not a subscriber")

            if not "vie_filter" in view_:
                raise APIError("filter not found in view")
            vie_filter_ = view_["vie_filter"]

            vie_projection_ = view_["vie_projection"] if "vie_projection" in view_ else []

            is_crud_ = True if vie_collection_id_[:1] != "_" else False

            vie_collection_ = Mongo().db["_collection"].find_one({"col_id": vie_collection_id_})

            # Get the collection structure of the query
            if is_crud_ and not "col_structure" in vie_collection_:
                raise APIError("structure not found in collection")

            col_structure_ = vie_collection_["col_structure"] if is_crud_ else self.root_schemes_f(f"{vie_collection_id_}")

            # Get properties of the structure
            if not "properties" in col_structure_:
                raise APIError("properties not found in structure")
            properties_ = col_structure_["properties"]

            # Set the properties of the all collections (own+parents)
            properties_master_ = {}

            for property_ in properties_:
                properties_property_ = properties_[property_]
                properties_master_[property_] = properties_property_
                bsonType_ = properties_property_["bsonType"] if "bsonType" in properties_property_ else None
                if bsonType_ == "array":
                    if "items" in properties_property_:
                        items_ = properties_property_["items"]
                        if "properties" in items_:
                            item_properties_ = items_["properties"]
                            for item_property_ in item_properties_:
                                properties_master_[item_property_] = item_properties_[item_property_]

            # Initializing of the aggregation elements
            pipe_ = []
            unset_ = []

            # Adding master collection's _id first
            set_ = {"$set": {"_ID": {"$toObjectId": "$_id"}}}
            pipe_.append(set_)

            # Get parents of the structure
            parents_ = []
            if "parents" in col_structure_:
                parents_ = col_structure_["parents"]

            if "vie_order_by" in view_ and len(view_["vie_order_by"]) > 0:
                sort_ = {}
                vie_order_by_ = view_["vie_order_by"]
                for ob_ in vie_order_by_:
                    sort_[ob_] = 1
            elif "sort" in col_structure_ and col_structure_["sort"] != {}:
                sort_ = col_structure_["sort"]
            else:
                sort_ = {"_modified_at_": -1}

            unset_.append("_modified_by")
            unset_.append("_modified_at")
            unset_.append("_modified_count")
            unset_.append("_created_at")
            unset_.append("_created_by")
            unset_.append("_structure")
            unset_.append("_tags")
            # unset_.append("_id")
            unset_.append("_ID")

            for properties_master__ in properties_master_:
                if properties_master__[:1] == "_" and properties_master__ not in Misc().get_except_underdashes():
                    unset_.append(properties_master__)

            for parent_ in parents_:
                if "lookup" in parent_ and "collection" in parent_:
                    parent_collection_ = parent_["collection"]
                    find_one_ = Mongo().db["_collection"].find_one({"col_id": parent_collection_})
                    if find_one_ and "col_structure" in find_one_ and "properties" in find_one_["col_structure"]:
                        for property_ in find_one_["col_structure"]["properties"]:
                            properties_master_[property_] = find_one_["col_structure"]["properties"][property_]

                        look_ = parent_["lookup"]
                        pipeline__ = []
                        let_ = {}

                        for look__ in look_:
                            if look__["local"] and look__["remote"]:
                                local_ = look__["local"]
                                remote_ = look__["remote"]
                                let_[f"{local_}"] = f"${local_}"
                                pipeline__.append({"$eq": [f"$${local_}", f"${remote_}"]}),

                        pipeline_ = [{"$match": {"$expr": {"$and": pipeline__}}}]

                        lookup_ = {
                            "from": f"{parent_collection_}_data",
                            "let": let_,
                            "pipeline": pipeline_,
                            "as": parent_collection_
                        }

                        unwind_ = {"path": f"${parent_collection_}", "preserveNullAndEmptyArrays": True}
                        replace_with_ = {"$mergeObjects": ["$$ROOT", f"${parent_collection_}"]}
                        pipe_.append({"$lookup": lookup_})
                        pipe_.append({"$unwind": unwind_})
                        pipe_.append({"$replaceWith": replace_with_})
                        unset_.append(parent_collection_)

            pipe_.append({"$sort": sort_})

            if len(vie_filter_) > 0:
                get_filtered_ = self.get_filtered_f({
                    "match": vie_filter_,
                    "properties": properties_master_ if properties_master_ else None
                })

                pipe_.append({"$match": get_filtered_})

            if unset_ and len(unset_) > 0:
                unset_ = list(dict.fromkeys(unset_))
                pipe_.append({"$unset": unset_})

            # Append limit and skip
            pipe_.append({"$skip": 0})

            # if view has a projection response will be limited according to projection keys
            if vie_projection_ and len(vie_projection_) > 0:

                project_ = {}
                for p_ in vie_projection_:
                    project_[p_] = 1
                pipe_.append({"$project": project_})

                properties_tmp_ = {}
                for p_ in properties_master_:
                    property_ = properties_master_[p_]
                    if p_ in vie_projection_:
                        properties_tmp_[p_] = properties_master_[p_]

                properties_master_ = properties_tmp_

            # Run aggregation
            data_ = f"{vie_collection_id_}_data" if is_crud_ else vie_collection_id_
            aggregate_ = list(Mongo().db[data_].aggregate(pipe_))

            records_ = []
            if source_ != "propsonly":
                records_ = json.loads(JSONEncoder().encode(aggregate_))

            count_ = len(records_) if records_ else 0

            res_ = {
                "result": True,
                "record": json.loads(JSONEncoder().encode(view_)) if source_ == "internal" else None,
                "data": records_ if source_ == "external" else [] if source_ == "propsonly" else records_[:10],
                "count": count_,
                "properties": properties_master_,
                "structure": vie_structure_,
                "col_id": vie_collection_id_,
                "col_structure": col_structure_
            }

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": vie_collection_id_,
                "op": "view",
                "user": email_,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def announce_f(self, input_):
        try:
            # checks if user data in the input
            if not "user" in input_:
                raise APIError("user not found in the input")

            # checks if tfac in the input
            if "tfac" not in input_:
                raise APIError("tfac not found in the input")

            # checks if view in the input
            if "view" not in input_:
                raise APIError("view not found in the input")

            # checks if email in the user input
            if "email" not in input_["user"]:
                raise APIError("email not found in user")

            if "scope" not in input_:
                raise APIError("scope found in the input")

            email_ = input_["user"]["email"]
            tfac_ = input_["tfac"]
            view_ = input_["view"]
            scope_ = input_["scope"]

            if scope_ not in ["test", "live"]:
                raise APIError("scope is invalid")

            # verify OTP
            verify_2fa_f_ = Auth().verify_otp_f(email_, tfac_, "announce")
            if not verify_2fa_f_["result"]:
                raise APIError(verify_2fa_f_["msg"])

            announce_view_f_ = Schedular().announce_view_f(view_, scope_, email_)
            if not announce_view_f_["result"]:
                raise APIError(announce_view_f_["msg"])

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def dump_f(self, obj):
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
                "_created_at": datetime.now(),
                "_created_by": email_,
                "_modified_at": datetime.now(),
                "_modified_by": email_
            }

            Mongo().db["_backup"].insert_one(doc_)
            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def parent_f(self, obji):
        try:
            collection_ = obji["collection"]
            fields_ = obji["fields"]

            data_collection_ = f"{collection_}_data"
            projection_ = {}
            for field_ in fields_:
                projection_[field_] = 1

            cursor_ = Mongo().db[data_collection_].find(filter={}, projection=projection_).limit(1000)
            docs_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []

            res_ = {
                "result": True,
                "data": docs_
            }

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def get_filtered_f(self, obj):
        match_ = obj["match"]
        properties_ = obj["properties"] if "properties" in obj else None
        fand_ = []
        filtered_ = {}
        if properties_:
            for f in match_:
                if f["key"] and f["op"] and (f["key"] in ["_id", "_upload_id"] or f["key"] in properties_):

                    fres_ = None
                    typ = properties_[f["key"]]["bsonType"] if f["key"] in properties_ else "string"

                    if f["op"] in ["eq", "contains"]:
                        if typ in ["number", "decimal"]:
                            fres_ = float(f["value"])
                        elif typ == "bool":
                            fres_ = bool(f["value"])
                        elif typ == "date":
                            fres_ = datetime.strptime(f["value"][:10], "%Y-%m-%d")
                        else:
                            if f["key"] == "_id":
                                fres_ = ObjectId(f["value"])
                            else:
                                fres_ = {"$regex": f["value"], "$options": "i"} if f["value"] else {"$regex": "", "$options": "i"}

                    if f["op"] in ["ne", "nc"]:
                        if typ in ["number", "decimal"]:
                            fres_ = {"$not": {"$eq": float(f["value"])}}
                        elif typ == "bool":
                            fres_ = {"$not": {"$eq": bool(f["value"])}}
                        elif typ == "date":
                            fres_ = {"$not": {"$eq": datetime.strptime(f["value"][:10], "%Y-%m-%d")}}
                        else:
                            fres_ = {"$not": {"$regex": f["value"], "$options": "i"}} if f["value"] else {"$not": {"$regex": "", "$options": "i"}}

                    elif f["op"] in ["in", "nin"]:
                        separated_ = re.split(",|;|\n", f["value"])
                        list_ = [s.strip() for s in separated_] if f["key"] != "_id" else [ObjectId(s.strip()) for s in separated_]
                        if f["op"] == "in":
                            fres_ = {"$in": list_ if typ != "number" else list(map(float, list_))}
                        else:
                            fres_ = {"$nin": list_ if typ != "number" else list(map(float, list_))}

                    elif f["op"] == "gt":
                        if typ in ["number", "decimal"]:
                            fres_ = {"$gt": float(f["value"])}
                        elif typ == "date":
                            fres_ = {"$gt": datetime.strptime(f["value"][:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$gt": f["value"]}

                    elif f["op"] == "gte":
                        if typ in ["number", "decimal"]:
                            fres_ = {"$gte": float(f["value"])}
                        elif typ == "date":
                            fres_ = {"$gte": datetime.strptime(f["value"][:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$gte": f["value"]}

                    elif f["op"] == "lt":
                        if typ in ["number", "decimal"]:
                            fres_ = {"$lt": float(f["value"])}
                        elif typ == "date":
                            fres_ = {"$lt": datetime.strptime(f["value"][:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$lt": f["value"]}

                    elif f["op"] == "lte":
                        if typ in ["number", "decimal"]:
                            fres_ = {"$lte": float(f["value"])}
                        elif typ == "date":
                            fres_ = {"$lte": datetime.strptime(f["value"][:10], "%Y-%m-%d")}
                        else:
                            fres_ = {"$lte": f["value"]}

                    elif f["op"] == "true":
                        fres_ = {"$eq": True}

                    elif f["op"] == "false":
                        fres_ = {"$eq": False}

                    elif f["op"] == "nnull":
                        array_ = []
                        array1_ = {}
                        array2_ = {}
                        array1_[f["key"]] = {"$ne": None}
                        array2_[f["key"]] = {"$exists": True}
                        array_.append(array1_)
                        array_.append(array2_)

                    elif f["op"] == "null":
                        array_ = []
                        array1_ = {}
                        array2_ = {}
                        array1_[f["key"]] = {"$eq": None}
                        array2_[f["key"]] = {"$exists": False}
                        array_.append(array1_)
                        array_.append(array2_)

                    fpart_ = {}
                    if f["op"] in ["null", "nnull"]:
                        fpart_["$or"] = array_
                    else:
                        fpart_[f["key"]] = fres_

                    fand_.append(fpart_)

            filtered_ = {"$and": fand_} if fand_ and len(fand_) > 0 else {}

        return filtered_

    def visual_f(self, obj):
        try:
            id_ = obj["id"]
            user_ = obj["user"]

            # checks enabled visuals
            doc_ = Mongo().db["_view"].find_one({"_id": ObjectId(id_)})
            if not doc_:
                raise APIError("no view found")

            value_ = 0
            perchange_ = 0
            color_scheme_def_ = ["FireBrick", "DarkSeaGreen", "CornFlowerBlue", "LightSkyBlue"]
            vie_p_xaxis_show_ = True if "vie_p_xaxis_show" in doc_ and doc_["vie_p_xaxis_show"] in ["true", True] else False
            vie_p_yaxis_show_ = True if "vie_p_yaxis_show" in doc_ and doc_["vie_p_yaxis_show"] in ["true", True] else False
            vie_p_xaxis_label_show_ = True if "vie_p_xaxis_label_show" in doc_ and doc_["vie_p_xaxis_label_show"] in ["true", True] else False
            vie_p_yaxis_label_show_ = True if "vie_p_yaxis_label_show" in doc_ and doc_["vie_p_yaxis_label_show"] in ["true", True] else False
            vie_p_legend_show_ = True if "vie_p_legend_show" in doc_ and doc_["vie_p_legend_show"] in ["true", True] else False
            vie_p_gradient_ = True if "vie_p_gradient" in doc_ and doc_["vie_p_gradient"] in ["true", True] else False
            vie_p_datalabel_show_ = True if "vie_p_datalabel_show" in doc_ and doc_["vie_p_datalabel_show"] in ["true", True] else False
            vie_p_grid_show_ = True if "vie_p_grid_show" in doc_ and doc_["vie_p_grid_show"] == True else False
            vie_p_kpi_ = True if "vie_p_kpi" in doc_ and doc_["vie_p_kpi"] in ["true", True] else False
            vie_kpi_target_value_ = doc_["vie_kpi_target_value"] if "vie_kpi_target_value" in doc_ else 0
            vie_visual_style_ = doc_["vie_visual_style"] if "vie_visual_style" in doc_ else "Vertical Bar"
            vie_chart_xaxis_ = doc_["vie_pivot_index"][0] if "vie_pivot_index" in doc_ and len(doc_["vie_pivot_index"]) > 0 else None
            vie_chart_yaxis_ = doc_["vie_pivot_values"][0]["key"] if "vie_pivot_values" in doc_ and len(doc_["vie_pivot_values"]) > 0 and "key" in doc_["vie_pivot_values"][0] else None
            vie_chart_function_ = doc_["vie_pivot_values"][0]["value"] if "vie_pivot_values" in doc_ and len(doc_["vie_pivot_values"]) > 0 and "value" in doc_["vie_pivot_values"][0] else "sum"
            vie_chart_legend_ = doc_["vie_pivot_columns"][0] if "vie_pivot_columns" in doc_ and len(doc_["vie_pivot_columns"]) > 0 else None
            vie_p_color_scheme_ = doc_["vie_p_color_scheme"] if "vie_p_color_scheme" in doc_ and len(doc_["vie_p_color_scheme"]) > 0 else []
            vie_p_color_scheme_ += color_scheme_def_
            view_id_ = doc_["vie_id"]

            generate_view_data_f_ = Crud().view_f({
                "email": user_["usr_id"],
                "source": "external",
                "vie_id": view_id_,
                "_id": None
            })

            if not generate_view_data_f_["result"]:
                raise APIError(generate_view_data_f_["msg"])

            view_data_ = generate_view_data_f_["data"] if generate_view_data_f_ and "data" in generate_view_data_f_ else []
            view_properties_ = generate_view_data_f_["properties"] if generate_view_data_f_ and "properties" in generate_view_data_f_ else {}

            vie_p_xaxis_label_ = view_properties_[vie_chart_xaxis_]["title"] if vie_chart_xaxis_ in view_properties_ and "title" in view_properties_[vie_chart_xaxis_] else vie_chart_xaxis_
            vie_p_yaxis_label_ = view_properties_[vie_chart_yaxis_]["title"] if vie_chart_yaxis_ in view_properties_ and "title" in view_properties_[vie_chart_yaxis_] else vie_chart_yaxis_
            vie_p_legend_title_ = view_properties_[vie_chart_legend_]["title"] if vie_chart_legend_ in view_properties_ and "title" in view_properties_[vie_chart_legend_] else vie_chart_legend_

            # convert view data to pandas df
            df_ = pd.DataFrame(list(view_data_)).fillna(0)

            dropped_ = []
            dropped_.append(vie_chart_xaxis_)
            dropped_.append(vie_chart_yaxis_)
            dropped_.append(vie_chart_legend_)

            groupby_ = []
            sort_ = None

            if vie_visual_style_ == "Line":
                if vie_chart_legend_ in df_:
                    groupby_.append(vie_chart_legend_)
                if vie_chart_xaxis_ in df_:
                    groupby_.append(vie_chart_xaxis_)
                    sort_ = vie_chart_xaxis_
            else:
                if vie_chart_xaxis_ in df_:
                    groupby_.append(vie_chart_xaxis_)
                if vie_chart_legend_ in df_:
                    groupby_.append(vie_chart_legend_)

            df_ = df_.drop([x for x in df_.columns if x not in dropped_], axis=1)

            count_ = 0
            if df_ is not None:
                count_ = len(df_)
                if count_ > 0 and vie_chart_yaxis_:
                    if vie_chart_function_ == "sum":
                        value_ = float(df_[vie_chart_yaxis_].sum())
                    elif vie_chart_function_ == "count":
                        value_ = int(len(df_[vie_chart_yaxis_]))
                    elif vie_chart_function_ == "unique":
                        value_ = int(df_[vie_chart_yaxis_].nunique())
                    elif vie_chart_function_ in ["mean", "avg"]:
                        value_ = float(df_[vie_chart_yaxis_].mean())
                    elif vie_chart_function_ in ["stdev", "std"]:
                        value_ = float(df_[vie_chart_yaxis_].std())
                    elif vie_chart_function_ == "var":
                        value_ = float(df_[vie_chart_yaxis_].var())
                    else:
                        raise APIError("invalid visual function")

                if vie_p_kpi_ and value_ >= 0 and vie_kpi_target_value_ > 0:
                    perchange_ = float(((value_ - vie_kpi_target_value_) / vie_kpi_target_value_) * 100)

                if sort_:
                    df_ = df_.sort_values(by=sort_)

                if len(groupby_) > 0:
                    df_ = df_.groupby(groupby_, as_index=False).sum() if vie_chart_function_ == "sum" else df_.groupby(groupby_, as_index=False).count()

            dfj_ = json.loads(df_.to_json(orient="records"))

            series_ = []
            series_sub_ = []
            xaxis_ = None
            legend_ = None

            if vie_chart_xaxis_:
                if vie_visual_style_ in ["Pie", "Vertical Bar", "Horizontal Bar"]:
                    for idx_, item_ in enumerate(dfj_):
                        xaxis_ = item_[vie_chart_xaxis_] if vie_chart_xaxis_ in item_ else None
                        yaxis_ = item_[vie_chart_yaxis_] if vie_chart_yaxis_ in item_ else None
                        if xaxis_ and yaxis_:
                            series_.append({"name": xaxis_, "value": yaxis_})
                elif vie_visual_style_ == "Line":
                    for idx_, item_ in enumerate(dfj_):
                        if idx_ > 0 and item_[vie_chart_legend_] != legend_:
                            series_.append({"name": legend_, "series": series_sub_})
                            series_sub_ = []
                        series_sub_.append({"name": item_[vie_chart_xaxis_], "value": item_[vie_chart_yaxis_]})
                        legend_ = item_[vie_chart_legend_] if vie_chart_legend_ in item_ else None
                    if legend_:
                        series_.append({"name": legend_, "series": series_sub_})
                else:
                    for idx_, item_ in enumerate(dfj_):
                        if idx_ > 0 and item_[vie_chart_xaxis_] != xaxis_:
                            series_.append({"name": xaxis_, "series": series_sub_})
                            series_sub_ = []
                        if vie_chart_legend_ in item_ and item_[vie_chart_legend_] is not None:
                            series_sub_.append({"name": item_[vie_chart_legend_], "value": item_[vie_chart_yaxis_]})
                        xaxis_ = item_[vie_chart_xaxis_] if vie_chart_xaxis_ in item_ else None
                    if xaxis_:
                        series_.append({"name": xaxis_, "series": series_sub_})

            res_ = {
                "result": True,
                "data": series_,
                "value": value_,
                "count": count_,
                "perchange": perchange_,
                "properties": view_properties_,
                "style": vie_visual_style_,
                "xaxis": vie_chart_xaxis_,
                "yaxis": vie_chart_yaxis_,
                "function": vie_chart_function_,
                "legend": vie_chart_legend_,
                "kpi": vie_p_kpi_,
                "kpi_target_value": vie_kpi_target_value_,
                "xaxis_label": vie_p_xaxis_label_,
                "yaxis_label": vie_p_yaxis_label_,
                "xaxis_show": vie_p_xaxis_show_,
                "xaxis_label_show": vie_p_xaxis_label_show_,
                "yaxis_show": vie_p_yaxis_show_,
                "yaxis_label_show": vie_p_yaxis_label_show_,
                "legend_show": vie_p_legend_show_,
                "legend_title": vie_p_legend_title_,
                "gradient": vie_p_gradient_,
                "datalabel_show": vie_p_datalabel_show_,
                "grid_show": vie_p_grid_show_,
                "color_scheme": vie_p_color_scheme_
            }

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def view_to_dataset_f(self, obj):
        try:
            id_ = obj["id"]
            user_ = obj["user"]

            doc_ = Mongo().db["_view"].find_one({
                "_id": ObjectId(id_),
                "_tags": {"$elemMatch": {"$in": user_["_tags"]}}
            })
            if not doc_:
                raise APIError("pivot view not found")

            vie_id_ = doc_["vie_id"]
            vie_collection_id_ = doc_["vie_collection_id"]
            vie_excluded_columns_ = doc_["vie_excluded_columns"] if "vie_excluded_columns" in doc_ and doc_["vie_excluded_columns"] != [] and len(doc_["vie_excluded_columns"]) > 0 else []

            col_id_ = f"{vie_collection_id_}_data"
            is_crud_ = True if vie_collection_id_[:1] != "_" else False

            # starting pivot
            collection_find_one_ = Mongo().db["_collection"].find_one({"col_id": vie_collection_id_})
            if is_crud_ and not collection_find_one_:
                raise APIError(f"collection not found to view: {col_id_}")

            generate_view_data_f_ = Crud().view_f({
                "email": user_["usr_id"],
                "source": "external",
                "vie_id": vie_id_,
                "_id": None
            })
            if not generate_view_data_f_["result"]:
                raise APIError(generate_view_data_f_["msg"])

            view_data_ = generate_view_data_f_["data"] if generate_view_data_f_ and "data" in generate_view_data_f_ else []
            if not view_data_ or len(view_data_) == 0:
                res_ = {
                    "result": True,
                    "pivot": None,
                    "file_csv": None,
                    "file_excel": None,
                    "file_csv_raw": None,
                    "file_excel_raw": None,
                    "count": 0,
                    "statistics": None,
                    "df": None
                }
                return

            df_ = pd.DataFrame(list(view_data_)).fillna("")

            dropped_ = [
                "_id",
                "_ID",
                "_created_at",
                "_created_by",
                "_modified_at",
                "_modified_by",
                "_modified_count",
                "_structure"
            ]

            df_.insert(0, "number_of_rows", "data")

            # checks properties to remove or non numeric to NaN

            view_properties_ = generate_view_data_f_["properties"] if generate_view_data_f_ and "properties" in generate_view_data_f_ else {}

            for prop_ in view_properties_:
                property_ = view_properties_[prop_]
                if "bsonType" in property_:
                    if prop_ in df_:
                        if property_["bsonType"] == "array":
                            df_[prop_] = df_[prop_].apply(",".join)
                        if property_["bsonType"] in ["number", "decimal"]:
                            df_[prop_] = pd.to_numeric(df_[prop_], errors="coerce")
                    if property_["bsonType"] in ["object", "array"]:
                        dropped_.append(prop_)

            for dropped__ in dropped_:
                if dropped__ not in df_:
                    dropped_.remove(dropped__)

            pvs_ = []
            aggfunc_ = {}

            vie_pivot_index_ = doc_["vie_pivot_index"] if "vie_pivot_index" in doc_ and len(doc_["vie_pivot_index"]) > 0 else ["number_of_rows"]
            vie_pivot_columns_ = doc_["vie_pivot_columns"] if "vie_pivot_columns" in doc_ and len(doc_["vie_pivot_columns"]) > 0 else []
            vie_pivot_totals_ = doc_["vie_pivot_totals"] if "vie_pivot_totals" in doc_ else False
            vie_pivot_values_ = doc_["vie_pivot_values"] if "vie_pivot_values" in doc_ else [{
                "key": "number_of_rows",
                "value": "count"
            }]

            # to sort pivot columns #1
            vie_pivot_values_.reverse()

            for idx_, f_ in enumerate(vie_pivot_values_):
                if "key" in f_ and "value" in f_:
                    key_ = f_["key"]
                    value_ = f_["value"]

                    # to sort pivot columns #2
                    r_ = ' ' * idx_
                    nc_ = f"{r_}{key_} [{value_}]"

                    df_[nc_] = df_[key_]
                    pvs_.append(nc_)

                    if value_ in ["sum", "mean", "average", "stdev", "var", "max", "min"]:
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

            if dropped_ and len(dropped_) > 0:
                df_ = df_.drop([x for x in dropped_ if x in df_.columns], axis=1)

            pvs_ = list(dict.fromkeys(pvs_))

            for index_ in vie_pivot_index_:
                vie_pivot_index_.remove(index_) if index_ not in df_.columns else None

            for index_ in vie_pivot_columns_:
                vie_pivot_columns_.remove(index_) if index_ not in df_.columns else None

            for index_ in vie_pivot_values_:
                vie_pivot_values_.remove(index_) if index_["key"] not in df_.columns else None

            df_raw_ = df_.groupby(list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns), as_index=False).sum()

            if vie_excluded_columns_ and len(vie_excluded_columns_) > 0:
                df_.drop(vie_excluded_columns_, axis=1, inplace=True)

            df_ = df_.groupby(list(df_.select_dtypes(exclude=["float", "int", "float64", "int64"]).columns), as_index=False).sum()

            pd.set_option("display.float_format", lambda x: "%.2f" % x)

            pivot_table_ = pd.pivot_table(
                df_,
                values=pvs_,
                index=vie_pivot_index_,
                columns=vie_pivot_columns_,
                aggfunc=aggfunc_,
                margins=vie_pivot_totals_,
                margins_name="Total",
                fill_value=0
            )

            if "number_of_rows" in df_.columns:
                df_.drop("number_of_rows", axis=1, inplace=True)
                df_raw_.drop("number_of_rows", axis=1, inplace=True)

            for c_ in df_.columns:
                if c_.find("[") != -1:
                    df_.drop(c_, axis=1, inplace=True)
                    df_raw_.drop(c_, axis=1, inplace=True)

            file_csv_ = f"{doc_['vie_id']}.csv"
            file_excel_ = f"{doc_['vie_id']}.xlsx"
            file_csv_raw_ = f"{doc_['vie_id']}-detail.csv"
            file_excel_raw_ = f"{doc_['vie_id']}-detail.xlsx"

            # save excel and csv into /cron folder at local storage
            df_.to_csv(f"/cron/{file_csv_}", sep=";", encoding="utf-8", header=True, decimal=".", index=False)
            df_.to_excel(f"/cron/{file_excel_}", sheet_name=col_id_, engine="xlsxwriter", header=True, index=False)
            df_raw_.to_csv(f"/cron/{file_csv_raw_}", sep=";", encoding="utf-8", header=True, decimal=".", index=False)
            df_raw_.to_excel(f"/cron/{file_excel_raw_}", sheet_name=col_id_, engine="xlsxwriter", header=True, index=False)
            dfj_ = df_raw_.head(10).to_json(orient="records")
            describe_ = df_.describe(include="all") if df_ is not None else None
            statistics_ = json.loads(describe_.to_json()) if describe_ is not None else None

            res_ = {
                "result": True,
                "pivot": pivot_table_,
                "file_csv": file_csv_,
                "file_excel": file_excel_,
                "file_csv_raw": file_csv_raw_,
                "file_excel_raw": file_excel_raw_,
                "count": len(df_),
                "statistics": statistics_,
                "df": dfj_
            }

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def views_f(self, obj):
        try:
            # receives the user in db
            user_ = obj["userindb"]
            records_ = []

            vie_structure_ = self.root_schemes_f("_view")
            if not vie_structure_:
                raise APIError("view structure not found")

            views_ = Mongo().db["_view"].find(filter={
                "_tags": {"$elemMatch": {"$in": user_["_tags"]}}
            }, sort=[("vie_priority", 1)])

            for view_ in views_:
                vie_collection_id_ = view_["vie_collection_id"]
                is_crud_ = True if vie_collection_id_[:1] != "_" else False
                collection_ = Mongo().db["_collection"].find_one({"col_id": vie_collection_id_}) if is_crud_ else self.root_schemes_f(f"{vie_collection_id_}")
                if not collection_:
                    continue
                records_.append(view_)

            res_ = {
                "result": True,
                "data": json.loads(JSONEncoder().encode(list(records_))),
                "structure": vie_structure_
            }

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def collections_f(self, obj):
        try:
            user_ = obj["userindb"]
            data_ = []
            structure_ = self.root_schemes_f("_collection")

            if Misc().permitted_user_f(user_):
                data_ = list(Mongo().db["_collection"].find(filter={}, sort=[("_updated_at", -1)]))
            else:
                usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
                for usr_tag_ in usr_tags_:
                    filter_ = {
                        "per_tag": usr_tag_,
                        "$or": [{"per_insert": True}, {"per_read": True}, {"per_update": True}, {"per_delete": True}]
                    }
                    permissions_ = Mongo().db["_permission"].find(filter=filter_, sort=[("per_collection_id", 1)])
                    for permission_ in permissions_:
                        collection_ = Mongo().db["_collection"].find_one({"col_id": permission_["per_collection_id"]})
                        data_.append(collection_)

            res_ = {
                "result": True,
                "data": json.loads(JSONEncoder().encode(data_)),
                "structure": structure_
            }

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def collection_f(self, obj):
        try:
            user_ = obj["userindb"]
            col_id_ = obj["collection"]
            data_ = {}
            usr_tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []

            if Misc().permitted_user_f(user_):
                permitted_ = True
            else:
                permitted_ = False
                for usr_tag_ in usr_tags_:
                    permissions_ = Mongo().db["_permission"].find_one({
                        "per_collection_id": col_id_,
                        "per_tag": usr_tag_,
                        "$or": [{"per_insert": True}, {"per_read": True}, {"per_update": True}, {"per_delete": True}]
                    })
                    if permissions_:
                        permitted_ = True
                        break

            if permitted_:
                data_ = Mongo().db["_collection"].find_one({"col_id": col_id_})
            else:
                raise APIError(f"no permission for {col_id_}")

            res_ = {
                "result": True,
                "data": data_
            }

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def read_f(self, input_):  # find_ function is used to generate a query from the database
        try:
            # gets the parameters required
            user_ = input_["user"]
            limit_ = input_["limit"]
            page = input_["page"]
            collection_id_ = input_["collection"]
            projection_ = input_["projection"]
            skip_ = limit_ * (page - 1)
            view_ = input_["view"]
            userindb_ = input_["userindb"]
            match_ = input_["match"] if "match" in input_ and len(input_["match"]) > 0 else []

            # generates the data collection name according to the collection id
            is_crud_ = True if collection_id_[:1] != "_" else False
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            # sets the sort collation up to the user preferences
            collation_ = {"locale": user_["locale"]} if user_ and "locale" in user_ else {"locale": "tr"}

            # created a cursor for retrieve the collection structure will be added into the respone
            cursor_ = Mongo().db["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemes_f(f"{collection_id_}")

            if not cursor_:
                raise APIError(f"collection not found to read: {collection_id_}")

            structure_ = cursor_["col_structure"] if is_crud_ else cursor_
            reconfig_ = cursor_["_reconfig_req"] if "_reconfig_req" in cursor_ and cursor_["_reconfig_req"] == True else False

            # combines view filter and user filter in view mode
            if view_ is not None and collection_id_ == view_["vie_collection_id"]:
                cursor_ = Mongo().db["_view"].find_one({
                    "vie_id": view_["vie_id"],
                    "_tags": {"$elemMatch": {"$in": userindb_["_tags"]}}
                })
                if cursor_:
                    match_ += cursor_["vie_filter"]

            get_filtered_ = self.get_filtered_f({
                "match": match_,
                "properties": structure_["properties"] if "properties" in structure_ else None
            })

            # sets default response as a cursor is empty
            res_ = {
                "result": True,
                "data": [],
                "count": 0,
                "structure": structure_,
                "reconfig": reconfig_
            }

            sort_ = list(input_["sort"].items()) if "sort" in input_ and input_["sort"] else list(structure_["sort"].items()) if "sort" in structure_ and structure_["sort"] else [("_modified_at", -1)]

            # create cursor for the query
            cursor_ = Mongo().db[collection_].find(filter=get_filtered_, projection=projection_, sort=sort_, collation=collation_).skip(skip_).limit(limit_)

            docs_ = json.loads(JSONEncoder().encode(list(cursor_)))[:limit_] if cursor_ else []
            count_ = Mongo().db[collection_].count_documents(get_filtered_)

            # sets the response object
            res_ = {
                "result": True,
                "data": docs_,
                "count": count_,
                "structure": structure_,
                "reconfig": reconfig_
            }

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_,
                "op": "read",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def crudscheme_validate_f(self, obj):
        try:
            properties_ = {}
            required_ = []
            validator_ = {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {},
                    "required": ["_id"]
                }
            }

            structure_ = obj["structure"]
            collection_ = obj["collection"]

            if collection_ in Mongo().db.list_collection_names() and "properties" in structure_:
                properties_ = structure_["properties"]
                properties_ = Misc().properties_cleaner_f(properties_)

                if "required" in structure_ and structure_["required"] and len(structure_["required"]) > 0:
                    required_ = structure_["required"]
                else:
                    required_ = None

                validator_["$jsonSchema"].update({"properties": properties_}) if properties_ else None
                validator_["$jsonSchema"].update({"required": required_}) if required_ else None

                Mongo().db.command({
                    "collMod": collection_,
                    "validator": validator_
                })

                Mongo().db[collection_].drop_indexes()
                if "index" in structure_ and len(structure_["index"]) > 0:
                    for indexes in structure_["index"]:
                        ixs = []
                        ix_name_ = ""
                        for ix in indexes:
                            ixs.append((ix, pymongo.ASCENDING))
                            ix_name_ += f"_{ix}"
                        ix_name_ = f"ix_{collection_}{ix_name_}"
                        Mongo().db[collection_].create_index(ixs, unique=False, name=ix_name_)

                if "unique" in structure_ and len(structure_["unique"]) > 0:
                    for uniques in structure_["unique"]:
                        uqs = []
                        uq_name_ = ""
                        for uq in uniques:
                            uqs.append((uq, pymongo.ASCENDING))
                            uq_name_ += f"_{uq}"
                        uq_name_ = f"uq_{collection_}{uq_name_}"
                        Mongo().db[collection_].create_index(uqs, unique=True, name=uq_name_)

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def nocrudscheme_validate_f(self, obj):
        try:
            collection_ = obj["collection"]

            structure_ = self.root_schemes_f(f"{collection_}")

            schemevalidate_ = self.crudscheme_validate_f({
                "collection": collection_,
                "structure": structure_})
            if not schemevalidate_["result"]:
                raise APIError(schemevalidate_["msg"])

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def reconfigure_f(self, obj):
        try:
            user_ = obj["userindb"] if "userindb" in obj else None
            cid_ = obj["collection"]

            permitted_ = Misc().permitted_user_f(user_)
            if not permitted_:
                raise APIError("not authorized")

            # read collection existing structure
            doc_ = Mongo().db["_collection"].find_one({"col_id": cid_})
            if not doc_:
                raise APIError("collection not found")

            structure_ = {
                "properties": {},
                "required": [],
                "index": [],
                "unique": [],
                "parents": [],
                "actions": [],
                "sort": {}
            }

            cursor_ = Mongo().db["_field"].find(filter={
                "fie_collection_id": cid_
            }, sort=[("fie_priority", 1)])

            required_ = []
            unique_ = []
            indexed_ = []
            parents_ = []
            actions_ = []
            sort_ = {}

            for index, doc_ in enumerate(cursor_, start=1):
                field_ = {}
                field_id_ = doc_["fie_id"]
                field_["bsonType"] = doc_["fie_type"] if "fie_type" in doc_ else "string"
                field_["title"] = doc_["fie_title"] if "fie_title" in doc_ else "Title"
                field_["description"] = doc_["fie_description"] if "fie_description" in doc_ else doc_["fie_title"]
                field_["width"] = doc_["fie_width"] if "fie_width" in doc_ else 110
                if "fie_barcoded" in doc_ and doc_["fie_barcoded"] == True:
                    field_["barcoded"] = True

                if field_["bsonType"] in ["number", "int", "decimal"]:
                    if "fie_minimum" in doc_ and doc_["fie_minimum"] is not None and doc_["fie_minimum"] > 0:
                        field_["minimum"] = int(doc_["fie_minimum"])
                    if "fie_maximum" in doc_ and doc_["fie_minimum"] is not None and doc_["fie_maximum"] > 0:
                        field_["maximum"] = int(doc_["fie_maximum"])

                if field_["bsonType"] == "string":
                    if "fie_min_length" in doc_ and doc_["fie_min_length"] is not None and doc_["fie_min_length"] > 0:
                        field_["minLength"] = int(doc_["fie_min_length"])
                    if "fie_max_length" in doc_ and doc_["fie_max_length"] is not None and doc_["fie_max_length"] > 0:
                        field_["maxLength"] = int(doc_["fie_max_length"])
                    if "fie_options" in doc_ and doc_["fie_options"] and len(doc_["fie_options"]) > 0:
                        field_["enum"] = doc_["fie_options"]

                if field_["bsonType"] == "array":
                    if "fie_array_unique_items" in doc_ and doc_["fie_array_unique_items"]:
                        field_["uniqueItems"] = True
                    if "fie_array_min_items" in doc_ and doc_["fie_array_min_items"] is not None and doc_["fie_array_min_items"] > 0:
                        field_["minItems"] = int(doc_["fie_array_min_items"])
                    if "fie_array_max_items" in doc_ and doc_["fie_array_max_items"] is not None and doc_["fie_array_max_items"] > 0:
                        field_["maxItems"] = int(doc_["fie_array_max_items"])
                    if "fie_array_manual_add" in doc_ and doc_["fie_array_manual_add"] == True:
                        field_["manualAdd"] = True

                    field_["items"] = {}
                    if "fie_array_items_type" in doc_ and doc_["fie_array_items_type"]:
                        field_["items"]["bsonType"] = doc_["fie_array_items_type"]
                    else:
                        field_["items"]["bsonType"] = "string"

                if "fie_default" in doc_ and doc_["fie_default"]:
                    field_["default"] = float(doc_["fie_default"]) if field_["bsonType"] in ["number", "decimal"] else int(doc_["fie_default"]) if field_["bsonType"] == "int" else str(doc_["fie_default"])

                if "fie_required" in doc_ and doc_["fie_required"]:
                    field_["required"] = True
                    required_.append(field_id_)

                if "fie_unique" in doc_ and doc_["fie_unique"]:
                    uq_ = []
                    uq_.append(field_id_)
                    if "fie_unique_add" in doc_ and doc_["fie_unique_add"] and len(doc_["fie_unique_add"]) > 0:
                        for uadd_ in doc_["fie_unique_add"]:
                            uq_.append(uadd_)
                    uq_ = Misc().make_array_unique_f(uq_)
                    unique_.append(uq_)

                if "fie_indexed" in doc_ and doc_["fie_indexed"]:
                    ix_ = []
                    ix_.append(field_id_)
                    if "fie_indexed_add" in doc_ and doc_["fie_indexed_add"] and len(doc_["fie_indexed_add"]) > 0:
                        for ixadd_ in doc_["fie_indexed_add"]:
                            ix_.append(ixadd_)
                    ix_ = Misc().make_array_unique_f(ix_)
                    indexed_.append(ix_)

                if "fie_permanent" in doc_ and doc_["fie_permanent"]:
                    field_["permanent"] = True

                if "fie_has_parent" in doc_ and doc_["fie_has_parent"]:
                    if "fie_parent_collection_id" in doc_ and doc_["fie_parent_collection_id"]:
                        if "fie_parent_field_id" in doc_ and doc_["fie_parent_field_id"]:
                            parents_.append({
                                "collection": doc_["fie_parent_collection_id"],
                                "lookup": [{
                                    "local": field_id_,
                                    "remote": doc_["fie_parent_field_id"]
                                }]
                            })

                if "fie_sort" in doc_ and doc_["fie_sort"]:
                    if doc_["fie_sort"] == "ascending":
                        sort_[field_id_] = 1
                    elif doc_["fie_sort"] == "descending":
                        sort_[field_id_] = -1

                structure_["properties"][field_id_] = field_

            if sort_ == {}:
                sort_["_modified_at"] = -1

            # set actions
            cursor_ = Mongo().db["_action"].find(filter={
                "act_collection_id": cid_,
                "act_enabled": True
            }, sort=[("act_title", 1)])

            if cursor_:
                for index_, doc_ in enumerate(cursor_, start=1):
                    actions_.append({
                        "id": doc_["act_id"],
                        "title": doc_["act_title"],
                        "enabled": doc_["act_enabled"],
                        "filter": doc_["act_filter"],
                        "set": doc_["act_set"],
                        "one_click": True if doc_["act_one_click"] and doc_["act_one_click"] == True else False
                    })

            structure_["required"] = Misc().make_array_unique_f(required_)
            structure_["unique"] = unique_
            structure_["index"] = indexed_
            structure_["sort"] = sort_
            structure_["parents"] = parents_
            structure_["actions"] = actions_

            # updates collection structure
            Mongo().db["_collection"].update_one({"col_id": cid_}, {"$set": {
                "col_structure": structure_,
                "_modified_at": datetime.now(),
                "_modified_by": user_["email"] if user_ and "email" in user_ else None
            }, "$inc": {"_modified_count": 1}})

            reconfig_set_f_ = self.config_field_to_structure_f({
                "op": "set",
                "collection": cid_,
                "user": user_
            })

            if not reconfig_set_f_["result"]:
                raise APIError(reconfig_set_f_["msg"])

            res_ = {"result": True, "structure": structure_}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": cid_,
                "op": "reconfigure",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def setprop_f(self, obj):
        try:
            user_ = obj["user"] if "user" in obj else None
            cid_ = obj["collection"]
            properties_ = obj["properties"]
            key_ = obj["key"]

            collection_f_ = self.inner_collection_f(cid_)
            if not collection_f_["result"]:
                raise APIError("collection not found")

            is_crud_ = True if cid_[:1] != "_" else False
            if not is_crud_:
                raise APIError("collection is not allowed to update")

            doc_ = Mongo().db["_collection"].find_one({"col_id": cid_})
            if not doc_:
                raise APIError("no collection found")

            for item_ in properties_[key_]:
                if item_ not in self.props_ + self.xtra_props_:
                    raise APIError(f"invalid property: {key_}")

            # set required items unique
            if "required" in properties_[key_] and properties_[key_]["required"]:
                if "required" in doc_["col_structure"] and len(doc_["col_structure"]["required"]) > 0:
                    doc_["col_structure"]["required"].append(key_)
                    doc_["col_structure"]["required"] = Misc().make_array_unique_f(doc_["col_structure"]["required"])
                else:
                    doc_["col_structure"]["required"] = [key_]
            else:
                if "required" in doc_["col_structure"] and key_ in doc_["col_structure"]["required"]:
                    doc_["col_structure"]["required"].remove(key_)
                    if (len(doc_["col_structure"]["required"]) == 0):
                        doc_["col_structure"].pop("required", None)

            # check impossibles
            if doc_["col_structure"]["properties"][key_]["bsonType"] == "string" and properties_[key_]["bsonType"] != "string":
                raise APIError("string is not convertible")

            if doc_["col_structure"]["properties"][key_]["bsonType"] in ["number", "decimal"] and properties_[key_]["bsonType"] not in ["number", "decimal", "string"]:
                raise APIError("number is not convertible")

            # set string items
            if properties_[key_]["bsonType"] == "string":
                properties_[key_].pop("minimum", None)
                properties_[key_].pop("maximum", None)
                if "minLength" in properties_[key_] and properties_[key_]["minLength"] in [None, 0, ""]:
                    properties_[key_].pop("minLength", None)
                if "maxLength" in properties_[key_] and properties_[key_]["maxLength"] in [None, 0, ""]:
                    properties_[key_].pop("maxLength", None)

            # set numeric items
            if properties_[key_]["bsonType"] in ["number", "decimal"]:
                properties_[key_].pop("minLength", None)
                properties_[key_].pop("maxLength", None)
                if "minimum" in properties_[key_] and properties_[key_]["minimum"] in [None, 0, ""]:
                    properties_[key_].pop("minimum", None)
                if "maximum" in properties_[key_] and properties_[key_]["maximum"] in [None, 0, ""]:
                    properties_[key_].pop("maximum", None)
                if "minimum" in properties_[key_] and properties_[key_]["minimum"] > 0 and "maximum" in properties_[key_] and properties_[key_]["maximum"] > 0 and properties_[key_]["minimum"] > properties_[key_]["maximum"]:
                    raise APIError("minimum value is greater than maximum value")

            # set bool and date items
            if properties_[key_]["bsonType"] in ["bool", "date"]:
                properties_[key_].pop("minimum", None)
                properties_[key_].pop("maximum", None)
                properties_[key_].pop("minLength", None)
                properties_[key_].pop("maxLength", None)

            # set width if not exists
            if "width" not in properties_[key_]:
                properties_[key_]["width"] = 100

            doc_["col_structure"]["properties"][key_] = properties_[key_]
            doc_["_modified_at"] = datetime.now()
            doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None

            Mongo().db["_collection"].update_one({"col_id": cid_}, {"$set": doc_}, upsert=False)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": cid_,
                "op": "setprop",
                "user": user_["email"] if user_ else None,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            datac_ = f"{cid_}_data"
            datac_not_found_ = False
            if datac_ not in Mongo().db.list_collection_names():
                datac_not_found_ = True
                Mongo().db[datac_].insert_one({})
            schemevalidate_ = self.crudscheme_validate_f({
                "collection": datac_,
                "structure": doc_["col_structure"]
            })
            if not schemevalidate_["result"]:
                raise APIError(schemevalidate_["msg"])
            if datac_not_found_:
                Mongo().db[datac_].delete_one({})

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": cid_,
                "op": "setprop",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def config_field_to_structure_f(self, obj):
        try:
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            op_ = obj["op"]
            email_ = user_["email"] if user_ and "email" in user_ else user_["usr_id"] if user_ and "usr_id" in user_ else None

            doc_ = {}
            if op_ == "request":
                doc_["_reconfig_req"] = True
                doc_["_reconfig_req_at"] = datetime.now()
                doc_["_reconfig_req_by"] = email_
            else:
                doc_["_reconfig_req"] = False
                doc_["_reconfig_set_at"] = datetime.now()
                doc_["_reconfig_set_by"] = email_

            Mongo().db["_collection"].update_one({
                "col_id": collection_id_
            }, {"$set": doc_, "$inc": {"_modified_count": 1}})
            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "reconfig",
                "user": email_,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def savescheme_f(self, obj):
        try:
            user_ = obj["user"] if "user" in obj else None
            op_ = obj["op"]
            collection_id_ = obj["collection"]
            email_ = user_["email"] if user_ and "email" in user_ else user_["usr_id"] if user_ and "usr_id" in user_ else None
            structure_ = obj["structure"]

            Mongo().db["_collection"].update_one({
                "col_id": collection_id_
            }, {"$set": {
                "col_structure": structure_
            }, "$inc": {"_modified_count": 1}})

            f_ = self.crudscheme_validate_f({
                "collection": f"{collection_id_}_data",
                "structure": structure_})

            if not f_["result"]:
                raise APIError(f_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": op_,
                "user": email_,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def config_structure_to_field_f(self, obj):
        try:
            collection_ = obj["collection"]
            doc_ = Mongo().db["_collection"].find_one({"col_id": collection_})
            if not doc_:
                raise APIError("no collection found")
            user_ = obj["user"] if "user" in obj else None
            structure_ = obj["structure"] if "structure" in obj else None
            properties_ = structure_["properties"] if "properties" in structure_ else None
            actions_ = structure_["actions"] if "actions" in structure_ and len(structure_["actions"]) > 0 else None
            sort_ = structure_["sort"] if "sort" in structure_ else None
            index_ = structure_["index"] if "index" in structure_ else None
            unique_ = structure_["unique"] if "unique" in structure_ else None
            parents_ = structure_["parents"] if "parents" in structure_ else None
            if properties_:
                priority_ = 0
                for prop_ in properties_:
                    property_ = properties_[prop_]
                    priority_ += 100
                    fie_indexed_ = False
                    fie_indexed_add_ = None
                    fie_unique_ = False
                    fie_unique_add_ = None
                    fie_has_parent_ = False
                    fie_parent_collection_id_ = None
                    fie_parent_field_id_ = None
                    if unique_ and len(unique_) > 0:
                        for uq_ in unique_:
                            if uq_[0] == prop_:
                                fie_unique_ = True
                                if len(uq_) > 1:
                                    fie_unique_add_ = uq_[1:]
                    if index_ and len(index_) > 0:
                        for ix_ in index_:
                            if ix_[0] == prop_:
                                fie_indexed_ = True
                                if len(ix_) > 1:
                                    fie_indexed_add_ = ix_[1:]
                    if parents_ and len(parents_) > 0:
                        for parent_ in parents_:
                            if "lookup" in parent_ and len(parent_["lookup"]) > 0 and parent_["lookup"][0]["local"] == prop_:
                                fie_has_parent_ = True
                                fie_parent_collection_id_ = parent_["collection"]
                                fie_parent_field_id_ = parent_["lookup"][0]["remote"] if "lookup" in parent_ and len(parent_["lookup"]) > 0 and parent_["lookup"][0]["remote"] else None

                    doc_ = {
                        "fie_collection_id": collection_,
                        "fie_id": prop_,
                        "fie_type": property_["bsonType"] if "bsonType" in property_ else None,
                        "fie_title": property_["title"] if "title" in property_ else None,
                        "fie_priority": priority_,
                        "fie_description": property_["description"] if "description" in property_ else None,
                        "fie_default": str(property_["default"]) if "default" in property_ else None,
                        "fie_enabled": property_["enabled"] if "enabled" in property_ else False,
                        "fie_required": property_["required"] if "required" in property_ else False,
                        "fie_permanent": property_["permanent"] if "permanent" in property_ else False,
                        "fie_indexed": fie_indexed_,
                        "fie_indexed_add": fie_indexed_add_,
                        "fie_unique": fie_unique_,
                        "fie_unique_add": fie_unique_add_,
                        "fie_min_length": property_["minLength"] if "minLength" in property_ else None,
                        "fie_max_length": property_["maxLength"] if "maxLength" in property_ else None,
                        "fie_minimum": property_["minimum"] if "minimum" in property_ else None,
                        "fie_maximum": property_["maximum"] if "maximum" in property_ else None,
                        "fie_array_unique_items": property_["uniqueItems"] if property_["bsonType"] == "array" and "uniqueItems" in property_ and property_["uniqueItems"] == True else False,
                        "fie_array_manual_add": property_["manualAdd"] if property_["bsonType"] == "array" and "manualAdd" in property_ and property_["manualAdd"] == True else False,
                        "fie_array_min_items": property_["minItems"] if property_["bsonType"] == "array" and "minItems" in property_ else None,
                        "fie_array_max_items": property_["maxItems"] if property_["bsonType"] == "array" and "maxItems" in property_ else None,
                        "fie_has_parent": fie_has_parent_,
                        "fie_parent_collection_id": fie_parent_collection_id_ if fie_has_parent_ and fie_parent_collection_id_ else None,
                        "fie_parent_field_id": fie_parent_field_id_ if fie_has_parent_ and fie_parent_collection_id_ and fie_parent_field_id_ else None,
                        "fie_options": property_["enum"] if "enum" in property_ else None,
                        "fie_width": property_["width"] if "width" in property_ else 100,
                        "fie_sort": "ascending" if sort_ and prop_ in sort_ and sort_[prop_] > 0 else "descending" if sort_ and prop_ in sort_ and sort_[prop_] < 0 else "unsorted",
                        "_modified_at": datetime.now(),
                        "_modified_by": user_["email"] if user_ and "email" in user_ else None
                    }
                    Mongo().db["_field"].update_one({
                        "fie_collection_id": collection_,
                        "fie_id": prop_
                    }, {"$set": doc_, "$inc": {"_modified_count": 1}}, upsert=True)

            if actions_:
                for action_ in actions_:
                    act_id_ = action_["id"] if "id" in action_ else None
                    act_collection_id_ = collection_
                    act_title_ = action_["title"] if "title" in action_ else None
                    act_enabled_ = True if "enabled" in action_ and action_["enabled"] == True else False
                    act_one_click_ = True if "one_click" in action_ and action_["one_click"] == True else False
                    act_filter_ = action_["filter"] if "filter" in action_ else None
                    act_set_ = action_["set"] if "set" in action_ else None
                    if act_id_ and act_collection_id_ and act_title_ and len(act_filter_) >= 0 and act_set_ and len(act_set_) > 0:
                        doc_ = {
                            "act_id": act_id_,
                            "act_collection_id": act_collection_id_,
                            "act_title": act_title_,
                            "act_enabled": act_enabled_,
                            "act_one_click": act_one_click_,
                            "act_filter": act_filter_,
                            "act_set": act_set_,
                            "_modified_at": datetime.now(),
                            "_modified_by": user_["email"] if user_ and "email" in user_ else None
                        }
                        Mongo().db["_action"].update_one({
                            "act_collection_id": act_collection_id_,
                            "act_id": act_id_
                        }, {"$set": doc_, "$inc": {"_modified_count": 1}}, upsert=True)
                        Misc().log_f({
                            "type": "Info",
                            "collection": "_action",
                            "op": "upsert",
                            "user": user_["email"] if user_ else None,
                            "document": doc_
                        })

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_,
                "op": "reverseinit",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def upsert_f(self, obj):
        try:
            doc = obj["doc"]
            _id = ObjectId(doc["_id"]) if "_id" in doc else None
            match_ = {"_id": _id} if _id else obj["match"] if "match" in obj and obj["match"] is not None and len(obj["match"]) > 0 else obj["filter"] if "filter" in obj else None
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            col_check_ = self.inner_collection_f(collection_id_)

            # protect _log collection from clonning and deleting
            if collection_id_ in ["_log", "_backup", "_announcement"]:
                raise APIError("this collection is protected")

            if not col_check_["result"]:
                raise APIError("collection not found")

            is_crud_ = True if collection_id_[:1] != "_" else False

            if not is_crud_:
                schemevalidate_ = self.nocrudscheme_validate_f({
                    "collection": collection_id_
                })
                if not schemevalidate_["result"]:
                    raise APIError(schemevalidate_["msg"])

            doc_ = {}
            for item in doc:
                if item[:1] != "_" or item in Misc().get_except_underdashes():
                    doc_[item] = doc[item] if doc[item] != "" else None

            doc_["_modified_at"] = datetime.now()
            doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None

            # add field prefix from the related collection
            if collection_id_ == "_field":
                field_col_ = Mongo().db["_collection"].find_one({"col_id": doc_["fie_collection_id"]})
                if not field_col_:
                    raise APIError(f"collection not found to upsert: {doc_['fie_collection_id']}")
                if doc_["fie_id"][:3] != field_col_["col_prefix"]:
                    doc_["fie_id"] = f"{field_col_['col_prefix']}_{doc_['fie_id']}"

            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            Mongo().db[collection_].update_one(match_, {"$set": doc_, "$inc": {"_modified_count": 1}}, upsert=False)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_id_,
                "op": "update",
                "user": user_["email"] if user_ else None,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "update",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def remove_f(self, obj):
        try:
            doc_ = obj["doc"]
            _id = ObjectId(doc_["_id"]) if "_id" in doc_ else None
            match_ = {"_id": _id} if _id else obj["match"]
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]

            # protect _log collection from delete requests
            if collection_id_ in ["_log", "_backup", "_announcement"]:
                raise APIError("this collection is protected to delete")

            is_crud_ = True if collection_id_[:1] != "_" else False
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            doc_["_removed_at"] = datetime.now()
            doc_["_removed_by"] = user_["email"] if user_ and "email" in user_ else None

            Mongo().db[collection_].delete_one(match_)

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
                c_ = doc_["col_id"]
                Mongo().db[f"{c_}_data"].aggregate([{"$match": {}}, {"$out": f"{c_}_data_removed"}])
                Mongo().db[f"{c_}_data"].drop()
                Mongo().db["_field"].delete_many({"fie_collection_id": c_})
                Mongo().db["_automation"].update_many({"$or": [{"aut_source_collection_id": c_}, {"aut_target_collection_id": c_}]}, {"$set": {"aut_enabled": False}})

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "remove",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def multiple_f(self, obj):
        try:
            collection_id_ = obj["collection"]
            user_ = obj["user"] if "user" in obj else None
            match_ = obj["match"] if "match" in obj else None

            # checks if the operator is either clone or delete
            op_ = obj["op"]
            if op_ != "clone" and op_ != "delete":
                raise APIError("operation not supported")

            # protect _log collection from clonning and deleting
            if collection_id_ in ["_log", "_backup", "_announcement"]:
                raise APIError("this collection is protected is protected for bulk processes")

            # protect _user collection from deleting requests
            if op_ == "delete":
                if collection_id_ == "_user":
                    raise APIError("user is protected to delete. please consider disabling user instead.")

            # collect object ids of the records to be processed
            ids_ = []
            for _id in match_:
                ids_.append(ObjectId(_id))

            is_crud_ = True if collection_id_[:1] != "_" else False
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            # retrieves the collection structure
            # root collection's structures can be found at github
            structure__ = Mongo().db["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemes_f(f"{collection_id_}")
            if structure__:
                structure_ = structure__["col_structure"] if is_crud_ else structure__
            else:
                raise APIError(f"collection structure not found: {collection_id_}")
            if not structure_:
                raise APIError("structure not found")

            # checks the unique key of the collection to generate a new key for the clone operation
            if "unique" in structure_ and "properties" in structure_:
                properties = structure_["properties"]
                unique = structure_["unique"]
            else:
                if op_ == "clone":
                    raise APIError("unique in structure not found")

            # creates a cursor from the object ids proceed to be cloned or deleted
            cursor = Mongo().db[collection_].find({"_id": {"$in": ids_}})
            for index, doc in enumerate(cursor, start=1):
                if op_ == "clone":
                    doc["_created_at"] = doc["_modified_at"] = datetime.now()
                    doc["_created_by"] = doc["_modified_by"] = user_["email"] if user_ and "email" in user_ else None
                    doc["_modified_count"] = 0
                    doc.pop("_id", None)
                    if unique:
                        for uq in unique:
                            if uq[0] in doc:
                                if "objectId" in properties[uq[0]] and properties[uq[0]]["objectId"] == True:
                                    doc[uq[0]] = str(bson.objectid.ObjectId())
                                elif properties[uq[0]]["bsonType"] == "string":
                                    # concat a suffix index no to field
                                    # doc[uq[0]] = f"{doc[uq[0]]}{index}"
                                    doc[uq[0]] = f"{doc[uq[0]]}_x" if "_" in doc[uq[0]] else f"{doc[uq[0]]}-{index}"
                    Mongo().db[collection_].insert_one(doc)

                elif op_ == "delete":
                    Mongo().db[collection_].delete_one({"_id": doc["_id"]})
                    doc["_deleted_at"] = datetime.now()
                    doc["_deleted_by"] = user_["email"] if user_ and "email" in user_ else None
                    bin = f"{collection_id_}_bin"
                    Mongo().db[bin].insert_one(doc)

                log_ = Misc().log_f({
                    "type": "Info",
                    "collection": collection_,
                    "op": f"multiple {op_}",
                    "user": user_["email"] if user_ else None,
                    "document": doc
                })
                if not log_["result"]:
                    raise APIError(log_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": f"multiple {op_}",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def action_f(self, obj):
        try:
            collection_id_ = obj["collection"]
            user_ = obj["user"] if "user" in obj else None
            userindb_ = obj["userindb"] if "userindb" in obj else None
            match_ = obj["match"] if "match" in obj else None
            filter_ = obj["filter"] if "filter" in obj else None
            doc_ = obj["doc"] if "doc" in obj else None
            view_ = obj["view"] if "view" in obj else None

            ids_ = []
            if match_:
                for _id in match_:
                    ids_.append(ObjectId(_id))

            if not filter_ and len(ids_) == 0:
                raise APIError("please select a row before performing an action")

            is_crud_ = True if collection_id_[:1] != "_" else False
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_

            structure__ = Mongo().db["_collection"].find_one({"col_id": collection_id_}) if is_crud_ else self.root_schemes_f(f"{collection_id_}")
            if structure__:
                structure_ = structure__["col_structure"] if is_crud_ else structure__
            else:
                raise APIError(f"collection structure not found: {collection_id_}")
            if not structure_:
                raise APIError("structure not found")

            if not match_:
                if filter_ and len(filter_) > 0:
                    match_ = filter_
                else:
                    match_ = []

            if view_ is not None:
                cursor_ = Mongo().db["_view"].find_one({
                    "vie_id": view_["vie_id"],
                    "_tags": {"$elemMatch": {"$in": userindb_["_tags"]}}
                })
                if not cursor_:
                    raise APIError(f"view not found {view_['vie_id']}")
                match_ = cursor_["vie_filter"] + match_

            doc_["_modified_at"] = datetime.now()
            doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None

            if ids_ and len(ids_) > 0:
                Mongo().db[collection_].update_many({"_id": {"$in": ids_}}, {"$set": doc_, "$inc": {"_modified_count": 1}}, upsert=False)
            else:
                get_filtered_ = self.get_filtered_f({
                    "match": match_,
                    "properties": structure_["properties"] if "properties" in structure_ else None
                })
                Mongo().db[collection_].update_many(get_filtered_, {"$set": doc_, "$inc": {"_modified_count": 1}}, upsert=False)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_,
                "op": "action",
                "user": user_["email"] if user_ else None,
                "document": {
                    "doc": doc_,
                    "match": match_
                }
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "action",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def insert_f(self, obj):
        try:
            # gets the required parameters
            user_ = obj["user"] if "user" in obj else None
            collection_id_ = obj["collection"]
            doc_ = obj["doc"]

            # remove unnecesssary items from the document
            doc_.pop("_id", None) if "_id" in doc_ else None
            doc_.pop("_structure", None) if "_structure" in doc_ else None

            is_crud_ = True if collection_id_[:1] != "_" else False
            collection_ = f"{collection_id_}_data" if is_crud_ else collection_id_
            doc_["_created_at"] = doc_["_modified_at"] = datetime.now()
            doc_["_created_by"] = doc_["_modified_by"] = user_["email"] if user_ and "email" in user_ else None

            if collection_id_ == "_collection":
                file_ = "template-foo.json"
                prefix_ = doc_["col_prefix"] if "col_prefix" in doc_ else "foo"
                path_ = f"/app/_templates/{file_}"
                if os.path.isfile(path_):
                    f_ = open(path_, "r")
                    jtxt_ = f_.read()
                    jtxt_ = jtxt_.replace("foo_", f"{prefix_}_")
                    structure_ = json.loads(jtxt_)
                doc_["col_structure"] = structure_

            Mongo().db[collection_].insert_one(doc_)

            if collection_id_ == "_collection":
                col_id_ = doc_["col_id"] if "col_id" in doc_ else None
                col_structure_ = doc_["col_structure"] if "col_structure" in doc_ else None
                datac_ = f"{col_id_}_data"
                if col_structure_ and col_structure_ != {} and datac_ not in Mongo().db.list_collection_names():
                    Mongo().db[datac_].insert_one({})
                    schemevalidate_ = self.crudscheme_validate_f({
                        "collection": datac_,
                        "structure": col_structure_})
                    if not schemevalidate_["result"]:
                        raise APIError(schemevalidate_["msg"])
                    Mongo().db[datac_].delete_one({})
            elif collection_id_ in ["_field", "_action"]:
                cid_ = doc_["fie_collection_id"] if collection_id_ == "_field" and "fie_collection_id" in doc_ else doc_["act_collection_id"] if collection_id_ == "_action" and "act_collection_id" in doc_ else None
                if cid_:
                    config_structure_f_ = self.config_field_to_structure_f({
                        "op": "request",
                        "collection": cid_,
                        "user": user_
                    })
                    if not config_structure_f_["result"]:
                        raise APIError(config_structure_f_["msg"])

            log_ = Misc().log_f({
                "type": "Info",
                "collection": collection_id_,
                "op": "insert",
                "user": user_["email"] if user_ else None,
                "document": doc_
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": collection_id_,
                "op": "insert",
                "user": user_["email"] if user_ else None,
                "document": exc.details
            })
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_


class Email():
    def __init__(self):
        self.disclaimer_ = f"<p>Sincerely,</p><p>{COMPANY_NAME_}</p><p>PLEASE DO NOT REPLY THIS EMAIL<br />--------------------------------<br />This email and its attachments transmitted with it may contain private, confidential or prohibited information. If you are not the intended recipient of this mail, you are hereby notified that storing, copying, using or forwarding of any part of the contents is strictly prohibited. Please completely delete it from your system and notify the sender. {COMPANY_NAME_} makes no warranty with regard to the accuracy or integrity of this mail and its transmission.</p>"
        self.disclaimer_text_ = f"\n\nSincerely,\n\n{COMPANY_NAME_}\n\nPLEASE DO NOT REPLY THIS EMAIL\n--------------------------------\nThis email and its attachments transmitted with it may contain private, confidential or prohibited information. If you are not the intended recipient of this mail, you are hereby notified that storing, copying, using or forwarding of any part of the contents is strictly prohibited. Please completely delete it from your system and notify the sender. {COMPANY_NAME_} makes no warranty with regard to the accuracy or integrity of this mail and its transmission."

    def sendEmail_SMTP_f(self, msg):
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
                email_to_ = f"{recipient_['name']} <{recipient_['email']}>" if recipient_["name"] and "name" in recipient_ else recipient_['email']
                recipients_str_ += email_to_ if recipients_str_ == "" else f", {email_to_}"
                recipients_.append(recipient_["email"])

            message_['To'] = recipients_str_
            server_.sendmail(email_from_, recipients_, message_.as_string())
            server_.close()
            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def sendEmail_f(self, msg):
        try:
            op_ = msg["op"] if "op" in msg else None
            files_ = msg["files"] if "files" in msg and len(msg["files"]) > 0 else []
            html_ = f"{msg['html']}" if "html" in msg else None
            personalizations_ = msg["personalizations"] if "personalizations" in msg else None
            subject_ = EMAIL_UPLOADERR_SUBJECT_ if op_ in [
                "uploaderr", "importerr"] else EMAIL_SIGNIN_SUBJECT_ if op_ == "signin" else EMAIL_TFA_SUBJECT_ if op_ == "tfa" else EMAIL_SIGNUP_SUBJECT_ if op_ == "signup" else msg["subject"] if msg["subject"] else EMAIL_DEFAULT_SUBJECT_

            if op_ is None or op_ == "":
                raise APIError("email operation is missing")

            if html_ is None or html_ == "":
                raise APIError("email message is missing")

            if personalizations_ is None:
                raise APIError("email personalizations is missing")

            if "to" not in personalizations_ or len(personalizations_["to"]) == 0:
                raise APIError("email to is missing")

            if subject_ is None:
                raise APIError("email subject is missing")

            subject_ = EMAIL_UPLOADERR_SUBJECT_ if op_ in [
                "uploaderr", "importerr"] else EMAIL_SIGNIN_SUBJECT_ if op_ == "signin" else EMAIL_TFA_SUBJECT_ if op_ == "tfa" else EMAIL_SIGNUP_SUBJECT_ if op_ == "signup" else msg["subject"] if msg["subject"] else EMAIL_DEFAULT_SUBJECT_

            msg_ = {
                "op": op_,
                "files": files_,
                "personalizations": personalizations_,
                "subject": subject_,
                "html": html_
            }

            email_sent_ = self.sendEmail_SMTP_f(msg_)

            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_


class Security():
    def __init__(self):
        self.HEADERS = request.headers
        self.URL = request.url
        self.QSTRING = request.query_string.decode()
        self.XAPIKEY = self.HEADERS["X-Api-Key"] if "X-Api-Key" in self.HEADERS else None
        self.ORIGIN = self.HEADERS["Origin"].replace("https://", "").replace("http://", "").replace("/", "").split(":")[0] if "Origin" in self.HEADERS else None

    def validate_request_f(self):
        try:
            if self.ORIGIN != DOMAIN_:
                raise APIError(f"invalid request from {self.ORIGIN}")

            if API_KEY_ != self.XAPIKEY:
                raise APIError("invalid api request")

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def header_simple_f(self):
        return {"Content-Type": "application/json; charset=utf-8"}


class OTP():
    def reset_otp_f(self, email_):
        try:
            # read auth
            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            aut_otp_secret_ = pyotp.random_base32()

            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=email_, issuer_name="Technoplatz-BI")

            Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_otp_secret": aut_otp_secret_,
                "aut_otp_validated": False,
                "_modified_at": datetime.now(),
                "_modified_by": email_,
                "_otp_secret_modified_at": datetime.now(),
                "_otp_secret_modified_by": email_,
            }, "$inc": {"_modified_count": 1}})

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_auth",
                "op": "reset-otp",
                "user": email_,
                "document": {
                    "_modified_at": datetime.now(),
                    "_modified_by": email_
                }
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res_ = {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            # sends the response
            return res_

    def validate_otp_f(self, email_, request_):
        try:
            # read auth
            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            aut_otp_secret_ = auth_["aut_otp_secret"] if "aut_otp_secret" in auth_ else None
            aut_otp_validated_ = auth_["aut_otp_validated"] if "aut_otp_validated" in auth_ else False

            if not aut_otp_secret_:
                raise AuthError("OTP secret is missing")

            otp_ = request_["otp"] if "otp" in request_ else None
            if not otp_:
                raise AuthError("OTP is missing")

            totp_ = pyotp.TOTP(aut_otp_secret_)
            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=email_, issuer_name="BI")

            validated_ = False

            if totp_.verify(otp_):
                validated_ = True
                Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                    "aut_otp_validated": validated_,
                    "_otp_validated_at": datetime.now(),
                    "_otp_validated_by": email_,
                    "_otp_validated_ip": Misc().get_user_ip_f()
                }, "$inc": {"_modified_count": 1}})
            else:
                if not aut_otp_validated_:
                    Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                        "aut_otp_validated": validated_,
                        "_otp_not_validated_at": datetime.now(),
                        "_otp_not_validated_by": email_,
                        "_otp_not_validated_ip": Misc().get_user_ip_f()
                    }, "$inc": {"_modified_count": 1}})

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_auth",
                "op": "validate-otp",
                "user": email_,
                "document": {
                    "otp": otp_,
                    "success": validated_,
                    "ip": Misc().get_user_ip_f(),
                    "_modified_at": datetime.now(),
                    "_modified_by": email_
                }
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            # sets the response
            res_ = {"result": True, "success": validated_, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            # sends the response
            return res_

    def show_otp_f(self, email_):
        try:
            # read auth
            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            aut_otp_secret_ = auth_["aut_otp_secret"] if "aut_otp_secret" in auth_ else None

            if not aut_otp_secret_:
                reset_otp_f_ = self.reset_otp_f(email_)
                if not reset_otp_f_["result"]:
                    raise APIError(reset_otp_f_["msg"])
                qr_ = reset_otp_f_["qr"]
            else:
                qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=email_, issuer_name="Technoplatz-BI")

            # sets the response
            res_ = {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            # sends the response
            return res_

    def request_otp_f(self, email_):
        try:
            # checks if the user was created already
            user_ = Mongo().db["_user"].find_one({"usr_id": email_})
            if not user_ or user_ is None:
                raise APIError("user not found for otp")

            if "usr_enabled" not in user_ or not user_["usr_enabled"]:
                raise APIError("user status is disabled to get logged in")

            # gets the user id
            usr_id_ = user_["usr_id"]
            name_ = user_["usr_name"]

            # generates a random number
            tfac_ = randint(100001, 999999)
            Mongo().db["_auth"].update_one({"aut_id": usr_id_}, {"$set": {
                "aut_tfac": tfac_,
                "_tfac_modified_at": datetime.now(),
            }, "$inc": {"_modified_count": 1}})

            # sends TFAC to the user with an email
            email_sent_ = Email().sendEmail_f({
                "op": "tfa",
                "personalizations": {"to": [{"email": usr_id_, "name": name_}]},
                "html": f"<p>Hi {name_},</p><p>Here's your backup two-factor access code so that you can validate your account;</p><p><h1>{tfac_}</h1></p>"
            })
            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_


class Auth():
    def saas_f(self):
        try:
            saas_ = {
                "company": COMPANY_NAME_,
                "version": "Technoplatz BI - Enterprise Edition" if SAAS_.lower() == "ee" else "Technoplatz BI - Community Edition"
            }

            res_ = {"result": True, "user": None, "saas": saas_}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def verify_otp_f(self, email_, tfac_, op_):
        try:

            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError(f"user auth not found {email_}")

            # checks if tfac is valid format
            compile_ = re.compile("^[0-9]{6,6}$")
            if not re.search(compile_, str(tfac_)):
                raise AuthError("invalid TFAC")

            aut_otp_secret_ = auth_["aut_otp_secret"] if "aut_otp_secret" in auth_ else None
            aut_otp_validated_ = auth_["aut_otp_validated"] if "aut_otp_validated" in auth_ else False
            aut_tfac_ = auth_["aut_tfac"] if "aut_tfac" in auth_ else None

            if aut_tfac_ and str(aut_tfac_) == str(tfac_):
                pass
            else:
                if aut_otp_secret_ and aut_otp_validated_:
                    validate_otp_f_ = OTP().validate_otp_f(email_, {"otp": tfac_})
                    if not validate_otp_f_["result"]:
                        raise AuthError("Invalid OTP code")
                else:
                    raise AuthError("Invalid OTP")

            Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_tfac": None,
                "aut_tfac_ex": aut_tfac_,
                "_modified_at": datetime.now()
            }, "$inc": {"_modified_count": 1}})

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

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
                    "_modified_at": datetime.now(),
                    "_modified_by": email_
                }
            })
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def checkup_f(self):
        try:
            input = request.json
            if not "email" in input or input["email"] is None:
                raise APIError("E-mail is missing")
            if not "name" in input or input["name"] is None:
                raise APIError("Full name is missing")
            pat = re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
            if not re.search(pat, input["email"]):
                raise APIError("Invalid e-mail address")
            if not "password" in input or input["password"] is None:
                raise APIError("Invalid email or password")
            res = {"result": True}

        except APIError as exc:
            res = Misc().api_error_f(exc)

        except Exception as exc:
            res = Misc().exception_f(exc)

        finally:
            return res

    def password_hash_f(self, password_, salted_):
        try:
            pat = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*.-_?&]{8,32}$")
            if not re.search(pat, password_):
                raise APIError("Invalid password")
            salt_ = os.urandom(32) if salted_ is None else salted_
            key_ = hashlib.pbkdf2_hmac("sha512", password_.encode("utf-8"), salt_, 101010, dklen=128)
            res_ = {"result": True, "salt": salt_, "key": key_}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def signout_f(self):
        try:
            # gets the required parameters
            input_ = request.json
            email_ = input_["email"]

            # sets None to auth token and TFAC code
            Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_token": None,
                "aut_tfac": None,
                "_modified_at": datetime.now()
            }, "$inc": {"_modified_count": 1}})

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def permission_f(self, input_):
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
                res_ = {"result": True, "allowmatch": allowmatch_}
                return

            if op_ in administratives_:
                raise AuthError(f"no {op_} permission for {collection_id_}")

            if not collection_id_:
                res_ = {"result": True, "allowmatch": allowmatch_} if op_ in permissive_ else {"result": False, "allowmatch": allowmatch_}
                return

            if collection_id_[:1] == "_" and op_ == "read":
                res_ = {"result": True, "allowmatch": allowmatch_}
                return

            collection_ = Mongo().db["_collection"].find_one({"col_id": collection_id_})
            if not collection_:
                raise APIError(f"no collection found {collection_id_}/{op_}")

            permission_ = False

            for ix_, usr_tag_ in enumerate(usr_tags_):
                permission_check_ = Mongo().db["_permission"].find_one({
                    "per_tag": usr_tag_,
                    "per_collection_id": collection_id_
                })
                if permission_check_:
                    per_insert_ = True if "per_insert" in permission_check_ and permission_check_["per_insert"] == True else False
                    per_read_ = True if "per_read" in permission_check_ and permission_check_["per_read"] == True else False
                    per_update_ = True if "per_update" in permission_check_ and permission_check_["per_update"] == True else False
                    per_delete_ = True if "per_delete" in permission_check_ and permission_check_["per_delete"] == True else False
                    per_share_ = True if "per_share" in permission_check_ and permission_check_["per_share"] == True else False
                    per_scheme_ = True if "per_scheme" in permission_check_ and permission_check_["per_scheme"] == True else False

                    if \
                        (op_ == "savescheme" and per_scheme_) or \
                        (op_ == "announce" and per_share_) or \
                        (op_ == "read" and per_read_) or \
                        (op_ in ["insert", "import"] and per_insert_) or \
                        (op_ == "upsert" and per_insert_ and per_update_) or \
                        (op_ in ["update", "action"] and per_read_ and per_update_) or \
                        (op_ == "clone" and per_read_ and per_insert_) or \
                            (op_ == "delete" and per_read_ and per_delete_):
                        if ix_ == 0:
                            allowmatch_ = permission_check_["per_match"] if "per_match" in permission_check_ and len(permission_check_["per_match"]) > 0 else []
                        permission_ = True
                        break

            if permission_ == False:
                raise AuthError(f"no {op_} permission for {collection_id_}")

            res_ = {"result": permission_, "allowmatch": allowmatch_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def firewall_f(self, user_):
        try:
            ip_ = Misc().get_user_ip_f()
            tags_ = user_["_tags"] if "_tags" in user_ and len(user_["_tags"]) > 0 else []
            allowed_ = Mongo().db["_firewall"].find_one({"$or": [
                {"fwa_tag": {"$in": tags_}, "fwa_source_ip": ip_, "fwa_enabled": True},
                {"fwa_tag": {"$in": tags_}, "fwa_source_ip": "0.0.0.0", "fwa_enabled": True}
            ]})
            if not allowed_:
                raise AuthError(f"connection is not allowed from IP address {ip_}")

            res_ = {"result": True}

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            Misc().log_f({
                "type": "Error",
                "collection": "_firewall",
                "op": "block",
                "user": user_["usr_id"],
                "document": {
                    "ip": ip_,
                    "exception": str(exc),
                    "_modified_at": datetime.now(),
                    "_modified_by":  user_["usr_id"],
                }
            })
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def session_f(self, input_):
        try:
            # gets the email and user token
            user_ = input_["user"] if "user" in input_ else input_
            email_ = user_["email"] if "email" in user_ else None
            token_ = user_["token"] if "token" in user_ else None
            jdate_curr_ = Misc().get_jdate_f()

            if not email_ or not token_:
                raise APIError("invalid session parameters")

            # check user's auth information on the _auth collection
            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise APIError(f"user auth not found {email_}")

            # sets the required variables
            token_db_ = auth_["aut_token"] if "aut_token" in auth_ else None

            # looks at if the session is valid by checking the user token
            if not token_db_ or token_ != token_db_:
                raise APIError(f"session closed for {email_}")

            if "jdate" not in user_:
                user_["jdate"] = jdate_curr_

            jdate_exp_ = int(user_["jdate"]) + int(SECUR_MAX_AGE_)

            if jdate_curr_ > jdate_exp_:
                raise APIError(f"session expired")

            res_ = {"result": True, "user": user_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_token": None,
                "aut_tfac": None,
                "_modified_at": datetime.now(),
                "_modified_by": "restapi"
            }, "$inc": {"_modified_count": 1}}, upsert=False)

            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def account_f(self, input_):
        try:
            user_ = input_["user"]
            op_ = input_["op"]

            email_ = user_["email"]

            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            response_ = {}
            apikey_ = None

            if op_ == "apikeygen":
                apikey_ = secrets.token_hex(16)
                Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                    "aut_apikey": apikey_,
                    "_apikey_modified_at": datetime.now(),
                    "_apikey_modified_by": email_
                }, "$inc": {"_apikey_modified_count": 1}}, upsert=False)
                log_ = Misc().log_f({
                    "type": "Info",
                    "collection": "_auth",
                    "op": op_,
                    "user": email_,
                    "document": {
                        "aut_apikey": f"********{apikey_[-4:]}",
                        "_modified_at": datetime.now(),
                        "_modified_by": email_
                    }
                })

                if not log_["result"]:
                    raise APIError(log_["msg"])

                response_ = {"apikey": apikey_, "_modified_at": datetime.now()}

            elif op_ == "apikeyget":
                apikey_modified_at_ = auth_["_apikey_modified_at"] if "_apikey_modified_at" in auth_ else None
                apikey_ = auth_["aut_apikey"] if "aut_apikey" in auth_ else None
                response_ = {"apikey": apikey_, "apikey_modified_at": apikey_modified_at_}

            else:
                raise APIError("account operation not supported " + op_)

            res_ = {"result": True, "user": response_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def forgot_f(self):
        try:
            # gets the required variables
            input_ = request.json
            if not "email" in input_ or input_["email"] is None:
                raise APIError("e-mail is missing")

            email_ = bleach.clean(input_["email"])

            # checks if the user account was created already
            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            OTP_send_ = OTP().request_otp_f(email_)
            if not OTP_send_["result"]:
                raise APIError(OTP_send_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def reset_f(self):
        try:
            input_ = request.json

            email_ = input_["email"]
            password_ = input_["password"]
            tfac_ = input_["tfac"]

            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if not auth_:
                raise AuthError("account not found")

            verify_2fa_f_ = Auth().verify_otp_f(email_, tfac_, "reset")
            if not verify_2fa_f_["result"]:
                raise AuthError(verify_2fa_f_["msg"])

            hash_f_ = self.password_hash_f(password_, None)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])

            salt_ = hash_f_["salt"]
            key_ = hash_f_["key"]

            Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_salt": salt_,
                "aut_key": key_,
                "aut_token": None,
                "aut_tfac": None,
                "aut_expires": 0,
                "_modified_at": datetime.now(),
                "_modified_by": email_
            }, "$inc": {"_modified_count": 1}}, upsert=False)

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_auth",
                "op": "reset",
                "user": email_,
                "document": {
                    "tfac": tfac_,
                    "_modified_at": datetime.now(),
                    "_modified_by": email_
                }
            })
            if not log_["result"]:
                raise APIError(log_["msg"])

            res_ = {"result": True}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def tfac_f(self):
        try:
            input_ = request.json
            email_ = input_["email"]
            password_ = input_["password"]
            tfac_ = input_["tfac"]

            user_validate_ = self.user_validate_by_basic_auth_f({"userid": email_, "password": password_}, "tfac")
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])
            user_ = user_validate_["user"] if "user" in user_validate_ else None

            verify_2fa_f_ = Auth().verify_otp_f(email_, tfac_, "signin")
            if not verify_2fa_f_["result"]:
                raise AuthError(verify_2fa_f_["msg"])

            verification_content_ = {"tfac": str(tfac_)}

            log_ = Misc().log_f({
                "type": "Info",
                "collection": "_auth",
                "op": "signin",
                "user": email_,
                "document": {
                    "verification": verification_content_,
                    "_modified_at": datetime.now(),
                    "_modified_by": email_
                }
            })

            if not log_["result"]:
                raise APIError(log_["msg"])

            # GENERATING JWT FOR USER
            name_db_ = user_["usr_name"]
            perm_ = True if Misc().permitted_user_f(user_) else False
            apikey_ = user_["aut_apikey"]
            jdate_ = Misc().get_jdate_f()
            token_ = jwt.encode({"some": "payload"}, password_, algorithm="HS256")

            Mongo().db["_auth"].update_one({"aut_id": email_}, {"$set": {
                "aut_token": token_,
                "aut_tfac": None,
                "_modified_at": datetime.now()
            }, "$inc": {"_modified_count": 1}}, upsert=False)

            # sets the users dict
            user_ = {
                "token": token_,
                "name": name_db_,
                "email": email_,
                "perm": perm_,
                "apikey": apikey_,
                "jdate": jdate_
            }

            ip_ = Misc().get_user_ip_f()

            email_sent_ = Email().sendEmail_f({
                "op": "signin",
                "personalizations": {"to": [{"email": email_, "name": name_db_}]},
                "html": f"<p>Hi {name_db_},<br /><br />You have now signed-in from {ip_}.</p>"
            })
            if not email_sent_["result"]:
                raise APIError(email_sent_["msg"])

            res_ = {"result": True, "user": user_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except AuthError as exc:
            res_ = Misc().auth_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def user_validate_by_basic_auth_f(self, input_, op_):
        try:
            user_id_ = bleach.clean(input_["userid"]) if "userid" in input_ else None
            password_ = bleach.clean(input_["password"]) if "password" in input_ else None
            token_ = bleach.clean(input_["token"]) if "token" in input_ else None

            if not user_id_:
                raise APIError("email must be provided")

            pat = re.compile("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
            if not re.search(pat, user_id_):
                raise APIError("invalid e-mail address")

            auth_ = Mongo().db["_auth"].find_one({"aut_id": user_id_})
            if not auth_:
                type_ = "auth"
                raise AuthError("account not found")

            if "aut_salt" not in auth_ or auth_["aut_salt"] == None:
                type_ = "salt"
                raise AuthError("please set a password")

            if "aut_key" not in auth_ or auth_["aut_key"] == None:
                type_ = "key"
                raise AuthError("please set a new password")

            user_ = Mongo().db["_user"].find_one({"usr_id": user_id_})
            if not user_:
                type_ = "user"
                raise AuthError("user not found for validate")

            user_["aut_apikey"] = auth_["aut_apikey"] if "aut_apikey" in auth_ and auth_["aut_apikey"] is not None else None

            enabled_ = user_["usr_enabled"] if "usr_enabled" in user_ else False
            if not enabled_:
                type_ = "disabled"
                raise AuthError("user is disabled")

            salt_ = auth_["aut_salt"]
            key_ = auth_["aut_key"]
            token_db_ = auth_["aut_token"] if "aut_token" in auth_ else None

            if not password_:
                if not token_:
                    type_ = "token"
                    raise AuthError("no credentials provided")
                else:
                    if token_db_ != token_:
                        type_ = "token"
                        raise AuthError("session closed")
            else:
                hash_f_ = self.password_hash_f(password_, salt_)
                if not hash_f_["result"]:
                    raise APIError(hash_f_["msg"])
                new_key_ = hash_f_["key"]
                if new_key_ != key_:
                    type_ = "hash"
                    raise AuthError("invalid email or password")

            firewall_ = self.firewall_f(user_)
            if not firewall_["result"]:
                type_ = "firewall"
                raise AuthError(firewall_["msg"])

            res_ = {"result": True, "user": user_, "auth": auth_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except AuthError as exc:
            if type_ != "firewall":
                Misc().log_f({
                    "type": "Error",
                    "collection": "_auth",
                    "op": op_,
                    "user": user_id_,
                    "document": {
                        "type": type_,
                        "exception": str(exc)
                    }
                })
            res_ = Misc().auth_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def user_validate_by_apikey_f(self, input_):
        try:
            # sets the required variables
            apikey_ = bleach.clean(input_["apikey"]) if "apikey" in input_ else None

            # user id must not be empty
            if not apikey_ or apikey_ == None:
                raise APIError("api key must be provided")

            # checks if user exists in the auth
            auth_ = Mongo().db["_auth"].find_one({"aut_apikey": apikey_})
            if not auth_:
                raise APIError("account or apikey not found")

            user_id_ = auth_["aut_id"]

            # checks if user exists in the users
            user_ = Mongo().db["_user"].find_one({"usr_id": user_id_})
            if not user_:
                raise APIError("user not found for api")

            # checks if user is enabled or not
            usr_enabled_ = user_["usr_enabled"] if "usr_enabled" in user_ else False
            if not usr_enabled_:
                raise APIError("user not validated")

            # checks if firewall entry exists
            firewall_ = self.firewall_f(user_)
            if not firewall_["result"]:
                raise APIError(firewall_["msg"])

            res_ = {"result": True, "user": user_, "auth": auth_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_

    def signin_f(self):
        try:
            input_ = request.json
            email_ = input_["email"]
            password_ = input_["password"]

            user_validate_ = self.user_validate_by_basic_auth_f({"userid": email_, "password": password_}, "signin")
            if not user_validate_["result"]:
                raise AuthError(user_validate_["msg"])

            OTP_send_ = OTP().request_otp_f(email_)
            if not OTP_send_["result"]:
                raise APIError(OTP_send_["msg"])

            res = {"result": True, "msg": "user needs to be validated by OTP"}

        except APIError as exc:
            res = Misc().api_error_f(exc)

        except AuthError as exc:
            res = Misc().auth_error_f(exc)

        except Exception as exc:
            res = Misc().exception_f(exc)

        finally:
            return res

    def signup_f(self):
        try:
            checkup_ = self.checkup_f()
            if not checkup_["result"]:
                raise APIError(checkup_["msg"])

            # gets the required variables
            input_ = request.json
            email_ = bleach.clean(input_["email"])
            password_ = bleach.clean(input_["password"])
            passcode_ = bleach.clean(input_["passcode"])

            # checks if the user account was created already
            auth_ = Mongo().db["_auth"].find_one({"aut_id": email_})
            if auth_:
                raise APIError("account already exist")

            # checks if the user was created already
            user_ = Mongo().db["_user"].find_one({"usr_id": email_})
            if not user_ or user_ is None:
                raise APIError("user invitation not found")

            if passcode_ != str(user_["_id"]):
                raise APIError("invitation codes do not match")

            if "usr_enabled" not in user_ or not user_["usr_enabled"]:
                raise APIError("user status is disabled to get logged in")

            # creates an encrypter password
            hash_f_ = self.password_hash_f(password_, None)
            if not hash_f_["result"]:
                raise APIError(hash_f_["msg"])

            salt_ = hash_f_["salt"]
            key_ = hash_f_["key"]

            aut_otp_secret_ = pyotp.random_base32()
            qr_ = pyotp.totp.TOTP(aut_otp_secret_).provisioning_uri(name=email_, issuer_name="Technoplatz-BI")
            apikey_ = secrets.token_hex(16)

            Mongo().db["_auth"].insert_one({
                "aut_id": email_,
                "aut_salt": salt_,
                "aut_key": key_,
                "aut_token": None,
                "aut_apikey": apikey_,
                "aut_tfac": None,
                "aut_expires": 0,
                "aut_otp_secret": aut_otp_secret_,
                "aut_otp_validated": False,
                "_qr_modified_at": datetime.now(),
                "_qr_modified_by": email_,
                "_qr_modified_count": 0,
                "_created_at": datetime.now(),
                "_created_by": email_,
                "_created_ip": Misc().get_user_ip_f(),
                "_modified_at": datetime.now(),
                "_modified_by": email_,
            })

            res_ = {"result": True, "qr": qr_}

        except pymongo.errors.PyMongoError as exc:
            res_ = Misc().mongo_error_f(exc)

        except APIError as exc:
            res_ = Misc().api_error_f(exc)

        except Exception as exc:
            res_ = Misc().exception_f(exc)

        finally:
            return res_


# IDENTIFICATION DIVISION

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
API_KEY_ = os.environ.get("API_KEY")
SECUR_MAX_AGE_ = os.environ.get("SECUR_MAX_AGE")
SAAS_ = os.environ.get("SAAS")
PERMISSIVE_TAGS_ = ["#Managers", "#Administrators"]
MONGO_REPLICASET_ = os.environ.get("MONGO_REPLICASET")
MONGO_HOST_ = os.environ.get("MONGO_HOST")
MONGO_REPLICA1_HOST_ = os.environ.get("MONGO_REPLICA1_HOST")
MONGO_REPLICA2_HOST_ = os.environ.get("MONGO_REPLICA2_HOST")
MONGO_PORT_ = int(os.environ.get("MONGO_PORT"))
MONGO_DB_ = os.environ.get("MONGO_DB")
MONGO_AUTH_DB_ = os.environ.get("MONGO_AUTH_DB")
MONGO_INITDB_ROOT_USERNAME_ = urllib.parse.quote_plus(os.environ.get("MONGO_INITDB_ROOT_USERNAME"))
MONGO_INITDB_ROOT_PASSWORD_ = urllib.parse.quote_plus(os.environ.get("MONGO_INITDB_ROOT_PASSWORD"))
MONGO_TLS_CERT_KEY_PASSWORD_ = urllib.parse.quote_plus(os.environ.get("MONGO_TLS_CERT_KEY_PASSWORD"))
MONGO_TLS_CA_KEYFILE_ = f"/cert/{os.environ.get('MONGO_TLS_CA_KEYFILE')}"
MONGO_TLS_CERT_KEYFILE_ = f"/cert/{os.environ.get('MONGO_TLS_CERT_KEYFILE')}"

# CORS CHECKPOINT
origins_ = [
    f"http://{DOMAIN_}",
    f"https://{DOMAIN_}",
    f"http://{DOMAIN_}:8100",
    f"http://{DOMAIN_}:8101"
]

app = Flask(__name__)
app.config["CORS_ORIGINS"] = origins_
app.config["CORS_HEADERS"] = ["Content-Type", "Origin", "Authorization", "X-Requested-With", "Accept", "x-auth"]
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
app.config["MAX_CONTENT_LENGTH"] = API_MAX_CONTENT_LENGTH_
app.config["UPLOAD_EXTENSIONS"] = ["pdf", "png", "jpg", "jpeg", "xlsx", "xls", "doc", "docx", "csv", "txt"]
app.config["UPLOAD_FOLDER"] = "/vault/"
CORS(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@app.route("/import", methods=["POST"], endpoint="import")
def storage_f():
    try:
        validate_ = Security().validate_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "validation error")

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
        email_ = form_["email"] if "email" in form_ else None
        token_ = form_["token"] if "token" in form_ else None

        validate_ = Auth().user_validate_by_basic_auth_f({"userid": email_, "token": token_}, "import")
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "crud validation error")
        user_ = validate_["user"]

        import_f_ = Crud().import_f({"form": form_, "file": file_, "collection": collection__, "user": user_, "prefix": prefix_})
        if not import_f_["result"]:
            raise APIError(import_f_["msg"])

        res_ = {
            "result": import_f_["result"],
            "count": import_f_["count"] if "count" in import_f_ and import_f_["count"] >= 0 else 0,
            "msg": import_f_["msg"] if "msg" in import_f_ else None
        }

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 400}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        return json.dumps(res_, default=json_util.default, sort_keys=False), status_, Security().header_simple_f()


@app.route("/crud", methods=["POST"], endpoint="crud")
def crud_f():
    try:
        # validates restapi request
        validate_ = Security().validate_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "validation error")

        # gets and cleans user input
        input_ = request.json

        # checks and set if the operator exists in request
        if not "op" in input_:
            raise APIError("no operation found")
        op_ = input_["op"]

        user_ = input_["user"] if "user" in input_ else None
        if not user_:
            raise APIError("user info not found")

        email_ = user_["email"] if "email" in user_ else None
        token_ = user_["token"] if "token" in user_ else None
        collection_ = input_["collection"] if "collection" in input_ else None
        match_ = input_["match"] if "match" in input_ and input_["match"] is not None and len(input_["match"]) > 0 else []

        validate_ = Auth().user_validate_by_basic_auth_f({"userid": email_, "token": token_}, "op")
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "crud validation error")
        input_["userindb"] = validate_["user"]

        permission_f_ = Auth().permission_f({"user": validate_["user"], "auth": validate_["auth"], "collection": collection_, "op": op_})
        if not permission_f_["result"]:
            raise AuthError(permission_f_["msg"])

        allowmatch_ = []
        allowmatch_ = permission_f_["allowmatch"] if "allowmatch" in permission_f_ and len(permission_f_["allowmatch"]) > 0 else []
        if op_ in ["read", "update", "upsert", "delete", "action"]:
            match_ = allowmatch_ + match_
        if op_ in ["update", "upsert", "insert", "action"]:
            if not "doc" in input_:
                raise APIError("document must be included in the request")
            decode_ = Crud().decode_crud_input_f(input_)
            if not decode_["result"]:
                raise APIError(decode_["msg"] if "msg" in decode_ else "decode error")
            input_["doc"] = decode_["doc"]
        elif op_ in ["remove", "clone", "delete"]:
            c_ = input_["collection"]
            col_check_ = Crud().inner_collection_f(c_)
            if not col_check_["result"]:
                raise APIError(col_check_["msg"])

        input_["match"] = match_
        input_["allowmatch"] = allowmatch_

        # distributes the operation to the right function
        if op_ == "read":
            res_ = Crud().read_f(input_)
        elif op_ in ["update", "import", "upload"]:
            res_ = Crud().upsert_f(input_)
        elif op_ == "insert":
            res_ = Crud().insert_f(input_)
        elif op_ in ["clone", "delete"]:
            res_ = Crud().multiple_f(input_)
        elif op_ == "action":
            res_ = Crud().action_f(input_)
        elif op_ == "remove":
            res_ = Crud().remove_f(input_)
        elif op_ == "setprop":
            res_ = Crud().setprop_f(input_)
        elif op_ == "reconfigure":
            res_ = Crud().reconfigure_f(input_)
        elif op_ == "saveasview":
            res_ = Crud().saveasview_f(input_)
        elif op_ == "purge":
            res_ = Crud().purge_f(input_)
        elif op_ == "view":
            res_ = Crud().view_f(input_)
        elif op_ == "views":
            res_ = Crud().views_f(input_)
        elif op_ == "announce":
            res_ = Crud().announce_f(input_)
        elif op_ == "collections":
            res_ = Crud().collections_f(input_)
        elif op_ == "collection":
            res_ = Crud().collection_f(input_)
        elif op_ == "parent":
            res_ = Crud().parent_f(input_)
        elif op_ in ["backup", "restore"]:
            res_ = Crud().dump_f(input_)
        elif op_ == "template":
            res_ = Crud().template_f(input_)
        elif op_ == "savescheme":
            res_ = Crud().savescheme_f(input_)
        else:
            raise APIError(f"{op_} is not a supported operation")

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 400}

    except AuthError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        return json.dumps(res_, default=json_util.default, sort_keys=False), status_, Security().header_simple_f()


@app.route("/otp", methods=["POST"])
def otp_f():
    try:
        # validates restapi request
        validate_ = Security().validate_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "web validation error")

        # gets and cleans user input
        input_ = request.json

        # checks input is set
        if not input_:
            raise APIError("input missing")

        # gets the email and user token
        user_ = input_["user"] if "user" in input_ else None
        if not user_:
            raise APIError("credentials are missing")

        request_ = input_["request"] if "request" in input_ else None
        if not request_:
            raise APIError("request is nissing")

        email_ = user_["email"] if "email" in user_ else None
        token_ = user_["token"] if "token" in user_ else None

        # validates restapi request
        validate_ = Auth().user_validate_by_basic_auth_f({"userid": email_, "token": token_}, "otp")
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "otp validation error")

        # checks and set if the operator exists in request
        if not "op" in request_:
            raise APIError("no operation found")

        op_ = request_["op"]

        if op_ == "reset":
            res_ = OTP().reset_otp_f(email_)
        elif op_ == "show":
            res_ = OTP().show_otp_f(email_)
        elif op_ == "request":
            res_ = OTP().request_otp_f(email_)
        elif op_ == "validate":
            res_ = OTP().validate_otp_f(email_, request_)
        else:
            raise APIError(f"operation not supported {op_}")

        if not res_["result"]:
            raise APIError(res_["msg"])

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        return json.dumps(res_, default=json_util.default), status_, Security().header_simple_f()


@app.route("/auth", methods=["POST"], endpoint="auth")
def auth_f():
    try:
        # validates restapi request
        validate_ = Security().validate_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "web validation error")

        # gets and cleans user input
        input_ = request.json

        # checks input is set
        if not input_:
            raise APIError("input missing")

        # checks and set if the operator exists in request
        if not "op" in input_:
            raise APIError("no operation found")

        op_ = input_["op"]
        token_ = None

        if op_ == "signup":
            auth_ = Auth().signup_f()
        elif op_ == "saas":
            auth_ = Auth().saas_f()
        elif op_ == "signin":
            auth_ = Auth().signin_f()
        elif op_ == "tfac":
            auth_ = Auth().tfac_f()
        elif op_ == "signout":
            auth_ = Auth().signout_f()
        elif op_ == "forgot":
            auth_ = Auth().forgot_f()
        elif op_ == "reset":
            auth_ = Auth().reset_f()
        elif op_ in ["apikeygen", "apikeyget"]:
            auth_ = Auth().account_f(input_)
        elif op_ == "session":
            auth_ = Auth().session_f(input_)
        else:
            raise APIError(f"operation not supported {op_}")

        if not auth_["result"]:
            raise APIError(auth_["msg"])

        user_ = auth_["user"] if auth_ and "user" in auth_ else None
        saas_ = auth_["saas"] if auth_ and "saas" in auth_ else None

        if op_ == "tfac":
            token_ = user_["token"] if "token" in user_ and user_["token"] != None else None

        res_ = {"result": True, "user": user_, "saas": saas_}

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        header_ = Security().header_simple_f()
        if token_ != None:
            header_["Set-Cookie"] = f"technoplatz-bi-session={token_}; path=/; samesite=strict; httponly"
        return json.dumps(res_, default=json_util.default, sort_keys=False), status_, header_


@app.route("/get/visual/<string:id>", methods=["GET"])
def get_visual_f(id):
    try:
        web_validate_ = Security().validate_request_f()
        if not web_validate_["result"]:
            raise APIError(web_validate_["msg"] if "msg" in web_validate_ else "validation error")

        if not request.headers:
            raise AuthError("no header provided")

        apikey_ = request.args.get("k", default=None, type=str)

        if not apikey_:
            raise AuthError("no api key provided")

        user_validate_ = Auth().user_validate_by_apikey_f({"apikey": apikey_})
        if not user_validate_["result"]:
            raise AuthError(user_validate_["msg"])

        user_ = user_validate_["user"] if "user" in user_validate_ else None
        if not user_ or not user_["usr_id"] or "usr_id" not in user_:
            raise AuthError("user not found for visual")

        view_to_visual_f_ = Crud().visual_f({
            "id": id,
            "user": user_
        })

        if not view_to_visual_f_["result"]:
            raise APIError(view_to_visual_f_["msg"])

        res_ = {
            "result": True,
            "visual": view_to_visual_f_
        }

    except AuthError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 400}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        return res_, status_, Security().header_simple_f()


@app.route("/get/pivot/<string:id>", methods=["GET"])
def get_pivot_f(id):
    try:
        validate_ = Security().validate_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "validation error")

        if not request.headers:
            raise AuthError("no header provided")

        apikey_ = request.args.get("k", default=None, type=str)

        if not apikey_:
            raise AuthError("no api key provided")

        user_validate_ = Auth().user_validate_by_apikey_f({"apikey": apikey_})
        if not user_validate_["result"]:
            raise AuthError(user_validate_["msg"])

        user_ = user_validate_["user"] if "user" in user_validate_ else None
        if not user_ or not user_["usr_id"] or "usr_id" not in user_:
            raise AuthError("user not found for pivot")

        view_to_dataset_f_ = Crud().view_to_dataset_f({
            "id": id,
            "user": user_
        })

        if not view_to_dataset_f_["result"]:
            raise APIError(view_to_dataset_f_["msg"])

        pivot_ = view_to_dataset_f_["pivot"].to_html().replace('border="1"', "") if "pivot" in view_to_dataset_f_ and view_to_dataset_f_["pivot"] is not None else ""
        statistics_ = view_to_dataset_f_["statistics"] if "statistics" in view_to_dataset_f_ else None
        count_ = view_to_dataset_f_["count"] if "count" in view_to_dataset_f_ and view_to_dataset_f_["count"] > 0 else 0

        res_ = {
            "result": True,
            "pivot": pivot_,
            "statistics": statistics_,
            "count": count_
        }

    except AuthError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 400}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        return json.dumps(res_, default=json_util.default, ensure_ascii=False, sort_keys=False), status_, Security().header_simple_f()


@app.route("/post", methods=["POST"])
def post_f():
    try:
        # start transaction
        session_db_ = Mongo().client[Crud().dbname_]
        session_ = Mongo().client.start_session(causal_consistency=True, default_transaction_options=None)
        session_.start_transaction()

        if not request.headers:
            raise AuthError("no headers provided")

        if not request.json:
            raise APIError("no data provided")

        if not API_OUTPUT_ROWS_LIMIT_:
            raise APIError("no api rows limit defined")

        # checks the authorization from the request header
        rh_apikey_ = request.headers.get("x-api-key", None) if "x-api-key" in request.headers and request.headers["x-api-key"] != "" else None
        if not rh_apikey_:
            raise AuthError("no api key provided")

        # checks the token
        rh_authorization_ = request.headers.get("Authorization", None) if "Authorization" in request.headers and request.headers["Authorization"] != "" else None
        if not rh_authorization_:
            raise AuthError("no authorization provided")
        auth_parts_ = rh_authorization_.split()
        if len(auth_parts_) == 1:
            raise AuthError("no access token provided")
        elif auth_parts_[0].lower() != "bearer":
            raise AuthError("invalid authorization format")
        rh_token_ = auth_parts_[1]

        # gets operation
        operation_ = request.headers.get("operation", None) if "operation" in request.headers and request.headers["operation"] != "" else None
        if not operation_ or operation_ not in ["read", "insert", "update", "upsert", "delete"]:
            raise APIError("invalid operation")

        # validate user by apikey
        user_validate_ = Auth().user_validate_by_apikey_f({"apikey": rh_apikey_})
        if not user_validate_["result"]:
            raise AuthError(user_validate_["msg"])

        # token validate
        token_validate_f_ = Misc().token_validate_f(rh_token_, operation_)
        if not token_validate_f_["result"]:
            raise AuthError(f"token is not permitted to {operation_}")

        # check collection
        rh_collection_ = request.headers.get("collection", None) if "collection" in request.headers and request.headers["collection"] != "" else None
        if not rh_collection_:
            raise APIError("no collection found")
        collection_f_ = Crud().inner_collection_f(rh_collection_)
        if not collection_f_["result"]:
            raise AuthError(collection_f_["msg"])

        # get structure
        collection_ = collection_f_["collection"] if "collection" in collection_f_ else None
        if not collection_:
            raise APIError("collection not found")
        structure_ = collection_["col_structure"] if "col_structure" in collection_ else None
        if not collection_:
            raise APIError("structure not found")

        properties_ = structure_["properties"] if "properties" in structure_ else None
        if not properties_:
            raise APIError("properties not found")

        unique_ = structure_["unique"] if "unique" in structure_ else []

        is_crud_ = True if rh_collection_[:1] != "_" else False
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
                    raise APIError(f"at leat one unique field must be provided for {operation_}")
            for ix_, item_ in enumerate(body_):
                filter__ = {}
                if operation_ in ["update", "upsert", "delete"]:
                    for key_ in filter_.keys():
                        if key_ in item_ and item_[key_] is not None:
                            filter__[key_] = item_[key_]
                    if filter__ == {}:
                        raise APIError(f"at least one unique field must be provided for {operation_} index {ix_}")
                # decode document
                decode_crud_doc_f_ = Crud().decode_crud_doc_f(item_, properties_)
                if not decode_crud_doc_f_["result"]:
                    raise APIError(decode_crud_doc_f_["msg"])
                doc__ = decode_crud_doc_f_["doc"]
                doc__["_modified_at"] = datetime.now()
                doc__["_modified_by"] = "API"
                if operation_ == "upsert":
                    session_db_[collection_data_].update_many(filter__, {"$set": doc__, "$inc": {"_modified_count": 1}}, upsert=True, session=session_)
                if operation_ == "update":
                    session_db_[collection_data_].update_many(filter__, {"$set": doc__, "$inc": {"_modified_count": 1}}, upsert=False, session=session_)
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

        response_ = json.loads(JSONEncoder().encode({
            "collection": rh_collection_,
            "operation": operation_,
            "count": count_,
            "output": output_
        }))

        session_.commit_transaction() if session_ else None

        res_ = {"result": True, "response": response_}

    except AuthError as exc:
        session_.abort_transaction() if session_ else None
        res_ = {"result": False, "response": str(exc), "status": 401}

    except APIError as exc:
        session_.abort_transaction() if session_ else None
        res_ = {"result": False, "response": str(exc), "status": 400}

    except Exception as exc:
        session_.abort_transaction() if session_ else None
        res_ = {"result": False, "response": str(exc), "status": 500}

    finally:
        Mongo().client.close() if Mongo().client else None
        status_ = res_["status"] if "status" in res_ else 200
        return json.dumps(res_, default=json_util.default, ensure_ascii=False, sort_keys=False), status_, Security().header_simple_f()


@app.route("/get/dump", methods=["POST"])
def get_dump_f():
    try:
        validate_ = Security().validate_request_f()
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "validation error")

        input_ = request.json

        user_ = input_["user"] if "user" in input_ else None
        if not user_:
            raise APIError("invalid credentials")

        email_ = user_["email"] if "email" in user_ else None
        token_ = user_["token"] if "token" in user_ else None

        validate_ = Auth().user_validate_by_basic_auth_f({"userid": email_, "token": token_}, "backup")
        if not validate_["result"]:
            raise APIError(validate_["msg"] if "msg" in validate_ else "request not validated")

        id_ = bleach.clean(input_["id"])
        if not id_:
            raise APIError("dump not selected")

        file_ = f"{id_}.gz"
        directory_ = "/dump"

        res_ = send_from_directory(directory=directory_, path=file_, as_attachment=True)

    except AuthError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 400}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        status_ = res_["status"] if "status" in res_ else 200
        return res_, status_, Security().header_simple_f()


@app.route("/get/view/<string:id>", methods=["GET"])
def get_data_f(id):
    try:
        if not request.headers:
            raise AuthError("no header provided")

        # validates restapi request
        arg_ = request.args.get("k", default=None, type=str)

        # checks the authorization from the request header
        apikey_ = request.headers["X-Api-Key"] if "X-Api-Key" in request.headers and request.headers["X-Api-Key"] != "" else arg_
        if not apikey_:
            raise AuthError("no api key provided")

        user_validate_ = Auth().user_validate_by_apikey_f({"apikey": apikey_})
        if not user_validate_["result"]:
            if not arg_:
                raise AuthError("no argument provided")
            else:
                user_validate_ = Auth().user_validate_by_apikey_f({"apikey": arg_})
                if not user_validate_["result"]:
                    raise AuthError(user_validate_["msg"])

        id_ = bleach.clean(id)
        user_ = user_validate_["user"] if "user" in user_validate_ else None

        if not user_:
            raise AuthError("user not found for view")

        if not user_["usr_id"] or "usr_id" not in user_:
            raise AuthError("user id not found")

        email_ = user_["usr_id"]

        generate_view_data_f_ = Crud().view_f({
            "email": email_,
            "source": "external",
            "vie_id": None,
            "_id": id_
        })

        if not generate_view_data_f_["result"]:
            raise APIError(generate_view_data_f_["msg"])

        res_ = generate_view_data_f_["data"] if generate_view_data_f_ and "data" in generate_view_data_f_ else []

    except AuthError as exc:
        res_ = {"msg": str(exc), "status": 401}

    except APIError as exc:
        res_ = {"msg": str(exc), "status": 400}

    except Exception as exc:
        res_ = {"msg": str(exc), "status": 500}

    finally:
        status_ = res_["status"] if "status" in res_ else 200
        return json.dumps(res_, default=json_util.default, ensure_ascii=False, sort_keys=False), status_, Security().header_simple_f()


if __name__ == "__main__":
    Schedular().main_f()
    app.run(host="0.0.0.0", port=80, debug=False)
