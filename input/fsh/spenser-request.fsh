Profile: SpenserRequest
Parent: MedicationRequest

* status = #active
* intent = #instance-order
* medication from SpenserMedsVS
* dispenseRequest.quantity.value = 1
* medication.concept.coding.code 1..1
* medication.concept from SpenserMedsVS


ValueSet: SpenserMedsVS
Title: "Spenser Medications - ValueSet"
Description: "A value set of medications that Spenser can dispense."
* codes from system SpenserMeds


CodeSystem: SpenserMeds
Title: "Spenser Medications - Code System"
Description: "A code system of medications that Spenser can dispense."
* #chocolate-dark "Dark Chocolate"
* #chocolate-milk "Milk Chocolate"



Instance: med-request-1234
InstanceOf: SpenserRequest
Title: "Example - Spenser Request"
Description: "Example of a MedicationRequest to send to Spenser"
Usage: #example
* status = #active
* intent = #instance-order
* medication.concept = SpenserMeds#chocolate-milk "Milk chocolate"
* dosageInstruction.text = "Just take it."
* subject = Reference(Patient/123)


Instance: Add5Milk
InstanceOf: InventoryReport
Title: "Example - Add to inventory - 5 Milk Chocolates"
Description: "Example - Add to inventory - 5 Milk Chocolates"
Usage: #example
* status = #draft
* countType = #difference
* reportedDateTime = 2025-05-01T12:00:00Z
* inventoryListing
  * location.display = "Bin 1"
  * item
    * item = SpenserMeds#chocolate-milk "Milk chocolate"
    * quantity
      * value = 5
      * unit = "pieces"
  * itemStatus = #available


Instance: SetDarkTo17
InstanceOf: InventoryReport
Title: "Example - Set inventory - 17 Dark Chocolates"
Description: "Example - Set inventory - 17 Dark Chocolates"
Usage: #example
* status = #draft
* countType = #snapshot
* reportedDateTime = 2025-05-01T12:00:00Z
* inventoryListing
  * location.display = "Bin 1"
  * item
    * item = SpenserMeds#chocolate-dark "Dark chocolate"
    * quantity
      * value = 17
      * unit = "pieces"
  * itemStatus = #available
