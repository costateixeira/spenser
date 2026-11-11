Deze pagina documenteert elke interface die een Spenser-unit aanbiedt: de
FHIR-interfaces, de private HTTP-API voor zijn eigen configuratie, en de
interfaces die helemaal geen HTTP zijn. Ze is de referentie achter de pagina
[Spenser gebruiken](usage.html), en de bron van waarheid is het
CapabilityStatement dat elke unit publiceert op zijn eigen `/metadata`.

Een unit is op het lokale netwerk bereikbaar als `http://spenser.local`, wat hij
via mDNS bekendmaakt, of op het adres dat zijn router hem geeft.

### Wat een sleutel nodig heeft {#what-needs-a-key}

Een unit lezen is open: zijn CapabilityStatement, zijn verstrekkingen, zijn orders,
zijn voorraad en zijn dashboard zijn beschikbaar voor iedereen die hem kan bereiken.
Alles wat een unit *wijzigt*, heeft de sleutel van die unit nodig: verstrekken,
instellingen, Wi-Fi, voorraad en firmware-updates. Die routes antwoorden `401` met
een OperationOutcome als de sleutel ontbreekt.

De sleutel wordt aangemaakt bij de eerste keer opstarten van de unit en bij elke
keer opstarten op zijn seriële console afgedrukt. Hij reist mee als
`Authorization: Bearer <key>`, als een `X-Spenser-Key`-header, of als `?key=` voor
een client die geen headers kan instellen. `GET /key` geeft hem terug gedurende
vijf minuten na een herstart, en op elk moment terwijl de unit in de installatiemodus
staat; dat is het venster dat de eigenaar wel heeft en een voorbijganger niet. Een
unit die zijn eigen access point aanbiedt, aanvaardt alles zonder sleutel, omdat er
daar geen netwerk te verdedigen valt.

`rest.security.description` in het CapabilityStatement van elke unit zegt hetzelfde,
zodat een client het kan ontdekken.

### Twee rollen {#two-roles}

Spenser is tegelijk een FHIR-**server** en een FHIR-**client**, en dat verschil is
van belang als u beslist waar u iets naartoe stuurt.

* **Als server** aanvaardt hij een order die rechtstreeks naar hem wordt gepost, en
  verstrekt hij ter plekke. Naar het apparaat posten is zelf de machtiging om te
  verstrekken.
* **Als client** pollt hij een orderserver op orders die hij moet uitvoeren, en
  meldt hij terug wat hij heeft gedaan. Hier is een order *geen* instructie, en
  handelt Spenser alleen op orders die uitvoerbaar zijn gemaakt.

Beide rollen staan vermeld in zijn
[CapabilityStatement](CapabilityStatement-SpenserFHIRCapabilityStatement.html).

### Actoren {#actors}

| Actor | Wat die doet |
|---|---|
| [Spenser-unit](ActorDefinition-SpenserUnit.html) | verstrekt, als FHIR-server en FHIR-client |
| [Orderplaatser](ActorDefinition-OrderPlacer.html) | vraagt om chocolade en beslist of een order uitvoerbaar is |
| [Orderserver](ActorDefinition-OrderServer.html) | bewaart orders tot een unit ze ophaalt, en ontvangt zijn meldingen |
| [Unit-eigenaar](ActorDefinition-UnitOwner.html) | heeft de sleutel, en configureert, bevoorraadt en updatet de unit |
| [Update-uitgever](ActorDefinition-UpdatePublisher.html) | publiceert het manifest en de images die een unit installeert |

### Wat een order uitvoerbaar maakt {#what-makes-an-order-actionable}

Volgens de richtlijnen van HL7 Clinical Orders Workflow is een MedicationRequest
op een server een machtiging, geen opdracht. Spenser voert ze alleen uit als een
van twee dingen waar is:

1. **Een tag.** De aanvraag draagt `meta.tag`
   `http://terminology.hl7.org/CodeSystem/common-tags#actionable`.
   Zie [Order die door een tag uitvoerbaar is gemaakt](MedicationRequest-ActionableDarkOrder.html).
2. **Een Task.** Een Task met status `requested` verwijst naar de aanvraag in
   `Task.focus`.
   Zie [Task die vraagt om een order uit te voeren](Task-FulfillPlainMilkOrder.html),
   die [deze gewone order](MedicationRequest-PlainMilkOrder.html)
   uitvoerbaar maakt.

