# Example - Order that is not actionable on its own - Spenser - a developer's companion v1.0.0

## Example MedicationRequest: Example - Order that is not actionable on its own

-------

**English**

-------

Profile: [SpenserRequest](StructureDefinition-SpenserRequest.md)

**status**: Active

**intent**: Instance Order

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Milk Chocolate |

**subject**: [Patient/123](Patient/123)



## Resource Content

```json
{
  "resourceType" : "MedicationRequest",
  "id" : "PlainMilkOrder",
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
        "display" : "Milk Chocolate"
      }]
    }
  },
  "subject" : {
    "reference" : "Patient/123"
  }
}

```
