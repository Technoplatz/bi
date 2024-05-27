#!/bin/bash

#
# Technoplatz BI
#
# Copyright ©Technoplatz IT Solutions GmbH, Mustafa Mat
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

apitempfilepath=$API_TEMPFILE_PATH
selfsigned=$MONGO_SELF_SIGNED_CERTS
selfsignedreplace=$MONGO_CERTS_REPLACE

echo "step-0: Initiating $apitempfilepath..."
mkdir -p $apitempfilepath
rm -rf $apitempfilepath/*
echo "$apitempfilepath was initiated sucessfully."

if [[ ! $selfsigned = true ]]; then
    echo "Certificate generation was skipped."
    exit 0
fi

cacontent=$(cat $MONGO_TLS_CA_KEYFILE)

if [[ ! $selfsignedreplace = true && -f $MONGO_TLS_CA_KEYFILE && -s $MONGO_TLS_CA_KEYFILE && -f $MONGO_TLS_CERT_KEYFILE && -s $MONGO_TLS_CERT_KEYFILE ]]; then
    if [[ "$cacontent" == *"-----BEGIN PRIVATE KEY-----"* && "$cacontent" == *"-----END CERTIFICATE-----"* && "$certcontent" == *"-----BEGIN PRIVATE KEY-----"* && "$certcontent" == *"-----END CERTIFICATE-----"* ]]; then
        echo "Certificate generation skipped."
        echo "MONGO_CERTS_REPLACE is $selfsignedreplace"
        exit 0
    fi
fi

echo "Step-1: Generating $MONGO_TLS_CA_KEYFILE..."
openssl req -nodes -newkey rsa:4096 -out mongo-ca.crt -new -x509 -keyout mongo-ca.key -passout pass:$MONGO_TLS_CERT_KEYFILE_PASSWORD -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST0/emailAddress=$ADMIN_EMAIL"
cat mongo-ca.key mongo-ca.crt > $MONGO_TLS_CA_KEYFILE
echo "✔ $MONGO_TLS_CA_KEYFILE generated sucessfully."
echo

echo "Step-2: Generating $MONGO_TLS_CERT_KEYFILE..."
openssl req -nodes -newkey rsa:4096 -sha256 -keyout $MONGO_HOST0.key -out $MONGO_HOST0.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST0/emailAddress=$ADMIN_EMAIL"
openssl x509 -req -in $MONGO_HOST0.csr -CA $MONGO_TLS_CA_KEYFILE -CAkey mongo-ca.key -passin pass:$MONGO_TLS_CERT_KEYFILE_PASSWORD -set_serial 00 -out $MONGO_HOST0.crt
cat $MONGO_HOST0.key $MONGO_HOST0.crt > $MONGO_TLS_CERT_KEYFILE
rm -rf *.key *.csr *.crt
echo "✔ $MONGO_TLS_CERT_KEYFILE generated sucessfully."
echo

echo "✔ Initialization OK."
echo
