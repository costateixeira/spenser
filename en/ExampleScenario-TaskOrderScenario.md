# Scenario - Ordering through an order server - Spenser - a developer's companion v1.0.0

## ExampleScenario: Scenario - Ordering through an order server (Experimental) 

### Actors

### Diagram

### Processes

### Instances



## Resource Content

```json
{
  "resourceType" : "ExampleScenario",
  "id" : "TaskOrderScenario",
  "url" : "http://costateixeira.github.io/spenser/ExampleScenario/TaskOrderScenario",
  "version" : "1.0.0",
  "name" : "TaskOrderScenario",
  "title" : "Ordering through an order server",
  "status" : "active",
  "experimental" : true,
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
  "description" : "A placer puts an order and a Task on an order server. The unit polls the server, dispenses what is addressed to it, and reports back what it did.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
      "code" : "001",
      "display" : "World"
    }]
  }],
  "purpose" : "The long way round, and the one that behaves like a real workflow.\n\nAn order on a server is an authorization: it says a chocolate may be dispensed,\nnot that one should be dispensed now. Something else has to ask for it to be\nfulfilled. A Task is that something, and `Task.requestedPerformer` is the only\nplace in R5 that can name the Device meant to do the work.\n\nThe unit is never connected to from outside here. It polls, which is what lets\na dispenser sit on a conference network with nothing open to it.",
  "actor" : [{
    "key" : "placer",
    "type" : "system",
    "title" : "Order Placer",
    "description" : "Creates the order and the Task, and closes the order once the Task is done. A Task closes itself; a MedicationRequest does not."
  },
  {
    "key" : "server",
    "type" : "system",
    "title" : "Order Server",
    "description" : "A plain FHIR server. It holds the order and the Task until a unit collects them, and it has to answer `_include=Task:focus`."
  },
  {
    "key" : "spenser",
    "type" : "system",
    "title" : "Spenser Unit",
    "description" : "Acting here as a FHIR client. It takes only the work addressed to it and leaves everything else alone."
  }],
  "instance" : [{
    "key" : "order",
    "structureType" : {
      "system" : "http://hl7.org/fhir/fhir-types",
      "code" : "MedicationRequest"
    },
    "structureProfileCanonical" : "http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest",
    "title" : "The order",
    "description" : "An untagged MedicationRequest, naming the unit meant to fill it in the `dispensingDevice` extension. On its own it sits there.",
    "content" : {
      "reference" : "MedicationRequest/PlainDarkOrderForOneUnit"
    },
    "version" : [{
      "key" : "order-active",
      "title" : "active",
      "description" : "As created: authorized, and not yet filled.",
      "content" : {
        "reference" : "MedicationRequest/PlainDarkOrderForOneUnit"
      }
    },
    {
      "key" : "order-completed",
      "title" : "completed",
      "description" : "After the placer closes it. The unit does not touch the order while a Task is coordinating the work."
    }]
  },
  {
    "key" : "task",
    "structureType" : {
      "system" : "http://hl7.org/fhir/fhir-types",
      "code" : "Task"
    },
    "title" : "The Task",
    "description" : "A `fulfill` Task whose `focus` is the order and whose `requestedPerformer` is the unit. This is what makes the order actionable.",
    "content" : {
      "reference" : "Task/FulfillForOneUnit"
    },
    "version" : [{
      "key" : "task-requested",
      "title" : "requested",
      "description" : "As created. Every other unit polling the same server skips it.",
      "content" : {
        "reference" : "Task/FulfillForOneUnit"
      }
    },
    {
      "key" : "task-completed",
      "title" : "completed",
      "description" : "After the chocolate came out, with the dispense in `Task.output`."
    }]
  },
  {
    "key" : "dispense",
    "structureType" : {
      "system" : "http://hl7.org/fhir/fhir-types",
      "code" : "MedicationDispense"
    },
    "title" : "The dispense",
    "description" : "What the unit writes back, naming itself as `performer` and the order in `authorizingPrescription`.",
    "content" : {
      "reference" : "MedicationDispense/DispenseForTaskOrder"
    }
  }],
  "process" : [{
    "title" : "Order a chocolate through an order server",
    "description" : "Place the work, let the unit find it, and read back what it did.",
    "preConditions" : "The unit has been pointed at the order server and its polling is on. The unit has written its own Device on the server, so a Task can name it.",
    "postConditions" : "A chocolate has been dispensed, the dispense is on the server, the Task is completed, and the order is closed.",
    "step" : [{
      "number" : "1",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "create"
        },
        "title" : "POST /MedicationRequest",
        "initiator" : "placer",
        "receiver" : "server",
        "description" : "Nothing happens yet, and that is the point.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "request" : {
          "instanceReference" : "order",
          "versionReference" : "order-active"
        }
      }
    },
    {
      "number" : "2",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "create"
        },
        "title" : "POST /Task",
        "initiator" : "placer",
        "receiver" : "server",
        "description" : "`code` is `fulfill`, `focus` is the order, `requestedPerformer` is the unit. Leave `requestedPerformer` out and any unit polling that server may take it.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "request" : {
          "instanceReference" : "task",
          "versionReference" : "task-requested"
        }
      },
      "alternative" : [{
        "title" : "Tag the order instead of creating a Task",
        "description" : "Put `actionable` from common-tags in the order's `meta.tag` and skip the Task. A unit accepts both routes on every check, and `orderMode` narrows it to one. With no Task coordinating the work the unit completes the MedicationRequest itself, and step 6 does not happen."
      }]
    },
    {
      "number" : "3",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "search-type"
        },
        "title" : "GET /Task",
        "initiator" : "spenser",
        "receiver" : "server",
        "description" : "`GET /Task?status=requested&_include=Task:focus&_count=5`. The unit polls on a timer, and a check can also be asked for by hand. Each check looks at the first five results only, so a long queue on the server can outrun one check. The unit remembers what it has already dealt with.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "response" : {
          "instanceReference" : "task",
          "versionReference" : "task-requested"
        }
      }
    },
    {
      "number" : "4",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "create"
        },
        "title" : "POST /MedicationDispense",
        "initiator" : "spenser",
        "receiver" : "server",
        "description" : "The servo turns and a piece drops out, and then the unit says so. The write is queued and retried, so a server that was briefly unreachable does not cost the record.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "request" : {
          "instanceReference" : "dispense"
        }
      },
      "alternative" : [{
        "title" : "The lane is empty",
        "description" : "The unit writes a dispense with `status` of `declined` and `notPerformedReason.concept` of `outofstock`. Whether the Task is then left open, so a refill retries it, or closed as failed, is the unit's `keepOrders` setting."
      }]
    },
    {
      "number" : "5",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "update"
        },
        "title" : "PUT /Task",
        "initiator" : "spenser",
        "receiver" : "server",
        "description" : "`PUT /Task/<id>`: `status` becomes `completed`, with the dispense in `Task.output`. Sent with `If-Match`, so a Task somebody else has moved on is not overwritten.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "request" : {
          "instanceReference" : "task",
          "versionReference" : "task-completed"
        }
      }
    },
    {
      "number" : "6",
      "operation" : {
        "type" : {
          "system" : "http://hl7.org/fhir/restful-interaction",
          "code" : "update"
        },
        "title" : "PUT /MedicationRequest",
        "initiator" : "placer",
        "receiver" : "server",
        "description" : "`PUT /MedicationRequest/<id>`. The placer closes its own order. The unit does not: it was asked to fill one Task, and it has no way of knowing whether the order authorized more than that.",
        "initiatorActive" : true,
        "receiverActive" : true,
        "request" : {
          "instanceReference" : "order",
          "versionReference" : "order-completed"
        }
      }
    }]
  }]
}

```
