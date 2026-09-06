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
  }]
}

```
