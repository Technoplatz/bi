#!/usr/bin/env bash
# 
# Mustafa Mat @Technoplatz 2019-2023
# 
# Technoplatz BI
# 
# Copyright (C) 2020-2023 Technoplatz IT Solutions GmbH, Mustafa Mat
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
MONGO_PASSWORD=$(</run/secrets/mongo-password)
if [ ! -f /init/mongo-init.flag ]; then
    echo "replicaset will be initialized within 10 seconds"
    sleep 10s
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
    echo "replicaset was initiated successfully"
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT,$MONGO_REPLICA1_HOST:$MONGO_PORT,$MONGO_REPLICA2_HOST:$MONGO_PORT/?replicaSet=$MONGO_REPLICASET&authSource=$MONGO_AUTH_DB" --quiet --eval "
        print('db user creating...');
        db = db.getSiblingDB('${MONGO_AUTH_DB}');
        db.createUser({ user: '${MONGO_USERNAME}', pwd: '${MONGO_PASSWORD}', roles: [{ role: 'root', db: '${MONGO_AUTH_DB}' },{ role: 'dbOwner', db: '${MONGO_DB}' }] });
        print('db user created');
    "
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT,$MONGO_REPLICA1_HOST:$MONGO_PORT,$MONGO_REPLICA2_HOST:$MONGO_PORT/?replicaSet=$MONGO_REPLICASET&authSource=$MONGO_AUTH_DB" --quiet --eval "
        print('db connected');
        print('update started');
        db = db.getSiblingDB('${MONGO_DB}');
        // SAAS
        db.getCollection('_saas').drop();
        db.createCollection('_saas', { 'capped': false });
        db.getCollection('_saas').updateOne({ sas_id: 'saas' }, { \$set: {
            sas_id: 'saas',
            sas_user_id: '${USER_EMAIL}',
            sas_user_name: '${USER_NAME}',
            sas_company_name: '${COMPANY_NAME}',
            _created_at: new Date(),
            _created_by: '${USER_EMAIL}'
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
            aut_id: '${USER_EMAIL}',
            aut_password: '\$2b\$08\$aSMAfk/MMV736M/jG3zHHeoMndfQURKfMBV02qOJ/K4Z/AOQuR8Vm',
            aut_token: null,
            aut_tfac: null,
            aut_expires: 0,
            aut_root: true,
            aut_apikey: apikey_,
            aut_otp_validated: false,
            aut_otp_secret: null,
            _created_at: new Date(),
            _created_by: '${USER_EMAIL}',
            _modified_at: new Date(),
            _modified_by: '${USER_EMAIL}',
            _modified_count: 0,
            _apikey_modified_at: new Date(),
            _apikey_modified_by: '${USER_EMAIL}'
        });
        db.getCollection('_auth').createIndex({ 'aut_id': 1 }, { unique: true });
        print('_auth created');
        // USER
        db.getCollection('_user').drop();
        db.createCollection('_user', { 'capped': false });
        db.getCollection('_user').insertOne({
            usr_id: '${USER_EMAIL}',
            usr_name: '${USER_NAME}',
            usr_enabled: true,
            usr_group_id: 'Managers',
            _tags: ['#Managers','#Administrators'],
            _created_at: new Date(),
            _created_by: '${USER_EMAIL}',
            _modified_at: new Date(),
            _modified_by: '${USER_EMAIL}',
            _modified_count: 0
        });
        db.getCollection('_user').createIndex({ 'usr_id': 1 }, { unique: true });
        print('_user created');
        // FIREWALL
        db.getCollection('_firewall').drop();
        db.createCollection('_firewall', { 'capped': false });
        db.getCollection('_firewall').insertOne({
            fwa_rule_id: 'manager-allow',
            fwa_user_id: '${USER_EMAIL}',
            fwa_ip: '0.0.0.0',
            fwa_enabled: true,
            _created_at: new Date(),
            _created_by: '${USER_EMAIL}',
            _modified_at: new Date(),
            _modified_by: '${USER_EMAIL}',
            _modified_count: 0
        });
        db.getCollection('_firewall').createIndex({ 'fwa_rule_id': 1, 'fwa_ip': 1, 'fwa_enabled':1 });
        db.getCollection('_firewall').createIndex({ 'fwa_rule_id': 1, 'fwa_user_id': 1 }, { unique: true });
        db.getCollection('_firewall').createIndex({ 'fwa_user_id': 1, 'fwa_ip': 1 }, { unique: true });
        print('_firewall created');
        print('update completed');
    "
    sh -c "echo 'replicaset initialized successfully' > /init/mongo-init.flag"
    echo "replicaset initialized successfully :)"
else
    echo "reconfiguration will be started in 10 seconds..."
    sleep 10s
    echo "primary node connecting..."
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
    echo "replicaset reconfigured successfully"
    mongosh "mongodb://$MONGO_HOST:$MONGO_PORT,$MONGO_REPLICA1_HOST:$MONGO_PORT,$MONGO_REPLICA2_HOST:$MONGO_PORT/?replicaSet=$MONGO_REPLICASET&authSource=$MONGO_AUTH_DB" --quiet --eval "
        print('db user credentials updating...');
        db = db.getSiblingDB('${MONGO_AUTH_DB}');
        db.changeUserPassword('${MONGO_USERNAME}','${MONGO_PASSWORD}');
        print('db user credentials updated');
        db = db.getSiblingDB('${MONGO_DB}');
        var saas_ = db.getCollection('_saas').findOne({ sas_id: 'saas' });
        var sas_user_id_ = saas_.sas_user_id;
        if(sas_user_id_ !== '${USER_EMAIL}') {
            var u1 = Math.random().toString(36).slice(2);
            var u2 = Math.random().toString(36).slice(2);
            var u3 = Math.random().toString(36).slice(2);
            var apikey_ = (u1 + u2 + u3).slice(1);
            var upsert_auth_ = db.getCollection('_auth').updateOne({ aut_id: '${USER_EMAIL}' }, { \$set: {
                aut_id: '${USER_EMAIL}',
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
                print('auth upserted', '${USER_EMAIL}');
            }
            var upsert_user_ = db.getCollection('_user').updateOne({ usr_id: '${USER_EMAIL}' }, { \$set: {
                usr_id: '${USER_EMAIL}',
                usr_name: '${USER_NAME}',
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
                print('user upserted', '${USER_EMAIL}');
            }
            var upsert_firewall_ = db.getCollection('_firewall').updateOne({ fwa_rule_id: 'manager-changed-allow' }, { \$set: {
                fwa_rule_id: 'manager-changed-allow',
                fwa_user_id: '${USER_EMAIL}',
                fwa_ip: '0.0.0.0',
                fwa_enabled: true,
                _created_at: new Date(),
                _created_by: 'saas',
                _modified_at: new Date(),
                _modified_by: 'saas',
                _modified_count: 0
            }}, { upsert: true });
            if(upsert_firewall_) {
                print('firewall added', '${USER_EMAIL}');
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
                sas_user_id: '${USER_EMAIL}',
                sas_user_name: '${USER_NAME}',
                sas_company_name: '${COMPANY_NAME}',
                _updated_at: new Date(),
                _updated_by: '${USER_EMAIL}'
            }}, { upsert: true });
        }
    "
    sh -c "echo 'init completed successfully' > /init/mongo-init.flag"
    echo "init completed successfully :)"
fi
echo "DB REPLICASET ENDED"