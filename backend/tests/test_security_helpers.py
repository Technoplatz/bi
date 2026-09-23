"""
Unit checks for the security helpers in the backend/api/bi package and backend/stream/stream.py.

Both modules read their configuration from the environment at import time and only open a
MongoDB connection when a request is handled, so they can be imported with a stub environment
and the pure helpers exercised without a database.

Run with:  pytest backend/tests
"""
import importlib.util
import os
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

API_ENV = {
    "API_MAX_CONTENT_LENGTH_MB": "10", "API_DEFAULT_AGGREGATION_LIMIT": "100", "API_DEFAULT_VISUAL_LIMIT": "100",
    "API_QUERY_PAGE_SIZE": "50", "API_SESSION_EXP_MINUTES": "60", "API_TEMPFILE_PATH": "/temp",
    "API_MONGODUMP_PATH": "/mongodump", "API_CORS_ORIGINS": "http://localhost", "API_S3_ACTIVE": "false",
    "API_PERMISSIVE_TAGS": "#Managers", "API_ADMIN_TAGS": "#Administrators", "API_QADMIN_TAGS": "#QueryAdmin",
    "API_ADMIN_IPS": "203.0.113.10", "API_DELETE_ALLOWED": "false", "RESTAPI_ENABLED": "false",
    "MONGO_RS": "rs0", "MONGO_HOST0": "m0", "MONGO_HOST1": "m1", "MONGO_HOST2": "m2", "MONGO_PORT0": "27017",
    "MONGO_PORT1": "27018", "MONGO_PORT2": "27019", "MONGO_DB": "bi", "MONGO_AUTH_DB": "admin",
    "MONGO_USERNAME": "u", "MONGO_PASSWORD": "p", "MONGO_TLS": "false", "MONGO_READPREF": "primary",
    "MONGO_RETRY_WRITES": "true", "API_OUTPUT_ROWS_LIMIT": "100", "API_JOB_UPDATE_LIMIT": "100",
    "SMTP_TLS_PORT": "587", "HTML_TABLE_MAX_ROWS": "10", "HTML_TABLE_MAX_COLS": "10",
    "API_SCHEDULE_INTERVAL_MIN": "5", "API_FW_TEMP_DURATION_MIN": "5", "API_UPLOAD_LIMIT_BYTES": "1000",
    "TZ": "Europe/Berlin", "DEFAULT_LOCALE": "en",
}


def load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def api():
    os.environ.update(API_ENV)
    sys.path.insert(0, str(ROOT / "backend" / "api"))
    from bi import create_app
    from bi.misc import Misc
    from bi.ratelimit import RateLimiter
    return types.SimpleNamespace(app=create_app(), Misc=Misc, RateLimiter=RateLimiter)


@pytest.fixture(scope="session")
def stream():
    os.environ.update(API_ENV)
    return load("stream_under_test", "backend/stream/stream.py")


# ---------------------------------------------------------------- client ip resolution
def ip_for(api, remote, xff=None, cf=None):
    headers = {}
    if xff is not None:
        headers["X-Forwarded-For"] = xff
    if cf is not None:
        headers["cf-connecting-ip"] = cf
    with api.app.test_request_context("/api/auth", headers=headers, environ_base={"REMOTE_ADDR": remote}):
        return api.Misc().get_client_ip_f()


@pytest.mark.parametrize("remote,xff,cf,expected", [
    ("198.51.100.7", None, "203.0.113.10", "198.51.100.7"),            # direct hit, spoofed cf header
    ("198.51.100.7", "203.0.113.10", None, "198.51.100.7"),            # direct hit, spoofed xff
    ("172.18.0.5", "198.51.100.7", None, "198.51.100.7"),              # via traefik
    ("172.18.0.5", "203.0.113.10, 198.51.100.7", None, "198.51.100.7"),  # attacker-prefixed xff
    ("172.18.0.5", "198.51.100.7", "203.0.113.10", "198.51.100.7"),    # cf header from non-cloudflare peer
    ("172.18.0.5", "9.9.9.9, 104.16.1.1", "198.51.100.7", "198.51.100.7"),  # via cloudflare edge
    ("172.18.0.5", "172.18.0.1", None, "172.18.0.1"),                  # all trusted, leftmost wins
    ("172.18.0.5", "192.168.178.21", None, "192.168.178.21"),          # lan client kept
    ("172.18.0.5", "104.16.1.1", "not-an-ip", "104.16.1.1"),           # malformed cf header ignored
])
def test_client_ip(api, remote, xff, cf, expected):
    assert ip_for(api, remote, xff, cf) == expected


# ---------------------------------------------------------------- aggregation allowlist
@pytest.mark.parametrize("pipeline", [
    [{"$match": {"a": 1}}, {"$group": {"_id": "$a", "n": {"$sum": 1}}}, {"$sort": {"n": -1}}],
    [{"$facet": {"a": [{"$match": {}}, {"$count": "n"}]}}],
])
def test_pipeline_allowed(api, pipeline):
    assert api.Misc().validate_pipeline_f(pipeline)["result"] is True