Dit zijn **geen twee modi van het apparaat**. Spenser zoekt bij elke controle naar
allebei en handelt op wat er opduikt. Als een order tegelijk via beide routes
binnenkomt, heeft de Task voorrang, en wordt de order nog steeds precies één keer
verstrekt. Een unit kan met de instelling `orderMode` tot één route worden beperkt,
wat nuttig is om het verschil te demonstreren, en voor weinig anders.

Wie de order afsluit, hangt af van de gebruikte route:

| route | wat Spenser instelt | wat hij met rust laat |
|---|---|---|
| tag, geen Task | de MedicationRequest op `completed` | |
| een Task | de Task op `completed`, met de verstrekking in `Task.output` | de MedicationRequest, die `active` blijft |

De tweede rij is bewust zo. Als een Task het werk coördineert, is het afsluiten van
de aanvraag de taak van de plaatser, niet van de uitvoerder, en een voltooide Task
is voor de plaatser het teken om dat te doen.

### FHIR-interface {#fhir-interface}

Aangeboden door het apparaat zelf.

| Interactie | Sleutel nodig | Betekenis |
|---|---|---|
| `GET /metadata` | | CapabilityStatement van deze unit, met beide rollen, de zoekparameters, de operatie en het beveiligingsschema |
| `POST /MedicationRequest` | ja | maakt een order aan, en verstrekt die dus |
| `GET /MedicationRequest` en `/{id}` | | de orders die deze unit heeft aanvaard |
| `POST /$dispense` | ja | verstrekt in één aanroep, en antwoordt met de MedicationDispense |
| `GET /MedicationDispense` en `/{id}` | | wat deze unit heeft verstrekt of geweigerd |
| `GET /InventoryReport` | | huidige voorraad, één regel per baan |
| `POST /InventoryReport` | ja | stelt de voorraad in op basis van een rapport |

**Aanmaken gedraagt zich als aanmaken.** U hoeft geen `id` mee te geven: de unit
kent er een toe als u die weglaat, zoals een FHIR-server hoort te doen. Het antwoord
is `201` met een `Location`-header die naar de aangemaakte order wijst, een `ETag`,
en de aangemaakte
[MedicationRequest](MedicationRequest-ActionableDarkOrder.html) als body.
`Prefer: return=minimal` en `Prefer: return=OperationOutcome` worden allebei
gehonoreerd. De order wordt bewaard, zodat ze achteraf kan worden teruggelezen.

**De verstrekking is een aparte resource**, op `/MedicationDispense/{id}-dispense`
als er een stukje is uitgekomen, of op `/MedicationDispense/{id}-declined` als de baan
leeg was. Als u de verstrekking wilt in plaats van de order, gebruik dan de
operatie: `POST /$dispense` neemt een MedicationRequest aan, of Parameters waarin er
een zit, en antwoordt `200` met de
[MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.html). Een
operatie rapporteert over zichzelf in de resource die ze teruggeeft, dus ook een lege
baan is een `200`, met daarin
[een geweigerde verstrekking](MedicationDispense-DeclinedDispenseOutOfStock.html). R5
heeft `MedicationDispense.statusReason` verwijderd, dus een weigering draagt haar
reden in `notPerformedReason`, een `CodeableReference`.

**Zoekopdrachten zijn echte zoekopdrachten.** Beide opslagplaatsen honoreren `_id`,
`status`, `subject` en `_count`, en verstrekkingen honoreren ook
`authorizingPrescription`. Een referentie matcht zowel volledig als op alleen haar
id, dus `subject=Patient/123` en `subject=123` vinden dezelfde records. De parameters
staan vermeld in het CapabilityStatement, en de self-link van de Bundle legt vast wat
de unit heeft begrepen.

**De records overleven een herstart.** Orders, verstrekkingen en voorraad staan op
het bestandssysteem van de unit in plaats van in het geheugen, dus herstarten of
updaten wist niet wat hij heeft gedaan. De oudste records vervallen als een
opslagplaats vol raakt.

`GET /MedicationDispense` is ook de manier om een unit te vragen waarmee hij bezig
is geweest. Naast de verstrekkingen zelf bevat de Bundle één entry met `search.mode`
op `outcome`: een OperationOutcome waarvan de severity, `issue.diagnostics` en
`issue.details.text` de laatste controle van de orderserver beschrijven, inclusief
welke routes de unit aanvaardt en hoe lang geleden hij heeft gekeken.

