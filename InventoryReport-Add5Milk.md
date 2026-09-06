# Example - Add to inventory - 5 Milk Chocolates - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Example - Add to inventory - 5 Milk Chocolates**

## Example InventoryReport: Example - Add to inventory - 5 Milk Chocolates

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
