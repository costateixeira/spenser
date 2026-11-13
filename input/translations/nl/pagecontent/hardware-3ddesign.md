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

Dit zijn dezelfde onderdelen, met de baan 17,5 mm smaller, 9 mm minder diep
en de rail 20,2 mm korter gesneden, zodat ze een stuk **tot 40 × 30 mm**
nemen, bij dezelfde dikte van 5,5 tot 7,5 mm. Meet een stuk voordat u
print: 30 mm is de grens in de duwrichting.

De diepte is de maat die op het stuk is gesneden, en die is exact. De breedte
niet: die wordt bepaald door de ruimte waarin de Atomic Motion Base zakt,
24 mm voor een module van 24 mm, en door de uitsparing van de servo ernaast,
12,26 mm voor een huis van 12,2. Beide staan tussen dezelfde twee zijwanden
als de baan en uit geen van beide kan iets weg, zodat 17,5 mm alles is wat
deze onderdelen in de breedte kunnen afstaan. Een stuk van 40 mm breed houdt
2,5 mm zijspeling over in wat rest, en zelfs een ruime pasvorm zou daar
niets kosten: een stuk van 30 × 40 kan niet draaien in een baan van 31 mm
diep, hoe breed die baan ook is.

Twee dingen veranderen aan de bouw. Zet `anglePush=78,6` op deze unit, in plaats
van de standaard 77. En monteer de arm zo dat hij in rust ongeveer 44,5° terug
staat ten opzichte van dwars op de baan, en niet haaks erop: dat zet het hele
traject verder naar achteren en is wat de behuizing zo kort laat zijn. De
controle is dat het duwvlak in rust net achter de chocoladestapel uitkomt. De
26,7 mm gaat er aan de achterkant af, achter de duwer, en niet bij de mond:
het stuk komt er aan de andere kant uit, en 6,5 mm daarvan gaat er onder de
servo weer in, waardoor zijn ruimte tegen het achtervlak komt te liggen. De
servo zelf gaat er omgekeerd in ten opzichte van de standaardunit, zodat de
kabel aan de achterkant naar buiten komt; de pen gaat dan in de tweede sleuf
van de duwer, die de 5 mm wegneemt die de omgekeerde behuizing de as verzet. De pen heeft hier een eigen
onderdeel en hoeft niet geboord te worden: het pengat in de arm is 3,1 mm in
deze bestanden tegen 2,76 in de standaardarm, en de pen zelf is 2,3 mm in
plaats van 2,55. Beide helften moesten mee. Een klein gat print onder de maat
en een dun asje erboven, en samen aten ze de 0,44 mm speling op die de
tekening had, zodat de pen er niet in ging; nu is er 0,79 mm. De standaardpen
blijft zoals hij is — boor de standaardarm 2,6 mm als u die bouwt.

Voor een ander formaat stuk snijdt [`tools/resize/build.py`](https://github.com/costateixeira/spenser/blob/master/tools/resize/build.py) deze drie
onderdelen op maat en laat zien wat het traject dan wordt. Een stuk wordt
opgegeven als breedte van de baan × lengte erlangs × dikte, dus
`--piece 40x30x7 --name small` is deze variant; zonder iets erachter neemt het
script de Belgische mignonette waarvoor de onderdelen hierboven al gesneden
zijn, en zegt dat er niets te snijden is.

| Onderdeel | Beschrijving | Downloads |
|------|-------------|-----------|
| **Behuizing** | Een baan van 43,5 × 31 mm in plaats van 61 × 40; 46,5 × 80,8 × 105 mm in totaal. De ruimte voor de module houdt haar volle 24 mm en de servo zijn 12,26, en geen enkele hoogte erin verandert: de richel die de duwer op zijn plaats houdt, de ruimte voor de servo en de uitgang zitten waar de standaardbehuizing ze heeft. De servo gaat er omgekeerd in, zodat zijn kabel aan de achterkant van de unit naar buiten komt in plaats van naar het magazijn, en zijn hele ruimte zit 6,5 mm verder naar achteren zodat de as ongeveer blijft waar hij was. De kabel moet dan de hele lengte van de toren overbruggen, en daarom loopt de zijwand van het magazijn 12,7 mm verder naar voren over de toren heen, even hoog als de modulerail ertegenover en met hetzelfde venster erin, zodat de kabel ertegenaan kan liggen. | [STL](spenser-body-small.stl) |
| **Duwer** | 42,4 × 46 mm, passend bij de smallere baan, met twee pensleuven van 2,55 mm: de pen past in beide, en de tweede, 5 mm verder naar binnen, houdt de duwer de hele slag 5 mm verder naar achteren, en dat is de sleuf die deze behuizing vraagt, nu de servo omgekeerd zit. | [STL](spenser-pusher-small.stl) |
| **Arm** | 26,75 mm tussen de gaten in plaats van 41, wat met `anglePush=78,6` een slag van 33,76 mm geeft, passend bij de minder diepe baan. | [STL](spenser-arm-small.stl) |
| **Pen** | 2,3 mm asdikte in plaats van 2,55, de andere helft van de pasvorm met de arm. | [STL](spenser-pin-small.stl) |
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
