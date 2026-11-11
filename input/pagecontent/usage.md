Spenser dispenses chocolate, and it treats chocolate as a medication. So you do
not press a button to get some. You place an order, and the dispenser decides
whether it is allowed to act on it.

This page walks through that from the outside in. The
[Interfaces](interfaces.html) page is the reference behind it.

### When to use

**The FHIR meetings.** The requirement is still being read out, and someone
already has an answer: a Bundle, with three profiles on it. You know who you
are. Order a chocolate: at least the question gets to the end of its sentence.

*Dosage: one unit at the first Bundle. Repeat as the agenda requires.*

**The developer meeting.** Everyone has read the specification, in the sense of
having searched for the keyword that justifies their initial design.
Somebody proposes containing everything. The only contained thing here that
solves a problem is the chocolate, and only until it is ordered.

*Dosage: one unit each, before the whiteboard comes out.*

**The terminology session.** Ninety minutes on whether something is a code or a
concept. Those ninety minutes are needed. You know you will revisit the decision 
in six months anyway, so you may as well enjoy this one. 
Quickly, before someone suggests the server will take care of it all.

*Dosage: one unit per binding. The discussion is the active ingredient.*

**The workflow discussion.** Somebody will ask whether this really needs a
Task. Everybody asks it once, and usually about a week before they need one.
Let them place the order without one, see it on the server, and still have no 
chocolate. see what they think after that. Add the Task and see the designated
unit respond, while the others leave it alone.

*Dosage: one unit per Task, dispensed by the unit the Task names.*

**The session you have to chair.** A room, an agenda, and no actual authority.
Someone has been "a very quick comment" for nineteen minutes. Alternate talking 
and chocolate: it just gives the room a rhythm.

*Dosage: administer before the discussion becomes circular.*

**The training session.** Somebody's first POST comes back 400, and they ask
what an OperationOutcome is, then read one properly for the first time. The
second request moves a servo and a chocolate falls out. They will hit the same
400 again next week, which is how it sticks. An order is an authorization and
not an instruction, and nobody quite believes that until they need chocolate.

*Dosage: one unit per successful request. A rejected request is not a dose.*

**The demo, the connectathon, and the slot right after lunch.** The queue forms
by itself, and everyone wants to send the next order themselves. Somebody will
ask whether it could dispense insulin. It cannot. One unit, several laptops,
one shared order server, and each unit takes only the Task addressed to it.

*Dosage: one unit per visitor. An empty lane is a declined dispense.*

What a dispenser really provides is a pause, and the certainty that no bad
decisions were taken during it. Half a minute in which the architecture cannot
get any worse.

If more than one of these is in your week, that is the normal number.

**Warnings and precautions.** Keep away from radiators and direct sunlight:
chocolate softens near body temperature, and a soft lane jams. The lanes hold
whatever was last loaded into them, which may contain milk or nuts.

**Side effects.** Common: better attendance. Uncommon: questions about how the
dispenser works. Rare: somebody reads the specification.

**If symptoms persist**, consult the [Interfaces](interfaces.html) page.

### Where the order goes

A unit sitting on your desk can be talked to directly. A unit somewhere else
cannot, so the arrangement that matters is the one where orders live on a FHIR
server and the dispenser comes looking for them.

The dispenser polls its order server every thirty seconds. You place an order
there, and within about half a minute a piece of chocolate falls out of the
machine. Nothing pushes anything to the dispenser, and nothing needs to know
where it is.

### The order

Post a MedicationRequest to the order server, using the
[SpenserMeds](CodeSystem-SpenserMeds.html) codes: `chocolate-dark` or
`chocolate-milk`. One piece at a time, which is the only quantity the
[SpenserRequest](StructureDefinition-SpenserRequest.html) profile allows.

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

The whole example is
[here](MedicationRequest-ActionableDarkOrder.html). The part that does the work
is `meta.tag`.

### Why the tag

A MedicationRequest is an authorization, not an instruction. Somebody may have
an order on file without anyone intending it to be filled right now, and a
dispenser that empties itself into the room every time an order is written is
not much use to anybody.

