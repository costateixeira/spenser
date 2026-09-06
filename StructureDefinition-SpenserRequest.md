# SpenserRequest - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **SpenserRequest**

## Resource Profile: SpenserRequest 

| | |
| :--- | :--- |
| *Official URL*:http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest | *Version*:1.0.0 |
| Active as of 2026-09-06 | *Computable Name*:SpenserRequest |

**Usages:**

* Examples for this Profile: [MedicationRequest/med-request-1234](MedicationRequest-med-request-1234.md)

You can also check for [usages in the FHIR IG Statistics](https://packages2.fhir.org/xig/resource/jct.fhir.spenser|current/StructureDefinition/StructureDefinition-SpenserRequest.json)

### Formal Views of Profile Content

 [Description of Profiles, Differentials, Snapshots and how the different presentations work](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#structure-definitions). 

 

Other representations of profile: [CSV](StructureDefinition-SpenserRequest.csv), [Excel](StructureDefinition-SpenserRequest.xlsx), [Schematron](StructureDefinition-SpenserRequest.sch) 



## Resource Content

```json
{
  "resourceType" : "StructureDefinition",
  "id" : "SpenserRequest",
  "url" : "http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest",
  "version" : "1.0.0",
  "name" : "SpenserRequest",
  "status" : "active",
  "date" : "2026-09-06T10:57:27+00:00",
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
  "fhirVersion" : "5.0.0",
  "mapping" : [{
    "identity" : "workflow",
    "uri" : "http://hl7.org/fhir/workflow",
    "name" : "Workflow Pattern"
  },
  {
    "identity" : "script10.6",
    "uri" : "http://ncpdp.org/SCRIPT10_6",
    "name" : "Mapping to NCPDP SCRIPT 10.6"
  },
  {
    "identity" : "w5",
    "uri" : "http://hl7.org/fhir/fivews",
    "name" : "FiveWs Pattern Mapping"
  },
  {
    "identity" : "rim",
    "uri" : "http://hl7.org/v3",
    "name" : "RIM Mapping"
  },
  {
    "identity" : "v2",
    "uri" : "http://hl7.org/v2",
    "name" : "HL7 V2 Mapping"
  }],
  "kind" : "resource",
  "abstract" : false,
  "type" : "MedicationRequest",
  "baseDefinition" : "http://hl7.org/fhir/StructureDefinition/MedicationRequest",
  "derivation" : "constraint",
  "differential" : {
    "element" : [{
      "id" : "MedicationRequest",
      "path" : "MedicationRequest"
    },
    {
      "id" : "MedicationRequest.status",
      "path" : "MedicationRequest.status",
      "patternCode" : "active"
    },
    {
      "id" : "MedicationRequest.intent",
      "path" : "MedicationRequest.intent",
      "patternCode" : "instance-order"
    },
    {
      "id" : "MedicationRequest.medication",
      "path" : "MedicationRequest.medication",
      "binding" : {
        "strength" : "required",
        "valueSet" : "http://costateixeira.github.io/spenser/ValueSet/SpenserMedsVS"
      }
    },
    {
      "id" : "MedicationRequest.medication.concept.coding.code",
      "path" : "MedicationRequest.medication.concept.coding.code",
      "min" : 1
    },
    {
      "id" : "MedicationRequest.dispenseRequest.quantity.value",
      "path" : "MedicationRequest.dispenseRequest.quantity.value",
      "patternDecimal" : 1
    }]
  }
}

```
