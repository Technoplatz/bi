#! /bin/bash
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
echo "MONGO_KEEP_EXISTING_CERTS=$MONGO_KEEP_EXISTING_CERTS"

cacontent=$(cat /init/mongo_ca.pem)
certcontent=$(cat /init/$MONGO_HOST.pem)
keepcerts=$MONGO_KEEP_EXISTING_CERTS

if [[ $keepcerts = true && -f /init/mongo_ca.pem && -s /init/mongo_ca.pem && -f /init/$MONGO_HOST.pem && -s /init/$MONGO_HOST.pem ]]; then
    if [[ "$cacontent" == *"-----BEGIN PRIVATE KEY-----"* && "$cacontent" == *"-----END CERTIFICATE-----"* && "$certcontent" == *"-----BEGIN PRIVATE KEY-----"* && "$certcontent" == *"-----END CERTIFICATE-----"* ]]; then
        echo "Certificate generation was skipped."
        echo "According to MONGO_KEEP_EXISTING_CERTS is $keepcerts"
        exit 0
    fi
fi

INC=0
DBPWD=""

if [[ ! -f /init/.tls-key-password ]]; then
    touch /init/.tls-key-password
    re='^[a-zA-Z]+$'
    while ! [[ ${DBPWD:0:1} =~ $re ]]; do
        DBPWD=$(openssl rand -hex 12)
        let "INC+=1"
    done
    echo $DBPWD >/init/.tls-key-password
fi

echo "step 1: Create a root certificate"
openssl req -nodes -newkey rsa:4096 -out /init/mongo_ca.crt -new -x509 -keyout /init/mongo_ca.key -passout pass:$DBPWD -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST/emailAddress=$ADMIN_EMAIL"
cat /init/mongo_ca.key /init/mongo_ca.crt >/init/mongo_ca.pem
echo "step 1 is ok"
echo
echo "step 2: Generate certificate requests and private keys"
openssl req -nodes -newkey rsa:4096 -sha256 -keyout /init/$MONGO_HOST.key -out /init/$MONGO_HOST.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_HOST/emailAddress=$ADMIN_EMAIL"
openssl req -nodes -newkey rsa:4096 -sha256 -keyout /init/$MONGO_REPLICA1_HOST.key -out /init/$MONGO_REPLICA1_HOST.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_REPLICA1_HOST/emailAddress=$ADMIN_EMAIL"
openssl req -nodes -newkey rsa:4096 -sha256 -keyout /init/$MONGO_REPLICA2_HOST.key -out /init/$MONGO_REPLICA2_HOST.csr -subj "/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME/CN=$MONGO_REPLICA2_HOST/emailAddress=$ADMIN_EMAIL"
echo "step 2 is ok"
echo
echo "step 3: Sign the certificate requests with mongo_ca.key"
openssl x509 -req -in /init/$MONGO_HOST.csr -CA /init/mongo_ca.pem -CAkey /init/mongo_ca.key -passin pass:$DBPWD -set_serial 00 -out /init/$MONGO_HOST.crt
openssl x509 -req -in /init/$MONGO_REPLICA1_HOST.csr -CA /init/mongo_ca.pem -CAkey /init/mongo_ca.key -passin pass:$DBPWD -set_serial 00 -out /init/$MONGO_REPLICA1_HOST.crt
openssl x509 -req -in /init/$MONGO_REPLICA2_HOST.csr -CA /init/mongo_ca.pem -CAkey /init/mongo_ca.key -passin pass:$DBPWD -set_serial 00 -out /init/$MONGO_REPLICA2_HOST.crt
echo "step 3 is ok"
echo
echo "step 4: Concat each Node Certificate with its key"
cat /init/$MONGO_HOST.key /init/$MONGO_HOST.crt >/init/$MONGO_HOST.pem
cat /init/$MONGO_REPLICA1_HOST.key /init/$MONGO_REPLICA1_HOST.crt >/init/$MONGO_REPLICA1_HOST.pem
cat /init/$MONGO_REPLICA2_HOST.key /init/$MONGO_REPLICA2_HOST.crt >/init/$MONGO_REPLICA2_HOST.pem
echo "step 4 is ok"
echo
echo $(date '+%Y%m%d%H%M%S')
echo "all steps are ok"
echo
