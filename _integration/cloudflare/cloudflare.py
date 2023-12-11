import requests
import json
import sys
import os
import pymongo
import pytz
from pymongo import MongoClient
from datetime import datetime
from flask import Flask, request, make_response
from flask_cors import CORS
from get_docker_secret import get_docker_secret
from functools import partial


class APIException(BaseException):
    """
    docstring is in progress
    """


class JSONEncoder(json.JSONEncoder):
    """
    docstring is in progress
    """

    def default(self, o):
        """
        docstring is in progress
        """
        if isinstance(o, ObjectId) or isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


class Mongo:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        MONGO_RS_ = os.environ.get("MONGO_RS")
        MONGO_HOST0_ = os.environ.get("MONGO_HOST0")
        MONGO_HOST1_ = os.environ.get("MONGO_HOST1")
        MONGO_HOST2_ = os.environ.get("MONGO_HOST2")
        MONGO_PORT0_ = int(os.environ.get("MONGO_PORT0"))
        MONGO_PORT1_ = int(os.environ.get("MONGO_PORT1"))
        MONGO_PORT2_ = int(os.environ.get("MONGO_PORT2"))
        MONGO_DB_ = os.environ.get("MONGO_DB")
        MONGO_AUTH_DB_ = os.environ.get("MONGO_AUTH_DB")
        MONGO_USERNAME_ = get_docker_secret("MONGO_USERNAME", default="")
        MONGO_PASSWORD_ = get_docker_secret("MONGO_PASSWORD", default="")
        MONGO_TLS_CERT_KEYFILE_PASSWORD_ = get_docker_secret(
            "MONGO_TLS_CERT_KEYFILE_PASSWORD", default=""
        )
        MONGO_TLS_ = str(os.environ.get("MONGO_TLS")).lower() == "true"
        MONGO_TLS_CA_KEYFILE_ = os.environ.get("MONGO_TLS_CA_KEYFILE")
        MONGO_TLS_CERT_KEYFILE_ = os.environ.get("MONGO_TLS_CERT_KEYFILE")

        mongo_appname_ = "cloudflare"
        mongo_readpref_primary_ = "primary"
        auth_source_ = f"authSource={MONGO_AUTH_DB_}" if MONGO_AUTH_DB_ else ""
        replicaset_ = (
            f"&replicaSet={MONGO_RS_}" if MONGO_RS_ and MONGO_RS_ != "" else ""
        )
        read_preference_primary_ = (
            f"&readPreference={mongo_readpref_primary_}"
            if mongo_readpref_primary_
            else ""
        )
        appname_ = f"&appname={mongo_appname_}" if mongo_appname_ else ""
        tls_ = "&tls=true" if MONGO_TLS_ else "&tls=false"
        tls_certificate_key_file_ = (
            f"&tlsCertificateKeyFile={MONGO_TLS_CERT_KEYFILE_}"
            if MONGO_TLS_CERT_KEYFILE_
            else ""
        )
        tls_certificate_key_file_password_ = (
            f"&tlsCertificateKeyFilePassword={MONGO_TLS_CERT_KEYFILE_PASSWORD_}"
            if MONGO_TLS_CERT_KEYFILE_PASSWORD_
            else ""
        )
        tls_ca_file_ = (
            f"&tlsCAFile={MONGO_TLS_CA_KEYFILE_}" if MONGO_TLS_CA_KEYFILE_ else ""
        )
        tls_allow_invalid_certificates_ = "&tlsAllowInvalidCertificates=true"
        self.connstr_ = f"mongodb://{MONGO_USERNAME_}:{MONGO_PASSWORD_}@{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}/?{auth_source_}{replicaset_}{read_preference_primary_}{appname_}{tls_}{tls_certificate_key_file_}{tls_certificate_key_file_password_}{tls_ca_file_}{tls_allow_invalid_certificates_}"
        client_ = MongoClient(self.connstr_)
        self.db_ = client_[MONGO_DB_]


