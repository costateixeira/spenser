# Setup - Spenser - a developer's companion v1.0.0

## Setup

 
Deze pagina bevat vertalingen van de oorspronkelijke taal waarin de gids is geschreven. Informatie over deze vertalingen en instructies voor feedback vindt u [hier](translationinfo.md). 

De unit is gemonteerd, geflasht en aangezet. Wat rest is hem op een netwerk krijgen en hem richten op de plek waar de orders vandaan gaan komen.

Eén feit bepaalt al het andere op deze pagina: **er hoeft nooit iets van buitenaf verbinding met een unit te maken.** Hij is bereikbaar wanneer het netwerk dat toestaat, en hij gaat zelf naar buiten kijken wanneer het netwerk dat niet toestaat. Daarom werkt een verstrekker op congres-wifi, en dat is precies waar dit soort demonstratie meestal sneuvelt.

### Eerste start

Zonder opgeslagen inloggegevens is de unit zijn eigen open wifi-netwerk. Dat netwerk heet `Spenser-` gevolgd door de laatste twee bytes van zijn MAC-adres, bijvoorbeeld `Spenser-E3D4`, en dat is overal elders ook de naam van de unit.

1. Maak verbinding met`Spenser-XXXX`vanaf een telefoon of laptop. De unit antwoordt op elke DNS-naam die hem gevraagd wordt, dus de instelpagina opent normaal gesproken vanzelf. Zo niet, ga dan naar[http://192.168.4.1](http://192.168.4.1).
1. Kies een netwerk uit de lijst, geef het wachtwoord en bewaar. De unit start opnieuw op en sluit zich erbij aan.
1. Vanaf dan zit hij op[http://spenser.local](http://spenser.local), of op het adres dat de router hem heeft gegeven.

**Neem de sleutel mee voordat u de instelmodus verlaat.** Alles wat een unit **verandert** heeft hem nodig: verstrekken, instellingen, voorraad, wifi en updates. `GET /key` geeft hem vijf minuten na een herstart terug, en op elk moment zolang de unit in instelmodus staat. Hij wordt ook bij elke start op de seriële console gezet, op 115200 baud. Een unit die zijn eigen toegangspunt bedient, aanvaardt alles zonder sleutel, omdat daar geen netwerk te verdedigen valt.

De knop drie seconden ingedrukt houden tijdens het opstarten brengt de instelmodus terug. Tien seconden wist de opgeslagen inloggegevens; de LED wordt rood zolang u hem vasthoudt, als waarschuwing voordat u loslaat.

### Welke opstelling

| | |
| :--- | :--- |
| Op uw eigen netwerk, met een orderserver | Allebei: rechtstreeks bij de unit geplaatst, of op de server gezet en opgehaald |
| Op uw eigen netwerk, zonder server | Rechtstreeks bij de unit geplaatst |
| Op zijn eigen toegangspunt | Rechtstreeks bij de unit geplaatst, door wie er verbinding mee maakt |
| Op een netwerk dat zijn clients isoleert | Op een orderserver op het internet gezet, en opgehaald |

#### Uw eigen netwerk

Thuis, kantoor, lab. De unit zit op de wifi, `spenser.local` werkt, en beide wegen staan voor u open: plaats een MedicationRequest rechtstreeks bij hem en er komt een chocolaatje uit, of zet orders op een orderserver en laat de unit ze ophalen.

Dit is de opstelling om tegenaan te ontwikkelen, omdat u beide helften kunt zien.

#### Helemaal geen netwerk

Laat de unit op zijn eigen toegangspunt staan en laat mensen verbinding maken met `Spenser-XXXX`. De unit zit op `192.168.4.1`, heeft daar geen sleutel nodig, en orders die bij hem geplaatst worden, worden meteen verstrekt. De volledige uitwisseling is [rechtstreeks bij de unit bestellen](ExampleScenario-DirectOrderScenario.md).

Zonder uplink ontbreken er twee dingen. Er is geen klok, want er is geen NTP, dus laat de unit `whenHandedOver` en consorten weg in plaats van een tijd te verzinnen. En er is geen orderserver, dus valt er niets op te halen; zet het periodiek ophalen uit met `pollEnabled=0` zodat de unit ophoudt met proberen.

#### Een netwerk dat zijn clients isoleert

Congreswifi, hotelwifi en zowat elk gastennetwerk zetten elke client in zijn eigen cel. Clients bereiken het internet en verder niets. `spenser.local` zal niet werken, het adres van de unit zal niet antwoorden, en er valt niets bij hem te plaatsen.

Met de unit is niets mis. Hij gaat nog steeds naar buiten.

Zet een orderserver ergens op het internet, richt de unit daarop, en laat iedereen zijn orders daar schrijven. De unit haalt op, neemt het werk dat aan hem gericht is, verstrekt, en meldt terug wat hij heeft gedaan. Dat is [bestellen via een orderserver](ExampleScenario-TaskOrderScenario.md), en client-isolatie is de reden dat dat scenario bestaat.

Controleer dit vóór de sessie en niet tijdens: ga met twee toestellen op het netwerk en probeer het ene vanaf het andere te bereiken.

#### Een hotspot op een telefoon

Hetzelfde als uw eigen netwerk, en in uw eigen hand, zolang de telefoon zijn clients niet ook isoleert — sommige doen dat. Het is de gebruikelijke uitweg wanneer de wifi van de locatie geïsoleerd blijkt en de orderserver toch al op het internet staat.

### De unit op een orderserver richten

Alles hieronder heeft de sleutel nodig.

```
KEY=... # van de seriële console, of van GET /key

curl -H "X-Spenser-Key: $KEY" \
  "http://spenser.local/setSettings?serverUrl=https://example.org/fhir&orderMode=both&pollEnabled=1&pollSeconds=30&writeBack=1&giveUpOnStockEmpty=0"

```

* `orderMode` staat standaard op `both`: de unit neemt zowel getagde orders als Tasks. `tag` of `task` beperkt hem tot één ervan. Het zijn geen twee werkingsmodi, alleen twee manieren waarop een order uitvoerbaar wordt.
* `pollSeconds` ligt tussen 5 en 3600, standaard 30. `GET /checkOrders` forceert nu een controle, en antwoordt `202` voordat die controle klaar is.
* `giveUpOnStockEmpty` uit laat een order die niet kon worden uitgevoerd openstaan, zodat het bijvullen van de lade hem bij een volgende controle alsnog uitvoert. Aan wordt hij één keer gemeld en losgelaten.

Het dashboard op `http://spenser.local` stelt hetzelfde in, en daarnaast ook voorraad, servohoeken en updates.

### Meerdere units in één ruimte

Elke unit haalt bij dezelfde server op en zou anders dezelfde orders nemen. Noem degene die een order moet uitvoeren in `Task.requestedPerformer`, en in de `dispensingDevice`-extensie op de order zelf; elke andere unit slaat hem over.

Elke controle kijkt alleen naar de eerste vijf resultaten. Een langere rij op de server kan één controle voorbijlopen, wat handig is om te weten voordat er bij een demo een rij ontstaat.

### Wanneer het niet werkt

* **`spenser.local` werkt niet.** Gebruik het adres van de router of van de seriële console. mDNS is het onderdeel dat het vaakst ontbreekt, niet de unit.
* **Alles antwoordt `401`.** De sleutel ontbreekt of klopt niet. Herstart de unit en lees `GET /key` binnen vijf minuten.
* **Verstrekkingen hebben geen tijdstip.** De klok is niet gezet: NTP heeft nog niet geantwoord, of er is geen weg naartoe. De unit laat de tijd weg in plaats van er een te verzinnen.
* **Orders worden niet opgepikt.** Controleer `serverUrl`, controleer of `pollEnabled` aanstaat, en onthoud dat afgehandelde orders onthouden worden: `GET /forgetOrders` voordat u hetzelfde scenario een tweede keer draait.
* **Een test loopt steeds de unit voor de voeten.** Zet het periodiek ophalen uit met `pollEnabled=0` tijdens het testen en stuur de controles zelf aan, en zet het daarna weer aan.
* **De instelpagina opent niet vanzelf.** Ga naar [http://192.168.4.1](http://192.168.4.1) terwijl u met `Spenser-XXXX` verbonden bent.

[Interfaces](interfaces.md) bevat de referentie achter dit alles: elke route, wat een sleutel nodig heeft, en wat elke instelling doet.

