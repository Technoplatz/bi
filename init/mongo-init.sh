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

echo $(date '+%Y%m%d%H%M%S')

selfsigned=$MONGO_SELF_SIGNED_CERTS
selfsignedreplace=$MONGO_CERTS_REPLACE
mongotlscertkeyfilepassword=$(</run/secrets/mongo_tls_keyfile_password)

if [[ ! $selfsigned = true ]]; then
    echo "Certificate generation skipped."
    echo "Parameter MONGO_SELF_SIGNED_CERTS is $selfsigned"
    exit 0
fi

cacontent=$(cat $MONGO_TLS_CA_KEYFILE)

if [[ ! $selfsignedreplace = true && -f $MONGO_TLS_CA_KEYFILE && -s $MONGO_TLS_CA_KEYFILE && -f $MONGO_TLS_CERT_KEYFILE && -s $MONGO_TLS_CERT_KEYFILE ]]; then
    if [[ "$cacontent" == *"-----BEGIN PRIVATE KEY-----"* && "$cacontent" == *"-----END CERTIFICATE-----"* && "$certcontent" == *"-----BEGIN PRIVATE KEY-----"* && "$certcontent" == *"-----END CERTIFICATE-----"* ]]; then
        echo "Certificate generation skipped."
        echo "As far as MONGO_CERTS_REPLACE is $selfsignedreplace"
        exit 0
    fi
fi

echo "step 1: Generating mongo-ca.crt and mongo-ca.key to build mongo-ca.pem to sign client certificates..."
openssl req -nodes -newkey rsa:4096 -out mongo-ca.crt -new -x509 -keyout mongo-ca.key -passout pass:$mongotlscertkeyfilepassword -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST0/emailAddress=$ADMIN_EMAIL"
cat mongo-ca.key mongo-ca.crt >$MONGO_TLS_CA_KEYFILE
echo "✔ mongo-ca.key generated sucessfully."
echo

echo "step 2: Generating mongo0.csr and mongo0.key together as a client certificate request..."
openssl req -nodes -newkey rsa:4096 -sha256 -keyout $MONGO_HOST0.key -out $MONGO_HOST0.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST0/emailAddress=$ADMIN_EMAIL"
echo "✔ mongo0.csr generated sucessfully."
echo

echo "step 3: Signing the mongo0.csr with mongo-ca.key to create mongo0.crt..."
openssl x509 -req -in $MONGO_HOST0.csr -CA $MONGO_TLS_CA_KEYFILE -CAkey mongo-ca.key -passin pass:$mongotlscertkeyfilepassword -set_serial 00 -out $MONGO_HOST0.crt
echo "✔ mongo0.crt generated sucessfully."
echo

echo "step 4: Combining key and crt as pem..."
cat $MONGO_HOST0.key $MONGO_HOST0.crt >$MONGO_TLS_CERT_KEYFILE
echo "✔ mongo-ca.pem and mongo0.pem generated sucessfully."
echo

echo "step 5: Cleaning key's csr's and crt's..."
rm -rf *.key
rm -rf *.csr
rm -rf *.crt
echo "✔ step 5 completed sucessfully."
echo "✔ all steps OK."
echo
