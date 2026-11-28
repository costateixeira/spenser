# Spenser Unit Properties - Spenser - a developer's companion v1.0.0

## CodeSystem: Spenser Unit Properties (Experimental) 

Este sistema de códigos é referenciado na definição dos seguintes conjuntos de valores:

* Este CodeSystem não é utilizado aqui; pode ser utilizado noutro local (por exemplo, em especificações e/ou implementações que utilizem este conteúdo)

-------

 [Descrição do(s) quadro(s) acima](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#terminology). 



## Resource Content

```json
{
  "resourceType" : "CodeSystem",
  "id" : "SpenserUnitProperty",
  "url" : "http://costateixeira.github.io/spenser/CodeSystem/SpenserUnitProperty",
  "version" : "1.0.0",
  "name" : "SpenserUnitProperty",
  "title" : "Spenser Unit Properties",
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
  "description" : "What a Spenser unit reports about itself in Device.property on the order server: its settings and its state. Written on the first check against a server, after a change of settings, and every ten minutes.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "caseSensitive" : true,
  "content" : "complete",
  "count" : 18,
  "concept" : [{
    "code" : "server-url",
    "display" : "Order server",
    "definition" : "The FHIR base URL the unit polls for orders."
  },
  {
    "code" : "order-mode",
    "display" : "Order mode",
    "definition" : "Which routes make an order actionable for this unit: both, tag or task."
  },
  {
    "code" : "order-query",
    "display" : "Order search",
    "definition" : "Extra search parameters for tagged orders."
  },
  {
    "code" : "task-query",
    "display" : "Task search",
    "definition" : "Extra search parameters for Tasks."
  },
  {
    "code" : "poll-enabled",
    "display" : "Polling",
    "definition" : "Whether the unit checks the order server on its own."
  },
  {
    "code" : "poll-seconds",
    "display" : "Poll interval",
    "definition" : "Seconds between checks."
  },
  {
    "code" : "write-back",
    "display" : "Write back",
    "definition" : "Whether the unit reports dispenses and closes orders on the server."
  },
  {
    "code" : "give-up-on-stock-empty",
    "display" : "Give up when empty",
    "definition" : "Whether an order for an empty lane is abandoned rather than retried after a refill."
  },
  {
    "code" : "update-mode",
    "display" : "Update mode",
    "definition" : "notify, or install firmware updates on its own."
  },
  {
    "code" : "update-check-minutes",
    "display" : "Update check interval",
    "definition" : "Minutes between looks at the release manifest."
  },
  {
    "code" : "stock-dark",
    "display" : "Dark stock",
    "definition" : "Pieces of dark chocolate the unit believes it holds."
  },
  {
    "code" : "stock-milk",
    "display" : "Milk stock",
    "definition" : "Pieces of milk chocolate the unit believes it holds."
  },
  {
    "code" : "last-check",
    "display" : "Last check",
    "definition" : "What the last order check reported."
  },
  {
    "code" : "last-configuration",
    "display" : "Last configuration",
    "definition" : "What the last configuration Task did."
  },
  {
    "code" : "ssid",
    "display" : "Wi-Fi network",
    "definition" : "The Wi-Fi network the unit is on."
  },
  {
    "code" : "ip-address",
    "display" : "IP address",
    "definition" : "The unit's address on its own network."
  },
  {
    "code" : "rssi",
    "display" : "Signal",
    "definition" : "Wi-Fi signal strength, in dBm."
  },
  {
    "code" : "largest-free-block",
    "display" : "Largest free block",
    "definition" : "The largest block of free memory, in bytes. A TLS connection needs about 40 KB in one piece."
  }]
}

```