@pytest.mark.parametrize("pipeline", [
    [{"$match": {}}, {"$out": "_user"}],
    [{"$merge": {"into": "_token"}}],
    [{"$lookup": {"from": "_auth", "as": "x", "localField": "a", "foreignField": "b"}}],
    [{"$match": {"$where": "sleep(1000)"}}],
    [{"$addFields": {"x": {"$function": {"body": "1", "args": [], "lang": "js"}}}}],
    [{"$unionWith": "_user"}],
    [{"$match": {}, "$limit": 1}],
    {"$match": {}},
    [{"$facet": {"a": [{"$lookup": {"from": "_auth"}}]}}],
])
def test_pipeline_rejected(api, pipeline):
    assert api.Misc().validate_pipeline_f(pipeline)["result"] is False


def test_forbidden_operator_scan(api):
    assert api.Misc().scan_forbidden_ops_f({"a": {"$in": [1]}, "b": {"$expr": {"$function": {}}}}) == "$function"
    assert api.Misc().scan_forbidden_ops_f({"a": {"$in": [1]}, "b": {"$gt": 2}}) is None


# ---------------------------------------------------------------- rate limiter and otp age
def test_rate_limiter(api):
    limiter = api.RateLimiter()
    assert [limiter.check_f("b", "k", 3, 600) for _ in range(5)] == [True, True, True, False, False]
    assert limiter.check_f("b", "other", 3, 600) is True


def test_age_minutes(api):
    misc = api.Misc()
    assert 4.9 < misc.age_minutes_f(datetime.now() - timedelta(minutes=5)) < 5.2
    aware = (datetime.now() - timedelta(minutes=5)).replace(tzinfo=timezone.utc)
    assert 4.9 < misc.age_minutes_f(aware) < 5.2
    assert misc.age_minutes_f(None) is None


# ---------------------------------------------------------------- jwt round trip
def test_jwt_round_trip(api):
    misc = api.Misc()
    payload = {"iss": "Technoplatz", "aud": "api", "sub": "bi", "id": "x@example.invalid",
               "iat": datetime.now(), "exp": datetime.now() + timedelta(minutes=5)}
    encoded = misc.jwt_proc_f("encode", None, "secret", payload, None)
    assert encoded["result"] is True
    decoded = misc.jwt_proc_f("decode", encoded["jwt"], "secret", {}, None)
    assert decoded["result"] is True and decoded["jwt"]["id"] == "x@example.invalid"
    assert misc.jwt_proc_f("decode", encoded["jwt"], "other", {}, None)["result"] is False
    bad_sub = dict(payload, sub="not-bi")
    encoded = misc.jwt_proc_f("encode", None, "secret", bad_sub, None)
    assert misc.jwt_proc_f("decode", encoded["jwt"], "secret", {}, None)["result"] is False


# ---------------------------------------------------------------- stream formula evaluator
class _Trigger:
    pass


def evaluator(stream):
    class T(stream.Trigger):
        def __init__(self):
            pass
    return T().safe_eval_f


@pytest.mark.parametrize("expr,expected", [("2*3+1", 7), ("(1.5+2.5)*2/4", 2.0), ("-3*-2", 6), ("17%5 + 17//5", 5)])
def test_safe_eval_arithmetic(stream, expr, expected):
    assert evaluator(stream)(expr) == pytest.approx(expected)


@pytest.mark.parametrize("expr", [
    "__import__('os').system('id')", "os.system", "abs(1)", "(1).real", "'a'*3", "9**999999", "1<2", "",
])
def test_safe_eval_rejects(stream, expr):
    with pytest.raises(stream.AppException):
        evaluator(stream)(expr)


# ---------------------------------------------------------------- csv export frame
def test_frame_from_docs_keeps_requested_columns_and_order(api):
    from bi.crud import Crud
    from bson.objectid import ObjectId
    oid = ObjectId()
    docs = [
        {"_id": oid, "a": 1, "b": {"c": "x"}, "extra": "ignored"},
        {"_id": ObjectId(), "a": 2},
    ]
    frame = Crud().frame_from_docs_f(docs, "b.c, a ,_id")
    assert list(frame.columns) == ["b.c", "a", "_id"]
    assert frame.iloc[0].tolist() == ["x", 1, str(oid)]
    assert frame.iloc[1]["b.c"] is None or frame.iloc[1]["b.c"] != frame.iloc[1]["b.c"]  # missing nested value stays empty
    assert Crud().frame_from_docs_f([], ["a"]).shape == (0, 1)


# ---------------------------------------------------------------- routes registered and health probe
def test_all_routes_registered(api):
    rules = {rule.rule for rule in api.app.url_map.iter_rules()}
    assert {"/api/health", "/api/import", "/api/crud", "/api/otp", "/api/auth", "/api/iot", "/api/post",
            "/api/get/query/<string:id_>"} <= rules


