# Exemple - Définition du stock - 17 chocolats noirs - Spenser - a developer's companion v1.0.0

## Exemple InventoryReport: Exemple - Définition du stock - 17 chocolats noirs

-------

**French**

-------

**status**: Draft

**countType**: Snapshot

**reportedDateTime**: 2025-05-01 12:00:00+0000

> **inventoryListing****location**: Bin 1**itemStatus**: available
> **item****quantity**: 17 pieces

### Items

| | |
| :--- | :--- |
| - | **Concept** |
| * | Dark chocolate |





## Resource Content

```json
{
  "resourceType" : "InventoryReport",
  "id" : "SetDarkTo17",
  "status" : "draft",
  "countType" : "snapshot",
  "reportedDateTime" : "2025-05-01T12:00:00Z",
  "inventoryListing" : [{
    "location" : {
      "display" : "Bin 1"
    },
    "itemStatus" : {
      "coding" : [{
        "code" : "available"
      }]
    },
    "item" : [{
      "quantity" : {
        "value" : 17,
        "unit" : "pieces"
      },
      "item" : {
        "concept" : {
          "coding" : [{
            "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
            "code" : "chocolate-dark",
            "display" : "Dark chocolate"
          }]
        }
      }
    }]
  }]
}

```
