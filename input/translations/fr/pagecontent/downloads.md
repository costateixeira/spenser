

### Micrologiciel

Le micrologiciel actuel d'une unité Spenser est publié à l'adresse
[costateixeira.github.io/spenser/firmware/](https://costateixeira.github.io/spenser/firmware/), avec les notes de version
de la version servie, les deux images et le manifeste que lit une unité :

* `firmware.bin` - le code
* `spiffs.bin` - le tableau de bord et le guide pour agents
* `manifest.json` - ce qu'une unité vérifie toutes les heures pour repérer une nouvelle version

Une unité se met à jour à partir de là : elle affiche un avis sur son propre tableau
de bord quand une version attend, et l'installe quand on le lui demande, après avoir
montré ce qu'elle contient. La page [Interfaces](interfaces.html) décrit les routes
de mise à jour, et le premier flashage d'une unité doit se faire par câble, car il
repartitionne la puce.
