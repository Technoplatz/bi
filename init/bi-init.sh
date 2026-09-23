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

certdir=$(dirname $MONGO_TLS_CA_KEYFILE)
marker=$certdir/.san-certificates
subj="/C=$COUNTRY_CODE/ST=$STATE_NAME/L=$CITY_NAME/O=$COMPANY_NAME/OU=$DEPARTMENT_NAME"
complete=true
for f in $MONGO_TLS_CA_KEYFILE $certdir/$MONGO_HOST0.pem $certdir/$MONGO_HOST1.pem $certdir/$MONGO_HOST2.pem $certdir/client.pem $marker; do
    [[ -s $f ]] || complete=false
done
if [[ ! $selfsignedreplace = true && $complete = true ]]; then
    echo "Certificate generation skipped, the member and client certificates exist."
    echo "MONGO_CERTS_REPLACE is $selfsignedreplace"
    exit 0
fi
echo "Step-1: Generating $MONGO_TLS_CA_KEYFILE..."
openssl req -nodes -newkey rsa:4096 -out mongo-ca.crt -new -x509 -days 3650 -keyout mongo-ca.key -passout pass:$MONGO_TLS_CERT_KEYFILE_PASSWORD -subj "$subj/CN=technoplatz-bi-mongo-ca/emailAddress=$ADMIN_EMAIL"
cat mongo-ca.key mongo-ca.crt > $MONGO_TLS_CA_KEYFILE
echo "✔ $MONGO_TLS_CA_KEYFILE generated sucessfully."
echo
# every member gets its own certificate whose subject alternative names cover its host name inside the
# docker network and the loopback address used from the host, so peers and clients can verify the host
# they talk to and tlsAllowInvalidCertificates is no longer needed
serial=1
for host in $MONGO_HOST0 $MONGO_HOST1 $MONGO_HOST2; do
    echo "Step-2: Generating $certdir/$host.pem..."
    printf "subjectAltName=DNS:%s,DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth,clientAuth\n" "$host" > $host.ext
    openssl req -nodes -newkey rsa:4096 -sha256 -keyout $host.key -out $host.csr -subj "$subj/CN=$host/emailAddress=$ADMIN_EMAIL"
    openssl x509 -req -in $host.csr -CA $MONGO_TLS_CA_KEYFILE -CAkey mongo-ca.key -passin pass:$MONGO_TLS_CERT_KEYFILE_PASSWORD -set_serial $serial -days 3650 -extfile $host.ext -out $host.crt
    cat $host.key $host.crt > $certdir/$host.pem
    serial=$((serial + 1))
    echo "✔ $certdir/$host.pem generated sucessfully."
done
echo "Step-3: Generating $certdir/client.pem..."
printf "extendedKeyUsage=clientAuth\n" > client.ext
openssl req -nodes -newkey rsa:4096 -sha256 -keyout client.key -out client.csr -subj "$subj/CN=technoplatz-bi-client/emailAddress=$ADMIN_EMAIL"
openssl x509 -req -in client.csr -CA $MONGO_TLS_CA_KEYFILE -CAkey mongo-ca.key -passin pass:$MONGO_TLS_CERT_KEYFILE_PASSWORD -set_serial $serial -days 3650 -extfile client.ext -out client.crt
cat client.key client.crt > $certdir/client.pem
rm -rf *.key *.csr *.crt *.ext
date '+%Y%m%d%H%M%S' > $marker
echo "✔ $certdir/client.pem generated sucessfully."
echo
echo "✔ Initialization OK."
echo
