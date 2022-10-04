#!/usr/bin/env bash
# Mustafa Mat @Technoplatz 2019-2023
openssl rand -base64 756 > /init/replicaset.key
chmod 400 /init/replicaset.key