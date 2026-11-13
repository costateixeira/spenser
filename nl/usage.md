# Gebruik - Spenser - a developer's companion v1.0.0

## Gebruik

 
Deze pagina bevat vertalingen van de oorspronkelijke taal waarin de gids is geschreven. Informatie over deze vertalingen en instructies voor feedback vindt u [hier](translationinfo.md). 

Spenser verstrekt chocolade, en behandelt chocolade als een geneesmiddel. U drukt dus niet op een knop om wat te krijgen. U plaatst een order, en de dispenser beslist of hij die mag uitvoeren.

Deze pagina loopt daar van buiten naar binnen doorheen. De pagina [Interfaces](interfaces.md) is de referentie erachter.

### Waar de order naartoe gaat

Met een unit die op uw bureau staat, kunt u rechtstreeks praten. Met een unit ergens anders niet, dus de opstelling die ertoe doet is die waarbij orders op een FHIR-server staan en de dispenser ze komt zoeken.

De dispenser pollt zijn orderserver om de dertig seconden. U plaatst daar een order, en binnen ongeveer een halve minuut valt er een stukje chocolade uit het apparaat. Niets duwt iets naar de dispenser, en niets hoeft te weten waar hij staat.

### De order

Post een MedicationRequest naar de orderserver, met de codes van [SpenserMeds](CodeSystem-SpenserMeds.md): `chocolate-dark` of `chocolate-milk`. Eén stukje tegelijk, de enige hoeveelheid die het profiel [SpenserRequest](StructureDefinition-SpenserRequest.md) toestaat.

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

Het volledige voorbeeld staat [hier](MedicationRequest-ActionableDarkOrder.md). Het deel dat het werk doet, is `meta.tag`.

### Waarom de tag

Een MedicationRequest is een machtiging, geen instructie. Iemand kan een order in het dossier hebben zonder dat iemand van plan is die nu meteen uit te voeren, en aan een dispenser die zich in de kamer leegt telkens wanneer er een order wordt geschreven, heeft niemand veel.

Spenser wacht dus tot hem wordt verteld dat een order klaar is om uitgevoerd te worden, wat de richtlijnen van Clinical Orders Workflow een uitvoerbare (actionable) order noemen. Haal de tag uit het voorbeeld hierboven en u hebt [een order die Spenser negeert](MedicationRequest-PlainMilkOrder.md): nog steeds een volkomen geldige order, alleen niet een die iemand heeft gevraagd uit te voeren.

### De andere manier om het te zeggen

Soms schrijft de ene persoon de order, en komt de vraag om ze uit te voeren later, of van ergens anders. Daar dient een Task voor. Laat de order zoals ze is, en post [een Task die ernaar verwijst](Task-FulfillPlainMilkOrder.md) met status `requested` en de order in `Task.focus`.

Beide routes werken, en de dispenser zoekt bij elke poll naar allebei. U hoeft hem niet in de ene of de andere modus te zetten. Als een order tegelijk met een tag en een Task opduikt, wordt ze nog steeds één keer verstrekt.

Het verschil blijkt achteraf, in wie wat afsluit:

| | | |
| :--- | :--- | :--- |
| de tag | de order op`completed` | niets |
| een Task | de Task op`completed`, met de verstrekking in`Task.output` | de order, die`active`blijft |

De tweede rij is bewust zo. Wanneer een Task het werk coördineert, is het afsluiten van de order de zaak van de plaatser, en een voltooide Task is het signaal om dat te doen.

### Wat er terugkomt

Elk stukje chocolade levert op de server een [MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.md) op, die via `authorizingPrescription` terugverwijst naar de order. Dat is het bewijs dat er fysiek iets is gebeurd, en daarnaar zoekt u als u wilt weten of uw order is uitgevoerd:

```
GET {server}/MedicationDispense?_count=20

```

### Als het niet lukt

Een baan raakt leeg. Spenser zegt dat, in plaats van stil te vallen: hij post [een verstrekking die niet is gebeurd](MedicationDispense-DeclinedDispenseOutOfStock.md), met status `declined` en de reden in `notPerformedReason`. Hij meldt dit één keer, niet bij elke poll.

Wat er dan met de order gebeurt, is een instelling. Standaard blijft de order open, zodat het bijvullen van de baan ze bij een latere poll uitvoert zonder dat iemand iets opnieuw hoeft te posten. De andere keuze is de order opgeven, en als een Task het werk coördineerde, wordt die Task op `failed` gezet.

### Een unit in de gaten houden

De dispenser houdt in FHIR zijn eigen register bij van wat hij heeft gedaan, of de order nu van een server kwam of hem rechtstreeks werd aangereikt:

```
GET http://spenser.local/MedicationDispense

```

De Bundle bevat zijn recente verstrekkingen, de nieuwste eerst. Ook bevat ze één entry met `search.mode` op `outcome`: een OperationOutcome die zegt hoe de laatste poll is verlopen, met welke server hij sprak, hoe lang geleden, hoeveel orders hij vond en hoeveel hij uitvoerde. Als er niets uitkomt, lees dan eerst die entry. Meestal staat de reden erin, en ze maakt het onderscheid tussen een dispenser die zijn server niet kan bereiken en een die correct werkt en gewoon niets heeft gekregen dat hij mag uitvoeren.

Het eigen scherm van de dispenser toont dezelfde twee dingen, en dat zijn de twee die ertoe doen: wat er in elke baan zit, en wat de laatste controle heeft gedaan.

Voor niets van het bovenstaande is toestemming nodig. Om een unit te wijzigen wel: handmatig verstrekken, instellingen, voorraad, Wi-Fi en updates hebben allemaal de sleutel van die unit nodig, die hij bij het opstarten op zijn seriële console afdrukt en die hij na een herstart vijf minuten lang afgeeft. Lezen wat hij heeft gedaan, vereist dat nooit.

### De instellingen die ertoe doen

Het grootste deel van de configuratie van een unit gaat over servo's, Wi-Fi en leds. Deze instellingen veranderen hoe orders zich gedragen:

| | |
| :--- | :--- |
| Order server | de FHIR-basis-URL die hij pollt |
| Accepted routes | zowel een tag als een Task, wat de standaard is, of beperkt tot één om het verschil te demonstreren |
| Check every | seconden tussen polls, standaard 30 |
| Report back | of hij de verstrekking en de afsluiting naar de server schrijft |
| Give up when the lane is empty | een order die niet uitgevoerd kan worden opgeven, of open houden voor een bijvulling |

### Als u ernaast staat

U kunt een order rechtstreeks naar de dispenser posten. Er is dan geen tag en geen Task, want de order met de hand posten is zelf de beslissing om te verstrekken, en hij antwoordt met de MedicationDispense:

```
POST http://spenser.local/MedicationRequest

```

En dan is er nog de knop aan de voorkant, die helemaal zonder FHIR verstrekt.

Ook een unit buiten bereik blijft onderhoudbaar: zowel zijn firmware als zijn webbestanden kunnen via Wi-Fi worden vervangen, en hij kan zichzelf up-to-date houden vanuit een gepubliceerde release. De pagina [Interfaces](interfaces.md) geeft de details.

**Voor noodgevallen heeft Spenser een "Hit me"-knop om wat chocolade te verstrekken.**
 **Deze functie moet met voorzichtigheid worden gebruikt.**

