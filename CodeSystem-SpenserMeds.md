# Spenser Medications - Code System - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Spenser Medications - Code System**

## CodeSystem: Spenser Medications - Code System 

| | |
| :--- | :--- |
| *Official URL*:http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds | *Version*:1.0.0 |
| Active as of 2026-09-06 | *Computable Name*:SpenserMeds |

 
A code system of medications that Spenser can dispense. 

 This Code system is referenced in the content logical definition of the following value sets: 

* [Spenser Medications - ValueSet](ValueSet-SpenserMedsVS.md)



## Resource Content

```json
{
  "resourceType" : "CodeSystem",
  "id" : "SpenserMeds",
  "url" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
  "version" : "1.0.0",
  "name" : "SpenserMeds",
  "title" : "Spenser Medications - Code System",
  "status" : "active",
  "date" : "2026-09-06T10:57:27+00:00",
  "publisher" : "Zeora",
  "contact" : [{
    "name" : "Zeora",
    "telecom" : [{
      "system" : "url",
      "value" : "http://example.com/committees"
    },
    {
      "system" : "email",
      "value" : "my-group@example.com"
    }]
  },
  {
    "name" : "José Costa Teixeira",
    "telecom" : [{
      "system" : "email",
      "value" : "you-know.it@gmail.com",
      "use" : "work"
    }]
  }],
  "description" : "A code system of medications that Spenser can dispense.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "content" : "complete",
  "count" : 2,
  "concept" : [{
    "code" : "chocolate-dark",
    "display" : "Dark Chocolate"
  },
  {
    "code" : "chocolate-milk",
    "display" : "Milk Chocolate"
  }]
}

```
