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

Runtime configuration read from the environment once at import time.
"""

import os
from functools import partial

from bi.ratelimit import RateLimiter


API_OUTPUT_ROWS_LIMIT_ = int(str(os.environ.get("API_OUTPUT_ROWS_LIMIT")))
API_JOB_UPDATE_LIMIT_ = int(str(os.environ.get("API_JOB_UPDATE_LIMIT")))
NOTIFICATION_PUSH_URL_ = os.environ.get("NOTIFICATION_PUSH_URL")
COMPANY_NAME_ = os.environ.get("COMPANY_NAME") if os.environ.get("COMPANY_NAME") else "Technoplatz BI"
TZ_ = os.environ.get("TZ")
DOMAIN_ = os.environ.get("DOMAIN")
DEFAULT_LOCALE_ = os.environ.get("DEFAULT_LOCALE")
ADMIN_NAME_ = os.environ.get("ADMIN_NAME")
ADMIN_EMAIL_ = os.environ.get("ADMIN_EMAIL")
SMTP_ENDPOINT_ = os.environ.get("SMTP_ENDPOINT")
SMTP_USERID_ = os.environ.get("SMTP_USERID")
SMTP_PASSWORD_ = os.environ.get("SMTP_PASSWORD")
SMTP_TLS_PORT_ = int(str(os.environ.get("SMTP_TLS_PORT")))
FROM_EMAIL_ = os.environ.get("FROM_EMAIL")
EMAIL_DISCLAIMER_HTML_ = os.environ.get("EMAIL_DISCLAIMER_HTML")
EMAIL_TFA_SUBJECT_ = "Your Backup OTP"
EMAIL_SIGNUP_SUBJECT_ = "Welcome"
EMAIL_SIGNIN_SUBJECT_ = "New Sign-in"
EMAIL_UPLOADERR_SUBJECT_ = "File Upload Result"
EMAIL_DEFAULT_SUBJECT_ = "Hello"
EMAIL_SUBJECT_PREFIX_ = os.environ.get("EMAIL_SUBJECT_PREFIX")
HTML_TABLE_MAX_ROWS_ = int(str(os.environ.get("HTML_TABLE_MAX_ROWS")))
HTML_TABLE_MAX_COLS_ = int(str(os.environ.get("HTML_TABLE_MAX_COLS")))
API_SCHEDULE_INTERVAL_MIN_ = int(str(os.environ.get("API_SCHEDULE_INTERVAL_MIN")))
API_FW_TEMP_DURATION_MIN_ = int(str(os.environ.get("API_FW_TEMP_DURATION_MIN")))
API_UPLOAD_LIMIT_BYTES_ = int(str(os.environ.get("API_UPLOAD_LIMIT_BYTES")))
API_MAX_CONTENT_LENGTH_MB_ = int(str(os.environ.get("API_MAX_CONTENT_LENGTH_MB")))
API_DEFAULT_AGGREGATION_LIMIT_ = int(str(os.environ.get("API_DEFAULT_AGGREGATION_LIMIT")))
API_DEFAULT_VISUAL_LIMIT_ = int(str(os.environ.get("API_DEFAULT_VISUAL_LIMIT")))
API_QUERY_PAGE_SIZE_ = int(str(os.environ.get("API_QUERY_PAGE_SIZE")))
API_SESSION_EXP_MINUTES_ = int(str(os.environ.get("API_SESSION_EXP_MINUTES")))
API_TEMPFILE_PATH_ = os.environ.get("API_TEMPFILE_PATH")
API_MONGODUMP_PATH_ = os.environ.get("API_MONGODUMP_PATH")
API_CORS_ORIGINS_ = os.environ.get("API_CORS_ORIGINS").strip().split(",")
API_S3_ACTIVE_ = os.environ.get("API_S3_ACTIVE") in [True, "true", "True", "TRUE"]
API_S3_REGION_ = os.environ.get("API_S3_REGION")
API_S3_KEY_ID_ = os.environ.get("API_S3_KEY_ID")
API_S3_KEY_ = os.environ.get("API_S3_KEY")
API_S3_BUCKET_NAME_ = os.environ.get("API_S3_BUCKET_NAME")
API_PERMISSIVE_TAGS_ = os.environ.get("API_PERMISSIVE_TAGS").replace(" ", "").split(",")
API_ADMIN_TAGS_ = os.environ.get("API_ADMIN_TAGS").replace(" ", "").split(",")
API_QADMIN_TAGS_ = os.environ.get("API_QADMIN_TAGS").replace(" ", "").split(",")
API_ADMIN_IPS_ = os.environ.get("API_ADMIN_IPS").replace(" ", "").split(",") if os.environ.get("API_ADMIN_IPS") else []
API_DELETE_ALLOWED_ = os.environ.get("API_DELETE_ALLOWED") in [True, "true", "True", "TRUE"]
RESTAPI_ENABLED_ = os.environ.get("RESTAPI_ENABLED") in [True, "true", "True", "TRUE"]
MONGO_RS_ = os.environ.get("MONGO_RS")
MONGO_HOST0_ = os.environ.get("MONGO_HOST0")
MONGO_HOST1_ = os.environ.get("MONGO_HOST1")
MONGO_HOST2_ = os.environ.get("MONGO_HOST2")
MONGO_PORT0_ = int(os.environ.get("MONGO_PORT0"))
MONGO_PORT1_ = int(os.environ.get("MONGO_PORT1"))
MONGO_PORT2_ = int(os.environ.get("MONGO_PORT2"))
MONGO_DB_ = os.environ.get("MONGO_DB")
MONGO_AUTH_DB_ = os.environ.get("MONGO_AUTH_DB")
MONGO_USERNAME_ = os.environ.get("MONGO_USERNAME")
MONGO_PASSWORD_ = os.environ.get("MONGO_PASSWORD")
MONGO_DUMP_HOURS_ = os.environ.get("MONGO_DUMP_HOURS") if os.environ.get("MONGO_DUMP_HOURS") else "23"
MONGO_TLS_ = os.environ.get("MONGO_TLS") in [True, "true", "True", "TRUE"]
MONGO_TLS_CA_KEYFILE_ = os.environ.get("MONGO_TLS_CA_KEYFILE")
MONGO_TLS_CERT_KEYFILE_ = os.environ.get("MONGO_TLS_CERT_KEYFILE")
MONGO_TLS_CERT_KEYFILE_PASSWORD_ = os.environ.get("MONGO_TLS_CERT_KEYFILE_PASSWORD")
MONGO_READPREF_ = os.environ.get("MONGO_READPREF")
MONGO_RETRY_WRITES_ = os.environ.get("MONGO_RETRY_WRITES") in [True, "true", "True", "TRUE"]
MONGO_TIMEOUT_MS_ = int(os.environ.get("MONGO_TIMEOUT_MS")) if os.environ.get(
    "MONGO_TIMEOUT_MS") and int(os.environ.get("MONGO_TIMEOUT_MS")) > 0 else 90000
PREVIEW_ROWS_ = int(os.environ.get("PREVIEW_ROWS")) if os.environ.get(
    "PREVIEW_ROWS") and int(os.environ.get("PREVIEW_ROWS")) > 0 else 10
API_TRUSTED_PROXIES_ = [
    net_.strip() for net_ in (os.environ.get("API_TRUSTED_PROXIES") or "172.16.0.0/12,127.0.0.0/8,::1/128").split(",") if net_.strip()
]
# current published cloudflare ranges; override with API_CLOUDFLARE_IPS when they change
API_CLOUDFLARE_IPS_ = [
    net_.strip() for net_ in (os.environ.get("API_CLOUDFLARE_IPS") or (
        "173.245.48.0/20,103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,141.101.64.0/18,108.162.192.0/18,"
        "190.93.240.0/20,188.114.96.0/20,197.234.240.0/22,198.41.128.0/17,162.158.0.0/15,104.16.0.0/13,"
        "104.24.0.0/14,172.64.0.0/13,131.0.72.0/22,2400:cb00::/32,2606:4700::/32,2803:f800::/32,"
        "2405:b500::/32,2405:8100::/32,2a06:98c0::/29,2c0f:f248::/32"
    )).split(",") if net_.strip()
]
API_OTP_EXP_MINUTES_ = int(os.environ.get("API_OTP_EXP_MINUTES")) if os.environ.get("API_OTP_EXP_MINUTES") else 10
API_OTP_MAX_ATTEMPTS_ = int(os.environ.get("API_OTP_MAX_ATTEMPTS")) if os.environ.get("API_OTP_MAX_ATTEMPTS") else 5
API_RATE_LIMIT_AUTH_IP_ = int(os.environ.get("API_RATE_LIMIT_AUTH_IP")) if os.environ.get("API_RATE_LIMIT_AUTH_IP") else 200
API_RATE_LIMIT_AUTH_USER_ = int(os.environ.get("API_RATE_LIMIT_AUTH_USER")) if os.environ.get("API_RATE_LIMIT_AUTH_USER") else 10
API_RATE_LIMIT_WINDOW_SEC_ = int(os.environ.get("API_RATE_LIMIT_WINDOW_SEC")) if os.environ.get("API_RATE_LIMIT_WINDOW_SEC") else 600
API_OUTBOUND_HOSTS_ = [
    host_.strip().lower() for host_ in (os.environ.get("API_OUTBOUND_HOSTS") or "edoksis,cloudflare").split(",") if host_.strip()
]
INTEGRATION_API_KEY_ = os.environ.get("INTEGRATION_API_KEY") or None
FORBIDDEN_AGG_OPS_ = {
    "$where", "$function", "$accumulator", "$out", "$merge", "$lookup", "$graphLookup", "$unionWith",
    "$currentOp", "$listSessions", "$listLocalSessions", "$collStats", "$indexStats", "$planCacheStats",
    "$search", "$searchMeta", "$vectorSearch", "$documents", "$changeStream", "$shardedDataDistribution",
    "$querySettings", "$listSampledQueries", "$listSearchIndexes", "$sql",
}
ALLOWED_AGG_STAGES_ = {
    "$match", "$project", "$group", "$sort", "$limit", "$skip", "$unwind", "$addFields", "$set", "$unset",
    "$count", "$facet", "$bucket", "$bucketAuto", "$sortByCount", "$replaceRoot", "$replaceWith", "$sample",
    "$redact", "$densify", "$fill", "$setWindowFields", "$geoNear",
}
RATE_LIMITER_ = RateLimiter()
JWT_ISSUER_, JWT_AUDIENCE_, JWT_SUBJECT_ = "Technoplatz", "api", "bi"
PROTECTED_COLLS_ = ["_log", "_dump", "_event", "_announcement"]
PROTECTED_INSDEL_EXC_COLLS_ = ["_token"]
STRUCTURE_KEYS_ = ["properties", "unique", "index", "required", "sort",
                   "parents", "links", "actions", "triggers", "import", "pagination"]
STRUCTURE_KEYS_OPTIN_ = ["queries"]
PROP_KEYS_ = ["bsonType", "title", "description"]
TEMP_PATH_ = "/temp"
DUMP_PATH_ = "/mongodump"
PRINT_ = partial(print, flush=True)
TFAC_OPS_ = ["announce"]
UPLOAD_EXTENSIONS_ = ["pdf", "png", "jpg", "jpeg", "xlsx", "xls", "doc", "docx", "csv", "txt"]
CORS_HEADERS_ = ["Content-Type", "Origin", "Authorization", "X-Requested-With", "Accept", "X-Auth"]
