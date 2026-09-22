"""
Integration tests against a running local stack (docker compose, replica set, stream service).

They exercise the bi package directly against the real database: row-level permission filters on
id-based updates, the administrator tag guard, link resolution from the stored schema, the
aggregation allowlist on saved queries, and trigger propagation through the stream service.

Everything they create is prefixed zztest and removed afterwards. Run them with

    backend/tests/run_integration.sh

which starts a throwaway container on the compose network with the api image and the .env file.
They are skipped unless BI_INTEGRATION=1 is set.
"""
import json
import os
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("BI_INTEGRATION") != "1", reason="needs the local stack; run backend/tests/run_integration.sh")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend" / "api"))

SOURCE, TARGET = "zztest", "zztest2"
ADMIN = {"usr_id": "it-admin@example.invalid", "email": "it-admin@example.invalid", "_tags": ["#Administrators", "#Managers"]}
MANAGER = {"usr_id": "it-manager@example.invalid", "email": "it-manager@example.invalid", "_tags": ["#Managers"]}
PLAIN = {"usr_id": "it-user@example.invalid", "email": "it-user@example.invalid", "_tags": ["#ITUsers"]}
QADMIN = {"usr_id": "it-qadmin@example.invalid", "email": "it-qadmin@example.invalid", "_tags": ["#QueryAdmin"]}


def structure(prefix):
    text = (ROOT / "backend" / "api" / "_template" / "_template.json").read_text().replace("zzz_", f"{prefix}_")
    return json.loads(text)


@pytest.fixture(scope="module")
def stack():
    os.makedirs(os.environ.get("API_TEMPFILE_PATH", "/temp"), exist_ok=True)
    from bi.db import Mongo
    db = Mongo().db_
    # schemas: source with a link to the target and a trigger that copies the number field on insert
    src = structure("zzt")
    src["links"] = [{"collection": TARGET, "get": "zz2_string", "match": [], "set": [{"key": "zz2_number", "value": "zzt_number"}],
                     "_tags": ["#Managers"], "notification": {"notify": False}}]
    src["triggers"] = [{"name": "copy-number", "enabled": True, "operations": ["insert"],
                        "changes": [{"key": "zzt_string", "op": "nnull", "value": None}],
                        "targets": [{"collection": TARGET, "match": [{"key": "zz2_string", "value": "zzt_string"}], "filter": [],
                                     "set": [{"key": "zz2_number", "value": "zzt_number"}], "upsert": False}]}]
    tgt = structure("zz2")
    cleanup(db)
    db["_collection"].insert_many([
        {"col_id": SOURCE, "col_prefix": "zzt", "col_title": "ZZ Test", "col_structure": src, "_tags": ["#ITUsers", "#Managers"]},
        {"col_id": TARGET, "col_prefix": "zz2", "col_title": "ZZ Target", "col_structure": tgt, "_tags": ["#Managers"]},
    ])
    db["_permission"].insert_one({"per_collection_id": SOURCE, "per_tag": "#ITUsers", "per_is_active": True, "per_read": True,
                                  "per_insert": True, "per_update": True, "per_delete": False, "per_action": False, "per_query": True,
                                  "per_match": [{"key": "zzt_enum", "op": "eq", "value": "00-Open"}]})
    db["_user"].insert_many([
        {**{k: v for k, v in MANAGER.items() if k != "email"}, "usr_name": "IT Manager", "usr_enabled": True, "usr_scope": "Internal"},
        {**{k: v for k, v in ADMIN.items() if k != "email"}, "usr_name": "IT Admin", "usr_enabled": True, "usr_scope": "Administrator"},
    ])
    db["_query"].insert_one({"que_id": "zztest-query", "que_collection_id": SOURCE, "que_title": "zz", "_tags": ["#QueryAdmin"], "que_aggregate": []})
    yield db
    cleanup(db)


def cleanup(db):
    db[f"{SOURCE}_data"].drop()
    db[f"{TARGET}_data"].drop()
    db["_collection"].delete_many({"col_id": {"$in": [SOURCE, TARGET]}})
    db["_permission"].delete_many({"per_collection_id": SOURCE})
    db["_user"].delete_many({"usr_id": {"$in": [ADMIN["usr_id"], MANAGER["usr_id"], PLAIN["usr_id"]]}})
    db["_query"].delete_many({"que_id": "zztest-query"})


def wait_for(predicate, seconds=20):
    deadline = time.time() + seconds
    while time.time() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.5)
    return None


