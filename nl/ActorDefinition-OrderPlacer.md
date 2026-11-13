# Orderplaatser - Spenser - a developer's companion v1.0.0

## ActorDefinition: Orderplaatser 



## Resource Content

```json
{
  "resourceType" : "ActorDefinition",
  "id" : "OrderPlacer",
  "url" : "http://costateixeira.github.io/spenser/ActorDefinition/OrderPlacer",
  "version" : "1.0.0",
  "name" : "OrderPlacer",
  "_name" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "OrderPlacer"
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
        "valueString" : "OrderPlacer"
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
        "valueString" : "OrderPlacer"
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  },
  "title" : "Order Placer",
  "_title" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Emissor de Prescrições"
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
        "valueString" : "Orderplaatser"
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
        "valueString" : "Émetteur d'ordonnances"
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
  "description" : "The system that asks for chocolate, by posting an order to a Spenser Unit or by placing one on an Order Server.",
  "_description" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "O sistema que pede chocolate, publicando uma prescrição numa Unidade Spenser ou emitindo-a num Servidor de Prescrições."
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
        "valueString" : "Het systeem dat om chocolade vraagt, door een order naar een Spenser-unit te posten of er een op een orderserver te plaatsen."
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
        "valueString" : "Le système qui demande du chocolat, en envoyant une ordonnance à une unité Spenser ou en en déposant une sur un serveur d'ordonnances."
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
  "documentation" : "On an Order Server, the placer decides whether an order is actionable, either by tagging the MedicationRequest or by creating a Task that points at it. When a Task coordinates the work, the placer also closes the MedicationRequest once the Task is completed.",
  "_documentation" : {
    "extension" : [{
      "extension" : [{
        "url" : "lang",
        "valueCode" : "pt"
      },
      {
        "url" : "content",
        "valueString" : "Num Servidor de Prescrições, o emissor decide se uma prescrição é acionável, quer colocando uma tag na MedicationRequest, quer criando uma Task que aponte para ela. Quando é uma Task a coordenar o trabalho, o emissor também fecha a MedicationRequest depois de a Task estar concluída."
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
        "valueString" : "Op een orderserver beslist de plaatser of een order uitvoerbaar is, door de MedicationRequest een tag te geven of door een Task aan te maken die ernaar verwijst. Als een Task het werk coördineert, sluit de plaatser ook de MedicationRequest af zodra de Task is voltooid."
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
        "valueString" : "Sur un serveur d'ordonnances, l'émetteur décide si une ordonnance est exécutable, soit en apposant un tag sur la MedicationRequest, soit en créant une Task qui pointe vers elle. Quand une Task coordonne le travail, l'émetteur clôture aussi la MedicationRequest une fois la Task terminée."
      }],
      "url" : "http://hl7.org/fhir/StructureDefinition/translation"
    }]
  }
}

```
