// Worked examples of the two ways an order becomes actionable, and of what
// Spenser reports back. These are the resources the Interfaces page walks
// through, and the shapes the firmware actually accepts and produces.

Alias: $CommonTags = http://terminology.hl7.org/CodeSystem/common-tags
Alias: $TaskCode = http://hl7.org/fhir/CodeSystem/task-code
Alias: $DispenseNotPerformed = http://hl7.org/fhir/CodeSystem/medicationdispense-status-reason


Instance: ActionableDarkOrder
InstanceOf: SpenserRequest
Title: "Example - Order made actionable by a tag"
Description: "A MedicationRequest the placer has marked actionable. Spenser dispenses it on its next check and, because no Task is coordinating the work, sets the request itself to completed."
Usage: #example
* meta.tag = $CommonTags#actionable
* status = #active
* intent = #instance-order
* medication.concept = SpenserMeds#chocolate-dark "Dark Chocolate"
* subject = Reference(Patient/123)
* dosageInstruction.text = "One bite"


Instance: PlainMilkOrder
InstanceOf: SpenserRequest
Title: "Example - Order that is not actionable on its own"
Description: "The same order without the tag. On its own this is an authorization and nothing more: Spenser ignores it until a Task asks for it to be fulfilled."
Usage: #example
* status = #active
* intent = #instance-order
* medication.concept = SpenserMeds#chocolate-milk "Milk Chocolate"
* subject = Reference(Patient/123)


Instance: FulfillPlainMilkOrder
InstanceOf: Task
Title: "Example - Task asking for an order to be fulfilled"
Description: "A Coordination Task pointing at the order in Task.focus. This is what makes the plain order actionable. Spenser completes the Task with the dispense in Task.output, and leaves the request itself to the placer."
Usage: #example
* identifier.system = "http://example.org/spenser-orders"
* identifier.value = "demo-1"
* status = #requested
* intent = #order
* code = $TaskCode#fulfill "Fulfill the focal request"
* focus = Reference(PlainMilkOrder)
* for = Reference(Patient/123)


Instance: DispenseForActionableDarkOrder
InstanceOf: MedicationDispense
Title: "Example - Dispense reported back"
Description: "What Spenser creates on the order server once a piece has come out, pointing back at the order in authorizingPrescription. The same resource is the answer to an order posted straight at the device."
Usage: #example
* status = #completed
* medication.concept = SpenserMeds#chocolate-dark "Dark Chocolate"
* subject = Reference(Patient/123)
* performer.actor = Reference(Spenser-E3D4) "Spenser-E3D4"
* authorizingPrescription = Reference(ActionableDarkOrder)


Instance: DeclinedDispenseOutOfStock
InstanceOf: MedicationDispense
Title: "Example - Dispense that did not happen"
Description: "An order Spenser could not fill because the lane is empty. R5 removed MedicationDispense.statusReason, so the reason lives in notPerformedReason, which is a CodeableReference - hence the .concept in the path."
Usage: #example
* status = #declined
* notPerformedReason.concept = $DispenseNotPerformed#outofstock "Drug not available - out of stock"
* medication.concept = SpenserMeds#chocolate-dark "Dark Chocolate"
* subject = Reference(Patient/123)
* authorizingPrescription = Reference(ActionableDarkOrder)


Instance: Spenser-E3D4
InstanceOf: Device
Title: "Example - A Spenser unit on the order server"
Description: "The Device a unit writes on the order server once per boot. Its id is the unit's name, the network it shows in setup mode: Spenser- and the last two bytes of its factory MAC."
Usage: #example
* identifier.system = "http://costateixeira.github.io/spenser/unit"
* identifier.value = "Spenser-E3D4"
* status = #active
* manufacturer = "Spenser"
* name.value = "Spenser-E3D4"
* name.type = #user-friendly-name
* version.value = "1.3.0"


Instance: PlainDarkOrderForOneUnit
InstanceOf: SpenserRequest
Title: "Example - Order meant for one unit"
Description: "A plain order, made actionable by the Task that addresses it to one unit. The order names the unit too, in the dispensingDevice extension, by a logical reference: R5 has no element on MedicationRequest that takes a Device."
Usage: #example
* extension[dispensingDevice].valueReference.identifier.system = "http://costateixeira.github.io/spenser/unit"
* extension[dispensingDevice].valueReference.identifier.value = "Spenser-E3D4"
* extension[dispensingDevice].valueReference.display = "Spenser-E3D4"
* status = #active
* intent = #instance-order
* medication.concept = SpenserMeds#chocolate-dark "Dark Chocolate"
* subject = Reference(Patient/123)


Instance: FulfillForOneUnit
InstanceOf: Task
Title: "Example - Task addressed to one unit"
Description: "Task.requestedPerformer names the unit that is to fill the order: the one Task element R5 lets name a Device. Every other unit skips this Task; the unit it names dispenses it and closes it."
Usage: #example
* status = #requested
* intent = #order
* code = $TaskCode#fulfill "Fulfill the focal request"
* focus = Reference(PlainDarkOrderForOneUnit)
* for = Reference(Patient/123)
* requestedPerformer.reference = Reference(Spenser-E3D4) "Spenser-E3D4"


Instance: ActionableDarkOrderForOneUnit
InstanceOf: SpenserRequest
Title: "Example - Tagged order for one unit"
Description: "An order made actionable by the tag, with no Task, that names the unit to dispense it in the dispensingDevice extension. Every other unit polling the server skips it."
Usage: #example
* meta.tag = $CommonTags#actionable
* extension[dispensingDevice].valueReference.identifier.system = "http://costateixeira.github.io/spenser/unit"
* extension[dispensingDevice].valueReference.identifier.value = "Spenser-E3D4"
* extension[dispensingDevice].valueReference.display = "Spenser-E3D4"
* status = #active
* intent = #instance-order
* medication.concept = SpenserMeds#chocolate-dark "Dark Chocolate"
* subject = Reference(Patient/123)
* dosageInstruction.text = "One bite"