So Spenser waits to be told that an order is ready to be acted on, which is what
the Clinical Orders Workflow guidance calls an actionable order. Remove the tag
from the example above and you have
[an order Spenser will ignore](MedicationRequest-PlainMilkOrder.html): still a
perfectly valid order, just not one anybody has asked to be filled.

### The other way to say it

Sometimes the order is written by one person and the request to fill it comes
later, or from somewhere else. That is what a Task is for. Leave the order
plain, and post
[a Task pointing at it](Task-FulfillPlainMilkOrder.html) with status
`requested` and the order in `Task.focus`.

Both routes work, and the dispenser looks for both on every poll. You do not
configure it into one mode or the other. If an order shows up with a tag and a
Task at the same time, it is still dispensed once.

The difference shows up afterwards, in who closes what:

| how the order was made actionable | what Spenser sets | what it leaves for you |
|---|---|---|
| the tag | the order to `completed` | nothing |
| a Task | the Task to `completed`, with the dispense in `Task.output` | the order, which stays `active` |

The second row is deliberate. When a Task is coordinating the work, finishing
the order is the placer's business, and a completed Task is the signal to do it.

### What comes back

Every piece of chocolate produces a
[MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.html) on
the server, pointing back at the order through `authorizingPrescription`. That
is the record that something physically happened, and it is the thing to look
for when you want to know whether your order was filled:

```
GET {server}/MedicationDispense?_count=20
```

### When it cannot

A lane runs out. Spenser says so rather than going quiet: it posts
[a dispense that did not happen](MedicationDispense-DeclinedDispenseOutOfStock.html),
with status `declined` and the reason in `notPerformedReason`. It reports this
once, not on every poll.

What happens to the order then is a setting. By default the order stays open, so
refilling the lane fulfils it on a later poll without anybody re-posting
anything. The other choice is to abandon it, and if a Task was coordinating the
work that Task is set to `failed`.

### Watching a unit

The dispenser keeps its own record of what it has done, in FHIR, whether the
order arrived from a server or was handed to it directly:

```
GET http://spenser.local/MedicationDispense
```

The Bundle holds its recent dispenses, newest first. It also carries one entry
with `search.mode` of `outcome`: an OperationOutcome saying how the last poll
went, which server it talked to, how long ago, how many orders it found and how
many it filled. If nothing is coming out, read that entry first. It usually says
why, and it distinguishes a dispenser that cannot reach its server from one that
is working correctly and has simply been given nothing it is allowed to act on.

The dispenser's own screen shows the same two things, which are the two that
matter: what is in each lane, and what the last check did.

Nothing above needs permission. Changing a unit does: dispensing by hand,
settings, stock, Wi-Fi and updates all need that unit's key, which it prints on
its serial console at boot and will hand over for five minutes after a restart.
Reading what it did never does.

### The settings that matter

Most of a unit's configuration is about servos, Wi-Fi and LEDs. These are the
ones that change how orders behave:

| Setting | What it decides |
|---|---|
| Order server | the FHIR base URL it polls |
| Accepted routes | both a tag and a Task, which is the default, or narrowed to one to demonstrate the difference |
| Check every | seconds between polls, 30 by default |
| Report back | whether it writes the dispense and the close-out to the server |
| Give up when the lane is empty | abandon an unfillable order, or keep it open for a refill |

### When you are standing next to it

You can post an order straight at the dispenser. There is no tag and no Task in
that case, because posting it by hand is itself the decision to dispense, and it
answers with the MedicationDispense:

```
POST http://spenser.local/MedicationRequest
```

And there is the button on the front, which dispenses without any FHIR at all.

A unit out of reach is still maintainable: its firmware and its web files can
both be replaced over Wi-Fi, and it can keep itself up to date from a published
release. The [Interfaces](interfaces.html) page has the details.

**For emergencies, Spenser has a "Hit me" button for dispensing some chocolate.**  
**This feature should be used with caution.**  
{:.stu-note}
