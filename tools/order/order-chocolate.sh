#!/bin/sh
# Order one chocolate through the order server and watch a Spenser unit fill it.
#
#   ./order-chocolate.sh                 # dark, unit Spenser-E3D4
#   ./order-chocolate.sh milk Spenser-A1B2
#
# A unit's name is its setup Wi-Fi name: Spenser- and the last two bytes of its MAC.
#
# Places a MedicationRequest on the order server, then a Task asking for it to be
# fulfilled by the unit named in Task.requestedPerformer. Waits
# for the unit to pick the Task up on its next poll, then shows the dispense.
#
# The unit is Device/<name> on the server, registered here if it is not there
# yet. requestedPerformer is the only Task element R5 lets name a Device.
# From firmware 1.3 a unit skips a Task meant for another unit and claims one
# that names no unit; to keep it off those too, set its task search to
# status=requested&requestedperformer-reference=Device/<name>&_include=Task:focus&_count=5.
#
# The unit is not put in MedicationRequest.performer: in R5 that element is the
# performer of the administration, and does not accept a Device.
#
# Needs only curl. SERVER and WAIT_SECONDS can be set in the environment.

set -eu

CHOCOLATE=${1:-dark}
UNIT=${2:-Spenser-E3D4}
SERVER=${SERVER:-https://spenser.178.104.103.200.sslip.io/fhir/r5}
WAIT_SECONDS=${WAIT_SECONDS:-120}

case "$CHOCOLATE" in
  dark) DISPLAY_NAME="Dark Chocolate" ;;
  milk) DISPLAY_NAME="Milk Chocolate" ;;
  *) echo "usage: $0 [dark|milk] [unit]" >&2; exit 2 ;;
esac

TYPE="Content-Type: application/fhir+json"
ACCEPT="Accept: application/fhir+json"

# The first "id" in a resource is its own: the server writes it right after resourceType.
first() { tr -d '\n' | sed -n "s/^[^{]*{[^}]*\"$1\" *: *\"\([^\"]*\)\".*/\1/p"; }

# 0. The unit, as a Device the Task can point at.
if [ "$(curl -s -o /dev/null -w '%{http_code}' "$SERVER/Device/$UNIT" -H "$ACCEPT")" != 200 ]; then
  curl -sS -o /dev/null -X PUT "$SERVER/Device/$UNIT" -H "$TYPE" -H "$ACCEPT" -d '{
    "resourceType": "Device", "id": "'"$UNIT"'", "status": "active", "manufacturer": "Spenser",
    "identifier": [{"system": "http://costateixeira.github.io/spenser/unit", "value": "'"$UNIT"'"}],
    "name": [{"value": "'"$UNIT"'", "type": "user-friendly-name"}]}'
  echo "Unit     Device/$UNIT registered"
fi

# 1. The order. No actionable tag: the Task is what makes it actionable.
ORDER_ID=$(curl -sS -X POST "$SERVER/MedicationRequest" -H "$TYPE" -H "$ACCEPT" -d '{
  "resourceType": "MedicationRequest", "status": "active", "intent": "instance-order",
  "medication": {"concept": {"coding": [{"system": "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
    "code": "chocolate-'"$CHOCOLATE"'", "display": "'"$DISPLAY_NAME"'"}]}},
  "subject": {"reference": "Patient/123"}, "dosageInstruction": [{"text": "One bite"}]}' | first id)
[ -n "$ORDER_ID" ] || { echo "The server did not return an id for the order." >&2; exit 1; }
echo "Order    MedicationRequest/$ORDER_ID ($DISPLAY_NAME)"

# 2. The Task: fulfil that order, by this unit.
TASK_ID=$(curl -sS -X POST "$SERVER/Task" -H "$TYPE" -H "$ACCEPT" -d '{
  "resourceType": "Task", "status": "requested", "intent": "order",
  "code": {"coding": [{"system": "http://hl7.org/fhir/CodeSystem/task-code", "code": "fulfill"}]},
  "focus": {"reference": "MedicationRequest/'"$ORDER_ID"'"},
  "for": {"reference": "Patient/123"},
  "authoredOn": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
  "requestedPerformer": [{"reference": {"reference": "Device/'"$UNIT"'", "display": "'"$UNIT"'"}}]}' | first id)
[ -n "$TASK_ID" ] || { echo "The server did not return an id for the Task." >&2; exit 1; }
echo "Task     Task/$TASK_ID, for unit $UNIT"

# 3. Wait for a unit to take it. It polls every 30 seconds by default.
WAITED=0
STATUS=requested
while [ "$STATUS" = requested ] && [ "$WAITED" -lt "$WAIT_SECONDS" ]; do
  sleep 5
  WAITED=$((WAITED + 5))
  STATUS=$(curl -sS "$SERVER/Task/$TASK_ID" -H "$ACCEPT" | tr -d '\n' | sed -n 's/.*"status" *: *"\([^"]*\)".*/\1/p')
  echo "$(date +%T)  Task is $STATUS"
done

# 4. What came of it.
DISPENSES=$(curl -sS "$SERVER/MedicationDispense?prescription=MedicationRequest/$ORDER_ID" -H "$ACCEPT" | tr -d '\n')
echo "Dispense $(echo "$DISPENSES" | grep -o '"status" *: *"[a-z-]*"' | sed 's/.*"\([a-z-]*\)"$/\1/' | tr '\n' ' ')"
echo "$DISPENSES" | grep -o '"medicationdispense-status-reason" *, *"code" *: *"[^"]*"' | sed 's/.*"\([^"]*\)"$/  reason: \1/' || true

case "$STATUS" in
  completed) echo "Done: the chocolate should be in the tray." ;;
  failed) echo "The unit gave up on it. The dispense above says why."; exit 1 ;;
  requested)
    echo "No unit took the Task within $WAIT_SECONDS seconds. Check:"
    echo "  - the unit is online and its serverUrl is exactly $SERVER"
    echo "  - polling is on (dashboard, or GET /settings on the unit)"
    echo "  - the server log shows GET /Task?status=requested every 30 seconds"
    exit 1 ;;
  *) echo "The Task ended as '$STATUS'." ;;
esac
