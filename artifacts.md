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
| [Example - Set inventory - 17 Dark Chocolates](InventoryReport-SetDarkTo17.md) | Example - Set inventory - 17 Dark Chocolates |
| [Example - Spenser Request](MedicationRequest-med-request-1234.md) | Example of a MedicationRequest to send to Spenser |

