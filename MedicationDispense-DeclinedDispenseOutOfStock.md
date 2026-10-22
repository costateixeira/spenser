# Example - Dispense that did not happen - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Example - Dispense that did not happen**

## Example MedicationDispense: Example - Dispense that did not happen

**status**: Declined

### NotPerformedReasons

| | |
| :--- | :--- |
| - | **Concept** |
| * | Drug not available - out of stock |

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
  "id" : "DeclinedDispenseOutOfStock",
  "status" : "declined",
  "notPerformedReason" : {
    "concept" : {
      "coding" : [{
        "system" : "http://hl7.org/fhir/CodeSystem/medicationdispense-status-reason",
        "code" : "outofstock",
        "display" : "Drug not available - out of stock"
      }]
    }
  },
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
