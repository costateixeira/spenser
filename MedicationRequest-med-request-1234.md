# Example - Spenser Request - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Example - Spenser Request**

## Example MedicationRequest: Example - Spenser Request

Profile: [SpenserRequest](StructureDefinition-SpenserRequest.md)

**status**: Active

**intent**: Instance Order

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Milk chocolate |

**subject**: [Patient/123](Patient/123)

### DosageInstructions

| | |
| :--- | :--- |
| - | **Text** |
| * | Just take it. |



## Resource Content

```json
{
  "resourceType" : "MedicationRequest",
  "id" : "med-request-1234",
  "meta" : {
    "profile" : ["http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest"]
  },
  "status" : "active",
  "intent" : "instance-order",
  "medication" : {
    "concept" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
        "code" : "chocolate-milk",
        "display" : "Milk chocolate"
      }]
    }
  },
  "subject" : {
    "reference" : "Patient/123"
  },
  "dosageInstruction" : [{
    "text" : "Just take it."
  }]
}

```
