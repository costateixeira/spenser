<#
.SYNOPSIS
  See how a Spenser unit is set up, or change its settings, through the order server.

.DESCRIPTION
  A unit is usually on a network you cannot reach, but it reports to the order
  server and takes instructions from it (firmware 1.3 and later).

  With no -Set, shows what the unit last reported: its Device on the server,
  with its settings and state in Device.property.

  With -Set, posts a Task with code SpenserTaskCodes#configure that names the
  unit, one input per setting, and waits for the unit to complete it (applied)
  or fail it (with the reason). The unit picks it up on its next check, so this
  only works while the unit can reach the server. Before moving to a new
  serverUrl the unit checks that the new server answers, and keeps the old one
  if it does not.

  Settings that can be set this way: serverUrl, orderMode, orderQuery,
  taskQuery, pollEnabled, pollSeconds, writeBack, giveUpOnStockEmpty,
  updateMode, updateCheckMinutes.

.EXAMPLE
  .\configure-unit.ps1
  .\configure-unit.ps1 -Set @{ pollSeconds = 60 }
  .\configure-unit.ps1 Spenser-A1B2 -Set @{ serverUrl = 'http://spenser.178.104.103.200.sslip.io/fhir/r5'; pollEnabled = $true }
#>
param(
  # A unit's name is its setup Wi-Fi name: Spenser- and the last two bytes of its MAC.
  [Parameter(Position = 0)] [string] $Unit = 'Spenser-E3D4',
  [hashtable] $Set,
  [string] $Server = 'https://spenser.178.104.103.200.sslip.io/fhir/r5',
  [int] $WaitSeconds = 180
)

$ErrorActionPreference = 'Stop'
$h = @{ Accept = 'application/fhir+json' }
$UnitSystem = 'http://costateixeira.github.io/spenser/unit'

function Show-Unit {
  try { $d = Invoke-RestMethod -Uri "$Server/Device/$Unit" -Headers $h }
  catch { Write-Host "No Device/$Unit on $Server yet: the unit writes it on its first check."; return }
  Write-Host ("{0}, firmware {1}, last reported {2}" -f $Unit, ($d.version | Select-Object -First 1).value, $d.meta.lastUpdated)
  foreach ($p in @($d.property)) {
    if (-not $p) { continue }
    $code = $p.type.coding[0].code
    $value = if ($null -ne $p.valueString) { $p.valueString }
             elseif ($null -ne $p.valueInteger) { $p.valueInteger }
             elseif ($null -ne $p.valueBoolean) { $p.valueBoolean }
             else { '' }
    Write-Host ("  {0,-24} {1}" -f $code, $value)
  }
  if (-not $d.property) { Write-Host '  (no settings reported: the unit runs firmware older than 1.3)' }
}

if (-not $Set -or $Set.Count -eq 0) { Show-Unit; return }

$inputs = foreach ($name in $Set.Keys) {
  $value = $Set[$name]
  $entry = [ordered]@{ type = @{ text = [string]$name } }
  if ($value -is [bool]) { $entry.valueBoolean = $value }
  elseif ($value -is [int] -or $value -is [long]) { $entry.valueInteger = [int]$value }
  else { $entry.valueString = [string]$value }
  $entry
}
$task = [ordered]@{
  resourceType       = 'Task'
  status             = 'requested'
  intent             = 'order'
  code               = @{ coding = @(@{ system = 'http://costateixeira.github.io/spenser/CodeSystem/SpenserTaskCodes'; code = 'configure' }) }
  requestedPerformer = @(@{ reference = @{ identifier = @{ system = $UnitSystem; value = $Unit }; display = $Unit } })
  authoredOn         = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  input              = @($inputs)
}
$body = $task | ConvertTo-Json -Depth 10
$taskId = (Invoke-RestMethod -Method Post -Uri "$Server/Task" -ContentType 'application/fhir+json' -Headers $h -Body $body).id
Write-Host "Task     Task/$taskId asks $Unit to set: $(($Set.Keys | ForEach-Object { "$_=$($Set[$_])" }) -join ', ')"

$deadline = (Get-Date).AddSeconds($WaitSeconds)
do {
  Start-Sleep -Seconds 5
  $t = Invoke-RestMethod -Uri "$Server/Task/$taskId" -Headers $h
  Write-Host ("{0}  Task is {1}" -f (Get-Date).ToString('T'), $t.status)
} while ($t.status -eq 'requested' -and (Get-Date) -lt $deadline)

switch ($t.status) {
  'completed' { Write-Host "Applied: $($t.output[0].valueString)"; Show-Unit }
  'failed'    { Write-Host "Refused: $($t.statusReason.concept.text)"; exit 1 }
  default     { Write-Host "The unit has not taken it yet. It stays on the server until the unit's next check reaches it."; exit 1 }
}
