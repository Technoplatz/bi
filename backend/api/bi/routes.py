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

HTTP routes of the api, registered as a Flask blueprint.
"""

import re
import json
import ast
import pymongo
from bson import json_util
from markupsafe import escape
from flask import Blueprint, make_response, request, send_file

from bi import config as cfg
from bi.auth import Auth
from bi.crud import Crud
from bi.db import Mongo
from bi.encoder import JSONEncoder
from bi.errors import APIError, AuthError, RateLimitError, SessionError
from bi.iot import Iot
from bi.misc import Misc
from bi.otp import OTP

bp = Blueprint("api", __name__)


@bp.route("/api/health", methods=["GET"])
def api_health_f():
    """
    liveness and readiness probe: verifies the database answers a ping
    """
    try:
        Mongo().client_.admin.command("ping")
        res_, sc__ = {"result": True, "db": True}, 200
    except Exception as exc__:
        res_, sc__ = {"result": False, "db": False, "msg": str(exc__)}, 503
    response_ = make_response(json.dumps(res_))
    response_.status_code = sc__
    response_.mimetype = "application/json"
    return response_


@bp.route("/api/import", methods=["POST"], endpoint="import")
def api_import_f():
    """
    docstring is in progress
    """
    try:
        jwt_validate_f_ = Auth().jwt_validate_f()
        if not jwt_validate_f_["result"]:
            raise SessionError(
                {"result": False, "msg": jwt_validate_f_["msg"]})

        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError({"result": False, "msg": "invalid user session"})

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

        permission_f_ = Auth().permission_f(
            {
                "user": jwt_validate_f_["user"],
                "auth": jwt_validate_f_["auth"],
                "collection": collection_,
                "op": process_,
            }
        )
        if not permission_f_["result"]:
            raise AuthError(permission_f_["msg"])

        prefix_ = col_check_["collection"]["col_prefix"]

        import_f_ = Crud().import_f(
            {
                "form": form_,
                "file": file_,
                "collection": collection_,
                "process": process_,
                "user": user_,
                "prefix": prefix_,
            }
        )

        if not import_f_["result"]:
            raise APIError(import_f_["msg"])

        count_ = import_f_["count"] if "count" in import_f_ and import_f_["count"] > 0 else 0
        msg_ = import_f_["msg"] if "msg" in import_f_ else None
        hdr_ = {"Content-Type": "application/json; charset=utf-8"}

        return (
            json.dumps(
                {"result": import_f_["result"], "count": count_, "msg": msg_},
                default=json_util.default,
                sort_keys=False,
            ),
            200,
            hdr_,
        )

    except SessionError as exc__:
        return {"result": False, "msg": str(exc__)}, 403

    except AuthError as exc__:
        return {"result": False, "msg": str(exc__)}, 401

    except APIError as exc__:
        return {"result": False, "msg": str(exc__)}, 400

    except Exception as exc__:
        Misc().notify_exception_f(exc__)
        return {"result": False, "msg": str(exc__)}, 500


@bp.route("/api/crud", methods=["POST"])
def api_crud_f():
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

        email_ = user_["usr_id"] if "usr_id" in user_ else None
        if not email_:
            raise SessionError({"result": False, "msg": "no session provided"})

        input_["user"] = user_
        input_["userindb"] = user_
        collection_ = input_["collection"] if "collection" in input_ else None
        match_ = input_["match"] if "match" in input_ and input_["match"] is not None and len(input_["match"]) > 0 else []
        allowmatch_ = []

        permission_f_ = Auth().permission_f(
            {
                "user": jwt_validate_f_["user"],
                "auth": jwt_validate_f_["auth"],
                "collection": collection_,
                "op": op_,
            }
        )
        if not permission_f_["result"]:
            raise AuthError(permission_f_)

        allowmatch_ = permission_f_["allowmatch"] if "allowmatch" in permission_f_ and len(permission_f_["allowmatch"]) > 0 else []

        if op_ in ["read", "update", "delete", "action", "remove"]:
            match_ += allowmatch_
            input_["match"] = match_

        if op_ in ["update", "insert", "action"]:
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
        elif op_ == "announce":
            query_id_ = input_["id"] if "id" in input_ and input_["id"] else None
            type_ = input_["type"] if "type" in input_ and input_["type"] else "test"

        if op_ in cfg.TFAC_OPS_:
            tfac_ = input_["tfac"] if "tfac" in input_ and input_["tfac"] else None
            if not tfac_:
                raise AuthError({"result": False, "msg": "no otp provided"})
            verify_otp_f_ = Auth().verify_otp_f(email_, tfac_, op_)
            if not verify_otp_f_["result"]:
                raise AuthError(verify_otp_f_)

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
        elif op_ == "announcements":
            res_ = Crud().announcements_f(input_)
        elif op_ == "collections":
            res_ = Crud().collections_f(input_)
        elif op_ == "collection":
            res_ = Crud().collection_f(input_)
        elif op_ == "query":
            res_ = Crud().query_f(input_)
        elif op_ == "job":
            res_ = Crud().job_f(input_)
        elif op_ in ["dumpu", "dumpd", "dumpr"]:
            res_ = Crud().dump_f(input_)
        elif op_ == "saveschema":
            res_ = Crud().saveschema_f(input_)
        elif op_ == "savequery":
            res_ = Crud().savequery_f(input_)
        elif op_ == "savejob":
            res_ = Crud().savejob_f(input_)
        elif op_ == "visuals":
            res_ = Crud().visuals_f(input_)
        elif op_ == "visual":
            res_ = Crud().visual_f(input_)
        elif op_ == "reqotp":
            res_ = OTP().request_otp_f(email_)
        elif op_ == "announce":
            res_ = Crud().query_f({"id": query_id_, "key": "announce", "sched": True, "userindb": user_, "type": type_})
        else:
            raise APIError(f"invalid operation: {op_}")

        if not res_["result"]:
            raise APIError(res_)

    except APIError as exc__:
        Misc().notify_exception_f(exc__)
        sc__, res_ = 400, ast.literal_eval(str(exc__))

    except AuthError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except SessionError as exc__:
        sc__, res_ = 403, ast.literal_eval(str(exc__))

    except Exception as exc__:
        Misc().notify_exception_f(exc__)
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        files_ = res_["files"] if "files" in res_ and len(res_["files"]) > 0 else None

        if "result" in res_ and res_["result"] is True and op_ in ["dumpd", "action"] and files_:
            path_ = files_[0]["name"].strip().lower()
            fname_ = path_.replace(f"{cfg.API_TEMPFILE_PATH_}/", "").replace(f"{cfg.API_MONGODUMP_PATH_}/", "")
            response_ = make_response(send_file(path_))
            response_.status_code = sc__
            response_.headers["Content-Type"] = (f"application/octet-stream; filename={fname_}")
            return response_

        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@bp.route("/api/otp", methods=["POST"])
def api_otp_f():
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
            raise SessionError(
                {"result": False, "msg": jwt_validate_f_["msg"]})

        user_ = jwt_validate_f_["user"] if "user" in jwt_validate_f_ else None
        if not user_:
            raise SessionError(
                {"result": False, "msg": "user session not found"})
        email_ = user_["email"] if "email" in user_ else None

        op_ = escape(request_["op"])

        # H-2: otp requests and validations are budgeted per account
        if not cfg.RATE_LIMITER_.check_f("otp-user", email_, cfg.API_RATE_LIMIT_AUTH_USER_, cfg.API_RATE_LIMIT_WINDOW_SEC_):
            raise RateLimitError({"result": False, "msg": "too many otp requests, please try again later"})

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

    except RateLimitError as exc__:
        sc__, res_ = 429, ast.literal_eval(str(exc__))

    except SessionError as exc__:
        sc__, res_ = 403, ast.literal_eval(str(exc__))

    except APIError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except Exception as exc__:
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@bp.route("/api/auth", methods=["POST"], endpoint="auth")
def api_auth_f():
    """
    docstring is in progress
    """
    sc__, res_ = 200, {}
    try:
        input_ = request.json
        if not input_:
            raise APIError({"result": False, "msg": "input is missing"})
        if "op" not in input_:
            raise APIError({"result": False, "msg": "no operation found"})
        op_ = input_["op"]

        # H-2: budget for credential and otp guesses, per client ip and per account
        ip_ = Misc().get_client_ip_f()
        if not cfg.RATE_LIMITER_.check_f("auth-ip", ip_, cfg.API_RATE_LIMIT_AUTH_IP_, cfg.API_RATE_LIMIT_WINDOW_SEC_):
            raise RateLimitError({"result": False, "msg": "too many attempts, please try again later"})
        email_key_ = str(input_["email"]).strip().lower() if "email" in input_ and input_["email"] else None
        if email_key_ and not cfg.RATE_LIMITER_.check_f("auth-user", email_key_, cfg.API_RATE_LIMIT_AUTH_USER_, cfg.API_RATE_LIMIT_WINDOW_SEC_):
            raise RateLimitError({"result": False, "msg": "too many attempts for this account, please try again later"})

        user_, auth_ = None, None

        if op_ == "signup":
            res_ = Auth().signup_f()
        elif op_ == "signin":
            res_ = Auth().signin_f()
        elif op_ == "tfac":
            res_ = Auth().tfac_f()
        elif op_ == "signout":
            jwt_validate_f_ = Auth().jwt_validate_f()
            if not jwt_validate_f_["result"]:
                raise SessionError(jwt_validate_f_["msg"])
            auth_ = jwt_validate_f_[
                "auth"] if "auth" in jwt_validate_f_ else None
            user_ = jwt_validate_f_[
                "user"] if "user" in jwt_validate_f_ else None
            if not auth_:
                raise SessionError(
                    {"result": False, "msg": "no authentication"})
            res_ = Auth().signout_f(auth_)
        elif op_ == "forgot":
            res_ = Auth().forgot_f()
        elif op_ == "reset":
            res_ = Auth().reset_f()
        else:
            raise APIError({"result": False, "msg": "operation not supported"})

        if not res_["result"]:
            raise AuthError(res_)

    except RateLimitError as exc__:
        sc__, res_ = 429, ast.literal_eval(str(exc__))

    except APIError as exc__:
        sc__, res_ = 400, ast.literal_eval(str(exc__))

    except SessionError as exc__:
        sc__, res_ = 403, ast.literal_eval(str(exc__))

    except AuthError as exc__:
        sc__, res_ = 401, ast.literal_eval(str(exc__))

    except Exception as exc__:
        sc__, res_ = 500, ast.literal_eval(str(exc__))

    finally:
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@bp.route("/api/iot", methods=["POST"])
def api_iot_f():
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
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = sc__
        response_.mimetype = "application/json"
        return response_


@bp.route("/api/post", methods=["POST"])
def api_post_f():
    """
    docstring is in progress
    """
    try:
        if not cfg.RESTAPI_ENABLED_:
            raise APIError("rest api is disabled")

        if not request.headers:
            raise AuthError("no headers provided")

        content_type_ = (
            request.headers.get("Content-Type", None)
            if "Content-Type" in request.headers
            else None
        )
        if not content_type_:
            raise APIError("no content type provided")

        operation_ = (
            request.headers.get("operation", None).lower()
            if "operation" in request.headers
            else None
        )
        if not operation_:
            raise APIError("no operation provided in header")

        if operation_ == "delete" and not cfg.API_DELETE_ALLOWED_:
            raise APIError("record deleting is not allowed")

        rh_collection_ = (
            request.headers.get("collection", None).lower()
            if "collection" in request.headers
            else None
        )
        if not rh_collection_:
            raise APIError("no collection provided in header")

        if operation_ not in ["read", "insert", "update", "delete"]:
            raise APIError("invalid operation")

        x_api_token_ = (
            request.headers["Authorization"]
            if "Authorization" in request.headers
            else None
        )
        if not x_api_token_:
            raise AuthError("no authorization provided")

        split_ = re.split(" ", x_api_token_)
        if not split_ or len(split_) != 2 or split_[0].lower() != "bearer":
            raise AuthError("invalid authorization bearer")

        access_validate_by_api_token_f_ = Auth().access_validate_by_api_token_f(
            x_api_token_, operation_, None
        )
        if not access_validate_by_api_token_f_["result"]:
            raise AuthError(access_validate_by_api_token_f_["msg"])

        # H-6: the rest api serves data collections only, and a token bound to a collection stays there
        if rh_collection_[:1] == "_":
            raise AuthError("system collections are not accessible through the rest api")
        token_doc_ = access_validate_by_api_token_f_["token"] if "token" in access_validate_by_api_token_f_ else {}
        tkn_collection_id_ = token_doc_["tkn_collection_id"] if "tkn_collection_id" in token_doc_ and token_doc_["tkn_collection_id"] else None
        if tkn_collection_id_ and tkn_collection_id_ != rh_collection_:
            raise AuthError(f"token is not allowed to access {rh_collection_}")

        if not request.json:
            raise APIError("no json data provided")

        if not cfg.API_OUTPUT_ROWS_LIMIT_:
            raise APIError("no api rows limit defined")

        collection_f_ = Crud().inner_collection_f(rh_collection_)
        if not collection_f_["result"]:
            raise APIError(collection_f_["msg"])

        collection_ = (
            collection_f_[
                "collection"] if "collection" in collection_f_ else None
        )
        if not collection_:
            raise APIError("collection not found")

        structure_ = (
            collection_[
                "col_structure"] if "col_structure" in collection_ else None
        )
        if not structure_:
            raise APIError(f"no structure found: {collection_}")

        properties_ = structure_[
            "properties"] if "properties" in structure_ else None
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

        session_client_ = pymongo.MongoClient(Mongo().connstr)
        session_db_ = session_client_[cfg.MONGO_DB_]
        session_ = session_client_.start_session()
        session_.start_transaction()

        if operation_ == "read":
            for item_ in body_:
                if not isinstance(item_, dict):
                    raise APIError("read filters must be objects")
                forbidden_ = Misc().scan_forbidden_ops_f(item_)
                if forbidden_:
                    raise APIError(f"filter operator is not allowed: {forbidden_}")
                cursor_ = session_db_[collection_data_].find(item_).limit(int(cfg.API_OUTPUT_ROWS_LIMIT_))
                docs_ = (
                    json.loads(JSONEncoder().encode(
                        list(cursor_))) if cursor_ else []
                )
                for doc_ in docs_:
                    output_.append(doc_)
                    count_ += 1
                    if count_ >= int(cfg.API_OUTPUT_ROWS_LIMIT_):
                        break
        elif operation_ in ["insert", "update", "delete"]:
            filter_ = {}
            if operation_ in ["update", "delete"]:
                if len(unique_) > 0:
                    for uq_ in unique_:
                        for uq__ in uq_:
                            filter_[uq__] = None
                else:
                    raise APIError(
                        f"at least one unique field must be provided for {operation_}"
                    )
            for ix_, item_ in enumerate(body_):
                filter__ = {}
                if operation_ in ["update", "delete"]:
                    for key_ in filter_:
                        if key_ in item_ and item_[key_] is not None:
                            filter__[key_] = item_[key_]
                    if not filter__:
                        raise APIError(
                            f"at least one unique field must be provided for {operation_} index {ix_}"
                        )
                if not isinstance(item_, dict):
                    raise APIError(f"item at index {ix_} must be an object")
                item_ = {key_: value_ for key_, value_ in item_.items() if not str(key_).startswith("_") and not str(key_).startswith("$")}
                decode_crud_doc_f_ = Crud().decode_crud_doc_f(item_, properties_)
                if not decode_crud_doc_f_["result"]:
                    raise APIError(decode_crud_doc_f_["msg"])
                doc__ = decode_crud_doc_f_["doc"]
                doc__ = {key_: value_ for key_, value_ in doc__.items() if not str(key_).startswith("_") and not str(key_).startswith("$")}
                doc__["_modified_at"] = Misc().get_now_f()
                doc__["_modified_by"] = "API"
                if operation_ in ["insert"]:
                    doc__["_created_at"] = Misc().get_now_f()
                    doc__["_created_by"] = "API"
                if operation_ == "update":
                    session_db_[collection_data_].update_many(
                        filter__,
                        {"$set": doc__, "$inc": {"_modified_count": 1}},
                        session=session_,
                    )
                elif operation_ == "insert":
                    session_db_[collection_data_].insert_one(
                        doc__, session=session_)
                elif operation_ == "delete":
                    session_db_[collection_data_].delete_many(
                        filter__, session=session_
                    )
                count_ += 1
                if count_ >= int(cfg.API_OUTPUT_ROWS_LIMIT_):
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

        session_.commit_transaction()
        session_client_.close()

        res_ = {
            "result": True,
            "operation": operation_,
            "count": count_,
            "output": output_,
        }
        response_ = make_response(
            json.dumps(
                res_, default=json_util.default, ensure_ascii=False, sort_keys=False
            )
        )
        response_.status_code = 200
        response_.mimetype = "application/json"
        return response_

    except AuthError as exc__:
        res_ = {"result": False, "msg": str(exc__)}
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = 401
        response_.mimetype = "application/json"
        return response_

    except APIError as exc__:
        res_ = {"result": False, "msg": str(exc__)}
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = 400
        response_.mimetype = "application/json"
        return response_

    except Exception as exc__:
        res_ = {"result": False, "msg": str(exc__)}
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = 500
        response_.mimetype = "application/json"
        return response_


@bp.route("/api/get/query/<string:id_>", methods=["GET"])
def api_get_query(id_):
    """
    docstring is in progress
    """
    status_code_ = 200
    res_ = None
    id_ = Misc().clean_f(id_)
    try:
        if not request.headers:
            raise AuthError({"result": False, "msg": "no headers provided"})

        if not id_:
            raise AuthError({"result": False, "msg": "no query id provided"})

        x_api_token_ = (
            request.headers["X-Api-Token"]
            if "X-Api-Token" in request.headers
            and request.headers["X-Api-Token"] is not None
            else None
        )
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
            raise APIError(f"no data generated at for query: {id_}")

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
        response_ = make_response(
            json.dumps(res_, default=json_util.default, sort_keys=False)
        )
        response_.status_code = status_code_
        response_.mimetype = "application/json"
        return response_
