This page documents every interface a Spenser unit exposes: the FHIR ones, the
private HTTP API it uses for its own configuration, and the interfaces that are
not HTTP at all. It is the reference behind the [Using Spenser](usage.html)
page, and the source of truth is the CapabilityStatement each unit publishes at
its own `/metadata`.

A unit is reachable on the local network as `http://spenser.local`, which it
advertises over mDNS, or at whatever address its router hands it.

### What needs a key

Reading a unit is open: its CapabilityStatement, its dispenses, its orders, its
inventory and its dashboard are all available to anyone who can reach it.
Everything that *changes* a unit needs that unit's key: dispensing, settings,
Wi-Fi, stock, and firmware updates. Those routes answer `401` with an
OperationOutcome when it is missing.

The key is generated on the unit's first boot and printed on its serial console
at every boot. It travels as `Authorization: Bearer <key>`, as an
`X-Spenser-Key` header, or as `?key=` for a client that cannot set headers.
`GET /key` returns it for five minutes after a restart, and at any time while
the unit is in setup mode, which is the window its owner has and a passer-by
does not. A unit serving its own access point accepts everything without a key,
because there is no network there to defend.

`rest.security.description` in each unit's CapabilityStatement says the same
thing, so a client can discover it.

### Two roles

Spenser is a FHIR **server** and a FHIR **client** at the same time, and the
difference matters when deciding where to send something.

* **As a server**, it accepts an order posted straight at it and dispenses on
  the spot. Posting to the device is itself the authorization to dispense.
* **As a client**, it polls an order server for orders it should fulfil, and
  reports back what it did. Here an order is *not* an instruction, and Spenser
  acts only on orders that have been made actionable.

Both roles are declared in its
[CapabilityStatement](CapabilityStatement-SpenserFHIRCapabilityStatement.html).

### What makes an order actionable

Following the HL7 Clinical Orders Workflow guidance, a MedicationRequest sitting
on a server is an authorization, not a command. Spenser fulfils it only when one
of two things is true:

1. **A tag.** The request carries `meta.tag`
   `http://terminology.hl7.org/CodeSystem/common-tags#actionable`.
   See [Order made actionable by a tag](MedicationRequest-ActionableDarkOrder.html).
2. **A Task.** A Task with status `requested` points at the request in
   `Task.focus`.
   See [Task asking for an order to be fulfilled](Task-FulfillPlainMilkOrder.html),
   which makes [this plain order](MedicationRequest-PlainMilkOrder.html)
   actionable.

These are **not two modes of the device**. Spenser looks for both on every check
and acts on whichever turns up. When an order arrives by both routes at once the
Task takes precedence, and the order is still dispensed exactly once. A unit can
be narrowed to one route with the `orderMode` setting, which is useful for
demonstrating the difference and for little else.

Who closes the order out depends on which route was used:

| route | what Spenser sets | what it leaves alone |
|---|---|---|
| tag, no Task | the MedicationRequest to `completed` | |
| a Task | the Task to `completed`, with the dispense in `Task.output` | the MedicationRequest, which stays `active` |

The second row is deliberate. With a Task coordinating the work, closing the
request is the placer's job, not the filler's, and a completed Task is the
placer's cue to do it.

### FHIR interface

Served by the device itself.

| Interaction | Needs a key | Meaning |
|---|---|---|
| `GET /metadata` | | CapabilityStatement for this unit, declaring both roles, the search parameters, the operation and the security scheme |
| `POST /MedicationRequest` | yes | create an order, which dispenses it |
| `GET /MedicationRequest` and `/{id}` | | the orders this unit accepted |
| `POST /$dispense` | yes | dispense in one call, answering with the MedicationDispense |
| `GET /MedicationDispense` and `/{id}` | | what this unit dispensed or refused |
| `GET /InventoryReport` | | current stock, one listing per lane |
| `POST /InventoryReport` | yes | set stock from a report |

**The create behaves like a create.** You need not supply an `id`: the unit
assigns one when you leave it out, which is what a FHIR server is supposed to
do. The answer is `201` with a `Location` header pointing at the created order,
an `ETag`, and the created
[MedicationRequest](MedicationRequest-ActionableDarkOrder.html) as the body.
`Prefer: return=minimal` and `Prefer: return=OperationOutcome` are both
honoured. The order is kept, so it can be read back afterwards.

**The dispense is a separate resource**, at `/MedicationDispense/{id}-dispense`
when a piece came out, or `/MedicationDispense/{id}-declined` when the lane was
empty. When what you want is the dispense rather than the order, use the
operation: `POST /$dispense` takes a MedicationRequest, or Parameters carrying
one, and answers `200` with the
[MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.html). An
operation reports itself in the resource it returns, so an empty lane is still a
`200`, carrying
[a declined dispense](MedicationDispense-DeclinedDispenseOutOfStock.html). R5
removed `MedicationDispense.statusReason`, so a refusal carries its reason in
`notPerformedReason`, which is a `CodeableReference`.

