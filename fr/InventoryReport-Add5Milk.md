# Exemple - Ajout au stock - 5 chocolats au lait - Spenser - a developer's companion v1.0.0

## Exemple InventoryReport: Exemple - Ajout au stock - 5 chocolats au lait

-------

**French**

-------

**status**: Draft

**countType**: Difference

**reportedDateTime**: 2025-05-01 12:00:00+0000

> **inventoryListing****location**: Bin 1**itemStatus**: available
> **item****quantity**: 5 pieces

### Items

| | |
| :--- | :--- |
| - | **Concept** |
| * | Milk chocolate |





## Resource Content

```json
{
  "resourceType" : "InventoryReport",
  "id" : "Add5Milk",
  "status" : "draft",
  "countType" : "difference",
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
        "value" : 5,
        "unit" : "pieces"
      },
      "item" : {
        "concept" : {
          "coding" : [{
            "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
            "code" : "chocolate-milk",
            "display" : "Milk chocolate"
          }]
        }
      }
    }]
  }]
}

```
