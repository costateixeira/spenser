# SpenserFHIRCapabilityStatement - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **SpenserFHIRCapabilityStatement**

## CapabilityStatement: SpenserFHIRCapabilityStatement 

| | |
| :--- | :--- |
| *Official URL*:http://costateixeira.github.io/spenser/CapabilityStatement/SpenserFHIRCapabilityStatement | *Version*:1.0.0 |
| Active as of 2025-04-18 | *Computable Name*: |

 [Raw OpenAPI-Swagger Definition file](SpenserFHIRCapabilityStatement.openapi.json) | [Download](SpenserFHIRCapabilityStatement.openapi.json) 



## Resource Content

```json
{
  "resourceType" : "CapabilityStatement",
  "id" : "SpenserFHIRCapabilityStatement",
  "url" : "http://costateixeira.github.io/spenser/CapabilityStatement/SpenserFHIRCapabilityStatement",
  "version" : "1.0.0",
  "status" : "active",
  "date" : "2025-04-18",
  "publisher" : "Zeora",
  "contact" : [{
    "name" : "Zeora",
    "telecom" : [{
      "system" : "url",
      "value" : "http://example.com/committees"
    },
    {
      "system" : "email",
      "value" : "my-group@example.com"
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
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "kind" : "instance",
  "implementation" : {
    "description" : "Spenser FHIR Endpoint"
  },
  "fhirVersion" : "5.0.0",
  "format" : ["json"],
  "rest" : [{
    "mode" : "server",
    "resource" : [{
      "type" : "MedicationRequest",
      "interaction" : [{
        "code" : "create"
      }]
    },
    {
      "type" : "MedicationDispense",
      "interaction" : [{
        "code" : "read"
      }]
    },
    {
      "type" : "InventoryReport",
      "interaction" : [{
        "code" : "read"
      },
      {
        "code" : "create"
      }]
    }]
  },
  {
    "mode" : "client",
    "documentation" : "Spenser also acts as a client: it polls a server for orders it should fulfil. Following the COW guidance on actionable orders, an order is only dispensed when the MedicationRequest carries the 'actionable' tag, or when a Task asks for it to be fulfilled.",
    "resource" : [{
      "type" : "MedicationRequest",
      "documentation" : "Searched for orders tagged as actionable. Set to 'completed' after dispensing, when no Task is coordinating the work.",
      "interaction" : [{
        "code" : "search-type"
      },
      {
        "code" : "update"
      }],
      "searchParam" : [{
        "name" : "_tag",
        "type" : "token",
        "documentation" : "Selects orders tagged http://terminology.hl7.org/CodeSystem/common-tags#actionable"
      },
      {
        "name" : "status",
        "type" : "token"
      },
      {
        "name" : "intent",
        "type" : "token"
      }]
    },
    {
      "type" : "Task",
      "documentation" : "Coordination Task pointing at the order in Task.focus. Set to 'completed' with the dispense in Task.output; the status of the request itself is left to the placer.",
      "interaction" : [{
        "code" : "search-type"
      },
      {
        "code" : "update"
      }],
      "searchInclude" : ["Task:focus"],
      "searchParam" : [{
        "name" : "status",
        "type" : "token"
      }]
    },
    {
      "type" : "MedicationDispense",
      "documentation" : "Created on the server once an order has been dispensed, referring to the order in authorizingPrescription.",
      "interaction" : [{
        "code" : "create"
      }]
    }]
  }]
}

```
