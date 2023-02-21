#!/usr/bin/env bash
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

echo "DB REPLICASET STARTED"
sleep 10s

if [ ! -f /init/mongo-init.flag ]; then
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT/?authSource=$MONGO_AUTH_DB" --quiet --eval "
        rs_ = {
            _id: '${MONGO_REPLICASET}',
            version: 1,
            members: [
                { _id: 0, host: '${MONGO_HOST}:${MONGO_PORT}', priority: 2 },
                { _id: 1, host: '${MONGO_REPLICA1_HOST}:${MONGO_PORT}', priority: 0 },
                { _id: 2, host: '${MONGO_REPLICA2_HOST}:${MONGO_PORT}', priority: 0 }
            ]
        }
        rs.initiate(rs_, { force: true });
    "
    echo "Replicaset was initiated successfully."
else
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT/?authSource=$MONGO_AUTH_DB" --quiet --eval "
        rs_ = {
            _id: '${MONGO_REPLICASET}',
            version: 1,
            members: [
                { _id: 0, host: '${MONGO_HOST}:${MONGO_PORT}', priority: 2 },
                { _id: 1, host: '${MONGO_REPLICA1_HOST}:${MONGO_PORT}', priority: 0 },
                { _id: 2, host: '${MONGO_REPLICA2_HOST}:${MONGO_PORT}', priority: 0 }
            ]
        }
        rs.reconfig(rs_, { force: true });
    "
    echo "Replicaset was reconfigured successfully."
fi
sleep 10s

