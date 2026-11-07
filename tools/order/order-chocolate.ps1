<#
.SYNOPSIS
  Order one chocolate through the order server and watch a Spenser unit fill it.

.DESCRIPTION
  Places a MedicationRequest on the order server, then a Task asking for it to be
  fulfilled by the unit named in Task.requestedPerformer. Waits
  for the unit to pick the Task up on its next poll, then shows the dispense.

  Both name the unit by a logical reference, its identifier in
  http://costateixeira.github.io/spenser/unit, so nothing has to exist on the
  server first: Task.requestedPerformer, the only Task element R5 lets name a
  Device, and the IG's dispensingDevice extension on the MedicationRequest,
  which has no such element. From firmware 1.3 a unit skips an order meant for
  another unit and claims a Task that names no unit; to keep it off those too,
  set its task search to
  status=requested&requestedperformer-reference:identifier=http://costateixeira.github.io/spenser/unit|<name>&_include=Task:focus&_count=5

.EXAMPLE
  .\order-chocolate.ps1
  .\order-chocolate.ps1 -Chocolate milk -Unit Spenser-A1B2
#>
param(
  [ValidateSet('dark', 'milk')] [string] $Chocolate = 'dark',
  # A unit's name is its setup Wi-Fi name: Spenser- and the last two bytes of its MAC.
  [string] $Unit = 'Spenser-E3D4',
  [string] $Server = 'https://spenser.178.104.103.200.sslip.io/fhir/r5',
  [int] $WaitSeconds = 120
)

$ErrorActionPreference = 'Stop'
$h = @{ Accept = 'application/fhir+json' }
$type = 'application/fhir+json'
$display = @{ dark = 'Dark Chocolate'; milk = 'Milk Chocolate' }[$Chocolate]

# The unit, by a logical reference: its identifier, which needs nothing on the server.
$unitRef = '{"identifier":{"system":"http://costateixeira.github.io/spenser/unit","value":"' + $Unit + '"},"display":"' + $Unit + '"}'

# 1. The order. No actionable tag: the Task is what makes it actionable.
$order = @"
{"resourceType":"MedicationRequest","status":"active","intent":"instance-order",
 "extension":[{"url":"http://costateixeira.github.io/spenser/StructureDefinition/dispensingDevice","valueReference":$unitRef}],
 "medication":{"concept":{"coding":[{"system":"http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
   "code":"chocolate-$Chocolate","display":"$display"}]}},
 "subject":{"reference":"Patient/123"},"dosageInstruction":[{"text":"One bite"}]}
"@
$orderId = (Invoke-RestMethod -Method Post -Uri "$Server/MedicationRequest" -ContentType $type -Headers $h -Body $order).id
if (-not $orderId) { throw 'The server did not return an id for the order.' }
Write-Host "Order    MedicationRequest/$orderId ($display), dispensingDevice $Unit"

# 2. The Task: fulfil that order, by this unit.
$task = @"
{"resourceType":"Task","status":"requested","intent":"order",
 "code":{"coding":[{"system":"http://hl7.org/fhir/CodeSystem/task-code","code":"fulfill"}]},
 "focus":{"reference":"MedicationRequest/$orderId"},
 "for":{"reference":"Patient/123"},
 "authoredOn":"$((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'))",
 "requestedPerformer":[{"reference":$unitRef}]}
"@
$taskId = (Invoke-RestMethod -Method Post -Uri "$Server/Task" -ContentType $type -Headers $h -Body $task).id
if (-not $taskId) { throw 'The server did not return an id for the Task.' }
Write-Host "Task     Task/$taskId, requestedPerformer $Unit"

# 3. Wait for a unit to take it. It polls every 30 seconds by default.
$deadline = (Get-Date).AddSeconds($WaitSeconds)
do {
  Start-Sleep -Seconds 5
  $status = (Invoke-RestMethod -Uri "$Server/Task/$taskId" -Headers $h).status
  Write-Host ("{0}  Task is {1}" -f (Get-Date).ToString('T'), $status)
} while ($status -eq 'requested' -and (Get-Date) -lt $deadline)

# 4. What came of it.
$dispenses = Invoke-RestMethod -Uri "$Server/MedicationDispense?prescription=MedicationRequest/$orderId" -Headers $h
foreach ($d in @($dispenses.entry | ForEach-Object { $_.resource })) {
  $reason = $d.notPerformedReason.concept.coding.code
  Write-Host ("Dispense MedicationDispense/{0}: {1}{2}" -f $d.id, $d.status, $(if ($reason) { " ($reason)" } else { '' }))
}

switch ($status) {
  'completed' { Write-Host 'Done: the chocolate should be in the tray.' }
  'failed'    { Write-Host 'The unit gave up on it. The dispense above says why.'; exit 1 }
  'requested' {
    Write-Host "No unit took the Task within $WaitSeconds seconds. Check:"
    Write-Host '  - the unit is online and its serverUrl is exactly' $Server
    Write-Host '  - polling is on (dashboard, or GET /settings on the unit)'
    Write-Host '  - the server log shows GET /Task?status=requested every 30 seconds'
    exit 1
  }
  default     { Write-Host "The Task ended as '$status'." }
}
