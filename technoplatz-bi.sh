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

cat << EOF

Technoplatz BI - Open Source Data Sharing Platform
Copyright 2019-$(date +'%Y'), Technoplatz IT Solutions GmbH
https://bi.technoplatz.com
----------------------------
EOF

function listAllCommands() {
    echo "Available commands: install,start,restart,stop"
    echo "See more at https://bi.technoplatz.com/support#script-commands-reference"
}

function installBI() {
    declare -a curlHeaders=("-H" "Accept: application/vnd.github.v3.raw")
    if [ $1 ]; then
        curlHeaders+=("-H" "Authorization: token $1")
    else
        echo "Process will continue without GitHub token."
    fi
    if [ -d $DIR ]; then
        echo "Platform directory ($DIR) already exists."
        echo "You can remove it manually to continue."
        return 0
    else
        mkdir $DIR
    fi
    if [ ! -d $DIR/$DIRINIT ]; then
        mkdir $DIR/$DIRINIT
    fi
    echo "Installation started."
    curl "${curlHeaders[@]}" -Ls -o $DIR/$DCYML -o $DIR/$DOTENV -o $DIR/$DBCONFF https://raw.githubusercontent.com/Technoplatz/bi/main/{$DCYML,$DOTENV,$DBCONFF}
    cd  $DIR
    CONTD=$(cat $DCYML | head -c 3)
    if [[ "$CONTD" == *"40"* ]]; then
        echo "Required files not found on GitHub ($CONTD)."
        echo "You may provide a token to get connected to the repository."
        return 0
    fi
    if [ ! -f .secret-mongo-password ]; then
        re='^[a-zA-Z]+$'
        while ! [[ ${DBPWD:0:1} =~ $re ]]
        do
            DBPWD=$(openssl rand -hex 12)
            let "INC+=1"
        done
        echo $DBPWD > .secret-mongo-password
        echo "Database password was created successfully ($INC)."
    fi
    echo
    ls -lah $DIR
    echo "Installation completed successfully :)"
    return 1
}

function startBI() {
    cd  $DIR
    if [ $1 ]; then
        echo "Invalid parameter: $1"
        return 0
    fi
    docker-compose up --detach --remove-orphans
    return 1
}

function stopBI() {
    cd  $DIR
    if [ $1 ]; then
        echo "Invalid parameter: $1"
        return 0
    fi
    docker-compose down
    return 1
}

# Setup
DIR="bii"
DIRINIT="_init"
DCYML="docker-compose.yml"
DOTENV=".env"
DBCONFF="$DIRINIT/mongod.conf"
INC=0

case $1 in
    "install")
	    installBI "$2"
	    ;;
    "start" | "restart")
        startBI "$2"
        ;;
    "stop")
        stopBI
        ;;
    *)
        echo "Command not found!"
        listAllCommands
esac

echo
