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

Barcode scanning and serial lookups.
"""

import json
from flask import request

from bi.db import Mongo
from bi.encoder import JSONEncoder
from bi.errors import APIError
from bi.misc import Misc


class Iot:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.props_ = Misc().props_
        self.xtra_props_ = Misc().xtra_props_

    def iot_query_f(self, searched_, page_):
        """
        docstring is in progress
        """
        try:
            aggregate_ = []
            limitn_ = 50
            match_ = {
                "$match": {
                    "$or": [
                        {"ser_dnn_no": {"$regex": searched_, "$options": "i"}},
                        {"ser_sscc_no": {"$regex": searched_, "$options": "i"}},
                    ]
                }
            }
            group_ = {
                "$group": {
                    "_id": {
                        "ser_sscc_no": "$ser_sscc_no",
                        "ser_dnn_no": "$ser_dnn_no",
                        "ser_line_no": "$ser_line_no",
                        "ser_prd_no": "$ser_prd_no",
                    },
                    "count": {"$sum": 1},
                    "ser_in_count": {
                        "$sum": {"$cond": [{"$eq": ["$ser_is_in", True]}, 1, 0]}
                    },
                    "ser_in_date": {"$first": "$ser_in_date"},
                }
            }
            replacewith_ = {"$replaceWith": {
                "$mergeObjects": ["$$ROOT", "$_id"]}}
            skip_ = {"$skip": limitn_ * (page_ - 1)}
            limit_ = {"$limit": limitn_}
            sort_ = {"$sort": {"ser_in_date": -1}}
            lookup_delivery_ = {
                "$lookup": {
                    "from": "delivery_data",
                    "let": {
                        "p_ser_dnn_no": "$ser_dnn_no",
                        "p_ser_line_no": "$ser_line_no",
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$dnn_no", "$$p_ser_dnn_no"]},
                                        {"$eq": ["$dnn_line_no",
                                                 "$$p_ser_line_no"]},
                                    ]
                                }
                            }
                        },
                        {
                            "$unset": [
                                "_modified_count",
                                "_created_at",
                                "_created_by",
                                "_modified_at",
                                "_modified_by",
                            ]
                        },
                    ],
                    "as": "delivery",
                }
            }
            unwind_delivery_ = {
                "$unwind": {"path": "$delivery", "preserveNullAndEmptyArrays": True}
            }
            replacewith_delivery_ = {
                "$replaceWith": {"$mergeObjects": ["$$ROOT", "$delivery"]}
            }
            unset_delivery_ = {"$unset": "delivery"}

            if searched_:
                aggregate_.append(match_)

            aggregate_.append(group_)
            aggregate_.append(replacewith_)
            aggregate_.append(sort_)
            aggregate_.append(skip_)
            aggregate_.append(limit_)
            aggregate_.append(lookup_delivery_)
            aggregate_.append(unwind_delivery_)
            aggregate_.append(replacewith_delivery_)
            aggregate_.append(unset_delivery_)

            cursor_ = Mongo().db_["serial_data"].aggregate(aggregate_)
            docs_ = json.loads(JSONEncoder().encode(
                list(cursor_))) if cursor_ else []

            return {"result": True, "payload": docs_, "msg": None, "status": 200}

        except APIError as exc__:
            return {"result": False, "payload": None, "msg": str(exc__), "status": 400}

        except Exception as exc__:
            return {"result": False, "payload": None, "msg": str(exc__), "status": 500}

    def barcode_scan_f(self, aut_id_):
        """
        docstring is in progress
        """
        try:
            data_ = request.json
            bar_operation_ = (
                data_["bar_operation"]
                if "bar_operation" in data_ and data_["bar_operation"] is not None
                else None
            )
            bar_input_ = (
                data_["bar_input"]
                if "bar_input" in data_ and data_["bar_input"] is not None
                else None
            )
            bar_mode_ = (
                data_["bar_mode"]
                if "bar_mode" in data_ and data_["bar_mode"] in ["auto", "manual"]
                else "auto"
            )

            if bar_operation_ is None or bar_input_ is None:
                raise APIError("invalid inputs")

            prefixes_ = ["1S", "1P", "P", "1K", "S", "Q", "16K", "00"]
            if bar_mode_ == "auto":
                for prfx_ in prefixes_:
                    if bar_input_.startswith(prfx_):
                        bar_input_ = bar_input_.removeprefix(prfx_)
                        break

            doc_ = {}
            doc_["bar_operation"] = bar_operation_
            doc_["bar_input"] = bar_input_
            doc_["bar_mode"] = bar_mode_
            doc_["_modified_at"] = Misc().get_now_f()
            doc_["_modified_by"] = aut_id_
            filter_ = {"bar_operation": bar_operation_,
                       "bar_input": bar_input_}

            read_ = Mongo().db_["barcode_data"].find_one(filter_)
            if not read_:
                doc_["_created_at"] = doc_["_modified_at"]
                doc_["_created_by"] = doc_["_modified_by"]
                Mongo().db_["barcode_data"].insert_one(doc_)
            else:
                Mongo().db_["barcode_data"].update_one(
                    filter_, {"$set": doc_}, upsert=True
                )

            data_ = {}
            payload_ = []
            total_ = 0
            total_in_ = 0
            find_one_ = (
                Mongo()
                .db_["serial_data"]
                .find_one(
                    {"$or": [{"ser_dnn_no": bar_input_},
                             {"ser_sscc_no": bar_input_}]}
                )
            )
            if find_one_:
                ser_dnn_no_ = (
                    find_one_[
                        "ser_dnn_no"] if "ser_dnn_no" in find_one_ else None
                )
                if ser_dnn_no_:
                    delivery_ = (
                        Mongo().db_["delivery_data"].find_one(
                            {"dnn_no": ser_dnn_no_})
                    )
                    if delivery_:
                        aggregate_ = []
                        match_ = {"$match": {"ser_dnn_no": ser_dnn_no_}}
                        group_ = {
                            "$group": {
                                "_id": {
                                    "ser_dnn_no": "$ser_dnn_no",
                                    "ser_sscc_no": "$ser_sscc_no",
                                },
                                "count": {"$sum": 1},
                                "ser_in_count": {
                                    "$sum": {
                                        "$cond": [{"$eq": ["$ser_is_in", True]}, 1, 0]
                                    }
                                },
                            }
                        }
                        replacewith_ = {
                            "$replaceWith": {"$mergeObjects": ["$$ROOT", "$_id"]}
                        }
                        sort_ = {"$sort": {"ser_sscc_no": 1}}
                        aggregate_.append(match_)
                        aggregate_.append(group_)
                        aggregate_.append(replacewith_)
                        aggregate_.append(sort_)
                        cursor_ = Mongo().db_[
                            "serial_data"].aggregate(aggregate_)
                        payload_ = (
                            json.loads(JSONEncoder().encode(list(cursor_)))
                            if cursor_
                            else []
                        )
                    else:
                        raise APIError(f"delivery not found {ser_dnn_no_}")
                else:
                    raise APIError(f"delivery not defined in {bar_mode_} mode")
            else:
                raise APIError(f"input not found in {bar_mode_} mode")

            for pl_ in payload_:
                total_ += pl_["count"]
                total_in_ += pl_["ser_in_count"]

            data_["payload"] = payload_
            data_["input"] = bar_input_
            data_["delivery"] = delivery_
            data_["total"] = total_
            data_["total_in"] = total_in_

            return {
                "result": True,
                "data": data_,
                "msg": f"{bar_input_} OK",
                "status": 200,
            }

        except APIError as exc__:
            return {"result": False, "payload": None, "msg": str(exc__), "status": 400}

        except Exception as exc__:
            return {"result": False, "payload": None, "msg": str(exc__), "status": 500}
