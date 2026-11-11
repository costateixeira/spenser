Twee banen, één voor pure chocolade en één voor melkchocolade. Alles wat met **2x**
is gemarkeerd, gebeurt één keer per baan.

Print eerst de [3D-onderdelen](hardware-3ddesign.html), koop de
[elektronica](hardware-bom.html), en zet de [firmware](firmware.html) op de
controller.

Deze tekeningen zijn gemaakt op basis van de 3D-modellen van de onderdelen, niet
gefotografeerd van een afgewerkte unit. Als iets hier niet overeenkomt met wat u in
handen hebt, [laat het ons dan weten](https://github.com/costateixeira/spenser/issues).
{:.stu-note}

<div class="assembly" markdown="0">

<figure class="assembly-step assembly-wide">
  <img src="assembly-00.svg" alt="De onderdelen: twee behuizingen, duwers, armen, pennen, servo's en hoorns, één Atom S3 Lite, één Atomic Motion-basis, één powerbank, zes schroeven en een schroevendraaier. Een stuk chocolade mag tot 60 bij 39 mm groot zijn en 5,5 tot 7,5 mm dik."/>
  <figcaption>Controleer of u alles hebt. De hoorns en schroeven worden met de servo's meegeleverd, en u hebt ook een USB-C-kabel nodig. Een stuk chocolade mag niet groter zijn dan 60 × 39 mm en moet tussen 5,5 en 7,5 mm dik zijn.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">1</span>
  <img src="assembly-01.svg" alt="Een servo wordt in de kast op de behuizing neergelaten, met de as naar beneden."/>
  <figcaption>Laat de servo in de kast zakken, met de as naar beneden, tot de oren op de richel rusten. De as wijst naar het plateau.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">2</span>
  <img src="assembly-02.svg" alt="Twee schroeven gaan door de oren van de servo."/>
  <figcaption>Zet hem vast met twee schroeven door de oren. Aangedraaid, niet muurvast: ze gaan in plastic.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">3</span>
  <img src="assembly-03.svg" alt="De Atom wordt op het uiteinde van de motion-basis tegenover de batterij gedrukt."/>
  <figcaption>Druk de Atom op het uiteinde van de Atomic Motion-basis tegenover de batterij.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">4</span>
  <img src="assembly-04.svg" alt="De basis schuift omlaag in het vak aan de voorkant van de toren, met de batterij eerst en de Atom bovenaan."/>
  <figcaption>Schuif de basis omlaag in het vak aan de voorkant van één toren, met het batterij-uiteinde eerst, zodat de Atom bovenaan komt. De batterij en de knop van de Atom zijn naar de lade gericht, en de servoaansluitingen zitten aan de kant van de servo. Maar één behuizing heeft hem nodig.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">5</span>
  <img src="assembly-05.svg" alt="Twee behuizingen naast elkaar. De ene servostekker gaat op de aansluiting gemarkeerd S4, de andere op S3. Een detail toont een stekker die op de pinnen gaat."/>
  <figcaption>Zet de behuizingen naast elkaar. Druk de servostekker van de baan voor pure chocolade op de aansluiting gemarkeerd S4 en die van de baan voor melkchocolade op S3, wat de firmware kanaal 3 en 2 noemt. De bruine draad is massa: laat hem overeenkomen met het massateken naast de aansluiting. Op het dashboard kunt u een andere keuze instellen.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">6</span>
  <img src="assembly-06.svg" alt="Een powerbank is met een USB-C-kabel verbonden met de poort boven op de Atom, en de aan/uit-schakelaar van de basis staat aan."/>
  <figcaption>Sluit de powerbank aan op de USB-C-poort boven op de Atom en zet de basis aan. Open het dashboard en druk op <strong>Move both to rest</strong>. Draai de servo's vanaf nu niet meer met de hand. De eigen batterij van de basis laadt via dezelfde kabel op.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">7</span>
  <img src="assembly-07.svg" alt="De duwer schuift van voren in de geul. Een detail toont de ribbels aan de onderkant."/>
  <figcaption>Schuif de duwer van voren in de geul, met de ribbels naar beneden en de lange sleuf naar u toe.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">8</span>
  <img src="assembly-08.svg" alt="De hoorn wordt in de arm gedrukt. De arm schuift onder de servokast, en een schroef wordt van onder de behuizing ingedraaid."/>
  <figcaption>Druk een hoorn in de groef van de arm. Schuif de arm onder de kast en op de as, en zet hem dan vast met de hoornschroef, door het gat aan de onderkant van de behuizing.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">8</span>
  <img src="assembly-08b.svg" alt="Van boven gezien: in de juiste stand wijst de arm naar de voorkant van het plateau en is de vloer van de toren vrij. In de verkeerde stand wijst de arm naar de toren en steekt de duwer aan de achterkant uit."/>
  <figcaption>In rust wijst de arm naar voren en laat de duwer de vloer van de toren vrij. Is dat niet zo, haal de arm er dan af en zet hem in de juiste stand terug op de as.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">9</span>
  <img src="assembly-09.svg" alt="De pen valt door het uiteinde van de arm in de sleuf van de duwer. Een detail toont de kop, die op de arm rust."/>
  <figcaption>Laat de pen door de arm in de sleuf vallen, met de kop naar boven. Hij moet vrij langs de sleuf kunnen schuiven. Loopt hij vast, vijl de sleuf dan iets breder.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">10</span>
  <img src="assembly-10.svg" alt="Van achteren gezien: de duwer komt uit de sleuf aan de achterkant van de toren, en een stukje chocolade gaat hem voor."/>
  <figcaption>Druk, met de toren nog leeg, op het dashboard op <strong>Test dark cycle</strong> en <strong>Test milk cycle</strong>. De duwer moet door de sleuf aan de achterkant reiken en dan terugkeren. Hier komt de chocolade naar buiten, dus laat plaats voor een kopje.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">11</span>
  <img src="assembly-11.svg" alt="Stukjes chocolade worden plat in de bovenkant van de toren gestapeld."/>
  <figcaption>Stapel de chocolade plat in de bovenkant van de toren. Het venster aan de achterkant toont hoeveel er nog over is. Geef op het dashboard aan de unit door hoeveel u hebt geladen.</figcaption>
</figure>

<figure class="assembly-step">
  <img src="assembly-12.svg" alt="De afgewerkte dispenser met twee banen, naast een glimlachende persoon met een stukje chocolade."/>
  <figcaption>Klaar. Nu <a href="usage.html">een order plaatsen</a>.</figcaption>
</figure>

</div>

Deze tekeningen worden gegenereerd uit dezelfde STL-bestanden die u print. Om er een te
wijzigen, past u `tools/assembly/build.py` in de bronrepository aan en voert u het
opnieuw uit.
