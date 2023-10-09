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
along with this program. If not, see https://www.gnu.org/licenses.

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
import re
import json
from functools import partial
import uuid
import base64
from datetime import datetime
from xml.etree import ElementTree
from bson.objectid import ObjectId
import requests
from pymongo import MongoClient, ReturnDocument
import pymongo
from get_docker_secret import get_docker_secret
from flask import Flask, request, make_response
from markupsafe import escape
from flask_cors import CORS


class APIError(BaseException):
    """
    docstring is in progress
    """


class AuthError(BaseException):
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


app = Flask(__name__)
app.config["CORS_ORIGINS"] = ["*"]
app.config["CORS_HEADERS"] = [
    "Content-Type", "Origin",
    "Authorization", "X-Requested-With",
    "Accept", "x-auth"
]
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
CORS(app)

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
MONGO_TLS_CERT_KEYFILE_PASSWORD_ = get_docker_secret("MONGO_TLS_CERT_KEYFILE_PASSWORD", default="")
MONGO_TLS_ = str(os.environ.get("MONGO_TLS")).lower() == "true"
MONGO_TLS_CA_KEYFILE_ = os.environ.get("MONGO_TLS_CA_KEYFILE")
MONGO_TLS_CERT_KEYFILE_ = os.environ.get("MONGO_TLS_CERT_KEYFILE")
MONGO_RETRY_WRITES_ = os.environ.get("MONGO_RETRY_WRITES") in [True, "true", "True", "TRUE"]
API_TEMPFILE_PATH_ = os.environ.get('API_TEMPFILE_PATH')
EDOKSIS_USER_ = os.environ.get("EDOKSIS_USER")
EDOKSIS_PASSWORD_ = os.environ.get("EDOKSIS_PASSWORD")
EDOKSIS_VKN_ = os.environ.get("EDOKSIS_VKN")
EDOKSIS_XML_SIZE_ = int(os.environ.get("EDOKSIS_XML_SIZE"))
CUSTOMIZATION_ID_ = os.environ.get("CUSTOMIZATION_ID")
UBL_VERSION_ID_ = os.environ.get("UBL_VERSION_ID")
ADVICE_TYPE_CODE_ = os.environ.get("ADVICE_TYPE_CODE")
IDENTIFICATION_SCHEME_ = os.environ.get("IDENTIFICATION_SCHEME")
PROFILE_ID_ = os.environ.get("PROFILE_ID")
EDOKSIS_URL_ = os.environ.get("EDOKSIS_URL")
EDOKSIS_TIMEOUT_SECONDS_ = int(os.environ.get("EDOKSIS_TIMEOUT_SECONDS"))
SUPPLIER_NAME_ = os.environ.get("SUPPLIER_NAME")
SUPPLIER_STREET_NAME_ = os.environ.get("SUPPLIER_STREET_NAME")
SUPPLIER_BUILDING_NUMBER_ = os.environ.get("SUPPLIER_BUILDING_NUMBER")
SUPPLIER_CITY_NAME_ = os.environ.get("SUPPLIER_CITY_NAME")
SUPPLIER_PROVINCE_NAME_ = os.environ.get("SUPPLIER_PROVINCE_NAME")
SUPPLIER_COUNTRY_NAME_ = os.environ.get("SUPPLIER_COUNTRY_NAME")
SUPPLIER_POSTAL_CODE_ = os.environ.get("SUPPLIER_POSTAL_CODE")
SUPPLIER_ADDRESS_ID_ = os.environ.get("SUPPLIER_ADDRESS_ID")
SUPPLIER_WEB_ADDRESS_ = os.environ.get("SUPPLIER_WEB_ADDRESS")
SUPPLIER_ALIAS_ = os.environ.get("SUPPLIER_ALIAS")
SUPPLIER_PHONE_ = os.environ.get("SUPPLIER_PHONE")
SUPPLIER_FAX_ = os.environ.get("SUPPLIER_FAX")
SUPPLIER_EMAIL_ = os.environ.get("SUPPLIER_EMAIL")
SUPPLIER_TAX_OFFICE_ = os.environ.get("SUPPLIER_TAX_OFFICE")
SUPPLIER_TAX_NO_ = os.environ.get("SUPPLIER_TAX_NO")
PRINT_ = partial(print, flush=True)


class Mongo:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        mongo_appname_ = "edoksis"
        mongo_readpref_primary_ = "primary"
        auth_source_ = f"authSource={MONGO_AUTH_DB_}" if MONGO_AUTH_DB_ else ""
        replicaset_ = f"&replicaSet={MONGO_RS_}" if MONGO_RS_ and MONGO_RS_ != "" else ""
        read_preference_primary_ = f"&readPreference={mongo_readpref_primary_}" if mongo_readpref_primary_ else ""
        appname_ = f"&appname={mongo_appname_}" if mongo_appname_ else ""
        tls_ = "&tls=true" if MONGO_TLS_ else "&tls=false"
        tls_certificate_key_file_ = f"&tlsCertificateKeyFile={MONGO_TLS_CERT_KEYFILE_}" if MONGO_TLS_CERT_KEYFILE_ else ""
        tls_certificate_key_file_password_ = f"&tlsCertificateKeyFilePassword={MONGO_TLS_CERT_KEYFILE_PASSWORD_}" if MONGO_TLS_CERT_KEYFILE_PASSWORD_ else ""
        tls_ca_file_ = f"&tlsCAFile={MONGO_TLS_CA_KEYFILE_}" if MONGO_TLS_CA_KEYFILE_ else ""
        tls_allow_invalid_certificates_ = "&tlsAllowInvalidCertificates=true"
        retry_writes_ = "&retryWrites=true" if MONGO_RETRY_WRITES_ else "&retryWrites=false"
        self.connstr_ = f"mongodb://{MONGO_USERNAME_}:{MONGO_PASSWORD_}@{MONGO_HOST0_}:{MONGO_PORT0_},{MONGO_HOST1_}:{MONGO_PORT1_},{MONGO_HOST2_}:{MONGO_PORT2_}/?{auth_source_}{replicaset_}{read_preference_primary_}{appname_}{tls_}{tls_certificate_key_file_}{tls_certificate_key_file_password_}{tls_ca_file_}{tls_allow_invalid_certificates_}{retry_writes_}"
        client_ = MongoClient(self.connstr_)
        self.db_ = client_[MONGO_DB_]


class Misc:
    """
    docstring is in progress
    """

    def get_now_f(self):
        """
        docstring is in progress
        """
        return datetime.now()

    def exception_show_f(self, exc_):
        """
        docstring is in progress
        """
        line_no_ = exc_.__traceback__.tb_lineno if hasattr(exc_, "__traceback__") and hasattr(exc_.__traceback__, "tb_lineno") else None
        name_ = type(exc_).__name__ if hasattr(type(exc_), "__name__") else "Exception"
        PRINT_(f"!!! {name_} at line {line_no_}:", str(exc_))
        return True


