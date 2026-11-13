# Servidor de Prescrições - Spenser - a developer's companion v1.0.0

## ActorDefinition: Servidor de Prescrições 



## Resource Content

```json
{
  "resourceType" : "ActorDefinition",
  "id" : "OrderServer",
  "url" : "http://costateixeira.github.io/spenser/ActorDefinition/OrderServer",
  "version" : "1.0.0",
  "name" : "OrderServer",
  "_name" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "OrderServer"
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
        "valueString" : "OrderServer"
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
        "valueString" : "OrderServer"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
  "title" : "Order Server",
  "_title" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Servidor de Prescrições"
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
        "valueString" : "Orderserver"
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
        "valueString" : "Serveur d'ordonnances"
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
  "description" : "A FHIR server that holds orders until a Spenser Unit collects them, and receives what the unit reports back.",
  "_description" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Um servidor FHIR que guarda as prescrições até uma Unidade Spenser as recolher, e recebe o que a unidade comunica de volta."
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
        "valueString" : "Een FHIR-server die orders bewaart tot een Spenser-unit ze ophaalt, en ontvangt wat de unit terugmeldt."
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
        "valueString" : "Un serveur FHIR qui conserve les ordonnances jusqu'à ce qu'une unité Spenser vienne les chercher, et reçoit les comptes rendus de l'unité."
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
  "documentation" : "Answers the unit's searches for tagged MedicationRequests and for requested Tasks, including `_include=Task:focus`. Accepts the MedicationDispense the unit creates and the updates it makes to the Task or MedicationRequest.\n\nSee [What Spenser asks of an order server](interfaces.html#what-spenser-asks-of-an-order-server)."
}

```
