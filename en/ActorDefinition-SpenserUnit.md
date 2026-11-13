# Spenser Unit - Spenser - a developer's companion v1.0.0

## ActorDefinition: Spenser Unit 



## Resource Content

```json
{
  "resourceType" : "ActorDefinition",
  "id" : "SpenserUnit",
  "url" : "http://costateixeira.github.io/spenser/ActorDefinition/SpenserUnit",
  "version" : "1.0.0",
  "name" : "SpenserUnit",
  "_name" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "SpenserUnit"
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
        "valueString" : "SpenserUnit"
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
        "valueString" : "SpenserUnit"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
  "title" : "Spenser Unit",
  "_title" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Unidade Spenser"
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
        "valueString" : "Spenser-unit"
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
        "valueString" : "Unité Spenser"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
  "status" : "draft",
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
  "description" : "A chocolate dispenser, acting as a FHIR server and a FHIR client at the same time.",
  "_description" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Um dispensador de chocolate, que atua como servidor FHIR e como cliente FHIR ao mesmo tempo."
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
        "valueString" : "Een chocoladedispenser die tegelijk als FHIR-server en als FHIR-client optreedt."
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
        "valueString" : "Un distributeur de chocolat, qui agit à la fois comme serveur FHIR et comme client FHIR."
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
  "type" : "system",
  "documentation" : "A single dispenser. As a **server** it accepts an order posted straight at it and dispenses on the spot, because posting to the device is itself the authorization to dispense. As a **client** it polls an Order Server, acts only on orders that have been made actionable, and reports back what it did.\n\nSee [Interfaces](interfaces.html)."
}

```
