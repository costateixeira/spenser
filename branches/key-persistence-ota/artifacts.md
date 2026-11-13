# Artifacts Summary - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* **Artifacts Summary**

## Artifacts Summary

This page provides a list of the FHIR artifacts defined as part of this implementation guide.

### Behavior: Capability Statements 

The following artifacts define the specific capabilities that different types of systems are expected to have in order to comply with this implementation guide. Systems conforming to this implementation guide are expected to declare conformance to one or more of the following capability statements.

| |
| :--- |
| [SpenserFHIRCapabilityStatement](CapabilityStatement-SpenserFHIRCapabilityStatement.md) |

### Structures: Resource Profiles 

These define constraints on FHIR resources for systems conforming to this implementation guide.

| |
| :--- |
| [SpenserRequest](StructureDefinition-SpenserRequest.md) |

### Terminology: Value Sets 

These define sets of codes used by systems conforming to this implementation guide.

| | |
| :--- | :--- |
| [Spenser Medications - ValueSet](ValueSet-SpenserMedsVS.md) | A value set of medications that Spenser can dispense. |

### Terminology: Code Systems 

These define new code systems used by systems conforming to this implementation guide.

| | |
| :--- | :--- |
| [Spenser Medications - Code System](CodeSystem-SpenserMeds.md) | A code system of medications that Spenser can dispense. |

### Example: Example Instances 

These are example instances that show what data produced and consumed by systems conforming with this implementation guide might look like.

| | |
| :--- | :--- |
| [Example - Add to inventory - 5 Milk Chocolates](InventoryReport-Add5Milk.md) | Example - Add to inventory - 5 Milk Chocolates |
| [Example - Dispense reported back](MedicationDispense-DispenseForActionableDarkOrder.md) | What Spenser creates on the order server once a piece has come out, pointing back at the order in authorizingPrescription. The same resource is the answer to an order posted straight at the device. |
| [Example - Dispense that did not happen](MedicationDispense-DeclinedDispenseOutOfStock.md) | An order Spenser could not fill because the lane is empty. R5 removed MedicationDispense.statusReason, so the reason lives in notPerformedReason, which is a CodeableReference - hence the .concept in the path. |
| [Example - Order made actionable by a tag](MedicationRequest-ActionableDarkOrder.md) | A MedicationRequest the placer has marked actionable. Spenser dispenses it on its next check and, because no Task is coordinating the work, sets the request itself to completed. |
| [Example - Order that is not actionable on its own](MedicationRequest-PlainMilkOrder.md) | The same order without the tag. On its own this is an authorization and nothing more: Spenser ignores it until a Task asks for it to be fulfilled. |
| [Example - Set inventory - 17 Dark Chocolates](InventoryReport-SetDarkTo17.md) | Example - Set inventory - 17 Dark Chocolates |
| [Example - Spenser Request](MedicationRequest-med-request-1234.md) | Example of a MedicationRequest to send to Spenser |
| [Example - Task asking for an order to be fulfilled](Task-FulfillPlainMilkOrder.md) | A Coordination Task pointing at the order in Task.focus. This is what makes the plain order actionable. Spenser completes the Task with the dispense in Task.output, and leaves the request itself to the placer. |