class Cloudflare:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.tz_ = os.environ.get("TZ")
        self.cf_active_ = os.environ.get("CF_ACTIVE") in [
            True, "true", "True", "TRUE"]
        self.cf_zone_id_ = os.environ.get("CF_ZONEID")
        self.token_ = os.environ.get("CF_TOKEN")
        self.cf_rule_name_ = os.environ.get("CF_RULE_NAME")
        self.cf_countries_ = os.environ.get(
            "CF_COUNTRIES").replace(" ", "").split(",")
        self.admin_ips_ = os.environ.get("CF_ADMIN_IPS").replace(
            " ", "").split(",") if os.environ.get("CF_ADMIN_IPS") else []
        self.cf_hosts_ = os.environ.get("CF_HOSTS").replace(" ", "").split(",")
        self.custom_phase_ = "http_request_firewall_custom"
        self.log_enabled_ = True
        self.headers_ = {
            "Authorization": f"Bearer {self.token_}",
            "Content-Type": "application/json",
        }

    def set_rules(self, json_):
        """
        docstring is in progress
        """
        result_, msg_, ruleset_id_, rule_id_, count_ = False, "", None, None, 0
        try:
            """
            Get Rule Sets
            """
            if not self.cf_active_:
                raise APIException("cloudflare api is not active")

            response_ = requests.get(
                f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id_}/rulesets",
                headers=self.headers_,
            )
            if response_.status_code != 200:
                raise APIException("no rule sets retrieved")

            content_ = json.loads(response_.content)
            rulesets_ = content_["result"] if "result" in content_ else None
            if not rulesets_:
                raise APIException("no custom rule set found")

            for ruleset_ in rulesets_:
                if ruleset_["phase"] == self.custom_phase_:
                    ruleset_id_ = ruleset_["id"]
            if not ruleset_id_:
                raise APIException("custom rule set id not found")

            """
            Get Rule Set
            """
            response_ = requests.get(
                f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id_}/rulesets/{ruleset_id_}",
                headers=self.headers_,
            )
            if response_.status_code != 200:
                raise APIException("rule set read error")

            content_ = json.loads(response_.content)
            ruleset_ = content_["result"] if "result" in content_ else None
            if not ruleset_:
                raise APIException("rule set not found")

            """
            Get Rules
            """
            rules_ = ruleset_["rules"] if "rules" in ruleset_ else None
            if not rules_:
                raise APIException("no rules found")

            for rule_ in rules_:
                if rule_["description"] == self.cf_rule_name_:
                    rule_id_ = rule_["id"]
                    response_ = requests.delete(
                        f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id_}/rulesets/{ruleset_id_}/rules/{rule_id_}",
                        headers=self.headers_,
                    )

            """
            Get Client IP's
            """
            client_ips_ = []
            cursor_ = (
                Mongo()
                .db_["_firewall"]
                .aggregate(
                    [
                        {
                            "$match": {
                                "fwa_source_ip": {"$ne": "0.0.0.0"},
                                "fwa_enabled": True,
                            },
                        },
                        {
                            "$group": {
                                "_id": "$fwa_source_ip",
                                "count": {"$sum": 1},
                            },
                        },
                    ]
                )
            )
            docs_ = json.loads(JSONEncoder().encode(
                list(cursor_))) if cursor_ else []
            for doc_ in docs_:
                client_ips_.append(doc_["_id"])

            ips_ = self.admin_ips_ + client_ips_
            count_ = len(ips_) if ips_ and len(ips_) > 0 else None
            if not count_:
                raise APIException("no ip addresses found")

            if not self.cf_hosts_:
                raise APIException("no hosts found")

            ipsq_ = "{" + " ".join(f"{ip_}" for ip_ in ips_) + "}"
            hosts_ = "{" + \
                " ".join(f'"{host_}"' for host_ in self.cf_hosts_) + "}"
            countriesq_ = (
                "{" + " ".join(f'"{country_}"' for country_ in self.cf_countries_) + "}"
            )

            expressions_ = []
            expressions_.append(f"http.host in {hosts_}")
            expressions_.append(f"ip.geoip.country in {countriesq_}")
            expressions_.append(f"ip.src in {ipsq_}")
            expressions_.append(f"ssl")
            expression_ = "(" + " and ".join(expressions_) + ")"

            json_data_ = {
                "description": self.cf_rule_name_,
                "expression": expression_,
                "action": "skip",
                "position": {"before": ""},
                "action_parameters": {"ruleset": "current"},
                "logging": {"enabled": self.log_enabled_},
            }

            response_ = requests.post(
                f"https://api.cloudflare.com/client/v4/zones/{self.cf_zone_id_}/rulesets/{ruleset_id_}/rules",
                headers=self.headers_,
                json=json_data_,
            )
            if response_.status_code != 200:
                content_ = json.loads(response_.content)
                raise APIException(content_)

            for doc_ in docs_:
                Mongo().db_["_firewall"].update_many(
                    {"fwa_source_ip": doc_["_id"]},
                    {"$set": {"fwa_waf_sync_date": datetime.now(
                        pytz.timezone(TZ_))}},
                )

            result_ = True
            msg_ = f"waf was synchronized successfully [{count_}]"

        except pymongo.errors.PyMongoError as exc__:
            result_ = False
            msg_ = str(exc__)

        except APIException as exc__:
            result_ = False
            msg_ = str(exc__)

        except Exception as exc__:
            result_ = False
            msg_ = str(exc__)

        finally:
            return {"result": result_, "msg": msg_}


PRINT_ = partial(print, flush=True)

app = Flask(__name__)
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
app.json_encoder = JSONEncoder
CORS(app)


@app.route("/waf", methods=["POST"], endpoint="waf")
def waf_f():
    """
    docstring is in progress
    """
    status_code_, count_, msg_ = 200, 0, ""
    try:
        json_ = request.json
        if not json_:
            raise APIError("no request json provided")

        set_rules_ = Cloudflare().set_rules(json_)
        msg_ = set_rules_["msg"] if "msg" in set_rules_ else None
        if not set_rules_["result"]:
            raise APIError(msg_)

    except APIError as exc__:
        status_code_, msg_ = 400, str(exc__)

    except Exception as exc__:
        status_code_, msg_ = 500, str(exc__)

    finally:
        response_ = make_response(
            {
                "result": True if status_code_ == 200 else False,
                "msg": msg_,
            },
            status_code_,
        )
        response_.mimetype = "application/json"
        return response_


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
