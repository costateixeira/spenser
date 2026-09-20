# Interfaces - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* **Interfaces**

## Interfaces

This page documents every interface a Spenser unit exposes: the FHIR ones, the private HTTP API it uses for its own configuration, and the interfaces that are not HTTP at all. It is the reference behind the [Using Spenser](usage.md) page, and the source of truth is the CapabilityStatement each unit publishes at its own `/metadata`.

A unit is reachable on the local network as `http://spenser.local`, which it advertises over mDNS, or at whatever address its router hands it.

### Two roles

Spenser is a FHIR **server** and a FHIR **client** at the same time, and the difference matters when deciding where to send something.

* **As a server**, it accepts an order posted straight at it and dispenses on the spot. Posting to the device is itself the authorization to dispense.
* **As a client**, it polls an order server for orders it should fulfil, and reports back what it did. Here an order is **not** an instruction, and Spenser acts only on orders that have been made actionable.

Both roles are declared in its [CapabilityStatement](CapabilityStatement-SpenserFHIRCapabilityStatement.md).

### What makes an order actionable

Following the HL7 Clinical Orders Workflow guidance, a MedicationRequest sitting on a server is an authorization, not a command. Spenser fulfils it only when one of two things is true:

1. **A tag.**The request carries`meta.tag``http://terminology.hl7.org/CodeSystem/common-tags#actionable`. See[Order made actionable by a tag](MedicationRequest-ActionableDarkOrder.md).
1. **A Task.**A Task with status`requested`points at the request in`Task.focus`. See[Task asking for an order to be fulfilled](Task-FulfillPlainMilkOrder.md), which makes[this plain order](MedicationRequest-PlainMilkOrder.md)actionable.

These are **not two modes of the device**. Spenser looks for both on every check and acts on whichever turns up. When an order arrives by both routes at once the Task takes precedence, and the order is still dispensed exactly once. A unit can be narrowed to one route with the `orderMode` setting, which is useful for demonstrating the difference and for little else.

Who closes the order out depends on which route was used:

| | | |
| :--- | :--- | :--- |
| tag, no Task | the MedicationRequest to`completed` |   |
| a Task | the Task to`completed`, with the dispense in`Task.output` | the MedicationRequest, which stays`active` |

The second row is deliberate. With a Task coordinating the work, closing the request is the placer's job, not the filler's, and a completed Task is the placer's cue to do it.

### FHIR interface

Served by the device itself.

| | |
| :--- | :--- |
| `GET /metadata` | CapabilityStatement for this unit, declaring both roles |
| `POST /MedicationRequest` | dispense now, answering with the MedicationDispense |
| `GET /MedicationDispense` | searchset of recent dispenses, newest first, with an OperationOutcome about the last check |
| `GET /MedicationDispense/{id}` | read one of them |
| `GET /InventoryReport` | current stock, one listing per lane |
| `POST /InventoryReport` | set stock from a report |

`POST /MedicationRequest` answers `200` with a completed [MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.md) when a piece came out, and `201` with a declined one when the lane is empty. R5 removed `MedicationDispense.statusReason`, so a refusal carries its reason in `notPerformedReason`, which is a `CodeableReference`. See [the declined example](MedicationDispense-DeclinedDispenseOutOfStock.md).

`GET /MedicationDispense` is how you ask a unit what it has been doing. Besides the dispenses themselves, the Bundle carries one entry with `search.mode` set to `outcome`: an OperationOutcome whose severity, `issue.diagnostics` and `issue.details.text` describe the last check of the order server, including which routes the unit is accepting and how long ago it looked.

Stock is reported as an [InventoryReport](InventoryReport-SetDarkTo17.md), and can be set the same way, either as a `snapshot` or as a `difference`.

### What Spenser asks of an order server

Point a unit at a server, and on every check it runs two searches and writes back what happened:

```
GET  {server}/Task?status=requested&_include=Task:focus&_count=5
GET  {server}/MedicationRequest?_tag=http://terminology.hl7.org/CodeSystem/common-tags|actionable&status=active&intent=instance-order&_count=5
POST {server}/MedicationDispense
PUT  {server}/Task/{id}
PUT  {server}/MedicationRequest/{id}

```

The `_include` matters: Spenser resolves `Task.focus` from the entries of that one Bundle rather than fetching each order separately, so a Task whose focus is not returned with it is reported as a problem and skipped.

`_count=5` matters when testing. Only the first five results of each search are considered per check, so with a longer queue a given order may not be picked up on a particular check.

Both `http://` and `https://` work. Certificates are not validated, so treat the link as you would any other unauthenticated local traffic.

### Orders you can copy

The IG carries these as formal examples:

