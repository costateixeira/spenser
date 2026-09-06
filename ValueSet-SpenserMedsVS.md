# Spenser Medications - ValueSet - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Spenser Medications - ValueSet**

## ValueSet: Spenser Medications - ValueSet 

| | |
| :--- | :--- |
| *Official URL*:http://costateixeira.github.io/spenser/ValueSet/SpenserMedsVS | *Version*:1.0.0 |
| Active as of 2026-09-06 | *Computable Name*:SpenserMedsVS |

 
A value set of medications that Spenser can dispense. 

 **References** 

* [SpenserRequest](StructureDefinition-SpenserRequest.md)

### Logical Definition (CLD)

 

### Expansion

-------

 Explanation of the columns that may appear on this page: 

| | |
| :--- | :--- |
| Level | A few code lists that FHIR defines are hierarchical - each code is assigned a level. In this scheme, some codes are under other codes, and imply that the code they are under also applies |
| System | The source of the definition of the code (when the value set draws in codes defined elsewhere) |
| Code | The code (used as the code in the resource instance) |
| Display | The display (used in the*display*element of a[Coding](http://hl7.org/fhir/R5/datatypes.html#Coding)). If there is no display, implementers should not simply display the code, but map the concept into their application |
| Definition | An explanation of the meaning of the concept |
| Comments | Additional notes about how to use the code |



## Resource Content

```json
{
  "resourceType" : "ValueSet",
  "id" : "SpenserMedsVS",
  "url" : "http://costateixeira.github.io/spenser/ValueSet/SpenserMedsVS",
  "version" : "1.0.0",
  "name" : "SpenserMedsVS",
  "title" : "Spenser Medications - ValueSet",
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
  "description" : "A value set of medications that Spenser can dispense.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "compose" : {
    "include" : [{
      "system" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds"
    }]
  }
}

```