class Edoksis:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.tag_prefix_ = "{http://tempuri.org/}"

    def get_waybill_f(self, input_):
        """
        docstring is in progress
        """
        exc_, files_ = None, []
        try:
            object_ids_ = input_["ids"]
            document_format_, file_type_ = 2, "pdf"
            cursor_ = Mongo().db_["shipment_data"].find(filter={"_id": {"$in": [ObjectId(o_) for o_ in object_ids_]}})
            shipments_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []
            if not shipments_:
                raise APIError("no shipment found")

            for shipment_ in shipments_:
                shipment_ettn_ = shipment_["shp_wayb_ettn"] if "shp_wayb_ettn" in shipment_ else None
                shipment_id_ = shipment_["shp_id"] if "shp_id" in shipment_ else None
                request_xml_ = f'''
                <soap:Envelope xmlns:soap ="http://www.w3.org/2003/05/soap-envelope" xmlns:tem="http://tempuri.org/">
                    <soap:Header/>
                    <soap:Body>
                        <tem:IrsaliyeIndir xmlns="http://tempuri.org/">
                            <tem:Girdi>
                                <tem:Kimlik>
                                    <tem:Kullanici>{EDOKSIS_USER_}</tem:Kullanici>
                                    <tem:Sifre>{EDOKSIS_PASSWORD_}</tem:Sifre>
                                </tem:Kimlik>
                                <tem:KimlikNo>{EDOKSIS_VKN_}</tem:KimlikNo>
                                <tem:IrsaliyeETTN>{shipment_ettn_}</tem:IrsaliyeETTN>
                                <tem:Tipi>2</tem:Tipi>
                                <tem:Format>{document_format_}</tem:Format>
                            </tem:Girdi>
                        </tem:IrsaliyeIndir>
                    </soap:Body>
                </soap:Envelope>
                '''

                request_xml_ = request_xml_.strip()
                if len(request_xml_) > EDOKSIS_XML_SIZE_:
                    raise APIError("issue request too long")

                match_ = re.search(r'^(\+|-)?(\d+|(\d*\.\d*))?(E|e)?([-+])?(\d+)?$', request_xml_)
                if match_:
                    raise APIError("invalid download request")

                headers_ = {
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "Content-Length": str(len(request_xml_)),
                    "SOAPAction": "IrsaliyeIndir"
                }
                response_ = requests.post(EDOKSIS_URL_, data=request_xml_.encode("utf-8"), headers=headers_, timeout=EDOKSIS_TIMEOUT_SECONDS_)
                root_ = ElementTree.fromstring(response_.content)

                for tag in root_.iter(f"{Edoksis().tag_prefix_}Sonuc"):
                    if not tag.text:
                        raise APIError("!!! missing sonuc tag")
                    if tag.text == "1":
                        for tag in root_.iter(f"{Edoksis().tag_prefix_}Icerik"):
                            if not tag.text:
                                raise APIError("!!! missing icerik tag")
                            document_ = base64.b64decode(tag.text)
                            fn_ = f"waybill_{shipment_id_}_{shipment_ettn_}.{file_type_}"
                            fullpath_ = os.path.normpath(os.path.join(API_TEMPFILE_PATH_, fn_))
                            os.makedirs(os.path.dirname(fullpath_), exist_ok=True)
                            with open(fullpath_, "wb") as file_:
                                file_.write(document_)
                                file_.close()
                            files_.append({"name": fullpath_, "type": file_type_})
                    else:
                        for tag in root_.iter(f"{Edoksis().tag_prefix_}Mesaj"):
                            if not tag.text:
                                raise APIError("!!! missing mesaj tag")
                            raise APIError(str(tag.text))

        except APIError as exc__:
            exc_ = exc__

        except Exception as exc__:
            exc_ = exc__

        finally:
            res_ = exc_ is None
            return {"result": res_, "exc": escape(exc_), "files": files_}


@app.route("/download", methods=["POST"], endpoint="download")
def download_f():
    """
    docstring is in progress
    """
    status_code_, res_, exc_, files_ = 200, {}, None, []
    try:
        if not request.headers:
            raise AuthError("no headers provided")

        content_type_ = request.headers.get("Content-Type", None) if "Content-Type" in request.headers and request.headers["Content-Type"] != "" else None
        if not content_type_:
            raise APIError("no content type provided")
        if content_type_ != "application/json":
            raise APIError(f"invalid content type: {request['Content-Type']}")

        json_ = request.json
        if not json_:
            raise APIError("no request json provided")

        ids_ = json_["ids"] if "ids" in json_ else None
        if not ids_:
            raise APIError("no input ids provided")

        get_waybill_f_ = Edoksis().get_waybill_f({"ids": ids_})
        if not get_waybill_f_["result"]:
            raise APIError(get_waybill_f_["exc"])

        files_ = get_waybill_f_["files"]

    except AuthError as exc__:
        status_code_, exc_ = 401, exc__

    except APIError as exc__:
        status_code_, exc_ = 400, exc__

    except Exception as exc__:
        status_code_, exc_ = 500, exc__

    finally:
        ok_ = status_code_ == 200
        if not ok_:
            Misc().exception_show_f(exc_)
        res_ = {"result": ok_, "content": "OK" if ok_ else escape(exc_), "files": files_}
        response_ = make_response(res_, status_code_)
        response_.mimetype = "application/json"
        return response_