**Fouten zijn altijd een OperationOutcome** met `application/fhir+json`. Er is
nergens in de FHIR-interface een tweede foutformaat.

De voorraad wordt gerapporteerd als een
[InventoryReport](InventoryReport-SetDarkTo17.html), en kan op dezelfde manier worden
ingesteld, als `snapshot` of als `difference`.

### Tijd {#time}

Een verstrekking draagt `recorded`, `whenPrepared` en `whenHandedOver`, en een
weigering draagt `recorded`, zodra de unit een NTP-server heeft bereikt. Tot dan
worden die elementen weggelaten in plaats van geraden: een ontbrekende tijdstempel
betekent dat de unit geen klok had, nooit dat de gebeurtenis op de epoch plaatsvond.
Hetzelfde geldt voor `InventoryReport.reportedDateTime`.

### Updates {#updates}

Zowel de firmware als de webbestanden van een unit kunnen via Wi-Fi worden vervangen,
en dat maakt een dispenser op afstand onderhoudbaar. De chip heeft twee
applicatieslots, dus een upload wordt weggeschreven naar het slot dat niet draait en
de unit herstart daarin; een nieuwe image wordt pas als goed gemarkeerd als ze een
minuut met een netwerk heeft gedraaid, en de vorige blijft beschikbaar om naar terug
te keren.

| Route | Betekenis |
|---|---|
| `GET /ota/status` | versie, actief slot, hoe vol het is, beschikbaarheid van terugdraaien, klok, laatste resultaat |
| `POST /ota/firmware` | de firmware-image als request body |
| `POST /ota/filesystem` | de image van het bestandssysteem, met daarin de webbestanden |
| `POST /ota/file?path=/index.html` | één bestand, zonder herstart |
| `POST /ota/check` | haalt het releasemanifest op en meldt wat er klaarstaat |
| `POST /ota/install` | neemt wat de controle heeft gevonden |
| `GET /ota/status` | meldt ook `updateAvailable`, `availableVersion` en hoe lang geleden hij heeft gekeken |
| `POST /ota/rollback` | keert terug naar de vorige image |

