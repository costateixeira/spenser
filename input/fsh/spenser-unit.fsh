// What a Spenser unit says about itself on the order server, and the Task that
// changes its settings from afar.

CodeSystem: SpenserUnitProperty
Id: SpenserUnitProperty
Title: "Spenser Unit Properties"
Description: "What a Spenser unit reports about itself in Device.property on the order server: its settings and its state. Written on the first check against a server, after a change of settings, and every ten minutes."
* ^url = "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty"
* ^status = #draft
* ^experimental = true
* ^caseSensitive = true
* #server-url "Order server" "The FHIR base URL the unit polls for orders."
* #order-mode "Order mode" "Which routes make an order actionable for this unit: both, tag or task."
* #order-query "Order search" "Extra search parameters for tagged orders."
* #task-query "Task search" "Extra search parameters for Tasks."
* #poll-enabled "Polling" "Whether the unit checks the order server on its own."
* #poll-seconds "Poll interval" "Seconds between checks."
* #write-back "Write back" "Whether the unit reports dispenses and closes orders on the server."
* #give-up-on-stock-empty "Give up when empty" "Whether an order for an empty lane is abandoned rather than retried after a refill."
* #update-mode "Update mode" "notify, or install firmware updates on its own."
* #update-check-minutes "Update check interval" "Minutes between looks at the release manifest."
* #stock-dark "Dark stock" "Pieces of dark chocolate the unit believes it holds."
* #stock-milk "Milk stock" "Pieces of milk chocolate the unit believes it holds."
* #last-check "Last check" "What the last order check reported."
* #last-configuration "Last configuration" "What the last configuration Task did."
* #ssid "Wi-Fi network" "The Wi-Fi network the unit is on."
* #ip-address "IP address" "The unit's address on its own network."
* #rssi "Signal" "Wi-Fi signal strength, in dBm."
* #largest-free-block "Largest free block" "The largest block of free memory, in bytes. A TLS connection needs about 40 KB in one piece."


CodeSystem: SpenserTaskCodes
Id: SpenserTaskCodes
Title: "Spenser Task Codes"
Description: "Task codes for work asked of a Spenser unit other than dispensing."
* ^url = "http://costateixeira.github.io/spenser/CodeSystem/SpenserTaskCodes"
* ^status = #draft
* ^experimental = true
* ^caseSensitive = true
* #configure "Configure" "Change the settings of the unit named in requestedPerformer. Each input is one setting: input.type names it, input.value[x] holds the value. The unit applies them all or none."


Instance: ConfigureSpenserE3D4
InstanceOf: Task
Title: "Example - Changing a unit's settings from afar"
Description: "Asks the unit Spenser-E3D4 to poll every 60 seconds and to use the order server over plain http. The unit applies both or neither, tests that the new server answers before moving to it, and completes the Task with what it applied, or fails it with the reason."
Usage: #example
* status = #requested
* intent = #order
* code = SpenserTaskCodes#configure "Configure"
* focus = Reference(Spenser-E3D4)
* requestedPerformer.reference.identifier.system = "http://costateixeira.github.io/spenser/unit"
* requestedPerformer.reference.identifier.value = "Spenser-E3D4"
* requestedPerformer.reference.display = "Spenser-E3D4"
* input[0].type.text = "pollSeconds"
* input[0].valueInteger = 60
* input[1].type.text = "serverUrl"
* input[1].valueString = "http://spenser.178.104.103.200.sslip.io/fhir/r5"
