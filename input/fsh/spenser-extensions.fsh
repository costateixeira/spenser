// Extensions this IG defines.

Extension: DispensingDevice
Id: dispensingDevice
Title: "Dispensing device"
Description: """The Spenser unit that is to dispense this order, named by a logical reference: the unit's identifier in http://costateixeira.github.io/spenser/unit, which is its name, Spenser- and the last two bytes of its factory MAC.

R5 has no element on MedicationRequest for this. MedicationRequest.performer and MedicationRequest.device take a DeviceDefinition, a kind of device, and dispenseRequest.dispenser takes only an Organization. A logical reference needs nothing on the server: the unit does not have to be registered as a Device for the order to name it.

When a Task makes the order actionable, a Device in Task.requestedPerformer takes precedence over this extension. On an order with no Task, or a Task that names no unit, a unit acts on this extension: it skips an order that names another unit."""
Context: MedicationRequest
* value[x] only Reference(Device)
* valueReference 1..1
* valueReference.reference 0..0
* valueReference.identifier 1..1
* valueReference.identifier.system 1..1
* valueReference.identifier.system = "http://costateixeira.github.io/spenser/unit" (exactly)
* valueReference.identifier.value 1..1
