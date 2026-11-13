# Médicaments Spenser - Système de codes - Spenser - a developer's companion v1.0.0

## CodeSystem: Médicaments Spenser - Système de codes 

Ce système de codes est référencé dans la définition des ensembles de valeurs suivants :

* [Spenser Medications - ValueSet](ValueSet-SpenserMedsVS.md)

-------

 [Description du (des) tableau(x) ci-dessus](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#terminology). 



## Resource Content

```json
{
  "resourceType" : "CodeSystem",
  "id" : "SpenserMeds",
  "url" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
  "version" : "1.0.0",
  "name" : "SpenserMeds",
  "_name" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "SpenserMeds"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    },
    {
      "extension" : [{
        "url" : "lang",
        "valueCode" : "nl"
      },
      {
        "url" : "content",
        "valueString" : "SpenserMeds"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    },
    {
      "extension" : [{
        "url" : "lang",
        "valueCode" : "fr"
      },
      {
        "url" : "content",
        "valueString" : "SpenserMeds"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
  "title" : "Spenser Medications - Code System",
  "_title" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Medicamentos Spenser - Sistema de códigos"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    },
    {
      "extension" : [{
        "url" : "lang",
        "valueCode" : "nl"
      },
      {
        "url" : "content",
        "valueString" : "Spenser-geneesmiddelen - Codesysteem"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    },
    {
      "extension" : [{
        "url" : "lang",
        "valueCode" : "fr"
      },
      {
        "url" : "content",
        "valueString" : "Médicaments Spenser - Système de codes"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
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
  "description" : "A code system of medications that Spenser can dispense.",
  "_description" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Um sistema de códigos dos medicamentos que o Spenser pode dispensar."
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    },
    {
      "extension" : [{
        "url" : "lang",
        "valueCode" : "nl"
      },
      {
        "url" : "content",
        "valueString" : "Een codesysteem van geneesmiddelen die Spenser kan verstrekken."
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    },
    {
      "extension" : [{
        "url" : "lang",
        "valueCode" : "fr"
      },
      {
        "url" : "content",
        "valueString" : "Un système de codes des médicaments que Spenser peut dispenser."
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
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
    "display" : "Dark Chocolate",
    "designation" : [{
      "language" : "pt",
      "value" : "Chocolate negro"
    },
    {
      "language" : "nl",
      "value" : "Pure chocolade"
    },
    {
      "language" : "fr",
      "value" : "Chocolat noir"
    }]
  },
  {
    "code" : "chocolate-milk",
    "display" : "Milk Chocolate",
    "designation" : [{
      "language" : "pt",
      "value" : "Chocolate de leite"
    },
    {
      "language" : "nl",
      "value" : "Melkchocolade"
    },
    {
      "language" : "fr",
      "value" : "Chocolat au lait"
    }]
  }]
}

```
