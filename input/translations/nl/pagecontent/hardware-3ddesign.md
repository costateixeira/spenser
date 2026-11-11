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

Dit zijn dezelfde onderdelen, met de baan 19,25 mm smaller, 9 mm minder diep
en de rail 20,2 mm korter gesneden, zodat ze een stuk **tot 40 × 30 mm**
nemen, bij dezelfde dikte van 5,5 tot 7,5 mm. Meet een stuk voordat u
print: 30 mm is de grens in de duwrichting.

Drie dingen veranderen aan de bouw. Zet `anglePush=81` op deze unit, in plaats
van de standaard 77. Monteer de arm zo dat hij in rust ongeveer 47° terug
staat ten opzichte van dwars op de baan, en niet haaks erop: dat zet het hele
traject verder naar achteren en is wat de behuizing zo kort laat zijn. De
controle is dat het duwvlak in rust net achter de chocoladestapel uitkomt. En
boor het pengat in de arm op 2,6 mm — het wordt geprint als een voorboring
van 1,25 mm, waar de pen van 2,55 mm niet in past. Aan het eind van de slag
steekt de staart 1,7 mm uit de mond, wat de bedoeling is; de pen is hetzelfde
onderdeel als eerder.

| Onderdeel | Beschrijving | Downloads |
|------|-------------|-----------|
| **Behuizing** | Een baan van 41,75 × 31 mm in plaats van 61 × 40; 44,75 × 80,8 × 107 mm in totaal. De richel die de duwer op zijn plaats houdt, zit 2 mm hoger om de arm door te laten, en de steun waarop de oren van de servo rusten zakt diezelfde 2 mm weer, zodat de arm niet met hem meestijgt. | [STL](spenser-body-small.stl) |
| **Duwer** | 40,65 × 46 mm, passend bij de smallere baan, met de pensleuf opengewerkt tot 2,8 mm. | [STL](spenser-pusher-small.stl) |
| **Arm** | 28,75 mm tussen de gaten in plaats van 41, wat met `anglePush=81` een slag van 37,11 mm geeft. | [STL](spenser-arm-small.stl) |
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
