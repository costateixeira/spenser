# Example - Dispense reported back - Spenser - a developer's companion v1.0.0

## Example MedicationDispense: Example - Dispense reported back

-------

**English**

-------

**status**: Completed

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Dark Chocolate |

**subject**: [Patient/123](Patient/123)

### Performers

| | |
| :--- | :--- |
| - | **Actor** |
| * | [Spenser-E3D4](Device-Spenser-E3D4.md) |

**authorizingPrescription**: [MedicationRequest: status = active; intent = instance-order](MedicationRequest-ActionableDarkOrder.md)



## Resource Content

```json
{
  "resourceType" : "MedicationDispense",
  "id" : "DispenseForActionableDarkOrder",
  "status" : "completed",
  "medication" : {
    "concept" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
        "code" : "chocolate-dark",
        "display" : "Dark Chocolate"
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
    "reference" : "MedicationRequest/ActionableDarkOrder"
  }]
}

```
