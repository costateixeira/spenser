// The two ways a chocolate gets ordered, end to end.
//
// The first is the whole exchange between a placer and one unit: posting an
// order at the device is itself the authorization to dispense.
//
// The second goes through an order server, the way a clinical workflow does.
// There the order is an authorization and nothing more, and something else has
// to ask for it to be fulfilled: a Task, or the actionable tag.

Alias: $RestfulInteraction = http://hl7.org/fhir/restful-interaction
Alias: $FHIRTypes = http://hl7.org/fhir/fhir-types


Instance: DirectOrderScenario
InstanceOf: ExampleScenario
Usage: #definition
Title: "Scenario - Ordering straight from the unit"
Description: "A placer posts an order to a Spenser unit and gets back the dispense. No server, no Task, no tag: the POST is the authorization."
* status = #active
* experimental = true
* name = "DirectOrderScenario"
* title = "Ordering straight from the unit"
* purpose = """
The short way round. There is no order server here, so nothing has to make the
order actionable: posting it at the unit is itself the instruction to dispense,
and the servo has already turned by the time the unit answers.

This is the route to start from when trying a unit out, and the one a workshop
runs on when the network is somebody's phone.
"""

* actor[+].key = "placer"
* actor[=].type = #system
* actor[=].title = "Order Placer"
* actor[=].description = "Whatever is asking for chocolate: a script, a client under development, or the unit's own dashboard."

* actor[+].key = "spenser"
* actor[=].type = #system
* actor[=].title = "Spenser Unit"
* actor[=].description = "One dispenser, acting here only as a FHIR server."

* instance[+].key = "order"
* instance[=].structureType = $FHIRTypes#MedicationRequest
* instance[=].structureProfileCanonical = Canonical(SpenserRequest)
* instance[=].title = "The order"
* instance[=].description = "A MedicationRequest naming a chocolate from the IG's own code system. Neither the actionable tag nor a Task is needed on this route."
* instance[=].content = Reference(PlainMilkOrder)

* instance[+].key = "dispense"
* instance[=].structureType = $FHIRTypes#MedicationDispense
* instance[=].title = "The dispense"
* instance[=].description = "What the unit returns, pointing back at the order in `authorizingPrescription`. An absent `whenHandedOver` means the unit's clock has not been set by NTP, not that the time is unknown."
* instance[=].content = Reference(DispenseForDirectOrder)

* process[+].title = "Order a chocolate from the unit"
* process[=].description = "One request, one chocolate."
* process[=].preConditions = "The unit is on the network and the placer can reach it. The lane for the code being ordered has stock."
* process[=].postConditions = "A chocolate has been dispensed, and the unit holds a MedicationDispense recording it."

* process[=].step[+].number = "1"
* process[=].step[=].operation.type = $RestfulInteraction#create
* process[=].step[=].operation.title = "POST /MedicationRequest"
* process[=].step[=].operation.initiator = "placer"
* process[=].step[=].operation.receiver = "spenser"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "The unit dispenses before it answers. The response is `201 Created` carrying the MedicationDispense, with a `Location` for the record the unit kept and an `ETag`. This changes the unit, so it needs the unit's key."
* process[=].step[=].operation.request.instanceReference = "order"
* process[=].step[=].operation.response.instanceReference = "dispense"
* process[=].step[=].alternative[+].title = "The lane is empty"
* process[=].step[=].alternative[=].description = "Nothing moves, and the unit still answers with a MedicationDispense: `status` of `declined`, and `notPerformedReason.concept` of `outofstock`. A refusal is an answer, not an error."
* process[=].step[=].alternative[+].title = "The order asks for something the unit does not carry"
* process[=].step[=].alternative[=].description = "The unit answers `400` with an OperationOutcome. Every error from a FHIR route on the unit is an OperationOutcome; there is no second error format."

