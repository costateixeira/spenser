# Exemple - Ordonnance rendue exécutable par un tag - Spenser - a developer's companion v1.0.0

## Exemple MedicationRequest: Exemple - Ordonnance rendue exécutable par un tag

-------

**French**

-------

Profil: [SpenserRequest](StructureDefinition-SpenserRequest.md)

Balise: [Actionable (Détails : code Common Tags actionable = 'Actionable')](http://terminology.hl7.org/7.5.0/CodeSystem-common-tags.html)

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
  "id" : "ActionableDarkOrder",
  "meta" : {
    "profile" : ["http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest"],
    "tag" : [{
      "system" : "http://terminology.hl7.org/CodeSystem/common-tags",
      "code" : "actionable"
    }]
  },
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
