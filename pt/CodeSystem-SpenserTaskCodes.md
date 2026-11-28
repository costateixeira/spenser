# Spenser Task Codes - Spenser - a developer's companion v1.0.0

## CodeSystem: Spenser Task Codes (Experimental) 

Este sistema de códigos é referenciado na definição dos seguintes conjuntos de valores:

* Este CodeSystem não é utilizado aqui; pode ser utilizado noutro local (por exemplo, em especificações e/ou implementações que utilizem este conteúdo)

-------

 [Descrição do(s) quadro(s) acima](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#terminology). 



## Resource Content

```json
{
  "resourceType" : "CodeSystem",
  "id" : "SpenserTaskCodes",
  "url" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserTaskCodes",
  "version" : "1.0.0",
  "name" : "SpenserTaskCodes",
  "title" : "Spenser Task Codes",
  "status" : "draft",
  "experimental" : true,
  "date" : "2026-11-26T15:58:54+00:00",
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
  "description" : "Task codes for work asked of a Spenser unit other than dispensing.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "caseSensitive" : true,
  "content" : "complete",
  "count" : 1,
  "concept" : [{
    "code" : "configure",
    "display" : "Configure",
    "definition" : "Change the settings of the unit named in requestedPerformer. Each input is one setting: input.type names it, input.value[x] holds the value. The unit applies them all or none."
  }]
}

```
