# Firmware - Spenser - a developer's companion v1.0.0

## Firmware

 
Deze pagina bevat vertalingen van de oorspronkelijke taal waarin de gids is geschreven. Informatie over deze vertalingen en instructies voor feedback vindt u [hier](translationinfo.md). 

De [firmware](https://github.com/costateixeira/spenser/tree/master/firmware) draait op een **dispenser op basis van de ESP32-S3**, met de [M5Stack AtomS3 Lite](https://shop.m5stack.com/products/atoms3-lite) en de [M5Stack Atomic Motion Base](https://shop.m5stack.com/products/atomic-motion), ontworpen om chocolade te verstrekken bij ontvangst van FHIR-`MedicationRequest`s via HTTP.

Hij ondersteunt:

* Een lokaal portaal voor Wi-Fi-configuratie (via captive portal of knop)
* RESTful endpoints voor FHIR-interactie 
* 📦 FHIR `InventoryReport` om de voorraad te rapporteren (GET) en aan te passen (POST)
* 🏥 `MedicationRequest`-resources aanvaarden via HTTP POST en antwoorden met `MedicationDispense`
 
* RESTful diensten voor debugging en voorraadbeheer

### Gebruik

1. Installeer PlatformIO - Let op: VSCode werkt, VSCodium niet
1. Sluit aan op een USB-poort. Gebruik op Windows de stuurprogramma's van Microsoft -**gebruik GEEN andere stuurprogramma's zoals CH340 enz.**
1. Voer vanuit de map`firmware`PlatformIo uit om te compileren, te uploaden en te monitoren
1. **Help alstublieft de code te verbeteren - PR's zijn meer dan welkom.**

-------

### 🌐 FHIR-endpoints

Deze endpoints voldoen aan [FHIR R5](https://hl7.org/fhir/R5):

#### GET /metadata

* Geeft een FHIR `CapabilityStatement` terug
* Vermeldt de ondersteuning voor de FHIR-resources

#### POST /MedicationRequest

* Aanvaardt een FHIR-resource `MedicationRequest` (JSON)
* Verstrekt pure chocolade of melkchocolade, afhankelijk van de medicatiecode
* Antwoordt met een resource `MedicationDispense`
* Is de voorraad op, dan antwoordt hij met een geweigerde `MedicationDispense`

#### POST /InventoryReport

* Aanvaardt een FHIR-resource `InventoryReport`
* Ondersteunt: 
* `countType: snapshot` — vervangt de voorraad
* `countType: difference` — past de voorraad stapsgewijs aan
 
* Valideert voorraadbeperkingen (bijv. geen negatieve waarden)
* Antwoordt met de bijgewerkte voorraad of een fout

#### GET /InventoryReport

* Geeft een `InventoryReport` in snapshotvorm terug die de huidige voorraad weergeeft
* Bevat de vaklocaties en de status van de artikelen

-------

### ⚙️ Configuratie- en debug-endpoints

Dit zijn hulpendpoints voor diagnose, installatie en interactief testen.

#### Wi-Fi-configuratie

| | |
| :--- | :--- |
| `GET /wifi-settings` | Markeert het apparaat om bij herstart naar de Wi-Fi-configuratiemodus te gaan |
| `GET /wifi-reboot-config` | Herstart meteen in de configuratiemodus |
| `GET /wifi-reset` | Wist de opgeslagen Wi-Fi-inloggegevens |
| `GET /startConfig` | Start de Wi-Fi-installatiemodus en herstart |
| `GET /wifi` | Stuurt door naar het configuratieportaal als er geen verbinding is |

#### Gebruikersinterface en informatie

| | |
| :--- | :--- |
| `GET /` | Biedt de UI aan vanuit SPIFFS, of stuurt door in AP-modus |
| `GET /ui.html` | Biedt de statische UI aan (`index.html`) |
| `GET /success` | Bevestigingsscherm na de Wi-Fi-installatie |
| `GET /ip-info` | Toont het IP-adres en stuurt daar automatisch naartoe |

#### Debugging en handmatige bediening

| | |
| :--- | :--- |
| `GET /setColor` | Wijzigt de kleur van de RGB-led via queryparameters |
| `GET /setServos` | Stelt de servohoeken in via queryparameters |
| `GET /reset` | Zet de led en beide servo's terug op 0 |
| `GET /flashServo1` | Zet servo 1 even op`dispenseAngle` |
| `GET /flashServo2` | Zet servo 2 even op`dispenseAngle` |
| `GET /inventory` | Toont de huidige voorraadniveaus in JSON |
| `GET /resetInventory?dark=10&milk=15` | Stelt de voorraadaantallen handmatig in |
| `GET /battery` | Meldt de batterijspanning en het percentage |

#### Compatibiliteit met captive portals

Deze endpoints sturen door naar `/success` om platformspecifieke captive portals af te handelen:

* `/generate_204`
* `/hotspot-detect.html`
* `/fwlink`
* `/connecttest.txt`
* `/ncsi.txt`
* `/i`

-------

### 🚀 Wi-Fi en opstarten

Zonder opgeslagen inloggegevens zet de firmware zijn eigen open toegangspunt op, met als naam `Spenser-` en de laatste twee bytes van zijn MAC-adres, op `192.168.4.1`. Maak verbinding met dat netwerk en de instelpagina opent vanzelf; daar krijgt de unit het netwerk waarmee hij verbinding moet maken, en die gegevens blijven bewaard over herstarts heen.
 Zodra hij op een netwerk zit, is hij bereikbaar op [http://spenser.local](http://spenser.local), dat hij via mDNS aankondigt als `spenser`.
 Zie [Een unit installeren](setup.md).

-------

### 🔋 Gedrag van de hardware

* **Pin van de knop:** GPIO 41 
* 3 seconden ingedrukt houden tijdens het opstarten: naar de Wi-Fi-configuratiemodus
* Kort indrukken tijdens de werking: verstrekt één puur chocolaatje - **alias PANIC ! / Hit Me !!**
 
* **Pin van de RGB-led:** GPIO 35 (WS2812)
* **Servo's:** 
* Servo 0: pure chocolade
* Servo 1: melkchocolade
* Standaard `dispenseAngle`: 97°
 

-------

### 📦 Opslag

* **SPIFFS** wordt gebruikt om `index.html` en de UI-bestanden aan te bieden.
* **Preferences** worden gebruikt om de vlag `forceConfig` voor de Wi-Fi-installatie te bewaren.

-------

### 🔋 Batterijbewaking

(WIP / YMMV)

* Leest de spanning af van de INA226-sensor op de Atomic Motion Base.
* Schat het batterijpercentage met een polynomiale benadering.
* Vraag de batterijstatus op via [`GET /battery`](#debugging--manual-control)

-------

### 🧪 Handmatig testen

Gebruik deze endpoints om de functionaliteit te testen:

* `GET /flashServo1` — Verstrekt handmatig pure chocolade
* `GET /flashServo2` — Verstrekt handmatig melkchocolade
* `GET /setColor?red=0&green=255&blue=0` — Zet de led op groen
* `GET /resetInventory?dark=20&milk=20` — Stelt de voorraad opnieuw in

-------

### ✅ Voorbeeld van een MedicationRequest-POST

```
{
  "resourceType": "MedicationRequest",
  "id": "req-123",
  "status": "active",
  "intent": "instance-order",
  "medicationCodeableConcept": {
    "coding": [
      {
        "code": "chocolate-dark",
        "display": "Dark Chocolate"
      }
    ]
  },
  "dosageInstruction": [
    { "text": "Dispense one dark chocolate" }
  ],
  "subject": { "reference": "Patient/example" }
}

```