**Searches are real searches.** Both stores honour `_id`, `status`, `subject`
and `_count`, and dispenses also honour `authorizingPrescription`. A reference
matches either in full or by its id alone, so `subject=Patient/123` and
`subject=123` find the same records. The parameters are declared in the
CapabilityStatement, and the Bundle's self link records what the unit
understood.

**The records survive a restart.** Orders, dispenses and stock are kept on the
unit's filesystem rather than in memory, so rebooting it, or updating it, does
not erase what it did. The oldest records are dropped when a store fills.

`GET /MedicationDispense` is also how you ask a unit what it has been doing.
Besides the dispenses themselves, the Bundle carries one entry with
`search.mode` set to `outcome`: an OperationOutcome whose severity,
`issue.diagnostics` and `issue.details.text` describe the last check of the
order server, including which routes the unit is accepting and how long ago it
looked.

**Errors are always an OperationOutcome** with `application/fhir+json`. There is
no second error format anywhere in the FHIR interface.

Stock is reported as an
[InventoryReport](InventoryReport-SetDarkTo17.html), and can be set the same
way, either as a `snapshot` or as a `difference`.

### Time

A dispense carries `recorded`, `whenPrepared` and `whenHandedOver`, and a
refusal carries `recorded`, as soon as the unit has reached an NTP server.
Until then those elements are left out rather than guessed: an absent timestamp
means the unit had no clock, never that the event happened at the epoch. The
same applies to `InventoryReport.reportedDateTime`.

### Updates

A unit's firmware and its web files are both replaceable over Wi-Fi, which is
what makes a remote dispenser supportable. The chip keeps two application
slots, so an upload is written to the one that is not running and the unit
reboots into it; a new image is marked good only once it has been up for a
minute with a network, and the previous one stays available to roll back to.

| Route | Meaning |
|---|---|
| `GET /ota/status` | version, running slot, how full it is, rollback availability, clock, last result |
| `POST /ota/firmware` | the firmware image as the request body |
| `POST /ota/filesystem` | the filesystem image, which carries the web files |
| `POST /ota/file?path=/index.html` | one file, with no restart |
| `POST /ota/check` | fetch the release manifest and report what is waiting |
| `POST /ota/install` | take what the check found |
| `GET /ota/status` | also reports `updateAvailable`, `availableVersion` and how long ago it looked |
| `POST /ota/rollback` | go back to the previous image |

A release publishes a small manifest beside the binaries, and a unit pointed at
it keeps itself current:

```json
{ "version": "1.2.0",
  "firmware": "https://.../firmware.bin",
  "filesystem": "https://.../spiffs.bin" }
```

```
GET /setSettings?updateUrl=https://.../manifest.json&updateCheckHours=24
```

Looking and taking are separate. `updateMode=notify`, the default, has a check
report what is waiting and stop there: `/ota/status` then carries
`updateAvailable` and `availableVersion`, the dashboard shows a notice reading
"New firmware available" with an Install button, and nothing reboots unasked.

A unit checks hourly by default, and **remembers what it found**. The notice
survives a power cycle, because an update that was waiting before the plug came
out is still waiting afterwards, and a notice that disappears on a restart is a
notice nobody acts on. It clears itself when a later check finds nothing newer,
or once the unit is running the version that was offered. `updateMode=install` has the unit take it
by itself, which suits a unit nobody can reach. Anything other than the exact
word `install` counts as notify, so a mistyped setting cannot turn a fleet into
one that updates itself unannounced.

Each unit reports what it is running as `software.version` in its
CapabilityStatement and as `firmwareVersion` in its settings, so a fleet can be
told apart.

### What Spenser asks of an order server

Point a unit at a server, and on every check it runs two searches and writes
back what happened:

```
GET  {server}/Task?status=requested&_include=Task:focus&_count=5
GET  {server}/MedicationRequest?_tag=http://terminology.hl7.org/CodeSystem/common-tags|actionable&status=active&intent=instance-order&_count=5
POST {server}/MedicationDispense
PUT  {server}/Task/{id}
PUT  {server}/MedicationRequest/{id}
```

The `_include` matters: Spenser resolves `Task.focus` from the entries of that
one Bundle rather than fetching each order separately, so a Task whose focus is
not returned with it is reported as a problem and skipped.

`_count=5` matters when testing. Only the first five results of each search are
considered per check, so with a longer queue a given order may not be picked up
on a particular check.

Both `http://` and `https://` work. Certificates are not validated, so treat the
link as you would any other unauthenticated local traffic.

### Orders you can copy

The IG carries these as formal examples:

