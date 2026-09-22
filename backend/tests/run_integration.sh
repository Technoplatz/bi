#!/bin/bash
#
# Runs the integration tests against the local docker compose stack.
# Requires the stack to be up (see docker-compose.yml) and a .env file in the repository root.
# A throwaway container from the api image joins the compose network and runs pytest with the
# repository mounted, so the tests see the same database as the running services.
#
set -euo pipefail
cd "$(dirname "$0")/../.."
IMAGE="${BI_API_IMAGE:-technoplatz/bi-api-dev0:latest}"
NETWORK="${BI_NETWORK:-network0}"
# docker run keeps the quotes of .env values (compose strips them), so pass an unquoted copy
ENVFILE="$(mktemp)"
trap 'rm -f "$ENVFILE"' EXIT
grep -vE '^\s*(#|$)' .env | sed -E 's/^([A-Za-z0-9_]+)="(.*)"$/\1=\2/' > "$ENVFILE"
docker run --rm --network "$NETWORK" --env-file "$ENVFILE" \
  -e BI_INTEGRATION=1 -e API_ADMIN_IPS=0.0.0.0 -e PIP_ROOT_USER_ACTION=ignore \
  -v bi-cert-volume:/cert:ro -v bi-storage-volume:/temp \
  -v "$PWD:/w" -w /w "$IMAGE" \
  sh -c "pip install -q pytest && python -m pytest -q -p no:cacheprovider backend/tests/integration ${*:-}"
