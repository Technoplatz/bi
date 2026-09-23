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

MongoDB client factory built from the configuration.
"""

import pymongo

from bi import config as cfg


class Mongo:
    """
    docstring is in progress
    """

    def __init__(self):
        """
        docstring is in progress
        """
        self.mongo_appname_ = "api"
        self.mongo_readpref_ = cfg.MONGO_READPREF_
        auth_source_ = f"authSource={cfg.MONGO_AUTH_DB_}" if cfg.MONGO_AUTH_DB_ else ""
        replicaset_ = (
            f"&replicaSet={cfg.MONGO_RS_}" if cfg.MONGO_RS_ and cfg.MONGO_RS_ is not None else ""
        )
        read_preference_primary_ = (
            f"&readPreference={self.mongo_readpref_}"
            if self.mongo_readpref_
            else ""
        )
        appname_ = f"&appname={self.mongo_appname_}" if self.mongo_appname_ else ""
        tls_ = "&tls=true" if cfg.MONGO_TLS_ else "&tls=false"
        tls_certificate_key_file_ = (
            f"&tlsCertificateKeyFile={cfg.MONGO_TLS_CERT_KEYFILE_}"
            if cfg.MONGO_TLS_CERT_KEYFILE_
            else ""
        )
        tls_certificate_key_file_password_ = (
            f"&tlsCertificateKeyFilePassword={cfg.MONGO_TLS_CERT_KEYFILE_PASSWORD_}"
            if cfg.MONGO_TLS_CERT_KEYFILE_PASSWORD_
            else ""
        )
        tls_ca_file_ = (
            f"&tlsCAFile={cfg.MONGO_TLS_CA_KEYFILE_}" if cfg.MONGO_TLS_CA_KEYFILE_ else ""
        )
        tls_allow_invalid_certificates_ = "&tlsAllowInvalidCertificates=true" if cfg.MONGO_TLS_ALLOW_INVALID_CERTIFICATES_ else ""
        retry_writes_ = (
            "&retryWrites=true" if cfg.MONGO_RETRY_WRITES_ else "&retryWrites=false"
        )
        tz_aware_ = "&tz_aware=true"
        timeout_ms_ = f"&timeoutMS={cfg.MONGO_TIMEOUT_MS_}"
        self.connstr = f"mongodb://{cfg.MONGO_USERNAME_}:{cfg.MONGO_PASSWORD_}@{cfg.MONGO_HOST0_}:{cfg.MONGO_PORT0_},{cfg.MONGO_HOST1_}:{cfg.MONGO_PORT1_},{cfg.MONGO_HOST2_}:{cfg.MONGO_PORT2_}/?{auth_source_}{replicaset_}{read_preference_primary_}{appname_}{tls_}{tls_certificate_key_file_}{tls_certificate_key_file_password_}{tls_ca_file_}{tls_allow_invalid_certificates_}{retry_writes_}{timeout_ms_}{tz_aware_}"
        self.client_ = pymongo.MongoClient(self.connstr)
        self.db_ = self.client_[cfg.MONGO_DB_]
