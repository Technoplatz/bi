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
from datetime import datetime
from xml.etree import ElementTree
from bson import json_util
import requests
from pymongo import MongoClient
import pytz
import pymongo
from get_docker_secret import get_docker_secret
from flask import Flask, request, make_response
from flask_cors import CORS


class APIError(BaseException):
    """
    docstring is in progress
    """


class IssueError(BaseException):
    """
    docstring is in progress
    """


class AuthError(BaseException):
    """
    docstring is in progress
    """


app = Flask(__name__)
app.config["CORS_ORIGINS"] = ["*"]
app.config["CORS_HEADERS"] = [
    "Content-Type", "Origin",
    "Authorization", "X-Requested-With",
    "Accept", "x-auth"
]
app.config["CORS_SUPPORTS_CREDENTIALS"] = True
CORS(app)

TZ_ = os.environ.get("TZ")
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
EDOKSIS_USER_ = os.environ.get("EDOKSIS_USER")
EDOKSIS_PASSWORD_ = os.environ.get("EDOKSIS_PASSWORD")
EDOKSIS_VKN_ = os.environ.get("EDOKSIS_VKN")
CUSTOMIZATION_ID_ = os.environ.get("CUSTOMIZATION_ID")
UBL_VERSION_ID_ = os.environ.get("UBL_VERSION_ID")
ADVICE_TYPE_CODE_ = os.environ.get("ADVICE_TYPE_CODE")
IDENTIFICATION_SCHEME_ = os.environ.get("IDENTIFICATION_SCHEME")
PROFILE_ID_ = os.environ.get("PROFILE_ID")
EDOKSIS_URL_ = os.environ.get("EDOKSIS_URL")
EDOKSIS_TIMEOUT_SECONDS_ = os.environ.get("EDOKSIS_TIMEOUT_SECONDS")
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
        return datetime.now(pytz.timezone(TZ_))

    def exception_show_f(self, exc_):
        """
        docstring is in progress
        """
        line_no_ = exc_.__traceback__.tb_lineno if hasattr(exc_, "__traceback__") and hasattr(exc_.__traceback__, "tb_lineno") else None
        name_ = type(exc_).__name__ if hasattr(type(exc_), "__name__") else "Exception"
        print_(f"!!! {name_} at line {line_no_}:", str(exc_))
        return True