def test_health_reports_database_state(api, monkeypatch):
    import bi.routes as routes

    class _Admin:
        def command(self, name):
            assert name == "ping"

    class _Client:
        admin = _Admin()

    class _Mongo:
        def __init__(self):
            self.client_ = _Client()

    monkeypatch.setattr(routes, "Mongo", _Mongo)
    with api.app.test_client() as client:
        response = client.get("/api/health")
    assert response.status_code == 200 and response.get_json() == {"result": True, "db": True}

    class _Down:
        def __init__(self):
            raise RuntimeError("no primary")

    monkeypatch.setattr(routes, "Mongo", _Down)
    with api.app.test_client() as client:
        response = client.get("/api/health")
    assert response.status_code == 503 and response.get_json()["db"] is False


# ---------------------------------------------------------------- medium findings: regex escaping, cell neutralising, loop guard
def test_regex_fragment_is_escaped_and_capped(api):
    misc = api.Misc()
    assert misc.regex_fragment_f("a.b*(c") == r"a\.b\*\(c"
    assert len(misc.regex_fragment_f("x" * 1000)) == 256


def test_filter_builder_escapes_client_values(api):
    from bi.crud import Crud
    props = {"name": {"bsonType": "string"}}
    like = Crud().get_filtered_f({"match": [{"key": "name", "op": "like", "value": "(a+)+$"}], "properties": props})
    assert like == {"$and": [{"name": {"$regex": "^" + r"\(a\+\)\+\$", "$options": "i"}}]}
    contains = Crud().get_filtered_f({"match": [{"key": "name", "op": "contains", "value": ".*"}], "properties": props})
    assert contains["$and"][0]["name"]["$regex"] == r"\.\*"


def test_neutralize_cells(api):
    import pandas as pd
    frame = pd.DataFrame({"t": ["=SUM(A1)", "+1", "-x", "@cmd", "safe", None], "n": [1, 2, 3, 4, 5, 6]})
    out = api.Misc().neutralize_cells_f(frame)
    assert out["t"].tolist()[:5] == ["'=SUM(A1)", "'+1", "'-x", "'@cmd", "safe"]
    assert out["n"].tolist() == [1, 2, 3, 4, 5, 6]
    assert frame["t"].tolist()[0] == "=SUM(A1)"  # original untouched


def test_stream_loop_guard(stream):
    class T(stream.Trigger):
        def __init__(self):
            self.guard_ = {}
    trigger = T()
    results = [trigger.loop_guard_f("zz_data", "id1") for _ in range(stream.TRIGGER_LOOP_LIMIT_ + 5)]
    assert results[:stream.TRIGGER_LOOP_LIMIT_] == [True] * stream.TRIGGER_LOOP_LIMIT_
    assert results[stream.TRIGGER_LOOP_LIMIT_:] == [False] * 5
    assert trigger.loop_guard_f("zz_data", "id2") is True


# ---------------------------------------------------------------- low findings: error payloads never evaluate exception text
def test_error_payload_shapes(api):
    from bi.errors import APIError, AuthError
    from bi.routes import error_payload_f
    assert error_payload_f(APIError({"result": False, "msg": "x", "extra": 1})) == {"result": False, "msg": "x", "extra": 1}
    assert error_payload_f(AuthError("plain text")) == {"result": False, "msg": "plain text"}
    assert error_payload_f(KeyError("missing")) == {"result": False, "msg": "missing"}
    assert error_payload_f(APIError({"msg": "no result key"})) == {"result": False, "msg": "no result key"}


def test_crud_route_reports_errors_with_status(api):
    with api.app.test_client() as client:
        response = client.post("/api/crud", json={"collection": "x"})
    assert response.status_code == 400 and response.get_json() == {"result": False, "msg": "no operation found"}
    with api.app.test_client() as client:
        response = client.post("/api/crud", json={"op": "read", "collection": "x"})
    assert response.status_code == 403 and response.get_json()["result"] is False


# ---------------------------------------------------------------- docker secrets (Phase 3)
def test_secret_prefers_mounted_file_over_environment(tmp_path, monkeypatch):
    from bi.config import secret_f
    monkeypatch.setenv("MONGO_PASSWORD", "from-env")
    assert secret_f("MONGO_PASSWORD", secrets_dir=str(tmp_path)) == "from-env"
    (tmp_path / "mongo_password").write_text("from-file\n")
    assert secret_f("MONGO_PASSWORD", secrets_dir=str(tmp_path)) == "from-file"
    monkeypatch.delenv("MONGO_PASSWORD")
    assert secret_f("MONGO_PASSWORD", secrets_dir=str(tmp_path)) == "from-file"
    assert secret_f("NOT_SET_ANYWHERE", default="d", secrets_dir=str(tmp_path)) == "d"

