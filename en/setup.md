# Setup - Spenser - a developer's companion v1.0.0

## Setup

The unit is assembled, flashed and switched on. What is left is getting it onto a network and pointing it at wherever the orders are going to come from.

One fact decides everything else on this page: **nothing ever has to connect into a unit.** It can be reached when the network allows it, and it polls outward when the network does not. That is why a dispenser works on conference Wi-Fi, which is where this kind of demo usually dies.

### First boot

With no credentials stored, the unit is its own open Wi-Fi network. The network is called `Spenser-` and the last two bytes of its MAC address, `Spenser-E3D4` for example, and that is the unit's name everywhere else as well.

1. Join`Spenser-XXXX`from a phone or a laptop. The unit answers every DNS name it is asked about, so the setup page normally opens by itself. If it does not, go to[http://192.168.4.1](http://192.168.4.1).
1. Pick a network from the list, give it the password, and save. The unit restarts and joins it.
1. From then on it is at[http://spenser.local](http://spenser.local), or at whatever address its router handed it.

**Take the key before you leave setup mode.** Everything that changes a unit needs it: dispensing, settings, stock, Wi-Fi and updates. `GET /key` returns it for five minutes after a restart, and at any time while the unit is in setup mode. It is also printed on the serial console, at 115200 baud, every time the unit boots. A unit serving its own access point accepts everything without a key, because there is no network there to defend.

Holding the button for three seconds during boot brings setup mode back. Ten seconds wipes the stored credentials; the LED turns red while you hold it, to warn you before you let go.

### Which arrangement

| | |
| :--- | :--- |
| On your own network, with an order server | Either way: posted straight at the unit, or placed on the server and collected |
| On your own network, no server | Posted straight at the unit |
| On its own access point | Posted straight at the unit, by whoever joined it |
| On a network that isolates its clients | Placed on an order server out on the internet, and collected |

#### Your own network

Home, office, lab. The unit is on the Wi-Fi, `spenser.local` resolves, and both routes are open to you: post a MedicationRequest straight at it and a chocolate comes out, or put orders on an order server and let the unit collect them.

This is the arrangement to develop against, because you can watch both halves.

#### No network at all

Leave the unit on its own access point and let people join `Spenser-XXXX`. The unit is at `192.168.4.1`, it needs no key there, and orders posted at it are dispensed on the spot. The whole exchange is [ordering straight from the unit](ExampleScenario-DirectOrderScenario.md).

Two things are missing without an uplink. There is no clock, because there is no NTP, so the unit leaves `whenHandedOver` and its siblings out rather than inventing a time. And there is no order server, so there is nothing to poll; turn polling off with `pollEnabled=0` so the unit stops trying.

#### A network that isolates its clients

Conference Wi-Fi, hotel Wi-Fi and most guest networks put every client in its own cell. Clients reach the internet and nothing else. `spenser.local` will not resolve, the unit's address will not answer, and nothing can be posted at it.

The unit is fine. It still reaches out.

Put an order server somewhere on the internet, point the unit at it, and let everyone write their orders there. The unit polls, takes the work addressed to it, dispenses, and writes back what it did. That is [ordering through an order server](ExampleScenario-TaskOrderScenario.md), and client isolation is the reason that scenario exists.

Check this before the session rather than during it: join the network with two devices and try to reach one from the other.

#### A phone hotspot

The same as your own network, and yours to control, as long as the phone is not isolating its clients too — some do. It is the usual fallback when the venue's Wi-Fi turns out to be isolated and the order server is already out on the internet.

### Pointing it at an order server

Everything below needs the key.

```
KEY=... # from the serial console, or GET /key

curl -H "X-Spenser-Key: $KEY" \
  "http://spenser.local/setSettings?serverUrl=https://example.org/fhir&orderMode=both&pollEnabled=1&pollSeconds=30&writeBack=1&giveUpOnStockEmpty=0"

```

* `orderMode` is `both` by default: the unit takes both tagged orders and Tasks. `tag` or `task` narrows it to one. They are not two modes of operation, only two ways for an order to become actionable.
* `pollSeconds` is between 5 and 3600, 30 by default. `GET /checkOrders` forces a check now, and returns `202` before the check has finished.
* `giveUpOnStockEmpty` off leaves an order that could not be filled open, so refilling the lane fulfils it on a later check. On, it is reported once and abandoned.

The dashboard at `http://spenser.local` sets the same things, and also stock, servo angles and updates.

### Several units in one room

Each unit polls the same server and would otherwise take the same orders. Name the one that should fill an order in `Task.requestedPerformer`, and in the `dispensingDevice` extension on the order itself; every other unit skips it.

Each check looks at the first five results only. A queue longer than that on the server can outrun one check, which is worth knowing before a demo queue forms.

### When it does not work

* **`spenser.local` does not resolve.** Use the address from the router or the serial console instead. mDNS is the part most likely to be missing, not the unit.
* **Everything answers `401`.** The key is missing or wrong. Restart the unit and read `GET /key` within five minutes.
* **Dispenses have no timestamp.** The clock has not been set: NTP has not answered yet, or there is no route to it. The unit leaves the time out rather than inventing one.
* **Orders are not picked up.** Check `serverUrl`, check that `pollEnabled` is on, and remember that handled orders are remembered: `GET /forgetOrders` before running the same scenario twice.
* **A test keeps racing the unit.** Turn background polling off with `pollEnabled=0` while testing and drive checks yourself, then turn it back on.
* **The setup page does not open by itself.** Go to [http://192.168.4.1](http://192.168.4.1) while joined to `Spenser-XXXX`.

[Interfaces](interfaces.md) has the reference behind all of this: every route, what needs a key, and what each setting does.