RS_OK=""
until [[ $RS_OK -eq "1" ]]; do
    echo "Checking replicaset status..."
    RS_STATUS=$(mongosh "mongodb://$MONGO_HOST:$MONGO_PORT/?authSource=$MONGO_AUTH_DB" --quiet --eval "
        JSON.stringify(rs.status());
    ")
    sleep 2s
    RS_OK=$(echo "$RS_STATUS" | jq '.ok' -r)
    echo "RS_OK: $RS_OK"
done

MONGO_PASSWORD=$(</run/secrets/mongo-password)

# CHECK WHETHER DB EXISTS OR NOT
MONGO_INDEXOF_DB=$(mongosh "mongodb://$MONGO_HOST:$MONGO_PORT/?authSource=$MONGO_AUTH_DB" --quiet --eval "
    db.getMongo().getDBNames().indexOf('${MONGO_DB}');
")
echo "MONGO_INDEXOF_DB $MONGO_INDEXOF_DB"

if [ $MONGO_INDEXOF_DB -eq "-1" ]; then
    echo "DB does not exist."
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT,$MONGO_REPLICA1_HOST:$MONGO_PORT,$MONGO_REPLICA2_HOST:$MONGO_PORT/?replicaSet=$MONGO_REPLICASET&authSource=$MONGO_AUTH_DB" --quiet --eval "
        print('DB user creating...');
        db = db.getSiblingDB('${MONGO_AUTH_DB}');
        db.createUser({ user: '${MONGO_USERNAME}', pwd: '${MONGO_PASSWORD}', roles: [{ role: 'root', db: '${MONGO_AUTH_DB}' },{ role: 'dbOwner', db: '${MONGO_DB}' }] });
        print('DB user created.');
    "
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT,$MONGO_REPLICA1_HOST:$MONGO_PORT,$MONGO_REPLICA2_HOST:$MONGO_PORT/?replicaSet=$MONGO_REPLICASET&authSource=$MONGO_AUTH_DB" --quiet --eval "
        print('db connected.');
        print('update started.');
        db = db.getSiblingDB('${MONGO_DB}');
        // SAAS
        db.getCollection('_saas').drop();
        db.createCollection('_saas', { 'capped': false });
        db.getCollection('_saas').updateOne({ sas_id: 'saas' }, { \$set: {
            sas_id: 'saas',
            sas_user_id: '${ADMIN_EMAIL}',
            sas_user_name: '${ADMIN_USER_NAME}',
            sas_company_name: '${COMPANY_NAME}',
            _created_at: new Date(),
            _created_by: '${ADMIN_EMAIL}'
        }}, { upsert: true });
        db.getCollection('_saas').createIndex({ 'sas_id': 1 }, { unique: true });
        db.getCollection('_saas').createIndex({ 'sas_id': 1, 'sas_user_id': 1 }, { unique: true });
        // AUTH
        var u1 = Math.random().toString(36).slice(2);
        var u2 = Math.random().toString(36).slice(2);
        var u3 = Math.random().toString(36).slice(2);
        var apikey_ = (u1 + u2 + u3).slice(1);
        db.getCollection('_auth').drop();
        db.createCollection('_auth', { 'capped': false });
        db.getCollection('_auth').insertOne({
            aut_id: '${ADMIN_EMAIL}',
            aut_password: '\$2b\$08\$aSMAfk/MMV736M/jG3zHHeoMndfQURKfMBV02qOJ/K4Z/AOQuR8Vm',
            aut_token: null,
            aut_tfac: null,
            aut_expires: 0,
            aut_root: true,
            aut_apikey: apikey_,
            aut_otp_validated: false,
            aut_otp_secret: null,
            _created_at: new Date(),
            _created_by: '${ADMIN_EMAIL}',
            _modified_at: new Date(),
            _modified_by: '${ADMIN_EMAIL}',
            _modified_count: 0,
            _apikey_modified_at: new Date(),
            _apikey_modified_by: '${ADMIN_EMAIL}'
        });
        db.getCollection('_auth').createIndex({ 'aut_id': 1 }, { unique: true });
        print('_auth created.');
        // USER
        db.getCollection('_user').drop();
        db.createCollection('_user', { 'capped': false });
        db.getCollection('_user').insertOne({
            usr_id: '${ADMIN_EMAIL}',
            usr_name: '${ADMIN_USER_NAME}',
            usr_scope: 'Administrator',
            usr_enabled: true,
            usr_group_id: 'Managers',
            _tags: ['#Managers','#Administrators'],
            _created_at: new Date(),
            _created_by: '${ADMIN_EMAIL}',
            _modified_at: new Date(),
            _modified_by: '${ADMIN_EMAIL}',
            _modified_count: 0
        });
        db.getCollection('_user').createIndex({ 'usr_id': 1 }, { unique: true });
        print('_user created.');
        // FIREWALL
        db.getCollection('_firewall').drop();
        db.createCollection('_firewall', { 'capped': false });
        db.getCollection('_firewall').insertOne({
            fwa_rule_id: 'manager-allow',
            fwa_user_id: '${ADMIN_EMAIL}',
            fwa_ip: '0.0.0.0',
            fwa_enabled: true,
            _created_at: new Date(),
            _created_by: '${ADMIN_EMAIL}',
            _modified_at: new Date(),
            _modified_by: '${ADMIN_EMAIL}',
            _modified_count: 0
        });
        db.getCollection('_firewall').createIndex({ 'fwa_rule_id': 1, 'fwa_ip': 1, 'fwa_enabled':1 });
        db.getCollection('_firewall').createIndex({ 'fwa_rule_id': 1, 'fwa_user_id': 1 }, { unique: true });
        db.getCollection('_firewall').createIndex({ 'fwa_user_id': 1, 'fwa_ip': 1 }, { unique: true });
        print('_firewall created.');
        print('update completed.');
    "
    sh -c "echo 'replicaset initialized successfully' > /init/mongo-init.flag"
    echo "replicaset initialized successfully :)"
else
    echo "DB already exists."
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT,$MONGO_REPLICA1_HOST:$MONGO_PORT,$MONGO_REPLICA2_HOST:$MONGO_PORT/?replicaSet=$MONGO_REPLICASET&authSource=$MONGO_AUTH_DB" --quiet --eval "
        print('db user credentials updating...');
        db = db.getSiblingDB('${MONGO_AUTH_DB}');
        db.changeUserPassword('${MONGO_USERNAME}','${MONGO_PASSWORD}');
        print('db user credentials updated.');
        db = db.getSiblingDB('${MONGO_DB}');
        var saas_ = db.getCollection('_saas').findOne({ sas_id: 'saas' });
        var sas_user_id_ = saas_.sas_user_id;
        if(sas_user_id_ !== '${ADMIN_EMAIL}') {
            var u1 = Math.random().toString(36).slice(2);
            var u2 = Math.random().toString(36).slice(2);
            var u3 = Math.random().toString(36).slice(2);
            var apikey_ = (u1 + u2 + u3).slice(1);
            var upsert_auth_ = db.getCollection('_auth').updateOne({ aut_id: '${ADMIN_EMAIL}' }, { \$set: {
                aut_id: '${ADMIN_EMAIL}',
                aut_password: '\$2b\$08\$aSMAfk/MMV736M/jG3zHHeoMndfQURKfMBV02qOJ/K4Z/AOQuR8Vm',
                aut_token: null,
                aut_tfac: null,
                aut_expires: 0,
                aut_root: true,
                aut_apikey: apikey_,
                aut_otp_validated: false,
                aut_otp_secret: null,
                _created_at: new Date(),
                _created_by: 'saas',
                _modified_at: new Date(),
                _modified_by: 'saas',
                _modified_count: 0,
                _apikey_modified_at: new Date(),
                _apikey_modified_by: 'saas'
            }}, { upsert: true });
            if(upsert_auth_) {
                print('auth upserted', '${ADMIN_EMAIL}');
            }
            var upsert_user_ = db.getCollection('_user').updateOne({ usr_id: '${ADMIN_EMAIL}' }, { \$set: {
                usr_id: '${ADMIN_EMAIL}',
                usr_name: '${ADMIN_USER_NAME}',
                usr_scope: 'Administrator',
                usr_enabled: true,
                usr_group_id: 'Managers',
                _tags: ['#Managers','#Administrators'],
                _created_at: new Date(),
                _created_by: 'saas',
                _modified_at: new Date(),
                _modified_by: 'saas',
                _modified_count: 0
            }}, { upsert: true });
            if(upsert_user_) {
                print('user upserted', '${ADMIN_EMAIL}');
            }
            var upsert_firewall_ = db.getCollection('_firewall').updateOne({ fwa_rule_id: 'manager-allow' }, { \$set: {
                fwa_rule_id: 'manager-allow',
                fwa_user_id: '${ADMIN_EMAIL}',
                fwa_ip: '0.0.0.0',
                fwa_enabled: true,
                _created_at: new Date(),
                _created_by: 'saas',
                _modified_at: new Date(),
                _modified_by: 'saas',
                _modified_count: 0
            }}, { upsert: true });
            if(upsert_firewall_) {
                print('firewall added', '${ADMIN_EMAIL}');
            }
            db.getCollection('_saas').updateOne({ sas_id: 'saas-ex' }, { \$set: {
                sas_id: 'saas-ex',
                sas_user_id: saas_.sas_user_id,
                sas_user_name: saas_.sas_user_name,
                sas_company_name: saas_.sas_company_name,
                _created_at: new Date(),
                _created_by: 'saas',
                _updated_at: new Date(),
                _updated_by: 'saas'
            }}, { upsert: true });
            db.getCollection('_saas').updateOne({ sas_id: 'saas' }, { \$set: {
                sas_id: 'saas',
                sas_user_id: '${ADMIN_EMAIL}',
                sas_user_name: '${ADMIN_USER_NAME}',
                sas_company_name: '${COMPANY_NAME}',
                _updated_at: new Date(),
                _updated_by: '${ADMIN_EMAIL}'
            }}, { upsert: true });
        }
    "
    sh -c "echo 'init completed successfully' > /init/mongo-init.flag"
    echo "init completed successfully :)"
fi
echo "DB REPLICASET ENDED"