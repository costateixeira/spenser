# Example - Changing a unit's settings from afar - Spenser - a developer's companion v1.0.0

## Exemple Task: Example - Changing a unit's settings from afar

-------

**French**

-------

**status**: Requested

**intent**: order

**code**: Configure

**focus**: [Device : identifier = http://costateixeira.github.io/spenser/unit#Spenser-E3D4; status = active; manufacturer = Spenser](Device-Spenser-E3D4.md)

### RequestedPerformers

| | |
| :--- | :--- |
| - | **Reference** |
| * | Spenser-E3D4 (Identifier:`http://costateixeira.github.io/spenser/unit`/Spenser-E3D4) |

> **input****type**: pollSeconds**value**: 60

> **input****type**: serverUrl**value**: http://spenser.178.104.103.200.sslip.io/fhir/r5



## Resource Content

```json
{
  "resourceType" : "Task",
  "id" : "ConfigureSpenserE3D4",
  "status" : "requested",
  "intent" : "order",
  "code" : {
    "coding" : [{
      "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserTaskCodes",
      "code" : "configure",
      "display" : "Configure"
    }]
  },
  "focus" : {
    "reference" : "Device/Spenser-E3D4"
  },
  "requestedPerformer" : [{
    "reference" : {
      "identifier" : {
        "system" : "http://costateixeira.github.io/spenser/unit",
        "value" : "Spenser-E3D4"
      },
      "display" : "Spenser-E3D4"
    }
  }],
  "input" : [{
    "type" : {
      "text" : "pollSeconds"
    },
    "valueInteger" : 60
  },
  {
    "type" : {
      "text" : "serverUrl"
    },
    "valueString" : "http://spenser.178.104.103.200.sslip.io/fhir/r5"
  }]
}

```
