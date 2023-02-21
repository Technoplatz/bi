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

EOF

function listAllCommands() {
    echo "Available commands:"
    echo "./technoplatz-bi.sh install [github-token]"
    echo "./technoplatz-bi.sh start"
    echo "./technoplatz-bi.sh restart (Pulls the latest images)"
    echo "./technoplatz-bi.sh build"
    echo "./technoplatz-bi.sh kill"
    echo "./technoplatz-bi.sh pull"
    echo "./technoplatz-bi.sh stop"
    echo "./technoplatz-bi.sh help"
    echo
    echo "See more at https://bi.technoplatz.com/support#script-commands-reference"
}

function getFiles() {
    declare -a curlHeaders=("-H" "Accept: application/vnd.github.v3.raw")
    if [ $1 ]; then
        curlHeaders+=("-H" "Authorization: token $1")
    else
        echo "Process will continue without GitHub token."
    fi
    curl "${curlHeaders[@]}" -Ls -o $DCYML -o $DOTENV -o $DBCONFF https://raw.githubusercontent.com/Technoplatz/bi/main/{$DCYML,$DOTENV,$DBCONFF}
    return 1
}

function installBI() {

    if [ -d $DIR ]; then
        echo "Oops! \"$DIR\" directory already exists. You should remove it manually."
        echo "Installation was canceled to avoid any data loss."
        return 0
    else
        mkdir $DIR
        mkdir $DIR/_init $DIR/_replicaset $DIR/pwa $DIR/api
    fi
    
    cd  $DIR

    getFiles "$1"
    
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
    
    echo "Required files were downloaded successfully :)"
    echo "** PLEASE DO NOT FORGET TO MAKE THE NECESSARY CHANGES ON \".env\" FILE **"
    echo "** THEN RUN ./technoplatz-bi start **"
    return 1
}

function startBI() {
    cd  $DIR
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    docker-compose up --detach --remove-orphans --no-build
    echo
    echo "The platform has been started"
    echo "** PLEASE BE PAITENT UP TO 20 SECONDS FOR THE PLATFORM TO BE FUNCTIONAL **"
    return 1
}

function restartBI() {
    cd  $DIR
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    docker-compose pull && docker-compose up --detach --remove-orphans --no-build
    echo
    echo "The platform has been restarted"
    echo "** PLEASE BE PAITENT UP TO 20 SECONDS FOR THE PLATFORM TO BE FUNCTIONAL **"
    return 1
}

function stopBI() {
    cd  $DIR
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    docker-compose down
    return 1
}

function pullBI() {
    cd  $DIR
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    docker-compose pull
    echo "The latest software updates have been received successfully"
    echo "** RUN \"./technoplatz-bi.sh start | restart\" FOR CHANGES TO BE APPLIED **"
    return 1
}

function buildBI() {
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    docker-compose build
    return 1
}

function killBI() {
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    if [[ ! -z $(docker container ls -qa) ]]; then
        docker container stop $(docker container ls -qa)
        docker container rm $(docker container ls -qa)
        echo "All containers have been stopped and removed successfully"
    else
        echo "No containers found!"
    fi
    
    return 1
}

# Setup
DIR="bi"
DCYML="docker-compose.yml"
DOTENV=".env"
DBCONFF="_init/mongod.conf"
INC=0

case $1 in
    "install")
	    installBI "$2"
	    ;;
    "start")
        startBI "$2"
        ;;
    "restart")
        restartBI "$2"
        ;;
    "build")
        buildBI "$2"
        ;;
    "kill")
        killBI "$2"
        ;;
    "pull")
        pullBI "$2"
        ;;
    "stop")
        stopBI "$2"
        ;;
    "help")
        listAllCommands
        ;;
    *)
        echo "Command not found!"
        listAllCommands
esac

echo