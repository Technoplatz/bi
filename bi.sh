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
    echo "./bi.sh install [token]"
    echo "./bi.sh up [--build] [--prod]"
    echo "./bi.sh down"
    echo "./bi.sh kill"
    echo "./bi.sh pull [--prod]"
    echo "./bi.sh build <image | --all> [--prod]"
    echo "./bi.sh prune"
    echo "./bi.sh help"
    echo
    echo "See more at https://bi.technoplatz.com/support#script-commands-reference"
}

function getSuffixBI() {
    SUFFIX=""
    BRANCH=$(git branch --show-current)
    if [[ ! -z $BRANCH ]]; then
        if [ $BRANCH != "main" ]; then
            SUFFIX="-$BRANCH"
        fi
        if [ $2 ]; then
            if [ $1 == "up" ]; then
                if [ $2 != "--build" ]; then 
                    SUFFIX="-1"
                else
                    if [ $3 ]; then
                        if [ $3 != "--prod" ]; then SUFFIX="-1"; else SUFFIX=""; fi
                    fi
                fi
            elif [ $1 == "build" ]; then
                if [ $3 ]; then
                    if [ $3 != "--prod" ]; then SUFFIX="-1"; else SUFFIX=""; fi
                fi
            else
                if [ $2 != "--prod" ]; then SUFFIX="-1"; else SUFFIX=""; fi
            fi
        fi
    fi
    echo $SUFFIX
    return 1
}

function getFiles() {
    declare -a curlHeaders=("-H" "Accept: application/vnd.github.v3.raw")
    if [ $1 ]; then
        curlHeaders+=("-H" "Authorization: token $1")
    else
        echo "Process will continue without GitHub token."
    fi
    curl "${curlHeaders[@]}" -Ls -o $DCYML -o $DOTENV -o $DBCONF https://raw.githubusercontent.com/Technoplatz/bi/main/{$DCYML,$DOTENV,$DBCONF}
    return 1
}

function installBI() {
    if [ -d $DIR ]; then
        echo "Oops! \"$DIR\" directory already exists. You should remove it manually."
        echo "Installation was canceled to avoid any data loss."
        return 0
    else
        mkdir $DIR
        mkdir $DIR/_init
    fi
    cd $DIR
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
    echo
    echo "PLEASE MAKE THE NECESSARY CHANGES ON \"_bi/.env\" FILE"
    echo "THEN RUN ./bi.sh up [--build] [--prod]"
    return 1
}

function upBI() {
    if [ ! -d $DIR ]; then
        echo "Oops! \"$DIR\" folder not found at the directory you are!"
        echo "You need to install the platform by ./bi.sh install [token]"
        return 0
    fi
    if [ $1 ]; then
        if [ $1 != "--build" ]; then
            echo "Invalid parameter: $1"
            return 0
        else
            BUILD=$(buildBI)
        fi
    fi
    cd $DIR
    DEV_SUFFIX=$GETSUFFIX docker-compose up --detach --remove-orphans --no-build
    echo
    echo "The platform has been started"
    echo "PLEASE BE PAITENT UP TO 20 SECONDS FOR THE PLATFORM TO BE FUNCTIONAL"
    return 1
}

function downBI() {
    cd $DIR
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    DEV_SUFFIX=$GETSUFFIX docker-compose down
    return 1
}

function pullBI() {
    if [ ! -d $DIR ]; then
        echo "Oops! \"$DIR\" folder not found at the directory you are!"
        return 0
    fi
    cd $DIR
    DEV_SUFFIX=$GETSUFFIX docker-compose pull
    echo "The latest software updates have been received successfully"
    echo "RUN \"./bi.sh up [--build] [--prod]\" FOR CHANGES TO BE APPLIED"
    return 1
}

function pruneBI() {
    if [ $1 ]; then
        echo "No parameter required: $1"
        return 0
    fi
    docker system prune
    echo "Unused resources have been removed"
    return 1
}

function buildBI() {
    if [ ! $1 ]; then
        echo "Please specify an image or add --all to build all images"
        return 0
    fi
    for row in $(echo "${BUILDS}" | jq -r '.[] | @base64'); do
        _jq() {
            echo ${row} | base64 --decode | jq -r ${1}
        }
    IMAGE=$(echo $(_jq '.image'))
    FOLDER=$(echo $(_jq '.folder'))
    TAG=$(echo $(_jq '.tag'))
    DOCKERFILE=$(echo $(_jq '.dockerfile'))
    if [[ $1 == "--all" || $1 == $IMAGE ]]; then
        docker build --tag $NS/$IMAGE$GETSUFFIX:$TAG --file $FOLDER/$DOCKERFILE $FOLDER/
    fi
    done
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
INC=0
NS="ghcr.io/technoplatz"
DIR="_bi"
DCYML="docker-compose.yml"
DOTENV=".env"
DBCONF="_init/mongod.conf"
BUILDS='[
    {"folder":"_init","image":"bi-init","tag":"latest","dockerfile":"Dockerfile"},
    {"folder":"_replicaset","image":"bi-replicaset","tag":"latest","dockerfile":"Dockerfile"},
    {"folder":"api","image":"bi-api","tag":"latest","dockerfile":"Dockerfile"},
    {"folder":"pwa","image":"bi-pwa","tag":"latest","dockerfile":"Dockerfile"}
    ]'

GETSUFFIX=$(getSuffixBI "$1" "$2" "$3")
if [ "$GETSUFFIX" == "-1" ]; then
    echo "Invalid command option: $1 $2 $3"
    echo
    exit 0
fi
echo "SUFFIX $GETSUFFIX"

case $1 in
    "install")
	    installBI "$2"
	    ;;
    "up")
        upBI "$2"
        ;;
    "build")
        buildBI "$2"
        ;;
    "kill")
        killBI "$2"
        ;;
    "prune")
        pruneBI "$2"
        ;;
    "pull")
        pullBI "$2"
        ;;
    "down")
        downBI "$2"
        ;;
    "help")
        listAllCommands
        ;;
    *)
        echo "Command not found!"
        listAllCommands
esac

echo
