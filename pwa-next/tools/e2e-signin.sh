#!/bin/bash
#
# Browser end-to-end check of the sign-in flow against the local stack.
# Seeds a throwaway user, registers its password through the api, drives the interface in a
# Playwright container, hands the e-mailed code over from the local database and cleans up.
# Usage: tools/e2e-signin.sh [url]   (default http://localhost:8101/)
#
set -uo pipefail
cd "$(dirname "$0")/../.."
set -a; . ./.env; set +a
URL="${1:-http://localhost:8101/}"
API="http://127.0.0.1:${API_CONTAINER_PORT}/api"
USER_ID="e2e-browser@example.invalid"
PASS='E2eBrowser#2026'
TOOLS="$PWD/pwa-next/tools"
MSH="docker exec mongo0 mongosh mongodb://$MONGO_USERNAME:$MONGO_PASSWORD@mongo0:27017/$MONGO_DB?authSource=$MONGO_AUTH_DB --quiet --tls --tlsCertificateKeyFile $MONGO_TLS_CERT_KEYFILE --tlsCertificateKeyFilePassword $MONGO_TLS_CERT_KEYFILE_PASSWORD --tlsCAFile $MONGO_TLS_CA_KEYFILE --tlsAllowInvalidCertificates --eval"
rm -f "$TOOLS/otp.txt" "$TOOLS/otp-requested.txt"

# wait until the api and the frontend answer; the api needs a few seconds after a restart
wait_for() {
  for i in $(seq 1 60); do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' "$1")" = "200" ]; then return 0; fi
    sleep 1
  done
  echo "not ready after 60s: $1"; exit 1
}
wait_for "$API/health"
wait_for "$URL"

CLIENT_IP=$(curl -s -o /dev/null -X POST -H 'Content-Type: application/json' -d '{"op":"signin","email":"x@x.invalid","password":"x"}' "$API/auth"; docker logs --tail 1 api 2>&1 | awk '{print $1}')
$MSH "db.getCollection('_user').deleteOne({usr_id:'$USER_ID'}); db.getCollection('_auth').deleteOne({aut_id:'$USER_ID'});
db.getCollection('_user').insertOne({usr_id:'$USER_ID', usr_name:'E2E Browser', usr_enabled:true, usr_scope:'Internal', usr_locale:'en', _tags:['#Managers'], _created_at:new Date(), _modified_at:new Date()});
db.getCollection('_firewall').updateOne({fwa_name:'e2e-allow'},{\$set:{fwa_name:'e2e-allow', fwa_tag:'#Managers', fwa_source_ip:'$CLIENT_IP', fwa_enabled:true, fwa_type:'Permanent', _tags:['#Managers'], _created_at:new Date(), _modified_at:new Date()}},{upsert:true});" >/dev/null
curl -s -o /dev/null -X POST -H 'Content-Type: application/json' -d "{\"op\":\"signup\",\"email\":\"$USER_ID\",\"name\":\"E2E Browser\",\"password\":\"$PASS\"}" "$API/auth"

# feed the code once the browser has requested it
( for i in $(seq 1 120); do
    if [ -f "$TOOLS/otp-requested.txt" ]; then
      sleep 1
      CODE=$($MSH "print(db.getCollection('_auth').findOne({aut_id:'$USER_ID'}).aut_tfac)" | tail -1)
      if [[ "$CODE" =~ ^[0-9]{6}$ ]]; then echo "$CODE" > "$TOOLS/otp.txt"; break; fi
    fi
    sleep 0.5
  done ) &
FEEDER=$!

docker run --rm --network host -v "$TOOLS:/probe" -w /probe mcr.microsoft.com/playwright:v1.58.0-noble \
  sh -c "npm install --silent --no-audit --no-fund playwright@1.58.0 >/dev/null 2>&1; node e2e-signin.mjs $URL $USER_ID '$PASS'"
RC=$?
kill $FEEDER 2>/dev/null; wait $FEEDER 2>/dev/null
$MSH "db.getCollection('_user').deleteOne({usr_id:'$USER_ID'}); db.getCollection('_auth').deleteOne({aut_id:'$USER_ID'}); db.getCollection('_firewall').deleteOne({fwa_name:'e2e-allow'});" >/dev/null
rm -f "$TOOLS/otp.txt" "$TOOLS/otp-requested.txt"
echo; [ $RC -eq 0 ] && echo "BROWSER E2E: all passed" || echo "BROWSER E2E: failures"
exit $RC
