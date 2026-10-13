# Working in this repository

Spenser is a chocolate dispenser that speaks FHIR R5. This file is for AI
agents and for people directing them: what lives where, how to build and test,
and the things that have already caught people out.

Two other documents matter, and they have different jobs:

* **`firmware/data/llms.txt`** is shipped on the device and served at
  `http://spenser.local/llms.txt`. It describes the running unit's interfaces
  with worked examples. Use it when writing a client, examples or tests
  **against a device**.
* **`input/pagecontent/interfaces.md`** is the formal specification page in the
  Implementation Guide, published on the IG site. Use it when documenting the
  system.

Keep all three in step. A change to a route in the firmware is not finished
until `llms.txt`, the interfaces page and the CapabilityStatement in
`/metadata` agree with it.

## Layout

| Path | What it is |
|---|---|
| `firmware/src/main.cpp` | the whole firmware: routes, order client, dispensing, Wi-Fi, battery |
| `firmware/data/` | files uploaded to the device filesystem: the dashboard `index.html`, `llms.txt` |
| `firmware/test/*.http` | REST Client request files, `orders.http` covers the order client |
| `input/fsh/` | profiles, value sets and the IG's formal examples |
| `input/pagecontent/` | IG pages, one markdown file per page, linked from the menu in `sushi-config.yaml` |
| `bruno/` | executable tests: an API collection split into the order server and the device |
| `server/` | a small Express stand-in for an order server, for working offline |
| `docker-compose*.yml`, `Caddyfile*` | the deployed order server, fhir-candle behind Caddy |

## Building and running

**Firmware.** PlatformIO, environment `esp32s3`. `pio run --target upload`
flashes the code, `pio run --target uploadfs` uploads `firmware/data/`. A change
to `llms.txt` or the dashboard needs the second one, which is easy to forget,
although both can now go over the air instead: see the update routes.

The build runs in CI on every push that touches `firmware/`, including a check
that the image still fits its OTA slot with room to grow. `firmware-v<version>`
tags publish a draft release carrying `firmware.bin`, `spiffs.bin` and the
`manifest.json` that units check. The tag and `FIRMWARE_VERSION` in `main.cpp`
have to agree, and the release job fails if they do not.

Dependencies are pinned, deliberately. They were floating, and FastLED 3.10 does
not compile against this core, so a fresh checkout stopped building while a
machine with a warm cache carried on fine. FastLED is unused by this code but
`M5AtomS3` includes it, so it is pinned rather than removed.

The partition table is `default_8MB.csv`, which the firmware now needs: the
image is larger than the 1.25 MB slot the 4 MB default table provides. Changing
the table requires one upload over the cable and erases the filesystem.

**Implementation Guide.** `_genonce.sh` or `_genonce.bat` runs the IG Publisher.
To check only that the FSH compiles, which is much faster, run
`npx fsh-sushi . -o <a temporary directory>` so the checked-in `fsh-generated/`
is left alone.

**Tests.** The Bruno collection is the real test suite.

```
cd bruno
npx @usebruno/cli run "1. Order server/1. Wiring" --env online
npx @usebruno/cli run "2. Spenser device/1. Setup" --env online
```

Pick the `online` environment for the deployed order server or `local` for one
on your machine, and set `spenser` to the unit if `spenser.local` does not
resolve on your network.

The collection is split by what it talks to, so a scenario interleaves the two
halves: place an order in `1. Order server`, trigger a check in
`2. Spenser device`, then verify back on the server. Order ids travel as runtime
variables inside one run. When you run the halves as separate CLI invocations,
pass the id yourself with `--env-var tagOrderId=<id>`, which every test that
needs one falls back to.

## Conventions

* FHIR R5. Medications go in `medication.concept`, and a refusal's reason goes
  in `notPerformedReason.concept`, because R5 removed
  `MedicationDispense.statusReason`.
* Codes come from the IG's own `SpenserMeds` code system. Do not invent codes
  for examples; add them to `input/fsh/spenser-request.fsh` if something new is
  genuinely needed.
* New examples belong in `input/fsh/examples-orders.fsh` as FSH instances, so
  they are published as part of the IG, and are then linked from the interfaces
  page.
* The firmware does its blocking HTTP work in `loop()`, never inside a request
  handler. A route that needs network work raises a flag and returns `202`.
  Order checks, update checks and the restart after an update all work this way.
* Reads are open; anything that changes the unit goes behind `requireKey`. A new
  mutating route without that guard is a bug.
* Records live in two newline-delimited JSON files on the device filesystem,
  reached only through the store helpers, which take a mutex because `loop()`
  writes while the web task reads.
* Errors from FHIR routes are built with `outcomeJson` or `sendOutcome`. There is
  no second error format.
* Anything the web task reads while `loop()` writes it uses a plain buffer, not
  an Arduino `String`, to avoid a reallocation under a reader.

## Traps that have already bitten

* **Chunked responses.** Never hand `http.getStream()` to ArduinoJson. A FHIR
  server may answer with `Transfer-Encoding: chunked`, and only the
  `writeToStream` path that `getString()` uses unwraps the chunk framing.
  Parsing the raw stream fails with `InvalidInput` on the hex chunk-size line.
* **A tag and a Task are not two modes.** The unit accepts both on every check.
  `orderMode` narrows it to one, and defaults to `both`.
* **`_count=5`.** Each search considers only the first five results per check.
  A test that leaves a long queue on the server may not see its own order
  dispensed.
* **`/checkOrders` returns before the work is done.** Wait for the check to
  finish, by watching the outcome entry in `GET /MedicationDispense`, rather
  than sleeping a fixed number of seconds.
* **Background polling races tests.** Turn it off with
  `GET /setSettings?pollEnabled=0` while testing, and restore it afterwards.
* **Handled orders are remembered.** A second run of the same scenario needs
  `GET /forgetOrders`, or the unit will skip the order it has already dealt
  with.
* **Unresolved template variables.** A request body sent with an unsubstituted
  `{{variable}}` creates a resource that points at nothing and lingers on the
  server. The collection asserts that a Task's focus resolved.
* **Running a test dispenses real chocolate.** Every fulfilled order moves a
  servo and consumes stock. Check what is queued on the order server before
  letting a unit poll it.
* **A test that writes needs the key.** Set `spenserKey` in the Bruno
  environment, or expect 401s. Read it from the serial console, or from `/key`
  within five minutes of a restart.
* **An absent timestamp is an unset clock.** The unit leaves `whenHandedOver`
  and friends out rather than inventing a time, so a dispense without one means
  NTP has not answered yet.