@app.route("/issue", methods=["POST"], endpoint="issue")
def issue_f():
    """
    docstring is in progress
    """
    try:
        print_("*** ok0")

        session_client_ = MongoClient(Mongo().connstr_)
        session_db_ = session_client_[MONGO_DB_]
        session_ = session_client_.start_session()
        session_.start_transaction()

        if not request.headers:
            raise AuthError("no headers provided")

        content_type_ = request.headers.get("Content-Type", None) if "Content-Type" in request.headers and request.headers["Content-Type"] != "" else None
        if not content_type_:
            raise APIError("no content type provided")

        if content_type_ != "application/json":
            raise APIError(f"invalid content type: {request['Content-Type']}")

        if not request.data:
            raise APIError("no data requested")

        body_ = request.json
        if not body_:
            raise APIError("no request json provided")

        shipment_collection_ = body_["shipment_collection"] if "shipment_collection" in body_ and body_["shipment_collection"] is not None else None
        if not shipment_collection_:
            raise APIError("missing shipment collection")

        shipment_id_field_ = body_["shipment_id_field"] if "shipment_id_field" in body_ and body_["shipment_id_field"] is not None else None
        if not shipment_id_field_:
            raise APIError("missing shipment id field")

        shipment_ettn_field_ = body_["shipment_ettn_field"] if "shipment_ettn_field" in body_ and body_["shipment_ettn_field"] is not None else None
        if not shipment_ettn_field_:
            raise APIError("missing shipment ettn field")

        shipment_ewaybill_no_field_ = body_["shipment_ewaybill_no_field"] if "shipment_ewaybill_no_field" in body_ and body_["shipment_ewaybill_no_field"] is not None else None
        if not shipment_ewaybill_no_field_:
            raise APIError("missing shipment ewaybill no field")

        shipment_ewaybill_date_field_ = body_["shipment_ewaybill_date_field"] if "shipment_ewaybill_date_field" in body_ and body_["shipment_ewaybill_date_field"] is not None else None
        if not shipment_ewaybill_date_field_:
            raise APIError("missing shipment ewaybill date field")

        shipment_account_no_field_ = body_["shipment_account_no_field"] if "shipment_account_no_field" in body_ and body_["shipment_account_no_field"] is not None else None
        if not shipment_account_no_field_:
            raise APIError("missing shipment account no field")

        shipment_status_field_ = body_["shipment_status_field"] if "shipment_status_field" in body_ and body_["shipment_status_field"] is not None else None
        if not shipment_status_field_:
            raise APIError("missing shipment status field")

        shipment_status_ok_value_ = body_["shipment_status_ok_value"] if "shipment_status_ok_value" in body_ and body_["shipment_status_ok_value"] is not None else None
        if not shipment_status_ok_value_:
            raise APIError("missing shipment ok value")

        shipment_ids_ = body_["shipment_ids"] if "shipment_ids" in body_ and len(body_["shipment_ids"]) > 0 else None
        if not shipment_ids_:
            raise APIError("no shipment id provided")

        account_collection_ = body_["account_collection"] if "account_collection" in body_ and body_["account_collection"] is not None else None
        if not account_collection_:
            raise APIError("missing account collection")

        account_no_field_ = body_["account_no_field"] if "account_no_field" in body_ and body_["account_no_field"] is not None else None
        if not account_no_field_:
            raise APIError("missing account no field")

        delivery_collection_ = body_["delivery_collection"] if "delivery_collection" in body_ and body_["delivery_collection"] is not None else None
        if not delivery_collection_:
            raise APIError("missing delivery collection")

        delivery_shipment_id_field_ = body_["delivery_shipment_id_field"] if "delivery_shipment_id_field" in body_ and body_["delivery_shipment_id_field"] is not None else None
        if not delivery_shipment_id_field_:
            raise APIError("missing delivery shipment id field")

        delivery_qty_field_ = body_["delivery_qty_field"] if "delivery_qty_field" in body_ and body_["delivery_qty_field"] is not None else None
        if not delivery_qty_field_:
            raise APIError("missing delivery qty field")

        delivery_no_field_ = body_["delivery_no_field"] if "delivery_no_field" in body_ and body_["delivery_no_field"] is not None else None
        if not delivery_no_field_:
            raise APIError("missing delivery no field")

        delivery_waybill_no_field_ = body_["delivery_waybill_no_field"] if "delivery_waybill_no_field" in body_ and body_["delivery_waybill_no_field"] is not None else None
        if not delivery_waybill_no_field_:
            raise APIError("missing delivery waybill no field")

        delivery_waybill_date_field_ = body_["delivery_waybill_date_field"] if "delivery_waybill_date_field" in body_ and body_["delivery_waybill_date_field"] is not None else None
        if not delivery_waybill_date_field_:
            raise APIError("missing delivery waybill date field")

        delivery_product_no_field_ = body_["delivery_product_no_field"] if "delivery_product_no_field" in body_ and body_["delivery_product_no_field"] is not None else None
        if not delivery_product_no_field_:
            raise APIError("missing delivery product no field")

        delivery_product_desc_field_ = body_["delivery_product_desc_field"] if "delivery_product_desc_field" in body_ and body_["delivery_product_desc_field"] is not None else None
        if not delivery_product_desc_field_:
            raise APIError("missing delivery product description field")

        ewaybills_ = []

        for shipment_id_ in shipment_ids_:
            try:
                shipment_filter_ = {}
                shipment_filter_[shipment_id_field_] = shipment_id_
                shipment_ = session_db_[shipment_collection_].find_one(shipment_filter_)
                if not shipment_:
                    raise IssueError("shipment not found")

                if shipment_[shipment_ettn_field_] is not None or shipment_[shipment_ewaybill_no_field_] is not None:
                    raise IssueError(f"shipment was already issued in {shipment_collection_}")

                prior_filter_ = {}
                prior_filter_[delivery_shipment_id_field_] = shipment_id_
                prior_deliveries_ = session_db_[delivery_collection_].find(prior_filter_)
                if prior_deliveries_.explain().get("executionStats", {}).get("nReturned") > 0 and \
                        delivery_waybill_no_field_ in prior_deliveries_ and \
                        prior_deliveries_[delivery_waybill_no_field_] is not None:
                    raise IssueError(f"shipment id was already issued in {delivery_collection_}")

                delivery_filter_ = {}
                delivery_filter_[delivery_shipment_id_field_] = shipment_id_
                deliveries_ = session_db_[delivery_collection_].find(delivery_filter_)
                line_count_ = deliveries_.explain().get("executionStats", {}).get("nReturned")
                if not deliveries_ or line_count_ == 0:
                    raise IssueError(f"no deliveries found with {delivery_shipment_id_field_}: {shipment_id_}")

                account_filter_ = {}
                account_filter_[account_no_field_] = shipment_[shipment_account_no_field_]
                account_ = session_db_[account_collection_].find_one(account_filter_)
                if not account_:
                    raise IssueError("account not found")

                deliverycustomerparty_websiteuri_ = account_["acc_web_address"] if "acc_web_address" in account_ else None
                deliverycustomerparty_id_ = account_["acc_tax_no"] if "acc_tax_no" in account_ else None
                deliverycustomerparty_idscheme_ = IDENTIFICATION_SCHEME_
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
                shipment_partyidentificationidscheme_ = IDENTIFICATION_SCHEME_
                shipment_partynamename_ = shipment_["shp_carrier_name"] if "shp_carrier_name" in shipment_ else None
                shipment_postaladdressid_ = account_["acc_ship_to_address_id"] if "acc_ship_to_address_id" in account_ else None
                shipment_streetname_ = account_["acc_ship_to_street"] if "acc_ship_to_street" in account_ else None
                shipment_buildingnumber_ = account_["acc_ship_to_building"] if "acc_ship_to_building" in account_ else None
                shipment_citysubdivisionname_ = account_["acc_ship_to_province"] if "acc_ship_to_province" in account_ else None
                shipment_cityname_ = account_["acc_ship_to_city"] if "acc_ship_to_city" in account_ else None
                shipment_postalzone_ = account_["acc_ship_to_postcode"] if "acc_ship_to_postcode" in account_ else None
                shipment_countryname_ = account_["acc_ship_to_country"] if "acc_ship_to_country" in account_ else None
                shipment_actualdespatchdate_ = datetime.now(pytz.timezone(TZ_)).strftime("%Y-%m-%d")
                shipment_actualdespatchtime_ = datetime.now(pytz.timezone(TZ_)).strftime("%H:%M:%S")
                customer_alias_ = account_["acc_alias"] if "acc_alias" in account_ else None
                zarf_ettn_ = str(uuid.uuid4())
                shp_date_ = shipment_["shp_date"] if "shp_date" in shipment_ else None
                issue_date_ = shp_date_.strftime("%Y-%m-%d")
                issue_time_ = shp_date_.strftime("%H:%M:%S")
                notes_ = ""

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

                request_xml_ = f'''\
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
                                                <tem:IDScheme>{deliverycustomerparty_idscheme_}</tem:IDScheme>
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
                                                <tem:PartyIdentificationIDScheme>{shipment_partyidentificationidscheme_}</tem:PartyIdentificationIDScheme>
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
                </soap:Envelope>'''

                request_xml_ = re.sub(r"\s+(?=<)", "", request_xml_).encode("utf8")
                print_("*** request_xml_", request_xml_)
                headers_ = {
                    "Content-Type": "application/soap+xml; charset=utf-8",
                    "SOAPAction": "IrsaliyeZarfGonderYapisal"
                }
                response_ = requests.post(EDOKSIS_URL_, data=request_xml_, headers=headers_, timeout=EDOKSIS_TIMEOUT_SECONDS_)
                print_("status", response_.status_code)
                root_ = ElementTree.fromstring(response_.content)

                for tag in root_.iter("{http://tempuri.org/}Sonuc"):
                    if not tag.text:
                        raise APIError("!!! missing sonuc tag")
                    if tag.text == "1":
                        for tag in root_.iter("{http://tempuri.org/}IRsaliyeNo"):
                            if not tag.text:
                                raise APIError("!!! missing irsaliyeno tag")
                            ewaybill_no_ = str(tag.text)
                            for tag in root_.iter("{http://tempuri.org/}IrsaliyeETTN"):
                                if not tag.text:
                                    raise APIError("!!! missing irsaliyeettn tag")
                                ewaybill_ettn_ = str(tag.text)
                    else:
                        for tag in root_.iter("{http://tempuri.org/}Mesaj"):
                            if not tag.text:
                                raise APIError("!!! missing mesaj tag")
                            raise APIError(tag.text)

                process_date_ = Misc().get_now_f()

                set_ = {}
                set_[shipment_ewaybill_no_field_] = ewaybill_no_
                set_[shipment_ewaybill_date_field_] = process_date_
                set_[shipment_ettn_field_] = ewaybill_ettn_
                set_[shipment_status_field_] = shipment_status_ok_value_

                session_db_[shipment_collection_].update_one(shipment_filter_, {"$set": set_})

                set_ = {}
                set_[delivery_waybill_no_field_] = ewaybill_no_
                set_[delivery_waybill_date_field_] = process_date_
                deliveries_ = session_db_[delivery_collection_].update_many(delivery_filter_, {"$set": set_})

                ewaybills_.append({"status": "OK", "shipment_id": shipment_id_, "msg": "OK", "ewaybill_no": ewaybill_no_, "ewaybill_ettn": ewaybill_ettn_})

            except IssueError as exc_:
                ewaybills_.append({"status": "Error", "shipment_id": shipment_id_, "msg": str(exc_), "ewaybill_no": None, "ewaybill_ettn": None})

            except pymongo.errors.PyMongoError as exc_:
                ewaybills_.append({"status": "Error", "shipment_id": shipment_id_, "msg": str(exc_), "ewaybill_no": None, "ewaybill_ettn": None})

        res_ = {"result": True, "ewaybills": ewaybills_}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.mimetype = "application/json"
        response_.status_code = 200
        session_.commit_transaction()
        session_client_.close()
        return response_

    except pymongo.errors.PyMongoError as exc_:
        session_.abort_transaction()
        Misc().exception_show_f(exc_)
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.mimetype = "application/json"
        response_.status_code = 500
        return response_

    except AuthError as exc_:
        session_.abort_transaction()
        Misc().exception_show_f(exc_)
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.mimetype = "application/json"
        response_.status_code = 401
        return response_

    except APIError as exc_:
        session_.abort_transaction()
        Misc().exception_show_f(exc_)
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.mimetype = "application/json"
        response_.status_code = 400
        return response_

    except Exception as exc_:
        session_.abort_transaction()
        Misc().exception_show_f(exc_)
        res_ = {"result": False, "msg": str(exc_)}
        response_ = make_response(json.dumps(res_, default=json_util.default, sort_keys=False))
        response_.mimetype = "application/json"
        response_.status_code = 500
        return response_


if __name__ == "__main__":
    print_ = partial(print, flush=True)
    app.run(host="0.0.0.0", port=80, debug=False)
