#!/bin/bash

#
# Technoplatz BI
#
# Copyright (C) 2019-2023 Technoplatz IT Solutions GmbH, Mustafa Mat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see https://www.gnu.org/licenses.
#
# If your software can interact with users remotely through a computer
# network, you should also make sure that it provides a way for users to
# get its source.  For example, if your program is a web application, its
# interface could display a "Source" link that leads users to an archive
# of the code.  There are many ways you could offer source, and different
# solutions will be better for different programs; see section 13 for the
# specific requirements.
#
# You should also get your employer (if you work as a programmer) or school,
# if any, to sign a "copyright disclaimer" for the program, if necessary.
# For more information on this, and how to apply and follow the GNU AGPL, see
# https://www.gnu.org/licenses.
# 

echo "COUNTRY_CODE=$COUNTRY_CODE"
echo "STATE_NAME=$STATE_NAME"
echo "CITY_NAME=$CITY_NAME"
echo "COMPANY_NAME=$COMPANY_NAME"
echo "DEPARTMENT_NAME=$DEPARTMENT_NAME"
echo "ADMIN_EMAIL=$ADMIN_EMAIL"
echo "MONGO_HOST=$MONGO_HOST"
echo "MONGO_REPLICA1_HOST=$MONGO_REPLICA1_HOST"
echo "MONGO_REPLICA2_HOST=$MONGO_REPLICA2_HOST"
echo "MONGO_SELF_SIGNED_CERTS=$MONGO_SELF_SIGNED_CERTS"
echo "MONGO_SECRETS_REPLACE=$MONGO_SECRETS_REPLACE"
echo "MONGO_TLS_CA_KEYFILE=$MONGO_TLS_CA_KEYFILE"
echo "MONGO_TLS_CERT_KEYFILE=$MONGO_TLS_CERT_KEYFILE"
echo "MONGO_TLS_CERT_KEY_PASSWORD=$MONGO_TLS_CERT_KEY_PASSWORD"

echo $(date '+%Y%m%d%H%M%S')

selfsigned=$MONGO_SELF_SIGNED_CERTS
selfsignedreplace=$MONGO_SECRETS_REPLACE
mongoca=$MONGO_TLS_CA_KEYFILE
mongocert=$MONGO_TLS_CERT_KEYFILE

if [[ ! $selfsigned = true ]]; then
    echo "Certificate generation skipped."
    echo "According to MONGO_SELF_SIGNED_CERTS is $selfsigned"
    exit 0
fi

cacontent=$(cat /cert/$mongoca)
certcontent=$(cat /cert/$mongocert)

if [[ ! $selfsignedreplace = true && -f /cert/$mongoca && -s /cert/$mongoca && -f /cert/$mongocert && -s /cert/$mongocert ]]; then
    if [[ "$cacontent" == *"-----BEGIN PRIVATE KEY-----"* && "$cacontent" == *"-----END CERTIFICATE-----"* && "$certcontent" == *"-----BEGIN PRIVATE KEY-----"* && "$certcontent" == *"-----END CERTIFICATE-----"* ]]; then
        echo "Certificate generation skipped."
        echo "As far as MONGO_SECRETS_REPLACE is $selfsignedreplace"
        exit 0
    fi
fi

echo "step 1: Creating a root certificate..."
openssl req -nodes -newkey rsa:4096 -out /cert/mongo_ca.crt -new -x509 -keyout /cert/mongo_ca.key -passout pass:$MONGO_TLS_CERT_KEY_PASSWORD -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST/emailAddress=$ADMIN_EMAIL"
cat /cert/mongo_ca.key /cert/mongo_ca.crt >/cert/$mongoca
echo "✔ step 1 completed sucessfully."
echo
echo "step 2: Generating certificate requests..."
openssl req -nodes -newkey rsa:4096 -sha256 -keyout /cert/$MONGO_HOST.key -out /cert/$MONGO_HOST.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST/emailAddress=$ADMIN_EMAIL"
openssl req -nodes -newkey rsa:4096 -sha256 -keyout /cert/$MONGO_REPLICA1_HOST.key -out /cert/$MONGO_REPLICA1_HOST.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_REPLICA1_HOST/emailAddress=$ADMIN_EMAIL"
openssl req -nodes -newkey rsa:4096 -sha256 -keyout /cert/$MONGO_REPLICA2_HOST.key -out /cert/$MONGO_REPLICA2_HOST.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_REPLICA2_HOST/emailAddress=$ADMIN_EMAIL"
echo "✔ step 2 completed sucessfully."
echo
echo "step 3: Signing node certificate requests with mongo_ca.key..."
openssl x509 -req -in /cert/$MONGO_HOST.csr -CA /cert/$mongoca -CAkey /cert/mongo_ca.key -passin pass:$MONGO_TLS_CERT_KEY_PASSWORD -set_serial 00 -out /cert/$MONGO_HOST.crt
openssl x509 -req -in /cert/$MONGO_REPLICA1_HOST.csr -CA /cert/$mongoca -CAkey /cert/mongo_ca.key -passin pass:$MONGO_TLS_CERT_KEY_PASSWORD -set_serial 00 -out /cert/$MONGO_REPLICA1_HOST.crt
openssl x509 -req -in /cert/$MONGO_REPLICA2_HOST.csr -CA /cert/$mongoca -CAkey /cert/mongo_ca.key -passin pass:$MONGO_TLS_CERT_KEY_PASSWORD -set_serial 00 -out /cert/$MONGO_REPLICA2_HOST.crt
echo "✔ step 3 completed sucessfully."
echo
echo "step 4: Combining key and crt as pem..."
cat /cert/$MONGO_HOST.key /cert/$MONGO_HOST.crt >/cert/$mongocert
cat /cert/$MONGO_REPLICA1_HOST.key /cert/$MONGO_REPLICA1_HOST.crt >/cert/$MONGO_REPLICA1_HOST.pem
cat /cert/$MONGO_REPLICA2_HOST.key /cert/$MONGO_REPLICA2_HOST.crt >/cert/$MONGO_REPLICA2_HOST.pem
echo "✔ step 4 completed sucessfully."
echo
echo "step 5: Cleaning..."
rm -rf /cert/*.key
rm -rf /cert/*.csr
rm -rf /cert/*.crt
echo "✔ step 5 completed sucessfully."
echo "✔ all steps OK."
echo
