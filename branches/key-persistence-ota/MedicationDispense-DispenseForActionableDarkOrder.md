# Example - Dispense reported back - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Example - Dispense reported back**

## Example MedicationDispense: Example - Dispense reported back

**status**: Completed

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Dark Chocolate |

**subject**: [Patient/123](Patient/123)

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
  "authorizingPrescription" : [{
    "reference" : "MedicationRequest/ActionableDarkOrder"
  }]
}

```
