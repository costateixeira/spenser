# Unit-eigenaar - Spenser - a developer's companion v1.0.0

## ActorDefinition: Unit-eigenaar 



## Resource Content

```json
{
  "resourceType" : "ActorDefinition",
  "id" : "UnitOwner",
  "url" : "http://costateixeira.github.io/spenser/ActorDefinition/UnitOwner",
  "version" : "1.0.0",
  "name" : "UnitOwner",
  "_name" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "UnitOwner"
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
        "valueString" : "UnitOwner"
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
        "valueString" : "UnitOwner"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
  "title" : "Unit Owner",
  "_title" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Proprietário da Unidade"
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
        "valueString" : "Unit-eigenaar"
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
        "valueString" : "Propriétaire de l'unité"
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
  "description" : "The person who holds a unit's key, and with it the authority to configure, restock and update the unit.",
  "_description" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "A pessoa que detém a chave de uma unidade e, com ela, a autoridade para configurar, reabastecer e atualizar a unidade."
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
        "valueString" : "De persoon die de sleutel van een unit heeft, en daarmee de bevoegdheid om de unit te configureren, te bevoorraden en te updaten."
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
        "valueString" : "La personne qui détient la clé d'une unité, et avec elle le pouvoir de configurer, de réapprovisionner et de mettre à jour l'unité."
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
  "type" : "person",
  "documentation" : "Reading a unit is open, but changing one needs its key. A script acting with the key acts as the owner.\n\nSee [What needs a key](interfaces.html#what-needs-a-key)."
}

```
