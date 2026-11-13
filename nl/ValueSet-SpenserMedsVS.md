# Spenser-geneesmiddelen - ValueSet - Spenser - a developer's companion v1.0.0

## ValueSet: Spenser Medications - ValueSet 

 **References** 

* [SpenserRequest](StructureDefinition-SpenserRequest.md)

### Logische definitie (CLD)

 

### Uitbreiding

-------

 [Beschrijving van bovenstaande tabel(len)](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#terminology). 



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
  "date" : "2026-11-13T21:21:03+00:00",
  "publisher" : "José Costa Teixeira",
  "contact" : [{
    "name" : "José Costa Teixeira",
    "telecom" : [{
      "system" : "url",
      "value" : "https://github.com/costateixeira"
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
