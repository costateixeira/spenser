# Example - Tagged order for one unit - Spenser - a developer's companion v1.0.0

## Exemple MedicationRequest: Example - Tagged order for one unit

-------

**French**

-------

Profil: [SpenserRequest](StructureDefinition-SpenserRequest.md)

Balise: [Actionable (Détails : code Common Tags actionable = 'Actionable')](http://terminology.hl7.org/7.5.0/CodeSystem-common-tags.html)

**Dispensing device**: Spenser-E3D4 (Identifier: `http://costateixeira.github.io/spenser/unit`/Spenser-E3D4)

**status**: Active

**intent**: Instance Order

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Dark Chocolate |

**subject**: [Patient/123](Patient/123)

### DosageInstructions

| | |
| :--- | :--- |
| - | **Text** |
| * | One bite |



## Resource Content

```json
{
  "resourceType" : "MedicationRequest",
  "id" : "ActionableDarkOrderForOneUnit",
  "meta" : {
    "profile" : ["http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest"],
    "tag" : [{
      "system" : "http://terminology.hl7.org/CodeSystem/common-tags",
      "code" : "actionable"
    }]
  },
  "extension" : [{
    "url" : "http://costateixeira.github.io/spenser/StructureDefinition/dispensingDevice",
    "valueReference" : {
      "identifier" : {
        "system" : "http://costateixeira.github.io/spenser/unit",
        "value" : "Spenser-E3D4"
      },
      "display" : "Spenser-E3D4"
    }
  }],
  "status" : "active",
  "intent" : "instance-order",
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
  "dosageInstruction" : [{
    "text" : "One bite"
  }]
}

```
