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
