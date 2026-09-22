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

Background scheduler for dumps, queries, jobs and firewall expiry.
"""

import re
import json
from datetime import datetime
import pymongo
from bson.objectid import ObjectId
from croniter import croniter
from apscheduler.schedulers.background import BackgroundScheduler

from bi import config as cfg
from bi.crud import Crud
from bi.db import Mongo
from bi.encoder import JSONEncoder
from bi.errors import APIError, PassException
from bi.misc import Misc


class Schedular:
    """
    docstring is in progress
    """

    def cron_looker_f(self, view_):
        """
        docstring is in progress
        """
        try:
            scheduled_ = view_["scheduled"] if "scheduled" in view_ else None
            if not scheduled_:
                raise PassException("view not scheduled")

            scheduled_cron_ = (
                view_["scheduled_cron"] if "scheduled_cron" in view_ else None
            )
            if not croniter.is_valid(scheduled_cron_):
                return {"result": False, "msg": "invalid crontab"}

            separated_ = re.split(" ", scheduled_cron_)
            if not (separated_ and len(separated_) == 5):
                return {"result": False, "msg": "invalid cron format"}

            minute_ = separated_[0].strip()
            hour_ = separated_[1].strip()
            day_ = separated_[2].strip()
            month_ = separated_[3].strip()
            day_of_week_ = separated_[4].lower().strip()

            return {
                "result": True,
                "minute": str(minute_),
                "hour": str(hour_),
                "day": str(day_),
                "month": str(month_),
                "day_of_week": str(day_of_week_),
            }

        except PassException as exc__:
            return Misc().pass_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def schedule_query_job_f(self, source_, sched_):
        """
        docstring is in progress
        """
        try:
            if source_ == "_query":
                schedules_ = (
                    Mongo()
                    .db_["_query"]
                    .find(
                        {"que_enabled": True, "que_scheduled": True, "_approved": True}
                    )
                )
            elif source_ == "_job":
                schedules_ = (
                    Mongo()
                    .db_["_job"]
                    .find(
                        {"job_enabled": True, "job_scheduled": True, "_approved": True}
                    )
                )
            else:
                return {"result": True}

            if not schedules_:
                return {"result": True}

            for query_ in schedules_:
                id__ = str(query_["_id"]) if "_id" in query_ else None

                if not id__:
                    continue

                scheduled_cron_ = (
                    query_["que_scheduled_cron"]
                    if source_ == "_query" and "que_scheduled_cron" in query_
                    else (
                        query_["job_scheduled_cron"]
                        if source_ == "_job" and "job_scheduled_cron" in query_
                        else None
                    )
                )

                if not croniter.is_valid(scheduled_cron_):
                    continue

                separated_ = re.split(" ", scheduled_cron_)
                if not (separated_ and len(separated_) == 5):
                    continue

                minute_ = str(separated_[0].strip())
                hour_ = str(separated_[1].strip())
                day_ = str(separated_[2].strip())
                month_ = str(separated_[3].strip())
                day_of_week_ = str(separated_[4].lower().strip())

                if source_ == "_job":
                    sched_.add_job(
                        Crud().job_f,
                        trigger="cron",
                        minute=minute_,
                        hour=hour_,
                        day=day_,
                        month=month_,
                        day_of_week=day_of_week_,
                        id=id__,
                        replace_existing=True,
                        args=[{"id": id__, "run": True}],
                    )
                elif source_ == "_query":
                    sched_.add_job(
                        Crud().query_f,
                        trigger="cron",
                        minute=minute_,
                        hour=hour_,
                        day=day_,
                        month=month_,
                        day_of_week=day_of_week_,
                        id=id__,
                        replace_existing=True,
                        args=[
                            {
                                "id": id__,
                                "sched": True,
                                "key": cfg.SMTP_PASSWORD_,
                                "type": "live",
                            }
                        ],
                    )
                else:
                    raise APIError("invalid scheduled source")

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except APIError as exc__:
            return Misc().notify_exception_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def schedule_fw_f(self):
        """
        docstring is in progress
        """
        try:
            past_ = datetime(2020, 1, 1, 00, 00)
            agg_ = [
                {
                    "$set": {
                        "minutediff": {
                            "$dateDiff": {
                                "startDate": {"$ifNull": ["$fwa_waf_sync_date", past_]},
                                "endDate": Misc().get_now_f(),
                                "unit": "minute",
                            },
                        }
                    },
                },
                {
                    "$match": {
                        "$and": [
                            {"fwa_type": {"$eq": "Temporary"}},
                            {"fwa_enabled": {"$eq": True}},
                            {"minutediff": {"$gt": cfg.API_FW_TEMP_DURATION_MIN_}},
                        ],
                    },
                },
            ]
            cursor_ = Mongo().db_["_firewall"].aggregate(agg_)
            rules_ = json.loads(JSONEncoder().encode(
                list(cursor_))) if cursor_ else []
            for rule_ in rules_:
                Mongo().db_["_firewall"].update_one(
                    {"_id": ObjectId(rule_["_id"])},
                    {
                        "$set": {
                            "fwa_enabled": False,
                            "_modified_at": Misc().get_now_f(),
                            "_modified_by": "cron",
                        }
                    },
                )

            return {"result": True}

        except pymongo.errors.PyMongoError as exc__:
            return Misc().mongo_error_f(exc__)

        except Exception as exc__:
            return Misc().notify_exception_f(exc__)

    def main_f(self):
        """
        docstring is in progress
        """
        try:
            sched_ = BackgroundScheduler(daemon=True)
            sched_.remove_all_jobs()
            sched_.add_job(
                Crud().dump_f,
                trigger="cron",
                minute="0",
                hour=f"{cfg.MONGO_DUMP_HOURS_}",
                day="*",
                month="*",
                day_of_week="*",
                id="schedule_dump",
                replace_existing=True,
                args=[{"user": {"email": "cronjob"}, "op": "dumpu"}],
            )
            sched_.add_job(
                self.schedule_query_job_f,
                trigger="cron",
                minute=f"*/{cfg.API_SCHEDULE_INTERVAL_MIN_}",
                hour="*",
                day="*",
                month="*",
                day_of_week="*",
                id="schedule_queries",
                replace_existing=True,
                args=["_query", sched_],
            )
            sched_.add_job(
                self.schedule_query_job_f,
                trigger="cron",
                minute=f"*/{cfg.API_SCHEDULE_INTERVAL_MIN_}",
                hour="*",
                day="*",
                month="*",
                day_of_week="*",
                id="schedule_jobs",
                replace_existing=True,
                args=["_job", sched_],
            )
            sched_.add_job(
                self.schedule_fw_f,
                trigger="cron",
                minute=f"*/{cfg.API_SCHEDULE_INTERVAL_MIN_}",
                hour="*",
                day="*",
                month="*",
                day_of_week="*",
                id="schedule_fw",
                replace_existing=True,
                args=[],
            )
            sched_.start()
            return True

        except APIError as exc:
            return Misc().notify_exception_f(exc)

        except Exception as exc:
            return Misc().notify_exception_f(exc)