# ---------------------------------------------------------------- permission row filter on id-based updates (H-5)
def test_upsert_respects_permission_row_filter(stack):
    from bi.auth import Auth
    from bi.crud import Crud
    db = stack
    open_id = db[f"{SOURCE}_data"].insert_one({"zzt_string": "open-1", "zzt_enum": "00-Open", "zzt_number": 1}).inserted_id
    closed_id = db[f"{SOURCE}_data"].insert_one({"zzt_string": "closed-1", "zzt_enum": "20-Closed", "zzt_number": 1}).inserted_id
    perm = Auth().permission_f({"user": PLAIN, "auth": None, "collection": SOURCE, "op": "update"})
    assert perm["result"] is True and perm["allowmatch"], perm

    ok = Crud().upsert_f({"collection": SOURCE, "doc": {"_id": str(open_id), "zzt_number": 7}, "match": list(perm["allowmatch"]), "user": PLAIN})
    assert ok["result"] is True, ok
    assert db[f"{SOURCE}_data"].find_one({"_id": open_id})["zzt_number"] == 7

    denied = Crud().upsert_f({"collection": SOURCE, "doc": {"_id": str(closed_id), "zzt_number": 7}, "match": list(perm["allowmatch"]), "user": PLAIN})
    assert denied["result"] is False and "not permitted" in denied["msg"], denied
    assert db[f"{SOURCE}_data"].find_one({"_id": closed_id})["zzt_number"] == 1


# ---------------------------------------------------------------- administrator tag guard (H-7)
def test_manager_cannot_grant_admin_tag(stack):
    from bi.crud import Crud
    db = stack
    me = db["_user"].find_one({"usr_id": MANAGER["usr_id"]})
    res = Crud().upsert_f({"collection": "_user", "doc": {"_id": str(me["_id"]), "_tags": ["#Managers", "#Administrators"]}, "match": [], "user": MANAGER})
    assert res["result"] is False and "administrator" in res["msg"].lower(), res
    assert db["_user"].find_one({"usr_id": MANAGER["usr_id"]})["_tags"] == ["#Managers"]

    res = Crud().insert_f({"collection": "_user", "doc": {"usr_id": "it-new@example.invalid", "usr_name": "x", "usr_enabled": True,
                                                          "usr_scope": "Internal", "_tags": ["#Administrators"]}, "user": MANAGER})
    assert res["result"] is False, res
    assert db["_user"].find_one({"usr_id": "it-new@example.invalid"}) is None


# ---------------------------------------------------------------- link definitions come from the schema (C-1)
def test_link_is_resolved_from_stored_schema(stack):
    from bi.crud import Crud
    hostile = {"collection": TARGET, "get": "zz2_string", "set": [{"key": "zz2_string", "value": "owned"}], "_tags": ["#Everyone"],
               "api": {"domain": "attacker.invalid"}, "notification": {"notify": True, "fields": "zz2_string"}}
    resolved = Crud().get_stored_link_f(SOURCE, hostile)
    assert resolved["result"] is True
    assert resolved["link"]["set"] == [{"key": "zz2_number", "value": "zzt_number"}]
    assert "api" not in resolved["link"] and resolved["link"]["_tags"] == ["#Managers"]
    assert Crud().get_stored_link_f(SOURCE, {"collection": "_user", "get": "usr_id"})["result"] is False
    assert Crud().get_stored_link_f("_user", hostile)["result"] is False


# ---------------------------------------------------------------- aggregation allowlist on saved queries (H-4)
def test_savequery_rejects_forbidden_stages(stack):
    from bi.crud import Crud
    db = stack
    qid = str(db["_query"].find_one({"que_id": "zztest-query"})["_id"])
    bad = Crud().savequery_f({"id": qid, "aggregate": [{"$match": {}}, {"$out": "_user"}], "userindb": QADMIN})
    assert bad["result"] is False and "not allowed" in bad["msg"], bad
    good = Crud().savequery_f({"id": qid, "aggregate": [{"$match": {"zzt_enum": "00-Open"}}, {"$count": "n"}], "userindb": QADMIN, "approved": True})
    assert good["result"] is True, good
    assert db["_query"].find_one({"que_id": "zztest-query"})["_approved"] is True


# ---------------------------------------------------------------- trigger propagation through the stream service (C-2 path)
def test_trigger_propagates_to_target(stack):
    from bi.crud import Crud
    db = stack
    db[f"{TARGET}_data"].insert_one({"zz2_string": "key-9", "zz2_number": 0})
    # give the stream service a moment to pick up the schema change from the _collection event
    wait_for(lambda: True, 1)
    res = Crud().insert_f({"collection": SOURCE, "doc": {"zzt_string": "key-9", "zzt_enum": "00-Open", "zzt_number": 42}, "user": ADMIN})
    assert res["result"] is True, res
    propagated = wait_for(lambda: db[f"{TARGET}_data"].find_one({"zz2_string": "key-9", "zz2_number": 42}))
    assert propagated is not None, "stream service did not copy the value within 20 seconds"
    assert propagated.get("_trigged_by") == "_trigger"
