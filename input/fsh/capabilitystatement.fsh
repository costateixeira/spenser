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

* rest[+]
  * mode = #client
  * documentation = "Spenser also acts as a client: it polls a server for orders it should fulfil. Following the COW guidance on actionable orders, an order is only dispensed when the MedicationRequest carries the 'actionable' tag, or when a Task asks for it to be fulfilled."
  * resource[0]
    * type = #MedicationRequest
    * documentation = "Searched for orders tagged as actionable. Set to 'completed' after dispensing, when no Task is coordinating the work."
    * interaction[0].code = #search-type
    * interaction[+].code = #update
    * searchParam[0]
      * name = "_tag"
      * type = #token
      * documentation = "Selects orders tagged http://terminology.hl7.org/CodeSystem/common-tags#actionable"
    * searchParam[+]
      * name = "status"
      * type = #token
    * searchParam[+]
      * name = "intent"
      * type = #token
  * resource[+]
    * type = #Task
    * documentation = "Coordination Task pointing at the order in Task.focus. Set to 'completed' with the dispense in Task.output; the status of the request itself is left to the placer."
    * interaction[0].code = #search-type
    * interaction[+].code = #update
    * searchParam[0]
      * name = "status"
      * type = #token
    * searchInclude = "Task:focus"
  * resource[+]
    * type = #MedicationDispense
    * documentation = "Created on the server once an order has been dispensed, referring to the order in authorizingPrescription."
    * interaction.code = #create