@app.route("/issue", methods=["POST"], endpoint="issue")
def issue_f():
    """
    docstring is in progress
    """
    status_code_, exc_, files_ = 200, None, []
    try:
        if not request.headers:
            raise AuthError("no headers provided")

        content_type_ = request.headers.get("Content-Type", None) if "Content-Type" in request.headers and request.headers["Content-Type"] != "" else None
        if not content_type_ or content_type_ != "application/json":
            raise APIError(f"invalid content type: {content_type_}")

        json_ = request.json
        if not json_:
            raise APIError("no request json provided")

        key_ = json_["key"] if "key" in json_ and json_["key"] is not None else None
        if not key_:
            raise APIError("no map key provided")
        value_ = json_["value"] if "value" in json_ and json_["value"] is not None else None
        if not value_:
            raise APIError("no map value provided")

        filter_ = {}
        filter_[key_] = value_
        shipment_id_ = value_
        email_ = json_["email"] if "email" in json_ else "shipment"

        deliveries_ = list(Mongo().db_["delivery_data"].find(filter_))
        if not deliveries_:
            raise APIError(f"no delivery found {shipment_id_}")

        account_no_ = deliveries_[0]["dnn_acc_no"]
        account_ = Mongo().db_["account_data"].find_one({"acc_no": account_no_})
        if not account_:
            raise APIError("account not found")

        deliverycustomerparty_websiteuri_ = account_["acc_web_address"] if "acc_web_address" in account_ else None
        deliverycustomerparty_id_ = account_["acc_tax_no"] if "acc_tax_no" in account_ else None
        deliverycustomerparty_name_ = account_["acc_name"] if "acc_name" in account_ else None
        deliverycustomerparty_postaladdressid_ = account_["acc_bill_to_address_id"] if "acc_bill_to_address_id" in account_ else None
        deliverycustomerparty_streetname_ = account_["acc_bill_to_street"] if "acc_bill_to_street" in account_ else None
        deliverycustomerparty_buildingnumber_ = account_["acc_bill_to_building"] if "acc_bill_to_building" in account_ else None
        deliverycustomerparty_citysubdivisionname_ = account_["acc_bill_to_province"] if "acc_bill_to_province" in account_ else None
        deliverycustomerparty_cityname_ = account_["acc_bill_to_city"] if "acc_bill_to_city" in account_ else None
        deliverycustomerparty_postalzone_ = account_["acc_bill_to_postcode"] if "acc_bill_to_postcode" in account_ else None
        deliverycustomerparty_countryname_ = account_["acc_bill_to_country"] if "acc_bill_to_country" in account_ else None
        deliverycustomerparty_taxschemename_ = account_["acc_tax_office"] if "acc_tax_office" in account_ else None
        deliverycustomerparty_telephone_ = account_["acc_phone"] if "acc_phone" in account_ else None
        deliverycustomerparty_telefax_ = account_["acc_fax"] if "acc_fax" in account_ else None
        deliverycustomerparty_electronicmail_ = account_["acc_email"] if "acc_email" in account_ else None
        shipment_postaladdressid_ = account_["acc_ship_to_address_id"] if "acc_ship_to_address_id" in account_ else None
        shipment_streetname_ = account_["acc_ship_to_street"] if "acc_ship_to_street" in account_ else None
        shipment_buildingnumber_ = account_["acc_ship_to_building"] if "acc_ship_to_building" in account_ else None
        shipment_citysubdivisionname_ = account_["acc_ship_to_province"] if "acc_ship_to_province" in account_ else None
        shipment_cityname_ = account_["acc_ship_to_city"] if "acc_ship_to_city" in account_ else None
        shipment_postalzone_ = account_["acc_ship_to_postcode"] if "acc_ship_to_postcode" in account_ else None
        shipment_countryname_ = account_["acc_ship_to_country"] if "acc_ship_to_country" in account_ else None
        shipment_actualdespatchdate_ = datetime.now().strftime("%Y-%m-%d")
        shipment_actualdespatchtime_ = datetime.now().strftime("%H:%M:%S")
        shipment_licenseplateidscheme_ = "PLAKA"
        customer_alias_ = account_["acc_alias"] if "acc_alias" in account_ else None
        zarf_ettn_ = str(uuid.uuid4())

        notes_ = ""
        despatch_lines_ = ""
        line_count_ = 0
        for delivery_ in deliveries_:
            delivery_qty_ = delivery_["dnn_qty"]
            delivery_no_ = delivery_["dnn_no"]
            delivery_product_no_ = delivery_["dnn_prd_no"]
            delivery_product_desc_ = delivery_["dnn_prd_description"]
            item_name_ = f"{delivery_no_} {delivery_product_no_} {delivery_product_desc_}"
            item_name_ = item_name_[:256]
            note_ = ""
            unit_code_ = "NIU"
            line_count_ += 1
            notes_ += f"{delivery_no_} "
            despatch_lines_ += f'<tem:DespatchLine><tem:ID>{line_count_}</tem:ID><tem:DeliveredQuantity>{delivery_qty_}</tem:DeliveredQuantity><tem:DeliveredQuantityUnitCode>{unit_code_}</tem:DeliveredQuantityUnitCode><tem:LineID>{shipment_id_}</tem:LineID><tem:ItemName>{item_name_}</tem:ItemName><tem:Note><tem:string>{note_}</tem:string></tem:Note></tem:DespatchLine>'
            shipment_licenseplateid_ = delivery_["dnn_wayb_vid"] if "dnn_wayb_vid" in delivery_ else None
            shipment_partyidentificationid_ = delivery_["dnn_wayb_cid"] if "dnn_wayb_cid" in delivery_ else None
            shipment_partynamename_ = delivery_["dnn_wayb_cname"] if "dnn_wayb_cname" in delivery_ else None
            shp_date_ = delivery_["dnn_wayb_date"] if "dnn_wayb_date" in delivery_ else None
            issue_date_ = shp_date_.strftime("%Y-%m-%d")
            issue_time_ = shp_date_.strftime("%H:%M:%S")

        set_ = {}
        set_["shp_id"] = shipment_id_
        set_["shp_date"] = shp_date_
        set_["shp_acc_no"] = account_no_
        set_["shp_carrier_name"] = shipment_partynamename_
        set_["shp_carrier_id"] = shipment_partyidentificationid_
        set_["shp_vehicle_id"] = shipment_licenseplateid_
        set_["shp_notes"] = notes_
        set_["shp_wayb_no"] = None
        set_["shp_wayb_date"] = None
        set_["shp_wayb_ettn"] = None
        set_["_created_at"] = Misc().get_now_f()
        set_["_created_by"] = email_
        set_["_modified_at"] = Misc().get_now_f()
        set_["_modified_by"] = email_
        update_one_ = Mongo().db_["shipment_data"].update_one({"shp_id": shipment_id_}, {"$set": set_}, upsert=True)

        request_xml_ = f'''
        <soap:Envelope xmlns:soap ="http://www.w3.org/2003/05/soap-envelope" xmlns:tem="http://tempuri.org/">
        <soap:Header/>
            <soap:Body>
                <tem:IrsaliyeZarfGonderYapisal>
                    <tem:IrsaliyeYapisal>
                        <tem:Kimlik>
                            <tem:Kullanici>{EDOKSIS_USER_}</tem:Kullanici>
                            <tem:Sifre>{EDOKSIS_PASSWORD_}</tem:Sifre>
                        </tem:Kimlik>
                        <tem:KimlikNo>{EDOKSIS_VKN_}</tem:KimlikNo>
                        <tem:Zarf>
                            <tem:ZarfETTN>{zarf_ettn_}</tem:ZarfETTN>
                        </tem:Zarf>
                        <tem:Belgeler>
                            <tem:IrsaliyeGonderim>
                                <tem:despatch>
                                    <tem:UBLVersionID>{UBL_VERSION_ID_}</tem:UBLVersionID>
                                    <tem:CustomizationID>{CUSTOMIZATION_ID_}</tem:CustomizationID>
                                    <tem:ProfileID>{PROFILE_ID_}</tem:ProfileID>
                                    <tem:ID>{EDOKSIS_VKN_}</tem:ID>
                                    <tem:CopyIndicator>false</tem:CopyIndicator>
                                    <tem:UUID>{zarf_ettn_}</tem:UUID>
                                    <tem:IssueDate>{issue_date_}</tem:IssueDate>
                                    <tem:IssueTime>{issue_time_}</tem:IssueTime>
                                    <tem:DespatchAdviceTypeCode>{ADVICE_TYPE_CODE_}</tem:DespatchAdviceTypeCode>
                                    <tem:LineCountNumeric>{line_count_}</tem:LineCountNumeric>
                                    <tem:Note><tem:string>{notes_}</tem:string></tem:Note>
                                    <tem:Signature>
                                        <tem:ID>{EDOKSIS_VKN_}</tem:ID>
                                        <tem:PartyIdentificationID>{EDOKSIS_VKN_}</tem:PartyIdentificationID>
                                        <tem:PartyIdentificationScheme>{IDENTIFICATION_SCHEME_}</tem:PartyIdentificationScheme>
                                        <tem:StreetName>{SUPPLIER_STREET_NAME_}</tem:StreetName>
                                        <tem:CitySubdivisionName>{SUPPLIER_PROVINCE_NAME_}</tem:CitySubdivisionName>
                                        <tem:CityName>{SUPPLIER_CITY_NAME_}</tem:CityName>
                                        <tem:CountryName>{SUPPLIER_COUNTRY_NAME_}</tem:CountryName>
                                    </tem:Signature>
                                    <tem:DespatchSupplierParty>
                                        <tem:WebsiteURI>{SUPPLIER_WEB_ADDRESS_}</tem:WebsiteURI>
                                        <tem:ID>{EDOKSIS_VKN_}</tem:ID>
                                        <tem:IDScheme>{IDENTIFICATION_SCHEME_}</tem:IDScheme>
                                        <tem:Name>{SUPPLIER_NAME_}</tem:Name>
                                        <tem:PostalAddressID>{SUPPLIER_ADDRESS_ID_}</tem:PostalAddressID>
                                        <tem:StreetName>{SUPPLIER_STREET_NAME_}</tem:StreetName>
                                        <tem:BuildingNumber>{SUPPLIER_BUILDING_NUMBER_}</tem:BuildingNumber>
                                        <tem:CitySubdivisionName>{SUPPLIER_PROVINCE_NAME_}</tem:CitySubdivisionName>
                                        <tem:CityName>{SUPPLIER_CITY_NAME_}</tem:CityName>
                                        <tem:PostalZone>{SUPPLIER_POSTAL_CODE_}</tem:PostalZone>
                                        <tem:CountryName>{SUPPLIER_COUNTRY_NAME_}</tem:CountryName>
                                        <tem:TaxSchemeName>{SUPPLIER_TAX_OFFICE_}</tem:TaxSchemeName>
                                        <tem:Telephone>{SUPPLIER_PHONE_}</tem:Telephone>
                                        <tem:Telefax>{SUPPLIER_FAX_}</tem:Telefax>
                                        <tem:ElectronicMail>{SUPPLIER_EMAIL_}</tem:ElectronicMail>
                                    </tem:DespatchSupplierParty>
                                    <tem:DeliveryCustomerParty>
                                        <tem:WebsiteURI>{deliverycustomerparty_websiteuri_}</tem:WebsiteURI>
                                        <tem:ID>{deliverycustomerparty_id_}</tem:ID>
                                        <tem:IDScheme>{IDENTIFICATION_SCHEME_}</tem:IDScheme>
                                        <tem:Name>{deliverycustomerparty_name_}</tem:Name>
                                        <tem:PostalAddressID>{deliverycustomerparty_postaladdressid_}</tem:PostalAddressID>
                                        <tem:StreetName>{deliverycustomerparty_streetname_}</tem:StreetName>
                                        <tem:BuildingNumber>{deliverycustomerparty_buildingnumber_}</tem:BuildingNumber>
                                        <tem:CitySubdivisionName>{deliverycustomerparty_citysubdivisionname_}</tem:CitySubdivisionName>
                                        <tem:CityName>{deliverycustomerparty_cityname_}</tem:CityName>
                                        <tem:PostalZone>{deliverycustomerparty_postalzone_}</tem:PostalZone>
                                        <tem:CountryName>{deliverycustomerparty_countryname_}</tem:CountryName>
                                        <tem:TaxSchemeName>{deliverycustomerparty_taxschemename_}</tem:TaxSchemeName>
                                        <tem:Telephone>{deliverycustomerparty_telephone_}</tem:Telephone>
                                        <tem:Telefax>{deliverycustomerparty_telefax_}</tem:Telefax>
                                        <tem:ElectronicMail>{deliverycustomerparty_electronicmail_}</tem:ElectronicMail>
                                    </tem:DeliveryCustomerParty>
                                    <tem:Shipment>
                                        <tem:ID>{shipment_id_}</tem:ID>
                                        <tem:LicensePlateID>{shipment_licenseplateid_}</tem:LicensePlateID>
                                        <tem:LicensePlateIDScheme>{shipment_licenseplateidscheme_}</tem:LicensePlateIDScheme>
                                        <tem:PartyIdentificationID>{shipment_partyidentificationid_}</tem:PartyIdentificationID>
                                        <tem:PartyIdentificationIDScheme>{IDENTIFICATION_SCHEME_}</tem:PartyIdentificationIDScheme>
                                        <tem:PartyNameName>{shipment_partynamename_}</tem:PartyNameName>
                                        <tem:PostalAddressID>{shipment_postaladdressid_}</tem:PostalAddressID>
                                        <tem:StreetName>{shipment_streetname_}</tem:StreetName>
                                        <tem:BuildingNumber>{shipment_buildingnumber_}</tem:BuildingNumber>
                                        <tem:CitySubdivisionName>{shipment_citysubdivisionname_}</tem:CitySubdivisionName>
                                        <tem:CityName>{shipment_cityname_}</tem:CityName>
                                        <tem:PostalZone>{shipment_postalzone_}</tem:PostalZone>
                                        <tem:CountryName>{shipment_countryname_}</tem:CountryName>
                                        <tem:ActualDespatchDate>{shipment_actualdespatchdate_}</tem:ActualDespatchDate>
                                        <tem:ActualDespatchTime>{shipment_actualdespatchtime_}</tem:ActualDespatchTime>
                                    </tem:Shipment>
                                    <tem:DespatchLine>{despatch_lines_}</tem:DespatchLine>
                                </tem:despatch>
                                <tem:gonderenVkn>{EDOKSIS_VKN_}</tem:gonderenVkn>
                                <tem:gonderenAlias>{SUPPLIER_ALIAS_}</tem:gonderenAlias>
                                <tem:aliciVkn>{deliverycustomerparty_id_}</tem:aliciVkn>
                                <tem:aliciAlias>{customer_alias_}</tem:aliciAlias>
                                <tem:erpNo>{shipment_id_}</tem:erpNo>
                            </tem:IrsaliyeGonderim>
                        </tem:Belgeler>
                    </tem:IrsaliyeYapisal>
                </tem:IrsaliyeZarfGonderYapisal>
            </soap:Body>
        </soap:Envelope>
        '''

        request_xml_ = request_xml_.strip()
        if len(request_xml_) > EDOKSIS_XML_SIZE_:
            raise APIError("issue request too long")

        headers_ = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "Content-Length": str(len(request_xml_)),
            "SOAPAction": "IrsaliyeZarfGonderYapisal"
        }

        response_ = requests.post(EDOKSIS_URL_, data=request_xml_.encode("utf-8"), headers=headers_, timeout=EDOKSIS_TIMEOUT_SECONDS_)
        if response_.status_code != 200:
            raise APIError(f"edoksis connection error: { str(response_) }")

        root_ = ElementTree.fromstring(response_.content)
        for tag in root_.iter(f"{Edoksis().tag_prefix_}Sonuc"):
            if not tag.text:
                raise APIError("!!! missing sonuc tag")
            if tag.text == "1":
                for tag in root_.iter(f"{Edoksis().tag_prefix_}IRsaliyeNo"):
                    if not tag.text:
                        raise APIError("!!! missing irsaliyeno tag")
                    waybill_no_ = str(tag.text)
                    for tag in root_.iter(f"{Edoksis().tag_prefix_}IrsaliyeETTN"):
                        if not tag.text:
                            raise APIError("!!! missing irsaliyeettn tag")
                        waybill_ettn_ = str(tag.text)
            else:
                for tag in root_.iter(f"{Edoksis().tag_prefix_}Mesaj"):
                    if not tag.text:
                        raise APIError("!!! missing mesaj tag")
                    raise APIError(str(tag.text))

        set_ = {}
        set_["dnn_wayb_ettn"] = waybill_ettn_
        set_["dnn_wayb_no"] = waybill_no_
        deliveries_ = Mongo().db_["delivery_data"].update_many(filter_, {"$set": set_})

        set_ = {}
        set_["shp_wayb_no"] = waybill_no_
        set_["shp_wayb_date"] = Misc().get_now_f()
        set_["shp_wayb_ettn"] = waybill_ettn_
        set_["_modified_at"] = Misc().get_now_f()
        set_["_modified_by"] = email_
        update_one_ = Mongo().db_["shipment_data"].find_one_and_update({"shp_id": shipment_id_}, {"$set": set_}, return_document=ReturnDocument.AFTER, upsert=True)
        ids__ = str(update_one_["_id"])

        if ids__:
            get_waybill_f_ = Edoksis().get_waybill_f({"ids": [ids__]})
            if not get_waybill_f_["result"]:
                raise APIError(get_waybill_f_["exc"])
            files_ = get_waybill_f_["files"] if "files" in get_waybill_f_ and len(get_waybill_f_["files"]) > 0 else []

    except pymongo.errors.PyMongoError as exc__:
        status_code_, exc_ = 500, exc__

    except AuthError as exc__:
        status_code_, exc_ = 401, exc__

    except APIError as exc__:
        status_code_, exc_ = 400, exc__

    except Exception as exc__:
        status_code_, exc_ = 500, exc__

    finally:
        ok_ = status_code_ == 200
        if not ok_:
            Misc().exception_show_f(exc_)
        res_ = {"result": ok_, "content": "OK" if ok_ else escape(exc_), "files": files_}
        response_ = make_response(res_, status_code_)
        response_.mimetype = "application/json"
        return response_


