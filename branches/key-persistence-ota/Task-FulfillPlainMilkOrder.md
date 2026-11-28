# Example - Task asking for an order to be fulfilled - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Example - Task asking for an order to be fulfilled**

## Example Task: Example - Task asking for an order to be fulfilled

**identifier**: `http://example.org/spenser-orders`/demo-1

**status**: Requested

**intent**: order

**code**: Fulfill the focal request

**focus**: [MedicationRequest: status = active; intent = instance-order](MedicationRequest-PlainMilkOrder.md)

**for**: [Patient/123](Patient/123)



## Resource Content

```json
{
  "resourceType" : "Task",
  "id" : "FulfillPlainMilkOrder",
  "identifier" : [{
    "system" : "http://example.org/spenser-orders",
    "value" : "demo-1"
  }],
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
    "reference" : "MedicationRequest/PlainMilkOrder"
  },
  "for" : {
    "reference" : "Patient/123"
  }
}

```
