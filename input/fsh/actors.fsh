// The parties to a Spenser exchange. A test plan names one of these as the
// thing under test, and a scenario's steps are written in terms of them.

Instance: SpenserUnit
InstanceOf: ActorDefinition
Usage: #definition
Title: "Spenser Unit"
Description: "A chocolate dispenser, acting as a FHIR server and a FHIR client at the same time."
* name = "SpenserUnit"
* title = "Spenser Unit"
* status = #draft
* type = #system
* documentation = """
A single dispenser. As a **server** it accepts an order posted straight at it and dispenses on the spot, because posting to the device is itself the authorization to dispense. As a **client** it polls an Order Server, acts only on orders that have been made actionable, and reports back what it did.

See [Interfaces](interfaces.html).
"""
* capabilities = Canonical(SpenserFHIRCapabilityStatement)


Instance: OrderPlacer
InstanceOf: ActorDefinition
Usage: #definition
Title: "Order Placer"
Description: "The system that asks for chocolate, by posting an order to a Spenser Unit or by placing one on an Order Server."
* name = "OrderPlacer"
* title = "Order Placer"
* status = #draft
* type = #system
* documentation = """
On an Order Server, the placer decides whether an order is actionable, either by tagging the MedicationRequest or by creating a Task that points at it. When a Task coordinates the work, the placer also closes the MedicationRequest once the Task is completed.
"""


Instance: OrderServer
InstanceOf: ActorDefinition
Usage: #definition
Title: "Order Server"
Description: "A FHIR server that holds orders until a Spenser Unit collects them, and receives what the unit reports back."
* name = "OrderServer"
* title = "Order Server"
* status = #draft
* type = #system
* documentation = """
Answers the unit's searches for tagged MedicationRequests and for requested Tasks, including `_include=Task:focus`. Accepts the MedicationDispense the unit creates and the updates it makes to the Task or MedicationRequest.

See [What Spenser asks of an order server](interfaces.html#what-spenser-asks-of-an-order-server).
"""


Instance: UnitOwner
InstanceOf: ActorDefinition
Usage: #definition
Title: "Unit Owner"
Description: "The person who holds a unit's key, and with it the authority to configure, restock and update the unit."
* name = "UnitOwner"
* title = "Unit Owner"
* status = #draft
* type = #person
* documentation = """
Reading a unit is open, but changing one needs its key. A script acting with the key acts as the owner.

See [What needs a key](interfaces.html#what-needs-a-key).
"""


Instance: UpdatePublisher
InstanceOf: ActorDefinition
Usage: #definition
Title: "Update Publisher"
Description: "The site that publishes the release manifest and firmware images a Spenser Unit checks for and installs."
* name = "UpdatePublisher"
* title = "Update Publisher"
* status = #draft
* type = #system
* documentation = """
This is a plain HTTP exchange rather than a FHIR one. The publisher serves a manifest naming a version, its firmware and filesystem images, and its release notes.

See [Updates](interfaces.html#updates).
"""
