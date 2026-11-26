#!/bin/sh
# See how a Spenser unit is set up, or change its settings, through the order server.
#
#   ./configure-unit.sh                                  # what Spenser-E3D4 last reported
#   ./configure-unit.sh Spenser-E3D4 pollSeconds=60
#   ./configure-unit.sh Spenser-E3D4 serverUrl=http://spenser.178.104.103.200.sslip.io/fhir/r5 pollEnabled=true
#
# A unit is usually on a network you cannot reach, but it reports to the order
# server and takes instructions from it (firmware 1.3 and later). With no
# settings, this shows its Device on the server. With settings, it posts a Task
# with code SpenserTaskCodes#configure naming the unit, one input per setting,
# and waits for the unit to complete it or fail it with the reason. Before
# moving to a new serverUrl the unit checks that the new server answers.
#
# true/false become valueBoolean, whole numbers valueInteger, anything else
# valueString. Settings that can be set this way: serverUrl, orderMode,
# orderQuery, taskQuery, pollEnabled, pollSeconds, writeBack,
# giveUpOnStockEmpty, updateMode, updateCheckMinutes.
#
# Needs curl. SERVER and WAIT_SECONDS can be set in the environment.

set -eu

UNIT=${1:-Spenser-E3D4}
[ $# -gt 0 ] && shift
SERVER=${SERVER:-https://spenser.178.104.103.200.sslip.io/fhir/r5}
WAIT_SECONDS=${WAIT_SECONDS:-180}
TYPE="Content-Type: application/fhir+json"
ACCEPT="Accept: application/fhir+json"

# Indented when a working python3 is about (Windows may offer only a stub), raw otherwise.
pretty() { body=$(cat); printf '%s\n' "$body" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$body"; }

if [ $# -eq 0 ]; then
  curl -sS "$SERVER/Device/$UNIT" -H "$ACCEPT" | pretty
  exit 0
fi

INPUTS=""
for pair in "$@"; do
  name=${pair%%=*}
  value=${pair#*=}
  case "$value" in
    true|false) v="\"valueBoolean\": $value" ;;
    *[!0-9]*|'') v="\"valueString\": \"$value\"" ;;
    *) v="\"valueInteger\": $value" ;;
  esac
  INPUTS="${INPUTS:+$INPUTS, }{\"type\": {\"text\": \"$name\"}, $v}"
done

TASK_ID=$(curl -sS -X POST "$SERVER/Task" -H "$TYPE" -H "$ACCEPT" -d '{
  "resourceType": "Task", "status": "requested", "intent": "order",
  "code": {"coding": [{"system": "http://costateixeira.github.io/spenser/CodeSystem/SpenserTaskCodes", "code": "configure"}]},
  "requestedPerformer": [{"reference": {"identifier": {"system": "http://costateixeira.github.io/spenser/unit", "value": "'"$UNIT"'"}, "display": "'"$UNIT"'"}}],
  "authoredOn": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
  "input": ['"$INPUTS"']}' | tr -d '\n' | sed -n 's/^[^{]*{[^}]*"id" *: *"\([^"]*\)".*/\1/p')
[ -n "$TASK_ID" ] || { echo "The server did not return an id for the Task." >&2; exit 1; }
echo "Task     Task/$TASK_ID asks $UNIT to set: $*"

WAITED=0
STATUS=requested
while [ "$STATUS" = requested ] && [ "$WAITED" -lt "$WAIT_SECONDS" ]; do
  sleep 5
  WAITED=$((WAITED + 5))
  TASK=$(curl -sS "$SERVER/Task/$TASK_ID" -H "$ACCEPT" | tr -d '\n')
  STATUS=$(echo "$TASK" | sed -n 's/^[^{]*{[^}]*"status" *: *"\([^"]*\)".*/\1/p')
  echo "$(date +%T)  Task is $STATUS"
done

case "$STATUS" in
  completed) echo "Applied: $(echo "$TASK" | sed -n 's/.*"output".*"valueString" *: *"\([^"]*\)".*/\1/p')" ;;
  failed) echo "Refused: $(echo "$TASK" | sed -n 's/.*"statusReason".*"text" *: *"\([^"]*\)".*/\1/p')"; exit 1 ;;
  *) echo "The unit has not taken it yet. It stays on the server until the unit's next check reaches it."; exit 1 ;;
esac
