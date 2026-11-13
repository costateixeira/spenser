# Scenario - Ordering straight from the unit - Spenser - a developer's companion v1.0.0

## ExampleScenario: Scenario - Ordering straight from the unit (Expérimental) 

### Acteurs

### Diagramme

### Processus

### Instances



## Resource Content

```json
{
  "resourceType" : "ExampleScenario",
  "id" : "DirectOrderScenario",
  "url" : "http://costateixeira.github.io/spenser/ExampleScenario/DirectOrderScenario",
  "version" : "1.0.0",
  "name" : "DirectOrderScenario",
  "title" : "Ordering straight from the unit",
  "status" : "active",
  "experimental" : true,
  "date" : "2026-11-13T21:21:03+00:00",
  "publisher" : "José Costa Teixeira",
  "contact" : [{
    "name" : "José Costa Teixeira",
    "telecom" : [{
      "system" : "url",
      "value" : "https://github.com/costateixeira"
    }]
  },
  {
    "name" : "José Costa Teixeira",
    "telecom" : [{
      "system" : "email",
      "value" : "you-know.it@gmail.com",
      "use" : "work"
    }]
  }],
  "description" : "A placer posts an order to a Spenser unit and gets back the dispense. No server, no Task, no tag: the POST is the authorization.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "purpose" : "The short way round. There is no order server here, so nothing has to make the\norder actionable: posting it at the unit is itself the instruction to dispense,\nand the servo has already turned by the time the unit answers.\n\nThis is the route to start from when trying a unit out, and the one a workshop\nruns on when the network is somebody's phone.",
  "actor" : [{
    "key" : "placer",
    "type" : "system",
    "title" : "Order Placer",
    "description" : "Whatever is asking for chocolate: a script, a client under development, or the unit's own dashboard."
  },
  {
    "key" : "spenser",
    "type" : "system",
    "title" : "Spenser Unit",
    "description" : "One dispenser, acting here only as a FHIR server."
  }],
  "instance" : [{
    "key" : "order",
    "structureType" : {
      "system" : "http://hl7.org/fhir/fhir-types",
      "code" : "MedicationRequest"
    },
    "structureProfileCanonical" : "http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest",
    "title" : "The order",
    "description" : "A MedicationRequest naming a chocolate from the IG's own code system. Neither the actionable tag nor a Task is needed on this route.",
    "content" : {
      "reference" : "MedicationRequest/PlainMilkOrder"
    }
  },
  {
    "key" : "dispense",
    "structureType" : {
      "system" : "http://hl7.org/fhir/fhir-types",
      "code" : "MedicationDispense"
    },
    "title" : "The dispense",
    "description" : "What the unit returns, pointing back at the order in `authorizingPrescription`. An absent `whenHandedOver` means the unit's clock has not been set by NTP, not that the time is unknown.",
    "content" : {
      "reference" : "MedicationDispense/DispenseForDirectOrder"
    }
  }],
  "process" : [{
    "title" : "Order a chocolate from the unit",
    "description" : "One request, one chocolate.",
    "preConditions" : "The unit is on the network and the placer can reach it. The lane for the code being ordered has stock.",
    "postConditions" : "A chocolate has been dispensed, and the unit holds a MedicationDispense recording it.",
    "step" : [{
      "number" : "1",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "create"
        },
        "title" : "POST /MedicationRequest",
        "initiator" : "placer",
        "receiver" : "spenser",
        "description" : "The unit dispenses before it answers. The response is `201 Created` carrying the MedicationDispense, with a `Location` for the record the unit kept and an `ETag`. This changes the unit, so it needs the unit's key.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "request" : {
          "instanceReference" : "order"
        },
        "response" : {
          "instanceReference" : "dispense"
        }
      },
      "alternative" : [{
        "title" : "The lane is empty",
        "description" : "Nothing moves, and the unit still answers with a MedicationDispense: `status` of `declined`, and `notPerformedReason.concept` of `outofstock`. A refusal is an answer, not an error."
      },
      {
        "title" : "The order asks for something the unit does not carry",
        "description" : "The unit answers `400` with an OperationOutcome. Every error from a FHIR route on the unit is an OperationOutcome; there is no second error format."
      }]
    },
    {
      "number" : "2",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "search-type"
        },
        "title" : "GET /MedicationDispense",
        "initiator" : "placer",
        "receiver" : "spenser",
        "description" : "Optional, and open: reads need no key. The unit keeps what it dispensed, so the record can be read back later. The searchset also carries an entry with `search.mode` of `outcome`, saying when the unit last looked for work and how that went.",
        "initiatorActive" : true,
        "receiverActive" : true
      }
    }]
  }]
}

```