* [Order made actionable by a tag](MedicationRequest-ActionableDarkOrder.html)
* [Order that is not actionable on its own](MedicationRequest-PlainMilkOrder.html)
* [Task asking for it to be fulfilled](Task-FulfillPlainMilkOrder.html)
* [Dispense reported back](MedicationDispense-DispenseForActionableDarkOrder.html)
* [Dispense that did not happen](MedicationDispense-DeclinedDispenseOutOfStock.html)
* [Set inventory](InventoryReport-SetDarkTo17.html) and
  [add to inventory](InventoryReport-Add5Milk.html)

The smallest useful order, placed on the order server:

```json
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

The same body without `meta.tag` is the negative case: Spenser must leave it
alone. Drop the tag, add a Task pointing at it, and it becomes actionable again
by the other route.

Medications come from the
[SpenserMeds code system](CodeSystem-SpenserMeds.html): `chocolate-dark` and
`chocolate-milk`, one piece per order. R5 puts the code in
`medication.concept`; a directly posted order may also use the R4
`medicationCodeableConcept` spelling, which this firmware still accepts.

### Non-FHIR interface

Everything below is the unit's own administrative API. It is plain JSON or text,
it is not FHIR, and it is not meant for exchanging clinical data. It exists to
configure a unit, to drive it during a demo, and to serve the built-in
dashboard.

| Group | Endpoints |
|---|---|
| Orders | `/checkOrders` queues a check and returns `202`, `/orders` reports the last check for the dashboard, `/forgetOrders` clears the list of orders already dealt with |
| Settings | `/settings`, `/setSettings`, `/resetSettings` |
| Updates | `/ota/status`, `/ota/firmware`, `/ota/filesystem`, `/ota/file`, `/ota/check`, `/ota/rollback` |
| The key | `/key`, within the window described above |
| Stock and hardware | `/inventory`, `/setInventory`, `/resetInventory`, `/setServos`, `/flashServo1`, `/flashServo2`, `/setColor`, `/battery`, `/reset` |
| Wi-Fi and identity | `/`, `/scan`, `/cfg`, `/save`, `/wifi-settings`, `/wifi-reset`, `/wifi-reboot-config`, `/getMac`, `/setMac`, `/clearMac` |
| Captive portal | `/generate_204`, `/hotspot-detect.html`, `/fwlink`, `/ncsi.txt`, `/connecttest.txt` |

`/setSettings` accepts any of `serverUrl`, `orderMode` with values `both`, `tag`
or `task`, `orderQuery`, `taskQuery`, `pollEnabled`, `pollSeconds` between 5 and
3600, `writeBack`, `giveUpOnStockEmpty`, `updateUrl`, `updateCheckHours`, and
the servo parameters. It answers with the full settings document, which includes
the firmware version and never includes the key.

A unit checks its order server every `pollSeconds`, 30 by default, while
`pollEnabled` is on. `/checkOrders` forces a check immediately. It returns
before the work is done, because the HTTP work happens in the main loop and
never inside a request handler, so a client should wait for the check to finish
rather than assume it has.

`giveUpOnStockEmpty` decides what happens to an order that cannot be filled.
Off, the order is reported once as out of stock and left open, so refilling the
lane fulfils it on a later check. On, it is reported once and abandoned, and a
coordinating Task is set to `failed`.

Anything not matched falls back to a static file from the device filesystem,
which is how the dashboard is served. `OPTIONS` returns `200` for CORS
preflight.

### Interfaces that are not HTTP

* **mDNS.** The unit advertises itself as `spenser` with an HTTP service on port
  80, so `http://spenser.local` works without knowing its address.
* **Access point and captive portal.** With no Wi-Fi configured it serves an
  open network and answers every DNS name, so a phone or laptop opens the setup
  page by itself.
* **Serial.** Logs at 115200 baud, including every order search and write-back.
* **The button.** A short press dispenses. Three seconds is a soft reset. Ten
  seconds wipes the stored credentials, and the LED turns red while held to warn
  you before you let go.

### Working with an AI agent

Each unit serves a guide written for AI agents at
**`http://spenser.local/llms.txt`**. It describes every endpoint, the exact
shapes accepted and produced, worked examples, a test that exercises the whole
loop, and the mistakes that catch people out. Point an agent at that URL and it
can write examples, tests or a client without guessing, against the unit in
front of it rather than against documentation that may have drifted.

It is discoverable from FHIR: the CapabilityStatement at `/metadata` names it in
`implementation.description`, so an agent that starts at the FHIR entry point
finds it.

Two things pair well with it. The `AGENTS.md` file in the source repository
covers the repository itself, how to build and flash, where the routes live, and
how to run the tests. The Bruno collection under `bruno/` is an executable
version of this page: it is split into the order server on one side and the
device on the other, and every scenario asserts on FHIR rather than on prose.
