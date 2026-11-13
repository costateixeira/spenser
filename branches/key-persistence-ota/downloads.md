# Downloads - Spenser - a developer's companion v1.0.0

* [**Table of Contents**](toc.md)
* **Downloads**

## Downloads

### Firmware

The current firmware for a Spenser unit is published at [costateixeira.github.io/spenser/firmware/](firmware/), with the release notes for the build it is serving, the two images, and the manifest a unit reads:

* `firmware.bin` - the code
* `spiffs.bin` - the dashboard and the agent guide
* `manifest.json` - what a unit checks hourly to notice a new build

A unit updates itself from there: it shows a notice on its own dashboard when a build is waiting, and installs it when asked, after showing what it contains. The [Interfaces](interfaces.md) page describes the update routes, and the first flash of a unit has to go over a cable because it repartitions the chip.

