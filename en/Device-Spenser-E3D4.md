# Example - A Spenser unit on the order server - Spenser - a developer's companion v1.0.0

## Example Device: Example - A Spenser unit on the order server

-------

**English**

-------

**identifier**: `http://costateixeira.github.io/spenser/unit`/Spenser-E3D4

**status**: Active

**manufacturer**: Spenser

### Names

| | | |
| :--- | :--- | :--- |
| - | **Value** | **Type** |
| * | Spenser-E3D4 | User Friendly name |

### Versions

| | |
| :--- | :--- |
| - | **Value** |
| * | 1.3.0 |

> **property****type**: Order server**value**: http://spenser.178.104.103.200.sslip.io/fhir/r5

> **property****type**: Order mode**value**: both

> **property****type**: Polling**value**: true

> **property****type**: Poll interval**value**: 30

> **property****type**: Dark stock**value**: 12

> **property****type**: Milk stock**value**: 15

> **property****type**: Last check**value**: No new orders

> **property****type**: IP address**value**: 192.168.1.50



## Resource Content

```json
{
  "resourceType" : "Device",
  "id" : "Spenser-E3D4",
  "identifier" : [{
    "system" : "http://costateixeira.github.io/spenser/unit",
    "value" : "Spenser-E3D4"
  }],
  "status" : "active",
  "manufacturer" : "Spenser",
  "name" : [{
    "value" : "Spenser-E3D4",
    "type" : "user-friendly-name"
  }],
  "version" : [{
    "value" : "1.3.0"
  }],
  "property" : [{
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "server-url"
      }]
    },
    "valueString" : "http://spenser.178.104.103.200.sslip.io/fhir/r5"
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "order-mode"
      }]
    },
    "valueString" : "both"
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "poll-enabled"
      }]
    },
    "valueBoolean" : true
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "poll-seconds"
      }]
    },
    "valueInteger" : 30
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "stock-dark"
      }]
    },
    "valueInteger" : 12
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "stock-milk"
      }]
    },
    "valueInteger" : 15
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "last-check"
      }]
    },
    "valueString" : "No new orders"
  },
  {
    "type" : {
      "coding" : [{
        "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
        "code" : "ip-address"
      }]
    },
    "valueString" : "192.168.1.50"
  }]
}

```
