Deux couloirs, un pour le chocolat noir et un pour le chocolat au lait. Tout ce qui
est marqué **2x** se fait une fois par couloir.

Imprimez les [pièces 3D](hardware-3ddesign.html), achetez
l'[électronique](hardware-bom.html), et commencez par mettre le
[micrologiciel](firmware.html) sur le contrôleur.

Ces dessins ont été réalisés à partir des modèles 3D des pièces, et non photographiés
sur une unité terminée. Si quelque chose ici ne correspond pas à ce que vous avez en
main, merci de nous le [signaler](https://github.com/costateixeira/spenser/issues).
{:.stu-note}

<div class="assembly" markdown="0">

<figure class="assembly-step assembly-wide">
  <img src="assembly-00.svg" alt="Les pièces : deux corps, poussoirs, bras, axes, servos et palonniers, un Atom S3 Lite, une base Atomic Motion, une batterie externe, six vis et un tournevis. Un morceau de chocolat peut mesurer jusqu'à 60 sur 39 mm, pour 5,5 à 7,5 mm d'épaisseur."/>
  <figcaption>Vérifiez que vous avez tout. Les palonniers et les vis sont fournis avec les servos, et il vous faut aussi un câble USB-C. Un morceau de chocolat ne doit pas dépasser 60 × 39 mm et doit faire entre 5,5 et 7,5 mm d'épaisseur.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">1</span>
  <img src="assembly-01.svg" alt="Un servo est descendu dans le boîtier du corps, l'arbre vers le bas."/>
  <figcaption>Descendez le servo dans le boîtier, arbre vers le bas, jusqu'à ce que ses oreilles reposent sur le rebord. L'arbre pointe vers le plateau.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">2</span>
  <img src="assembly-02.svg" alt="Deux vis passent dans les oreilles du servo."/>
  <figcaption>Fixez-le avec deux vis passées dans les oreilles. Serrez juste ce qu'il faut, sans forcer : elles entrent dans du plastique.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">3</span>
  <img src="assembly-03.svg" alt="L'Atom est enfoncé sur l'extrémité de la base de mouvement opposée à la batterie."/>
  <figcaption>Enfoncez l'Atom sur l'extrémité de la base Atomic Motion opposée à la batterie.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">4</span>
  <img src="assembly-04.svg" alt="La base glisse vers le bas dans la baie à l'avant de la tour, côté batterie en premier, l'Atom en haut."/>
  <figcaption>Faites glisser la base vers le bas dans la baie à l'avant d'une tour, côté batterie en premier, de sorte que l'Atom se retrouve en haut. La batterie et le bouton de l'Atom sont tournés vers le plateau, et les connecteurs des servos du côté du servo. Un seul corps en a besoin.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">5</span>
  <img src="assembly-05.svg" alt="Deux corps côte à côte. Une fiche de servo va sur le connecteur marqué S4 et l'autre sur S3. Un détail montre une fiche qui s'enfonce sur les broches."/>
  <figcaption>Placez les corps côte à côte. Enfoncez la fiche du servo du couloir chocolat noir sur le connecteur marqué S4 et celle du couloir chocolat au lait sur S3, que le micrologiciel appelle canaux 3 et 2. Le fil marron est la masse : alignez-le sur la marque de masse à côté du connecteur. Un autre choix peut être réglé sur le tableau de bord.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">6</span>
  <img src="assembly-06.svg" alt="Une batterie externe est reliée par un câble USB-C au port situé au-dessus de l'Atom, et l'interrupteur de la base est allumé."/>
  <figcaption>Branchez la batterie externe sur le port USB-C situé au-dessus de l'Atom et allumez la base. Ouvrez le tableau de bord et appuyez sur <strong>Move both to rest</strong>. Ne tournez plus les servos à la main à partir de maintenant. La batterie de la base se recharge par le même câble.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">7</span>
  <img src="assembly-07.svg" alt="Le poussoir glisse dans la glissière par l'avant. Un gros plan montre les nervures en dessous."/>
  <figcaption>Engagez le poussoir dans la glissière par l'avant, nervures vers le bas et longue fente vers vous.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">8</span>
  <img src="assembly-08.svg" alt="Le palonnier est enfoncé dans le bras. Le bras glisse sous le boîtier du servo, et une vis est vissée par le dessous du corps."/>
  <figcaption>Enfoncez un palonnier dans la rainure du bras. Glissez le bras sous le boîtier et sur l'arbre, puis fixez-le avec la vis du palonnier, par le trou situé sous le corps.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">8</span>
  <img src="assembly-08b.svg" alt="Vue du dessus : en bonne position, le bras pointe vers l'avant du plateau et le fond de la tour est dégagé. En mauvaise position, le bras pointe vers la tour et le poussoir dépasse par l'arrière."/>
  <figcaption>Au repos, le bras pointe vers l'avant et le poussoir laisse le fond de la tour dégagé. Sinon, retirez le bras et remettez-le sur l'arbre dans la bonne position.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">9</span>
  <img src="assembly-09.svg" alt="La goupille tombe à travers l'extrémité du bras et dans la fente du poussoir. Un gros plan montre sa tête reposant sur le bras."/>
  <figcaption>Laissez tomber la goupille à travers le bras et dans la fente, tête vers le haut. Elle doit coulisser librement le long de la fente. Si elle coince, limez un peu la fente pour l'élargir.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">10</span>
  <img src="assembly-10.svg" alt="Vu de derrière, le poussoir sort par la fente à l'arrière de la tour, et un morceau de chocolat sort devant lui."/>
  <figcaption>Tour encore vide, appuyez sur <strong>Test dark cycle</strong> et <strong>Test milk cycle</strong> sur le tableau de bord. Le poussoir doit passer par la fente à l'arrière, puis revenir. C'est par ici que sort le chocolat : laissez la place pour une tasse.</figcaption>
</figure>

<figure class="assembly-step">
  <span class="assembly-number">11</span>
  <img src="assembly-11.svg" alt="Des morceaux de chocolat sont empilés à plat par le haut de la tour."/>
  <figcaption>Empilez le chocolat à plat par le haut de la tour. La fenêtre à l'arrière montre ce qu'il reste. Indiquez à l'unité combien vous en avez chargé, sur le tableau de bord.</figcaption>
</figure>

<figure class="assembly-step">
  <img src="assembly-12.svg" alt="Le distributeur terminé, avec ses deux couloirs, à côté d'une personne souriante tenant un morceau de chocolat."/>
  <figcaption>C'est fini. Maintenant, <a href="usage.html">déposez une ordonnance</a>.</figcaption>
</figure>

</div>

Ces dessins sont générés à partir des mêmes fichiers STL que ceux que vous imprimez.
Pour en modifier un, éditez `tools/assembly/build.py` dans le dépôt source et
relancez-le.
