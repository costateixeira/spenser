Instance: SpenserFHIRCapabilityStatement
InstanceOf: CapabilityStatement
Usage: #definition
* status = #active
* date = "2025-04-18"
* publisher = "Spenser"
* kind = #instance
* fhirVersion = #5.0.0
* format = #json
* implementation.description = "Spenser FHIR Endpoint"
* rest
  * mode = #server
  * resource[0]
    * type = #MedicationRequest
    * interaction.code = #create
  * resource[+]
    * type = #MedicationDispense
    * interaction[0].code = #read
  * resource[+]
    * type = #InventoryReport
    * interaction[0].code = #read
    * interaction[+].code = #create


    