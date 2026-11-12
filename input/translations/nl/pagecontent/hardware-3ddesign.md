Hieronder staan de 3D-onderdelen waarmee **Spenser** wordt gebouwd.


### Beschrijving

<br clear="all">

| Onderdeel | Afbeelding | Beschrijving | Downloads |
|------|-------|-------------|-----------|
| **Behuizing** | ![](spenser-body.png){:width="120px"} | Bevat de chocoladestapel, de servomotor en de geleiderails, op een eigen voet. | [STL](spenser-body.stl) |
| **Duwer** | ![](spenser-pusher.png){:width="120px"} | Schuift langs de rails en duwt één chocolaatje naar buiten. | [STL](spenser-pusher.stl) |
| **Arm** | ![](spenser-arm.png){:width="120px"} | Wordt op de hoorn van de servo bevestigd en drijft de duwer aan. | [STL](spenser-arm.stl) |
| **Pen** | ![](spenser-pin.png){:width="120px"} | Asje dat de arm met de duwer verbindt. | [STL](spenser-pin.stl) |
{:.table-bordered}

### Voor kleinere chocolaatjes {#for-smaller-chocolates}

De baan hierboven neemt een stuk tot 60 × 39 mm, wat bij een Belgische
napolitain past. Een Zwitserse is kleiner — een Lindt Napolitain is ongeveer
40 × 25 mm — en heeft er ruimte om te schuiven. De 9 mm speling in de
duwrichting is de speling die telt: genoeg om een stuk onder de keerwand naar
voren te laten kruipen, waar de duwer het met de kop raakt.

Dit zijn dezelfde onderdelen, met de baan 7 mm smaller, 9 mm minder diep
en de rail 20,2 mm korter gesneden, zodat ze een stuk **tot 40 × 30 mm**
nemen, bij dezelfde dikte van 5,5 tot 7,5 mm. Meet een stuk voordat u
print: 30 mm is de grens in de duwrichting.

De diepte is de maat die op het stuk is gesneden, en die is exact. De breedte
niet, en dat kan ook niet: de ruimte waarin de Atomic Motion Base zakt, het
kanaal waarin de servostekkers komen en de uitsparing van de servo zelf staan
alle drie tussen dezelfde twee zijwanden als de baan en nemen samen 53 van de
61 mm, zodat alleen de strook van 7 mm naast de richel vrij is. Een stuk van
40 mm breed houdt 14 mm zijspeling over in wat rest, en dat kost niets: een
stuk van 30 × 40 kan niet draaien in een baan van 31 mm diep, hoe breed die
baan ook is.

Twee dingen veranderen aan de bouw. Zet `anglePush=81` op deze unit, in plaats
van de standaard 77. En monteer de arm zo dat hij in rust ongeveer 47° terug
staat ten opzichte van dwars op de baan, en niet haaks erop: dat zet het hele
traject verder naar achteren en is wat de behuizing zo kort laat zijn. De
controle is dat het duwvlak in rust net achter de chocoladestapel uitkomt.
Aan het eind van de slag komt de staart net niet uit de mond, wat de bedoeling
is. De pen is hetzelfde onderdeel als eerder en hoeft hier niet geboord te
worden: het pengat in de arm is 3 mm in deze bestanden, tegen 2,76 in de
standaardarm, die onder de maat print en op de pen van 2,55 mm klemt.

Voor een ander formaat stuk snijdt [`tools/resize/build.py`](https://github.com/costateixeira/spenser/blob/master/tools/resize/build.py) deze drie
onderdelen op maat en laat zien wat het traject dan wordt. Een stuk wordt
opgegeven als breedte van de baan × lengte erlangs × dikte, dus
`--piece 40x30x7 --name small` is deze variant; zonder iets erachter neemt het
script de Belgische mignonette waarvoor de onderdelen hierboven al gesneden
zijn, en zegt dat er niets te snijden is.

| Onderdeel | Beschrijving | Downloads |
|------|-------------|-----------|
| **Behuizing** | Een baan van 54 × 31 mm in plaats van 61 × 40; 57 × 80,8 × 105 mm in totaal. Er beweegt verder niets in: de richel die de duwer op zijn plaats houdt, de ruimte voor de servo, de uitgang, de ruimte voor de module en het kanaal ernaast zitten alle waar de standaardbehuizing ze heeft. | [STL](spenser-body-small.stl) |
| **Duwer** | 52,9 × 46 mm, passend bij de smallere baan, met de pensleuf opengewerkt tot 2,8 mm. | [STL](spenser-pusher-small.stl) |
| **Arm** | 26,75 mm tussen de gaten in plaats van 41, wat met `anglePush=81` een slag van 34,53 mm geeft, passend bij de minder diepe baan. | [STL](spenser-arm-small.stl) |
| **Pen** | Hetzelfde onderdeel als hierboven. | [STL](spenser-pin.stl) |
{:.table-bordered}

### Stuklijst

**De vermelde aantallen gelden voor de dispenser met 2 posities.**

| Onderdeel   | Beschrijving | Aantal |
|---|---|---------|
| Behuizing | Bevat de chocolaatjes, de motor en de geleiderails | 2 |
| Arm | Draaiende arm die op de servo is bevestigd | 2 |
| Pen  | Verbindt de arm met de duwer | 2  |
| Duwer  | Duwt een chocolaatje naar buiten  | 2  |
{:.table-bordered}
