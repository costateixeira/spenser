# Example - Task addressed to one unit - Spenser - a developer's companion v1.0.0

## Exemplo Task: Example - Task addressed to one unit

-------

**Portuguese**

-------

**status**: Requested

**intent**: order

**code**: Fulfill the focal request

**focus**: [MedicationRequest: extension = ->Spenser-E3D4; status = active; intent = instance-order](MedicationRequest-PlainDarkOrderForOneUnit.md)

**for**: [Patient/123](Patient/123)

### RequestedPerformers

| | |
| :--- | :--- |
| - | **Reference** |
| * | [Spenser-E3D4](Device-Spenser-E3D4.md) |



## Resource Content

```json
{
  "resourceType" : "Task",
  "id" : "FulfillForOneUnit",
  "status" : "requested",
  "intent" : "order",
  "code" : {
    "coding" : [{
      "system" : "http://hl7.org/fhir/CodeSystem/task-code",
      "code" : "fulfill",
      "display" : "Fulfill the focal request"
    }]
  },
  "focus" : {
    "reference" : "MedicationRequest/PlainDarkOrderForOneUnit"
  },
  "for" : {
    "reference" : "Patient/123"
  },
  "requestedPerformer" : [{
    "reference" : {
      "reference" : "Device/Spenser-E3D4",
      "display" : "Spenser-E3D4"
    }
  }]
}

```