* [Order made actionable by a tag](MedicationRequest-ActionableDarkOrder.md)
* [Order that is not actionable on its own](MedicationRequest-PlainMilkOrder.md)
* [Task asking for it to be fulfilled](Task-FulfillPlainMilkOrder.md)
* [Dispense reported back](MedicationDispense-DispenseForActionableDarkOrder.md)
* [Dispense that did not happen](MedicationDispense-DeclinedDispenseOutOfStock.md)
* [Set inventory](InventoryReport-SetDarkTo17.md) and [add to inventory](InventoryReport-Add5Milk.md)

The smallest useful order, placed on the order server:

```
{
  "resourceType": "MedicationRequest",
  "meta": {
    "tag": [
      { "system": "http://terminology.hl7.org/CodeSystem/common-tags",
        "code": "actionable" }
    ]
  },
  "status": "active",
  "intent": "instance-order",
  "medication": {
    "concept": {
      "coding": [
        { "system": "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds",
          "code": "chocolate-dark",
          "display": "Dark Chocolate" }
      ]
    }
  },
  "subject": { "reference": "Patient/123" },
  "dosageInstruction": [ { "text": "One bite" } ]
}

```

The same body without `meta.tag` is the negative case: Spenser must leave it alone. Drop the tag, add a Task pointing at it, and it becomes actionable again by the other route.

Medications come from the [SpenserMeds code system](CodeSystem-SpenserMeds.md): `chocolate-dark` and `chocolate-milk`, one piece per order. R5 puts the code in `medication.concept`; a directly posted order may also use the R4 `medicationCodeableConcept` spelling, which this firmware still accepts.

### Non-FHIR interface

Everything below is the unit's own administrative API. It is plain JSON or text, it is not FHIR, and it is not meant for exchanging clinical data. It exists to configure a unit, to drive it during a demo, and to serve the built-in dashboard.

| | |
| :--- | :--- |
| Orders | `/checkOrders`queues a check and returns`202`,`/orders`reports the last check for the dashboard,`/forgetOrders`clears the list of orders already dealt with |
| Settings | `/settings`,`/setSettings`,`/resetSettings` |
| Stock and hardware | `/inventory`,`/setInventory`,`/resetInventory`,`/setServos`,`/flashServo1`,`/flashServo2`,`/setColor`,`/battery`,`/reset` |
| Wi-Fi and identity | `/`,`/scan`,`/cfg`,`/save`,`/wifi-settings`,`/wifi-reset`,`/wifi-reboot-config`,`/getMac`,`/setMac`,`/clearMac` |
| Captive portal | `/generate_204`,`/hotspot-detect.html`,`/fwlink`,`/ncsi.txt`,`/connecttest.txt` |

`/setSettings` accepts any of `serverUrl`, `orderMode` with values `both`, `tag` or `task`, `orderQuery`, `taskQuery`, `pollEnabled`, `pollSeconds` between 5 and 3600, `writeBack`, `giveUpOnStockEmpty`, and the servo parameters. It answers with the full settings document.

A unit checks its order server every `pollSeconds`, 30 by default, while `pollEnabled` is on. `/checkOrders` forces a check immediately. It returns before the work is done, because the HTTP work happens in the main loop and never inside a request handler, so a client should wait for the check to finish rather than assume it has.

`giveUpOnStockEmpty` decides what happens to an order that cannot be filled. Off, the order is reported once as out of stock and left open, so refilling the lane fulfils it on a later check. On, it is reported once and abandoned, and a coordinating Task is set to `failed`.

Anything not matched falls back to a static file from the device filesystem, which is how the dashboard is served. `OPTIONS` returns `200` for CORS preflight.

### Interfaces that are not HTTP

* **mDNS.** The unit advertises itself as `spenser` with an HTTP service on port 80, so `http://spenser.local` works without knowing its address.
* **Access point and captive portal.** With no Wi-Fi configured it serves an open network and answers every DNS name, so a phone or laptop opens the setup page by itself.
* **Serial.** Logs at 115200 baud, including every order search and write-back.
* **The button.** A short press dispenses. Three seconds is a soft reset. Ten seconds wipes the stored credentials, and the LED turns red while held to warn you before you let go.

### Working with an AI agent

Each unit serves a guide written for AI agents at **`http://spenser.local/llms.txt`**. It describes every endpoint, the exact shapes accepted and produced, worked examples, a test that exercises the whole loop, and the mistakes that catch people out. Point an agent at that URL and it can write examples, tests or a client without guessing, against the unit in front of it rather than against documentation that may have drifted.

It is discoverable from FHIR: the CapabilityStatement at `/metadata` names it in `implementation.description`, so an agent that starts at the FHIR entry point finds it.

Two things pair well with it. The `AGENTS.md` file in the source repository covers the repository itself, how to build and flash, where the routes live, and how to run the tests. The Bruno collection under `bruno/` is an executable version of this page: it is split into the order server on one side and the device on the other, and every scenario asserts on FHIR rather than on prose.