Builds worden naast deze specificatie gepubliceerd, op
[costateixeira.github.io/spenser/firmware/](https://costateixeira.github.io/spenser/firmware/), waar een unit standaard
kijkt. Die pagina vermeldt wat er is veranderd in de build die ze aanbiedt, met de
binaries en het manifest ernaast. Een manifest beschrijft een build voor de unit:

```json
{ "version": "1.2.0",
  "firmware": "https://.../firmware.bin",
  "filesystem": "https://.../spiffs.bin" }
```

```
GET /setSettings?updateUrl=https://.../manifest.json&updateCheckMinutes=15
```

Een unit kijkt standaard om de 15 minuten, en `/ota/status` meldt wanneer hij voor het
laatst heeft gekeken en wanneer hij weer zal kijken. Bij een interval van uren zou u
het niet zien werken, en een manifest is kleiner dan een kilobyte.

Kijken en nemen zijn twee dingen. Met `updateMode=notify`, de standaard, meldt een
controle wat er klaarstaat en stopt ze daar: `/ota/status` bevat dan `updateAvailable`
en `availableVersion`, het dashboard toont de melding
"New firmware available" met een knop Install, en niets herstart ongevraagd.

Een unit controleert standaard om de 15 minuten, en **onthoudt wat hij heeft gevonden**.
De melding overleeft een stroomonderbreking, want een update die klaarstond voordat de
stekker eruit ging, staat daarna nog steeds klaar, en een melding die bij een herstart
verdwijnt, is een melding waar niemand iets mee doet. Ze verdwijnt vanzelf als een
latere controle niets nieuwers vindt, of zodra de unit de aangeboden versie draait.

**Wat een update bevat, kunt u lezen voordat u ze neemt.** Het manifest bevat release
notes; de unit bewaart ze, biedt ze in `/ota/status` aan als `availableNotes` en
`availableNotesUrl`, en het dashboard toont ze in een pop-up als u op Install drukt, met
de volledige lijst een link verder. Blind installeren is geen optie die een beheerder
moet krijgen.

Een gepubliceerde versie vermeldt de commit waaruit ze is gebouwd, als `1.2.0+a1b2c3d`.
Daardoor kan een unit de ene build van de volgende onderscheiden, en tot rust komen
zodra hij er een heeft geïnstalleerd. Met `updateMode=install` neemt de unit ze uit
zichzelf, wat past bij een unit die niemand kan bereiken. Alles behalve het exacte woord
`install` telt als notify, zodat een tikfout in een instelling een vloot niet kan
veranderen in een vloot die zichzelf onaangekondigd updatet.

Elke unit meldt wat hij draait als `software.version` in zijn CapabilityStatement en als
`firmwareVersion` in zijn instellingen, zodat de units van een vloot uit elkaar te houden
zijn.

### Wat Spenser van een orderserver vraagt {#what-spenser-asks-of-an-order-server}

Wijs een unit naar een server, en bij elke controle voert hij twee zoekopdrachten uit
en schrijft hij terug wat er is gebeurd:

```
PUT  {server}/Device/{unit name}
GET  {server}/Task?status=requested&_include=Task:focus&_count=5
PUT  {server}/Task/{id}
GET  {server}/MedicationRequest?_tag=http://terminology.hl7.org/CodeSystem/common-tags|actionable&status=active&intent=instance-order&_count=5
POST {server}/MedicationDispense
PUT  {server}/Task/{id}
PUT  {server}/MedicationRequest/{id}
```

De eerste `PUT` naar een Task is de claim die wordt beschreven onder
[Een order aan één unit richten](#addressing-an-order-to-one-unit); de tweede sluit
hem af.

De `_include` is belangrijk: Spenser zoekt `Task.focus` op in de entries van die ene
Bundle in plaats van elke order apart op te halen, dus een Task waarvan de focus niet
wordt meegeleverd, wordt als probleem gemeld en overgeslagen.

`_count=5` is belangrijk bij het testen. Alleen de eerste vijf resultaten van elke
zoekopdracht worden per controle bekeken, dus bij een langere wachtrij kan het dat een
bepaalde order bij een bepaalde controle niet wordt opgepikt.

Zowel `http://` als `https://` werken. Certificaten worden niet gevalideerd, dus
behandel de verbinding zoals u elk ander niet-geauthenticeerd lokaal verkeer zou
behandelen.

### Een order aan één unit richten {#addressing-an-order-to-one-unit}

Veel units kunnen één orderserver delen, dus een order kan zeggen welke ervan hem moet
uitvoeren.

**Elke unit heeft een naam**, het netwerk dat hij in configuratiemodus toont:
`Spenser-` en de laatste twee bytes van zijn MAC-adres af fabriek, zoals
`Spenser-E3D4`. Het is `unitName` in `GET /settings`, en het dashboard toont hem in de
kop. Op de orderserver is de unit `Device/<naam>`, die hij zelf één keer per opstart
schrijft, met zijn identifier in `http://costateixeira.github.io/spenser/unit` en zijn
firmwareversie. Dat doet hij alleen met `writeBack` aan.

**De order noemt de unit in de Task**, in `Task.requestedPerformer`, het enige
element van de Task waarmee R5 een Device laat noemen: `Task.owner` en
`Task.performer.actor` accepteren er geen. Alleen de Devices die daar staan tellen;
een Organization of een soort uitvoerder zegt niets over welke unit.

```json
"requestedPerformer": [
  { "reference": { "reference": "Device/Spenser-E3D4", "display": "Spenser-E3D4" } }
]
```

Zie [een Task die aan één unit is gericht](Task-FulfillForOneUnit.html), de
[gewone order](MedicationRequest-PlainDarkOrderForOneUnit.html) waarnaar hij wijst,
en [de unit](Device-Spenser-E3D4.html) zoals hij op de server staat.

**Het verzoek kan de unit ook zelf noemen**, in de extensie
[dispensingDevice](StructureDefinition-dispensingDevice.html) van de IG. R5 heeft op
MedicationRequest geen element daarvoor: `performer` en `device` accepteren een
DeviceDefinition, een soort apparaat, en `dispenseRequest.dispenser` accepteert alleen
een Organization. De extensie bevat een logische referentie, de identifier van de
unit, dus de unit hoeft niet op de server geregistreerd te zijn:

```json
"extension": [ {
  "url": "http://costateixeira.github.io/spenser/StructureDefinition/dispensingDevice",
  "valueReference": {
    "identifier": { "system": "http://costateixeira.github.io/spenser/unit", "value": "Spenser-E3D4" },
    "display": "Spenser-E3D4"
  }
} ]
```

Zie [een order met de tag voor één unit](MedicationRequest-ActionableDarkOrderForOneUnit.html),
die geen Task heeft en zijn unit alleen in de extensie noemt.

Een unit kan worden genoemd met een letterlijke referentie, `Device/<naam>`, of met een
logische, een identifier in `http://costateixeira.github.io/spenser/unit`, zowel in
`requestedPerformer` als in de extensie.

**Bij elke controle bepaalt de unit voor welke unit een order is**: de units in
`Task.requestedPerformer` als de Task er een noemt, en anders de extensie
`dispensingDevice` van het verzoek.

| De order is voor | Wat de unit doet |
|---|---|
| andere units, niet deze | slaat hem over |
| deze unit, met of zonder andere | verstrekt hem |
| geen unit, met een Task | claimt de Task, en verstrekt hem als de claim gelukt is |
| geen unit, met de tag en zonder Task | verstrekt hem, als hij het eerst controleert |

De claim is een `PUT` van de Task waarin deze unit aan `requestedPerformer` is
toegevoegd, op voorwaarde van de zojuist gelezen versie (`If-Match`). Van twee units
die om dezelfde Task strijden, komt één schrijfactie door en wordt de andere
geweigerd, en de verliezer laat de Task met rust: bij zijn volgende controle noemt de
Task de winnaar. De status blijft `requested` zolang de Task geclaimd is, dus een Task
die op een lege baan wacht, wordt na het bijvullen opnieuw geprobeerd, door de unit
die hem claimde. Zonder `writeBack` kan er niets worden geclaimd, en wordt een Task
die geen unit noemt verstrekt zoals voorheen.

Een order met de tag en zonder Task kan zijn unit alleen in de extensie noemen. Met
meerdere units op één server geeft u orders met de tag de extensie, of gebruikt u
Tasks, met `orderMode=task`. Om een unit helemaal weg te houden van Tasks zonder
geadresseerde, voegt u `requestedperformer-reference:identifier=http://costateixeira.github.io/spenser/unit|<naam>`
toe aan zijn `taskQuery`. Een zoekopdracht vindt maar één vorm: Tasks die de unit als
`Device/<naam>` noemen, hebben in plaats daarvan `requestedperformer-reference=Device/<naam>` nodig.

**Elke MedicationDispense noemt de unit die hem maakte**, in `performer.actor`, dus de
server laat zien welke unit welke order heeft uitgevoerd.

### Orders die u kunt kopiëren {#orders-you-can-copy}

De IG bevat deze als formele voorbeelden:

* [Order die door een tag uitvoerbaar is gemaakt](MedicationRequest-ActionableDarkOrder.html)
* [Order die op zichzelf niet uitvoerbaar is](MedicationRequest-PlainMilkOrder.html)
* [Task die vraagt om ze uit te voeren](Task-FulfillPlainMilkOrder.html)
* [Teruggemelde verstrekking](MedicationDispense-DispenseForActionableDarkOrder.html)
* [Verstrekking die niet is gebeurd](MedicationDispense-DeclinedDispenseOutOfStock.html)
* [Voorraad instellen](InventoryReport-SetDarkTo17.html) en
  [aan de voorraad toevoegen](InventoryReport-Add5Milk.html)

De kleinste nuttige order, geplaatst op de orderserver:

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

Dezelfde body zonder `meta.tag` is het negatieve geval: Spenser moet die met rust
laten. Laat de tag weg, voeg een Task toe die ernaar verwijst, en ze wordt via de
andere route weer uitvoerbaar.

Geneesmiddelen komen uit het
[codesysteem SpenserMeds](CodeSystem-SpenserMeds.html): `chocolate-dark` en
`chocolate-milk`, één stukje per order. R5 plaatst de code in
`medication.concept`; een rechtstreeks geposte order mag ook de R4-schrijfwijze
`medicationCodeableConcept` gebruiken, die deze firmware nog aanvaardt.

### Niet-FHIR-interface {#non-fhir-interface}

Alles hieronder is de eigen beheer-API van de unit. Die is gewone JSON of tekst, is
geen FHIR, en is niet bedoeld om klinische gegevens uit te wisselen. Ze bestaat om een
unit te configureren, om hem tijdens een demo aan te sturen, en om het ingebouwde
dashboard aan te bieden.

| Groep | Endpoints |
|---|---|
| Orders | `/checkOrders` zet een controle in de wachtrij en geeft `202` terug, `/orders` meldt de laatste controle voor het dashboard, `/forgetOrders` wist de lijst van orders die al zijn afgehandeld |
| Instellingen | `/settings`, `/setSettings`, `/resetSettings` |
| Updates | `/ota/status`, `/ota/firmware`, `/ota/filesystem`, `/ota/file`, `/ota/check`, `/ota/rollback` |
| De sleutel | `/key`, binnen het hierboven beschreven venster |
| Voorraad en hardware | `/inventory`, `/setInventory`, `/resetInventory`, `/setServos`, `/flashServo1`, `/flashServo2`, `/setColor`, `/battery`, `/reset` |
| Wi-Fi en identiteit | `/`, `/scan`, `/cfg`, `/save`, `/wifi-settings`, `/wifi-reset`, `/wifi-reboot-config`, `/getMac`, `/setMac`, `/clearMac` |
| Captive portal | `/generate_204`, `/hotspot-detect.html`, `/fwlink`, `/ncsi.txt`, `/connecttest.txt` |

`/setSettings` aanvaardt elk van `serverUrl`, `orderMode` met de waarden `both`, `tag`
of `task`, `orderQuery`, `taskQuery`, `pollEnabled`, `pollSeconds` tussen 5 en
3600, `writeBack`, `giveUpOnStockEmpty`, `updateUrl`, `updateCheckHours`, en de
servoparameters. Het antwoord is het volledige instellingendocument, met daarin de
firmwareversie en nooit de sleutel.

Een unit controleert zijn orderserver elke `pollSeconds`, standaard 30, zolang
`pollEnabled` aan staat. `/checkOrders` dwingt onmiddellijk een controle af. Die route
keert terug voordat het werk klaar is, omdat het HTTP-werk in de hoofdlus gebeurt en
nooit in een request handler, dus een client moet wachten tot de controle klaar is in
plaats van dat aan te nemen.

`giveUpOnStockEmpty` bepaalt wat er gebeurt met een order die niet kan worden
uitgevoerd. Uit: de order wordt één keer als niet op voorraad gemeld en blijft open,
zodat het bijvullen van de baan ze bij een latere controle uitvoert. Aan: ze wordt één
keer gemeld en opgegeven, en een coördinerende Task wordt op `failed` gezet.

Alles wat niet overeenkomt, valt terug op een statisch bestand uit het bestandssysteem
van het apparaat, en zo wordt het dashboard aangeboden. `OPTIONS` geeft `200` terug voor
CORS-preflight.

### Interfaces die geen HTTP zijn {#interfaces-that-are-not-http}

* **mDNS.** De unit maakt zichzelf bekend als `spenser` met een HTTP-dienst op poort
  80, zodat `http://spenser.local` werkt zonder dat u zijn adres kent.
* **Access point en captive portal.** Zonder geconfigureerde Wi-Fi biedt hij een open
  netwerk aan en beantwoordt hij elke DNS-naam, zodat een telefoon of laptop de
  installatiepagina vanzelf opent.
* **Serieel.** Logs op 115200 baud, inclusief elke orderzoekopdracht en elke
  terugschrijving.
* **De knop.** Kort drukken verstrekt. Drie seconden is een soft reset. Tien seconden
  wist de opgeslagen inloggegevens, en de led wordt rood terwijl u de knop vasthoudt,
  om u te waarschuwen voordat u loslaat.

### Werken met een AI-agent {#working-with-an-ai-agent}

Elke unit biedt op **`http://spenser.local/llms.txt`** een handleiding aan die voor
AI-agents is geschreven. Die beschrijft elk endpoint, de exacte vormen die worden
aanvaard en geproduceerd, uitgewerkte voorbeelden, een test die de hele lus doorloopt,
en de fouten waar mensen in trappen. Wijs een agent naar die URL en hij kan zonder
gokken voorbeelden, tests of een client schrijven, tegen de unit die voor hem staat in
plaats van tegen documentatie die intussen is afgedreven.

Ze is via FHIR te ontdekken: het CapabilityStatement op `/metadata` noemt ze in
`implementation.description`, zodat een agent die bij het FHIR-toegangspunt begint, ze
vindt.

Twee dingen passen er goed bij. Het bestand `AGENTS.md` in de bronrepository gaat over
de repository zelf: hoe u bouwt en flasht, waar de routes staan, en hoe u de tests
uitvoert. De Bruno-collectie onder `bruno/` is een uitvoerbare versie van deze pagina:
ze is opgesplitst in de orderserver aan de ene kant en het apparaat aan de andere, en
elk scenario controleert op FHIR in plaats van op proza.
