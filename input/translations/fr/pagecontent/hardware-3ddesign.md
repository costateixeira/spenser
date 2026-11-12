Voici les pièces 3D utilisées pour construire **Spenser**.


### Description

<br clear="all">

| Pièce | Image | Description | Téléchargements |
|------|-------|-------------|-----------|
| **Corps** | ![](spenser-body.png){:width="120px"} | Contient la pile de chocolats, le servomoteur et les rails de guidage, sur sa propre base. | [STL](spenser-body.stl) |
| **Poussoir** | ![](spenser-pusher.png){:width="120px"} | Coulisse le long des rails et pousse un chocolat vers la sortie. | [STL](spenser-pusher.stl) |
| **Bras** | ![](spenser-arm.png){:width="120px"} | Se fixe sur le palonnier du servo et entraîne le poussoir. | [STL](spenser-arm.stl) |
| **Goupille** | ![](spenser-pin.png){:width="120px"} | Axe reliant le bras au poussoir. | [STL](spenser-pin.stl) |
{:.table-bordered}

### Pour des chocolats plus petits {#for-smaller-chocolates}

Le couloir ci-dessus accepte un morceau jusqu'à 60 × 39 mm, ce qui convient à
un napolitain belge. Un napolitain suisse est plus petit — un Lindt Napolitain
mesure environ 40 × 25 mm — et a de la place pour bouger. Le jeu de 9 mm dans
le sens de la poussée est celui qui compte : il suffit à un morceau pour se
glisser vers l'avant sous la paroi de retenue, où le poussoir le rencontre par
la tranche.

Ce sont les mêmes pièces, le couloir réduit de 19,25 mm en largeur, de 9 mm
en profondeur et de 20,2 mm en longueur de glissière : elles acceptent un
morceau **jusqu'à 40 × 30 mm**, à la même épaisseur de 5,5 à 7,5 mm.
Mesurez un morceau avant d'imprimer : 30 mm est la limite dans le sens de
la poussée.

Deux choses changent dans la construction. Réglez `anglePush=81` sur cette
unité, au lieu de la valeur par défaut de 77. Et montez le bras de sorte
qu'au repos il soit environ 47° en arrière de la perpendiculaire au couloir,
et non d'équerre : cela recule toute la course et c'est ce qui permet au
corps d'être aussi court. Le contrôle : au repos, la face de poussée doit se
trouver juste derrière la pile de chocolats. En fin de course la queue
s'arrête juste avant la bouche, ce qui est voulu. La goupille est la même
pièce qu'avant et n'exige aucun perçage ici : son trou dans le bras fait 3 mm
dans ces fichiers, contre 2,76 sur le bras standard, qui s'imprime sous la
cote et serre sur la goupille de 2,55 mm.

| Pièce | Description | Téléchargements |
|------|-------------|-----------|
| **Corps** | Un couloir de 41,75 × 31 mm au lieu de 61 × 40 ; 44,75 × 80,8 × 105 mm hors tout. Rien n'y change de hauteur : l'épaulement qui retient le poussoir, le boîtier du servo et la sortie restent là où le corps standard les place, et c'est le bras qui est raccourci pour dégager l'épaulement. | [STL](spenser-body-small.stl) |
| **Poussoir** | 40,65 × 46 mm, pour correspondre au couloir plus étroit, avec la rainure de goupille ouverte à 2,8 mm. | [STL](spenser-pusher-small.stl) |
| **Bras** | 26,75 mm entre les trous au lieu de 41, ce qui donne une course de 34,53 mm avec `anglePush=81` et laisse son extrémité à un millimètre de l'épaulement. | [STL](spenser-arm-small.stl) |
| **Goupille** | La même pièce que ci-dessus. | [STL](spenser-pin.stl) |
{:.table-bordered}

### Nomenclature

**Les quantités indiquées sont celles du distributeur à 2 positions.**

| Article   | Description | Quantité |
|---|---|---------|
| Corps | Contient les chocolats, le moteur et les rails de guidage | 2 |
| Bras | Bras rotatif fixé au servo | 2 |
| Goupille  | Relie le bras au poussoir | 2  |
| Poussoir  | Pousse un chocolat vers la sortie  | 2  |
{:.table-bordered}
