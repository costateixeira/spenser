# Example - Dispense answering an order posted at the unit - Spenser - a developer's companion v1.0.0

## Exemple MedicationDispense: Example - Dispense answering an order posted at the unit

-------

**French**

-------

**status**: Completed

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Milk Chocolate |

**subject**: [Patient/123](Patient/123)

### Performers

| | |
| :--- | :--- |
| - | **Actor** |
| * | [Spenser-E3D4](Device-Spenser-E3D4.md) |

**authorizingPrescription**: [MedicationRequest : status = active; intent = instance-order](MedicationRequest-PlainMilkOrder.md)



## Resource Content

```json
{
  "resourceType" : "MedicationDispense",
  "id" : "DispenseForDirectOrder",
  "status" : "completed",
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
  },
  "performer" : [{
    "actor" : {
      "reference" : "Device/Spenser-E3D4",
      "display" : "Spenser-E3D4"
    }
  }],
  "authorizingPrescription" : [{
    "reference" : "MedicationRequest/PlainMilkOrder"
  }]
}

```
