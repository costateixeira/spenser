# Usage - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* **Usage**

## Usage

Spenser dispenses chocolate, and it treats chocolate as a medication. So you do not press a button to get some. You place an order, and the dispenser decides whether it is allowed to act on it.

This page walks through that from the outside in. The [Interfaces](interfaces.md) page is the reference behind it.

### Where the order goes

A unit sitting on your desk can be talked to directly. A unit somewhere else cannot, so the arrangement that matters is the one where orders live on a FHIR server and the dispenser comes looking for them.

The dispenser polls its order server every thirty seconds. You place an order there, and within about half a minute a piece of chocolate falls out of the machine. Nothing pushes anything to the dispenser, and nothing needs to know where it is.

### The order

Post a MedicationRequest to the order server, using the [SpenserMeds](CodeSystem-SpenserMeds.md) codes: `chocolate-dark` or `chocolate-milk`. One piece at a time, which is the only quantity the [SpenserRequest](StructureDefinition-SpenserRequest.md) profile allows.

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

The whole example is [here](MedicationRequest-ActionableDarkOrder.md). The part that does the work is `meta.tag`.

### Why the tag

A MedicationRequest is an authorization, not an instruction. Somebody may have an order on file without anyone intending it to be filled right now, and a dispenser that empties itself into the room every time an order is written is not much use to anybody.

So Spenser waits to be told that an order is ready to be acted on, which is what the Clinical Orders Workflow guidance calls an actionable order. Remove the tag from the example above and you have [an order Spenser will ignore](MedicationRequest-PlainMilkOrder.md): still a perfectly valid order, just not one anybody has asked to be filled.

### The other way to say it

Sometimes the order is written by one person and the request to fill it comes later, or from somewhere else. That is what a Task is for. Leave the order plain, and post [a Task pointing at it](Task-FulfillPlainMilkOrder.md) with status `requested` and the order in `Task.focus`.

Both routes work, and the dispenser looks for both on every poll. You do not configure it into one mode or the other. If an order shows up with a tag and a Task at the same time, it is still dispensed once.

The difference shows up afterwards, in who closes what:

| | | |
| :--- | :--- | :--- |
| the tag | the order to`completed` | nothing |
| a Task | the Task to`completed`, with the dispense in`Task.output` | the order, which stays`active` |

The second row is deliberate. When a Task is coordinating the work, finishing the order is the placer's business, and a completed Task is the signal to do it.

### What comes back

Every piece of chocolate produces a [MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.md) on the server, pointing back at the order through `authorizingPrescription`. That is the record that something physically happened, and it is the thing to look for when you want to know whether your order was filled:

```
GET {server}/MedicationDispense?_count=20

```

### When it cannot

A lane runs out. Spenser says so rather than going quiet: it posts [a dispense that did not happen](MedicationDispense-DeclinedDispenseOutOfStock.md), with status `declined` and the reason in `notPerformedReason`. It reports this once, not on every poll.

What happens to the order then is a setting. By default the order stays open, so refilling the lane fulfils it on a later poll without anybody re-posting anything. The other choice is to abandon it, and if a Task was coordinating the work that Task is set to `failed`.

### Watching a unit

The dispenser keeps its own record of what it has done, in FHIR, whether the order arrived from a server or was handed to it directly:

```
GET http://spenser.local/MedicationDispense

```

The Bundle holds its recent dispenses, newest first. It also carries one entry with `search.mode` of `outcome`: an OperationOutcome saying how the last poll went, which server it talked to, how long ago, how many orders it found and how many it filled. If nothing is coming out, read that entry first. It usually says why, and it distinguishes a dispenser that cannot reach its server from one that is working correctly and has simply been given nothing it is allowed to act on.

The dispenser's own screen shows the same two things, which are the two that matter: what is in each lane, and what the last check did.

### The settings that matter

Most of a unit's configuration is about servos, Wi-Fi and LEDs. These are the ones that change how orders behave:

| | |
| :--- | :--- |
| Order server | the FHIR base URL it polls |
| Accepted routes | both a tag and a Task, which is the default, or narrowed to one to demonstrate the difference |
| Check every | seconds between polls, 30 by default |
| Report back | whether it writes the dispense and the close-out to the server |
| Give up when the lane is empty | abandon an unfillable order, or keep it open for a refill |

### When you are standing next to it

You can post an order straight at the dispenser. There is no tag and no Task in that case, because posting it by hand is itself the decision to dispense, and it answers with the MedicationDispense:

```
POST http://spenser.local/MedicationRequest

```

And there is the button on the front, which dispenses without any FHIR at all.

**For emergencies, Spenser has a "Hit me" button for dispensing some chocolate.**
 **This feature should be used with caution.**