* process[=].step[+].number = "2"
* process[=].step[=].operation.type = $RestfulInteraction#search-type
* process[=].step[=].operation.title = "GET /MedicationDispense"
* process[=].step[=].operation.initiator = "placer"
* process[=].step[=].operation.receiver = "spenser"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "Optional, and open: reads need no key. The unit keeps what it dispensed, so the record can be read back later. The searchset also carries an entry with `search.mode` of `outcome`, saying when the unit last looked for work and how that went."


Instance: TaskOrderScenario
InstanceOf: ExampleScenario
Usage: #definition
Title: "Scenario - Ordering through an order server"
Description: "A placer puts an order and a Task on an order server. The unit polls the server, dispenses what is addressed to it, and reports back what it did."
* status = #active
* experimental = true
* name = "TaskOrderScenario"
* title = "Ordering through an order server"
* purpose = """
The long way round, and the one that behaves like a real workflow.

An order on a server is an authorization: it says a chocolate may be dispensed,
not that one should be dispensed now. Something else has to ask for it to be
fulfilled. A Task is that something, and `Task.requestedPerformer` is the only
place in R5 that can name the Device meant to do the work.

The unit is never connected to from outside here. It polls, which is what lets
a dispenser sit on a conference network with nothing open to it.
"""

* actor[+].key = "placer"
* actor[=].type = #system
* actor[=].title = "Order Placer"
* actor[=].description = "Creates the order and the Task, and closes the order once the Task is done. A Task closes itself; a MedicationRequest does not."

* actor[+].key = "server"
* actor[=].type = #system
* actor[=].title = "Order Server"
* actor[=].description = "A plain FHIR server. It holds the order and the Task until a unit collects them, and it has to answer `_include=Task:focus`."

* actor[+].key = "spenser"
* actor[=].type = #system
* actor[=].title = "Spenser Unit"
* actor[=].description = "Acting here as a FHIR client. It takes only the work addressed to it and leaves everything else alone."

* instance[+].key = "order"
* instance[=].structureType = $FHIRTypes#MedicationRequest
* instance[=].structureProfileCanonical = Canonical(SpenserRequest)
* instance[=].title = "The order"
* instance[=].description = "An untagged MedicationRequest, naming the unit meant to fill it in the `dispensingDevice` extension. On its own it sits there."
* instance[=].content = Reference(PlainDarkOrderForOneUnit)
* instance[=].version[+].key = "order-active"
* instance[=].version[=].title = "active"
* instance[=].version[=].description = "As created: authorized, and not yet filled."
* instance[=].version[=].content = Reference(PlainDarkOrderForOneUnit)
* instance[=].version[+].key = "order-completed"
* instance[=].version[=].title = "completed"
* instance[=].version[=].description = "After the placer closes it. The unit does not touch the order while a Task is coordinating the work."

* instance[+].key = "task"
* instance[=].structureType = $FHIRTypes#Task
* instance[=].title = "The Task"
* instance[=].description = "A `fulfill` Task whose `focus` is the order and whose `requestedPerformer` is the unit. This is what makes the order actionable."
* instance[=].content = Reference(FulfillForOneUnit)
* instance[=].version[+].key = "task-requested"
* instance[=].version[=].title = "requested"
* instance[=].version[=].description = "As created. Every other unit polling the same server skips it."
* instance[=].version[=].content = Reference(FulfillForOneUnit)
* instance[=].version[+].key = "task-completed"
* instance[=].version[=].title = "completed"
* instance[=].version[=].description = "After the chocolate came out, with the dispense in `Task.output`."

* instance[+].key = "dispense"
* instance[=].structureType = $FHIRTypes#MedicationDispense
* instance[=].title = "The dispense"
* instance[=].description = "What the unit writes back, naming itself as `performer` and the order in `authorizingPrescription`."
* instance[=].content = Reference(DispenseForTaskOrder)

* process[+].title = "Order a chocolate through an order server"
* process[=].description = "Place the work, let the unit find it, and read back what it did."
* process[=].preConditions = "The unit has been pointed at the order server and its polling is on. The unit has written its own Device on the server, so a Task can name it."
* process[=].postConditions = "A chocolate has been dispensed, the dispense is on the server, the Task is completed, and the order is closed."

