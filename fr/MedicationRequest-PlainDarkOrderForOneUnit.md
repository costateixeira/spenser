# Example - Order meant for one unit - Spenser - a developer's companion v1.0.0

## Exemple MedicationRequest: Example - Order meant for one unit

-------

**French**

-------

Profil: [SpenserRequest](StructureDefinition-SpenserRequest.md)

**Dispensing device**: Spenser-E3D4 (Identifier: `http://costateixeira.github.io/spenser/unit`/Spenser-E3D4)

**status**: Active

**intent**: Instance Order

### Medications

| | |
| :--- | :--- |
| - | **Concept** |
| * | Dark Chocolate |

**subject**: [Patient/123](Patient/123)



## Resource Content

```json
{
  "resourceType" : "MedicationRequest",
  "id" : "PlainDarkOrderForOneUnit",
  "meta" : {
    "profile" : ["http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest"]
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
  }
}

```