@app.route("/multi-issue", methods=["POST"], endpoint="multi-issue")
def multi_issue_f():
    """
    docstring is in progress
    """
    status_code_, exc_, files_ = 200, None, []
    try:
        if not request.headers:
            raise AuthError("no headers provided")

        content_type_ = request.headers.get("Content-Type", None) if "Content-Type" in request.headers and request.headers["Content-Type"] != "" else None
        if not content_type_:
            raise APIError("no content type provided")

        if content_type_ != "application/json":
            raise APIError(f"invalid content type: {request['Content-Type']}")

        json_ = request.json
        if not json_:
            raise APIError("no request json provided")

        map_ = json_["map"] if "map" in json_ else None
        if not map_:
            raise APIError("no mapping provided")

        ids_ = json_["ids"] if "ids" in json_ else None
        if not ids_:
            raise APIError("no input ids provided")

        email_ = json_["email"] if "email" in json_ else "shipment"

        shipment_collection_ = map_["shipment_collection"] if "shipment_collection" in map_ else None
        if not shipment_collection_:
            raise APIError("missing shipment collection in mapping")

        shipment_id_field_ = map_["shipment_id_field"] if "shipment_id_field" in map_ else None
        if not shipment_id_field_:
            raise APIError("missing shipment id field in mapping")

        shipment_ettn_field_ = map_["shipment_ettn_field"] if "shipment_ettn_field" in map_ else None
        if not shipment_ettn_field_:
            raise APIError("missing shipment ettn field in mapping")

        shipment_waybill_no_field_ = map_["shipment_waybill_no_field"] if "shipment_waybill_no_field" in map_ else None
        if not shipment_waybill_no_field_:
            raise APIError("missing shipment waybill no field in mapping")

        shipment_waybill_date_field_ = map_["shipment_waybill_date_field"] if "shipment_waybill_date_field" in map_ else None
        if not shipment_waybill_date_field_:
            raise APIError("missing shipment waybill date field in mapping")

        shipment_account_no_field_ = map_["shipment_account_no_field"] if "shipment_account_no_field" in map_ else None
        if not shipment_account_no_field_:
            raise APIError("missing shipment account no field in mapping")

        shipment_notes_field_ = map_["shipment_notes_field"] if "shipment_notes_field" in map_ else None
        if not shipment_notes_field_:
            raise APIError("missing shipment notes field in mapping")

        account_collection_ = map_["account_collection"] if "account_collection" in map_ else None
        if not account_collection_:
            raise APIError("missing account collection in mapping")

        account_no_field_ = map_["account_no_field"] if "account_no_field" in map_ else None
        if not account_no_field_:
            raise APIError("missing account no field in mapping")

        delivery_collection_ = map_["delivery_collection"] if "delivery_collection" in map_ else None
        if not delivery_collection_:
            raise APIError("missing delivery collection in mapping")

        delivery_shipment_id_field_ = map_["delivery_shipment_id_field"] if "delivery_shipment_id_field" in map_ else None
        if not delivery_shipment_id_field_:
            raise APIError("missing delivery shipment id field in mapping")

        delivery_qty_field_ = map_["delivery_qty_field"] if "delivery_qty_field" in map_ else None
        if not delivery_qty_field_:
            raise APIError("missing delivery qty field in mapping")

        delivery_no_field_ = map_["delivery_no_field"] if "delivery_no_field" in map_ else None
        if not delivery_no_field_:
            raise APIError("missing delivery no field in mapping")

        delivery_account_no_field_ = map_["delivery_account_no_field"] if "delivery_account_no_field" in map_ else None
        if not delivery_account_no_field_:
            raise APIError("missing delivery account no field in mapping")

        delivery_product_no_field_ = map_["delivery_product_no_field"] if "delivery_product_no_field" in map_ else None
        if not delivery_product_no_field_:
            raise APIError("missing delivery product no field in mapping")

        delivery_product_desc_field_ = map_["delivery_product_desc_field"] if "delivery_product_desc_field" in map_ else None
        if not delivery_product_desc_field_:
            raise APIError("missing delivery product description field in mapping")

        delivery_set_status_ = map_["delivery_set_status"] if "delivery_set_status" in map_ else None
        if not delivery_set_status_:
            raise APIError("missing delivery set status in mapping")

        delivery_status_field_ = map_["delivery_status_field"] if "delivery_status_field" in map_ else None
        if not delivery_status_field_:
            raise APIError("missing delivery status field in mapping")

        tag_prefix_ = map_["tag_prefix"] if "tag_prefix" in map_ else None
        if not tag_prefix_:
            raise APIError("missing tag prefix in mapping")

        document_format_ = map_["document_format"] if "document_format" in map_ else None
        if not document_format_:
            raise APIError("missing document format in mapping")

        shipments_ = []
        projection_ = {}
        projection_[shipment_id_field_] = 1

        object_ids_ = [ObjectId(i) for i in ids_]
        cursor_ = Mongo().db_[shipment_collection_].find(filter={"_id": {"$in": object_ids_}}, projection=projection_)
        shipments_ = json.loads(JSONEncoder().encode(list(cursor_))) if cursor_ else []
        if not shipments_:
            raise APIError("no shipment id provided")

        err_ = False
        for shipment_ in shipments_:
            shipment_id_ = shipment_[shipment_id_field_] if shipment_id_field_ in shipment_ else None
            if not shipment_id_:
                continue

            shipment_filter_ = {}
            shipment_filter_[shipment_id_field_] = shipment_id_
            shipment_ = Mongo().db_[shipment_collection_].find_one(shipment_filter_)
            if not shipment_:
                raise APIError("shipment not found")

            if shipment_[shipment_ettn_field_] is not None or shipment_[shipment_waybill_no_field_] is not None:
                raise APIError("shipment was already issued")

            delivery_filter_ = {}
            delivery_filter_[delivery_shipment_id_field_] = shipment_id_
            deliveries_ = Mongo().db_[delivery_collection_].find(delivery_filter_)
            line_count_ = deliveries_.explain().get("executionStats", {}).get("nReturned")
            if not deliveries_ or line_count_ == 0:
                raise APIError(f"no deliveries found with {delivery_shipment_id_field_}={shipment_id_}")

            shipment_account_no_ = shipment_[shipment_account_no_field_]
            delivery_account_filter1_ = delivery_account_filter2_ = {}
            delivery_account_filter1_[delivery_shipment_id_field_] = shipment_id_
            delivery_account_filter2_[delivery_account_no_field_] = {"$ne": shipment_account_no_}
            delivery_account_filter_ = {"$and": [delivery_account_filter1_, delivery_account_filter2_]}
            delivery_accounts_ = Mongo().db_[delivery_collection_].find(delivery_account_filter_).explain().get("executionStats", {}).get("nReturned")
            if delivery_accounts_ > 0:
                raise APIError(f"account numbers in {delivery_collection_} don't match with {shipment_collection_}")

            account_filter_ = {}
            account_filter_[account_no_field_] = shipment_[shipment_account_no_field_]
            account_ = Mongo().db_[account_collection_].find_one(account_filter_)
            if not account_:
                raise APIError("account not found")

            deliverycustomerparty_websiteuri_ = account_["acc_web_address"] if "acc_web_address" in account_ else None
            deliverycustomerparty_id_ = account_["acc_tax_no"] if "acc_tax_no" in account_ else None
            deliverycustomerparty_name_ = account_["acc_name"] if "acc_name" in account_ else None
            deliverycustomerparty_postaladdressid_ = account_["acc_bill_to_address_id"] if "acc_bill_to_address_id" in account_ else None
            deliverycustomerparty_streetname_ = account_["acc_bill_to_street"] if "acc_bill_to_street" in account_ else None
            deliverycustomerparty_buildingnumber_ = account_["acc_bill_to_building"] if "acc_bill_to_building" in account_ else None
            deliverycustomerparty_citysubdivisionname_ = account_["acc_bill_to_province"] if "acc_bill_to_province" in account_ else None
            deliverycustomerparty_cityname_ = account_["acc_bill_to_city"] if "acc_bill_to_city" in account_ else None
            deliverycustomerparty_postalzone_ = account_["acc_bill_to_postcode"] if "acc_bill_to_postcode" in account_ else None
            deliverycustomerparty_countryname_ = account_["acc_bill_to_country"] if "acc_bill_to_country" in account_ else None
            deliverycustomerparty_taxschemename_ = account_["acc_tax_office"] if "acc_tax_office" in account_ else None
            deliverycustomerparty_telephone_ = account_["acc_phone"] if "acc_phone" in account_ else None
            deliverycustomerparty_telefax_ = account_["acc_fax"] if "acc_fax" in account_ else None
            deliverycustomerparty_electronicmail_ = account_["acc_email"] if "acc_email" in account_ else None
            shipment_licenseplateid_ = shipment_["shp_vehicle_id"] if "shp_vehicle_id" in shipment_ else None
            shipment_licenseplateidscheme_ = "PLAKA"
            shipment_partyidentificationid_ = shipment_["shp_carrier_id"] if "shp_carrier_id" in shipment_ else None
            shipment_partynamename_ = shipment_["shp_carrier_name"] if "shp_carrier_name" in shipment_ else None
            shipment_postaladdressid_ = account_["acc_ship_to_address_id"] if "acc_ship_to_address_id" in account_ else None
            shipment_streetname_ = account_["acc_ship_to_street"] if "acc_ship_to_street" in account_ else None
            shipment_buildingnumber_ = account_["acc_ship_to_building"] if "acc_ship_to_building" in account_ else None
            shipment_citysubdivisionname_ = account_["acc_ship_to_province"] if "acc_ship_to_province" in account_ else None
            shipment_cityname_ = account_["acc_ship_to_city"] if "acc_ship_to_city" in account_ else None
            shipment_postalzone_ = account_["acc_ship_to_postcode"] if "acc_ship_to_postcode" in account_ else None
            shipment_countryname_ = account_["acc_ship_to_country"] if "acc_ship_to_country" in account_ else None
            shipment_actualdespatchdate_ = datetime.now().strftime("%Y-%m-%d")
            shipment_actualdespatchtime_ = datetime.now().strftime("%H:%M:%S")
            customer_alias_ = account_["acc_alias"] if "acc_alias" in account_ else None
            zarf_ettn_ = str(uuid.uuid4())
            shp_date_ = shipment_["shp_date"] if "shp_date" in shipment_ else None
            issue_date_ = shp_date_.strftime("%Y-%m-%d")
            issue_time_ = shp_date_.strftime("%H:%M:%S")
            notes_ = f"{shipment_[shipment_notes_field_]} " if shipment_notes_field_ in shipment_ else ""

            despatch_lines_ = ""
            line_id_ = 0
            for delivery_ in deliveries_:
                delivery_qty_ = delivery_[delivery_qty_field_]
                delivery_no_ = delivery_[delivery_no_field_]
                delivery_product_no_ = delivery_[delivery_product_no_field_]
                delivery_product_desc_ = delivery_[delivery_product_desc_field_]
                item_name_ = f"{delivery_no_} {delivery_product_no_} {delivery_product_desc_}"
                item_name_ = item_name_[:256]
                note_ = ""
                unit_code_ = "NIU"
                line_id_ += 1
                notes_ += f"{delivery_no_} "
                despatch_lines_ += f'<tem:DespatchLine><tem:ID>{line_id_}</tem:ID><tem:DeliveredQuantity>{delivery_qty_}</tem:DeliveredQuantity><tem:DeliveredQuantityUnitCode>{unit_code_}</tem:DeliveredQuantityUnitCode><tem:LineID>{shipment_id_}</tem:LineID><tem:ItemName>{item_name_}</tem:ItemName><tem:Note><tem:string>{note_}</tem:string></tem:Note></tem:DespatchLine>'

            request_xml_ = f'''
            <soap:Envelope xmlns:soap ="http://www.w3.org/2003/05/soap-envelope" xmlns:tem="http://tempuri.org/">
            <soap:Header/>
                <soap:Body>
                    <tem:IrsaliyeZarfGonderYapisal>
                        <tem:IrsaliyeYapisal>
                            <tem:Kimlik>
                                <tem:Kullanici>{EDOKSIS_USER_}</tem:Kullanici>
                                <tem:Sifre>{EDOKSIS_PASSWORD_}</tem:Sifre>
                            </tem:Kimlik>
                            <tem:KimlikNo>{EDOKSIS_VKN_}</tem:KimlikNo>
                            <tem:Zarf>
                                <tem:ZarfETTN>{zarf_ettn_}</tem:ZarfETTN>
                            </tem:Zarf>
                            <tem:Belgeler>
                                <tem:IrsaliyeGonderim>
                                    <tem:despatch>
                                        <tem:UBLVersionID>{UBL_VERSION_ID_}</tem:UBLVersionID>
                                        <tem:CustomizationID>{CUSTOMIZATION_ID_}</tem:CustomizationID>
                                        <tem:ProfileID>{PROFILE_ID_}</tem:ProfileID>
                                        <tem:ID>{EDOKSIS_VKN_}</tem:ID>
                                        <tem:CopyIndicator>false</tem:CopyIndicator>
                                        <tem:UUID>{zarf_ettn_}</tem:UUID>
                                        <tem:IssueDate>{issue_date_}</tem:IssueDate>
                                        <tem:IssueTime>{issue_time_}</tem:IssueTime>
                                        <tem:DespatchAdviceTypeCode>{ADVICE_TYPE_CODE_}</tem:DespatchAdviceTypeCode>
                                        <tem:LineCountNumeric>{line_count_}</tem:LineCountNumeric>
                                        <tem:Note><tem:string>{notes_}</tem:string></tem:Note>
                                        <tem:Signature>
                                            <tem:ID>{EDOKSIS_VKN_}</tem:ID>
                                            <tem:PartyIdentificationID>{EDOKSIS_VKN_}</tem:PartyIdentificationID>
                                            <tem:PartyIdentificationScheme>{IDENTIFICATION_SCHEME_}</tem:PartyIdentificationScheme>
                                            <tem:StreetName>{SUPPLIER_STREET_NAME_}</tem:StreetName>
                                            <tem:CitySubdivisionName>{SUPPLIER_PROVINCE_NAME_}</tem:CitySubdivisionName>
                                            <tem:CityName>{SUPPLIER_CITY_NAME_}</tem:CityName>
                                            <tem:CountryName>{SUPPLIER_COUNTRY_NAME_}</tem:CountryName>
                                        </tem:Signature>
                                        <tem:DespatchSupplierParty>
                                            <tem:WebsiteURI>{SUPPLIER_WEB_ADDRESS_}</tem:WebsiteURI>
                                            <tem:ID>{EDOKSIS_VKN_}</tem:ID>
                                            <tem:IDScheme>{IDENTIFICATION_SCHEME_}</tem:IDScheme>
                                            <tem:Name>{SUPPLIER_NAME_}</tem:Name>
                                            <tem:PostalAddressID>{SUPPLIER_ADDRESS_ID_}</tem:PostalAddressID>
                                            <tem:StreetName>{SUPPLIER_STREET_NAME_}</tem:StreetName>
                                            <tem:BuildingNumber>{SUPPLIER_BUILDING_NUMBER_}</tem:BuildingNumber>
                                            <tem:CitySubdivisionName>{SUPPLIER_PROVINCE_NAME_}</tem:CitySubdivisionName>
                                            <tem:CityName>{SUPPLIER_CITY_NAME_}</tem:CityName>
                                            <tem:PostalZone>{SUPPLIER_POSTAL_CODE_}</tem:PostalZone>
                                            <tem:CountryName>{SUPPLIER_COUNTRY_NAME_}</tem:CountryName>
                                            <tem:TaxSchemeName>{SUPPLIER_TAX_OFFICE_}</tem:TaxSchemeName>
                                            <tem:Telephone>{SUPPLIER_PHONE_}</tem:Telephone>
                                            <tem:Telefax>{SUPPLIER_FAX_}</tem:Telefax>
                                            <tem:ElectronicMail>{SUPPLIER_EMAIL_}</tem:ElectronicMail>
                                        </tem:DespatchSupplierParty>
                                        <tem:DeliveryCustomerParty>
                                            <tem:WebsiteURI>{deliverycustomerparty_websiteuri_}</tem:WebsiteURI>
                                            <tem:ID>{deliverycustomerparty_id_}</tem:ID>
                                            <tem:IDScheme>{IDENTIFICATION_SCHEME_}</tem:IDScheme>
                                            <tem:Name>{deliverycustomerparty_name_}</tem:Name>
                                            <tem:PostalAddressID>{deliverycustomerparty_postaladdressid_}</tem:PostalAddressID>
                                            <tem:StreetName>{deliverycustomerparty_streetname_}</tem:StreetName>
                                            <tem:BuildingNumber>{deliverycustomerparty_buildingnumber_}</tem:BuildingNumber>
                                            <tem:CitySubdivisionName>{deliverycustomerparty_citysubdivisionname_}</tem:CitySubdivisionName>
                                            <tem:CityName>{deliverycustomerparty_cityname_}</tem:CityName>
                                            <tem:PostalZone>{deliverycustomerparty_postalzone_}</tem:PostalZone>
                                            <tem:CountryName>{deliverycustomerparty_countryname_}</tem:CountryName>
                                            <tem:TaxSchemeName>{deliverycustomerparty_taxschemename_}</tem:TaxSchemeName>
                                            <tem:Telephone>{deliverycustomerparty_telephone_}</tem:Telephone>
                                            <tem:Telefax>{deliverycustomerparty_telefax_}</tem:Telefax>
                                            <tem:ElectronicMail>{deliverycustomerparty_electronicmail_}</tem:ElectronicMail>
                                        </tem:DeliveryCustomerParty>
                                        <tem:Shipment>
                                            <tem:ID>{shipment_id_}</tem:ID>
                                            <tem:LicensePlateID>{shipment_licenseplateid_}</tem:LicensePlateID>
                                            <tem:LicensePlateIDScheme>{shipment_licenseplateidscheme_}</tem:LicensePlateIDScheme>
                                            <tem:PartyIdentificationID>{shipment_partyidentificationid_}</tem:PartyIdentificationID>
                                            <tem:PartyIdentificationIDScheme>{IDENTIFICATION_SCHEME_}</tem:PartyIdentificationIDScheme>
                                            <tem:PartyNameName>{shipment_partynamename_}</tem:PartyNameName>
                                            <tem:PostalAddressID>{shipment_postaladdressid_}</tem:PostalAddressID>
                                            <tem:StreetName>{shipment_streetname_}</tem:StreetName>
                                            <tem:BuildingNumber>{shipment_buildingnumber_}</tem:BuildingNumber>
                                            <tem:CitySubdivisionName>{shipment_citysubdivisionname_}</tem:CitySubdivisionName>
                                            <tem:CityName>{shipment_cityname_}</tem:CityName>
                                            <tem:PostalZone>{shipment_postalzone_}</tem:PostalZone>
                                            <tem:CountryName>{shipment_countryname_}</tem:CountryName>
                                            <tem:ActualDespatchDate>{shipment_actualdespatchdate_}</tem:ActualDespatchDate>
                                            <tem:ActualDespatchTime>{shipment_actualdespatchtime_}</tem:ActualDespatchTime>
                                        </tem:Shipment>
                                        <tem:DespatchLine>{despatch_lines_}</tem:DespatchLine>
                                    </tem:despatch>
                                    <tem:gonderenVkn>{EDOKSIS_VKN_}</tem:gonderenVkn>
                                    <tem:gonderenAlias>{SUPPLIER_ALIAS_}</tem:gonderenAlias>
                                    <tem:aliciVkn>{deliverycustomerparty_id_}</tem:aliciVkn>
                                    <tem:aliciAlias>{customer_alias_}</tem:aliciAlias>
                                    <tem:erpNo>{shipment_id_}</tem:erpNo>
                                </tem:IrsaliyeGonderim>
                            </tem:Belgeler>
                        </tem:IrsaliyeYapisal>
                    </tem:IrsaliyeZarfGonderYapisal>
                </soap:Body>
            </soap:Envelope>
            '''

            request_xml_ = request_xml_.strip()
            if len(request_xml_) > EDOKSIS_XML_SIZE_:
                raise APIError("multi issue request too long")

            match_ = re.search(r'^(\+|-)?(\d+|(\d*\.\d*))?(E|e)?([-+])?(\d+)?$', request_xml_)
            if match_:
                raise APIError("invalid multi issue request")

            headers_ = {
                "Content-Type": "application/soap+xml; charset=utf-8",
                "Content-Length": str(len(request_xml_)),
                "SOAPAction": "IrsaliyeZarfGonderYapisal"
            }

            response_ = requests.post(EDOKSIS_URL_, data=request_xml_.encode("utf-8"), headers=headers_, timeout=EDOKSIS_TIMEOUT_SECONDS_)
            root_ = ElementTree.fromstring(response_.content)

            for tag in root_.iter(f"{tag_prefix_}Sonuc"):
                if not tag.text:
                    raise APIError("!!! missing sonuc tag")
                if tag.text == "1":
                    for tag in root_.iter(f"{tag_prefix_}IRsaliyeNo"):
                        if not tag.text:
                            raise APIError("!!! missing irsaliyeno tag")
                        waybill_no_ = str(tag.text)
                        for tag in root_.iter(f"{tag_prefix_}IrsaliyeETTN"):
                            if not tag.text:
                                raise APIError("!!! missing irsaliyeettn tag")
                            waybill_ettn_ = str(tag.text)
                else:
                    for tag in root_.iter(f"{tag_prefix_}Mesaj"):
                        if not tag.text:
                            raise APIError("!!! missing mesaj tag")
                        raise APIError(str(tag.text))

            process_date_ = Misc().get_now_f()

            set_ = {}
            set_["shp_id"] = shipment_id_
            set_["shp_date"] = shp_date_
            set_["shp_acc_no"] = shipment_account_no_
            set_["shp_carrier_name"] = shipment_partynamename_
            set_["shp_carrier_id"] = shipment_partyidentificationid_
            set_["shp_vehicle_id"] = shipment_licenseplateid_
            set_["shp_notes"] = notes_
            set_["shp_wayb_no"] = waybill_no_
            set_["shp_wayb_date"] = process_date_
            set_["shp_wayb_ettn"] = waybill_ettn_
            set_["_modified_at"] = process_date_
            set_["_modified_by"] = email_
            Mongo().db_[shipment_collection_].update_one(shipment_filter_, {"$set": set_})

            set_ = {}
            set_["dnn_wayb_id"] = shipment_id_
            set_["dnn_wayb_no"] = waybill_no_
            set_["dnn_wayb_date"] = process_date_
            set_["dnn_wayb_ettn"] = waybill_ettn_
            set_["dnn_status"] = delivery_set_status_
            set_["_modified_at"] = process_date_
            set_["_modified_by"] = email_
            deliveries_ = Mongo().db_[delivery_collection_].update_many(delivery_filter_, {"$set": set_})

        files_ = []
        if not err_:
            get_waybill_f_ = Edoksis().get_waybill_f({
                "shipment_ettn_field": shipment_ettn_field_,
                "shipment_id_field": shipment_id_field_,
                "shipment_collection": shipment_collection_,
                "document_format": document_format_,
                "tag_prefix": tag_prefix_,
                "ids": object_ids_
            })
            if not get_waybill_f_["result"]:
                raise APIError(get_waybill_f_["exc"])
            files_ = get_waybill_f_["files"] if "files" in get_waybill_f_ and len(get_waybill_f_["files"]) > 0 else []

    except pymongo.errors.PyMongoError as exc__:
        status_code_, exc_ = 500, exc__

    except AuthError as exc__:
        status_code_, exc_ = 401, exc__

    except APIError as exc__:
        status_code_, exc_ = 400, exc__

    except Exception as exc__:
        status_code_, exc_ = 500, exc__

    finally:
        ok_ = status_code_ == 200
        if not ok_:
            Misc().exception_show_f(exc_)
        res_ = {"result": ok_, "content": "OK" if ok_ else escape(exc_), "files": files_}
        response_ = make_response(res_, status_code_)
        response_.mimetype = "application/json"
        return response_


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