* process[=].step[+].number = "1"
* process[=].step[=].operation.type = $RestfulInteraction#create
* process[=].step[=].operation.title = "POST /MedicationRequest"
* process[=].step[=].operation.initiator = "placer"
* process[=].step[=].operation.receiver = "server"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "Nothing happens yet, and that is the point."
* process[=].step[=].operation.request.instanceReference = "order"
* process[=].step[=].operation.request.versionReference = "order-active"

* process[=].step[+].number = "2"
* process[=].step[=].operation.type = $RestfulInteraction#create
* process[=].step[=].operation.title = "POST /Task"
* process[=].step[=].operation.initiator = "placer"
* process[=].step[=].operation.receiver = "server"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "`code` is `fulfill`, `focus` is the order, `requestedPerformer` is the unit. Leave `requestedPerformer` out and any unit polling that server may take it."
* process[=].step[=].operation.request.instanceReference = "task"
* process[=].step[=].operation.request.versionReference = "task-requested"
* process[=].step[=].alternative[+].title = "Tag the order instead of creating a Task"
* process[=].step[=].alternative[=].description = "Put `actionable` from common-tags in the order's `meta.tag` and skip the Task. A unit accepts both routes on every check, and `orderMode` narrows it to one. With no Task coordinating the work the unit completes the MedicationRequest itself, and step 6 does not happen."

* process[=].step[+].number = "3"
* process[=].step[=].operation.type = $RestfulInteraction#search-type
* process[=].step[=].operation.title = "GET /Task?status=requested&_include=Task:focus&_count=5"
* process[=].step[=].operation.initiator = "spenser"
* process[=].step[=].operation.receiver = "server"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "The unit polls on a timer, and a check can also be asked for by hand. Each check looks at the first five results only, so a long queue on the server can outrun one check. The unit remembers what it has already dealt with."
* process[=].step[=].operation.response.instanceReference = "task"
* process[=].step[=].operation.response.versionReference = "task-requested"

* process[=].step[+].number = "4"
* process[=].step[=].operation.type = $RestfulInteraction#create
* process[=].step[=].operation.title = "POST /MedicationDispense"
* process[=].step[=].operation.initiator = "spenser"
* process[=].step[=].operation.receiver = "server"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "The servo turns and a piece drops out, and then the unit says so. The write is queued and retried, so a server that was briefly unreachable does not cost the record."
* process[=].step[=].operation.request.instanceReference = "dispense"
* process[=].step[=].alternative[+].title = "The lane is empty"
* process[=].step[=].alternative[=].description = "The unit writes a dispense with `status` of `declined` and `notPerformedReason.concept` of `outofstock`. Whether the Task is then left open, so a refill retries it, or closed as failed, is the unit's `keepOrders` setting."

* process[=].step[+].number = "5"
* process[=].step[=].operation.type = $RestfulInteraction#update
* process[=].step[=].operation.title = "PUT /Task/[id]"
* process[=].step[=].operation.initiator = "spenser"
* process[=].step[=].operation.receiver = "server"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "`status` becomes `completed`, with the dispense in `Task.output`. Sent with `If-Match`, so a Task somebody else has moved on is not overwritten."
* process[=].step[=].operation.request.instanceReference = "task"
* process[=].step[=].operation.request.versionReference = "task-completed"

* process[=].step[+].number = "6"
* process[=].step[=].operation.type = $RestfulInteraction#update
* process[=].step[=].operation.title = "PUT /MedicationRequest/[id]"
* process[=].step[=].operation.initiator = "placer"
* process[=].step[=].operation.receiver = "server"
* process[=].step[=].operation.initiatorActive = true
* process[=].step[=].operation.receiverActive = true
* process[=].step[=].operation.description = "The placer closes its own order. The unit does not: it was asked to fill one Task, and it has no way of knowing whether the order authorized more than that."
* process[=].step[=].operation.request.instanceReference = "order"
* process[=].step[=].operation.request.versionReference = "order-completed"
