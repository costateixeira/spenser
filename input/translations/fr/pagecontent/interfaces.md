Cette page documente toutes les interfaces qu'expose une unité Spenser : les
interfaces FHIR, l'API HTTP privée qu'elle utilise pour sa propre configuration,
et les interfaces qui ne sont pas du tout HTTP. C'est la référence derrière la
page [Utiliser Spenser](usage.html), et la source de vérité est le
CapabilityStatement que chaque unité publie à son propre `/metadata`.

Une unité est joignable sur le réseau local à `http://spenser.local`, qu'elle
annonce par mDNS, ou à l'adresse que son routeur lui attribue.

### Ce qui nécessite une clé {#what-needs-a-key}

La lecture d'une unité est libre : son CapabilityStatement, ses dispensations, ses
ordonnances, son stock et son tableau de bord sont accessibles à quiconque peut
la joindre. Tout ce qui *modifie* une unité nécessite la clé de cette unité :
dispenser, les réglages, le Wi-Fi, le stock et les mises à jour du micrologiciel.
Ces routes répondent `401` avec un OperationOutcome quand elle manque.

La clé est générée au premier démarrage de l'unité et affichée sur sa console
série à chaque démarrage. Elle circule sous la forme
`Authorization: Bearer <key>`, d'un en-tête `X-Spenser-Key`, ou de `?key=` pour un
client qui ne peut pas définir d'en-têtes. `GET /key` la renvoie pendant cinq
minutes après un redémarrage, et à tout moment tant que l'unité est en mode de
configuration : c'est la fenêtre dont dispose son propriétaire et que n'a pas un
passant. Une unité qui sert son propre point d'accès accepte tout sans clé, car
il n'y a là aucun réseau à défendre.

`rest.security.description` dans le CapabilityStatement de chaque unité dit la
même chose, afin qu'un client puisse le découvrir.

### Deux rôles {#two-roles}

Spenser est à la fois un **serveur** FHIR et un **client** FHIR, et la différence
compte au moment de décider où envoyer quelque chose.

* **En tant que serveur**, il accepte une ordonnance qui lui est envoyée
  directement et dispense sur-le-champ. L'envoi à l'appareil est en soi
  l'autorisation de dispenser.
* **En tant que client**, il interroge un serveur d'ordonnances pour trouver les
  ordonnances qu'il doit exécuter, et rend compte de ce qu'il a fait. Ici, une
  ordonnance n'est *pas* une instruction, et Spenser n'agit que sur les
  ordonnances rendues exécutables.

Les deux rôles sont déclarés dans son
[CapabilityStatement](CapabilityStatement-SpenserFHIRCapabilityStatement.html).

### Acteurs {#actors}

| Acteur | Ce qu'il fait |
|---|---|
| [Unité Spenser](ActorDefinition-SpenserUnit.html) | dispense, en tant que serveur FHIR et client FHIR |
| [Émetteur d'ordonnances](ActorDefinition-OrderPlacer.html) | demande du chocolat et décide si une ordonnance est exécutable |
| [Serveur d'ordonnances](ActorDefinition-OrderServer.html) | conserve les ordonnances jusqu'à ce qu'une unité vienne les chercher, et reçoit ses comptes rendus |
| [Propriétaire de l'unité](ActorDefinition-UnitOwner.html) | détient la clé, et configure, réapprovisionne et met à jour l'unité |
| [Éditeur des mises à jour](ActorDefinition-UpdatePublisher.html) | publie le manifeste et les images qu'une unité installe |

### Ce qui rend une ordonnance exécutable {#what-makes-an-order-actionable}

Selon le guide HL7 Clinical Orders Workflow, une MedicationRequest qui se trouve
sur un serveur est une autorisation, pas une commande. Spenser ne l'exécute que si
l'une de ces deux conditions est remplie :

1. **Un tag.** La demande porte le `meta.tag`
   `http://terminology.hl7.org/CodeSystem/common-tags#actionable`.
   Voir [Ordonnance rendue exécutable par un tag](MedicationRequest-ActionableDarkOrder.html).
2. **Une Task.** Une Task de statut `requested` pointe vers la demande dans
   `Task.focus`.
   Voir [Task demandant l'exécution d'une ordonnance](Task-FulfillPlainMilkOrder.html),
   qui rend [cette ordonnance simple](MedicationRequest-PlainMilkOrder.html)
   exécutable.

Ce ne sont **pas deux modes de l'appareil**. Spenser cherche les deux à chaque
vérification et agit sur ce qui se présente. Quand une ordonnance arrive par les
deux voies à la fois, la Task a la priorité, et l'ordonnance n'est quand même
dispensée qu'une seule fois. Une unité peut être limitée à une seule voie avec le
réglage `orderMode`, ce qui est utile pour montrer la différence et pas pour
grand-chose d'autre.

La personne qui clôture l'ordonnance dépend de la voie utilisée :

| voie | ce que Spenser définit | ce qu'il ne touche pas |
|---|---|---|
| tag, pas de Task | la MedicationRequest à `completed` | |
| une Task | la Task à `completed`, avec la dispensation dans `Task.output` | la MedicationRequest, qui reste `active` |

La seconde ligne est délibérée. Quand une Task coordonne le travail, clôturer la
demande revient à l'émetteur, pas à celui qui l'exécute, et une Task terminée est
pour l'émetteur le signal de le faire.

### Interface FHIR {#fhir-interface}

Servie par l'appareil lui-même.

| Interaction | Clé requise | Signification |
|---|---|---|
| `GET /metadata` | | CapabilityStatement de cette unité, qui déclare les deux rôles, les paramètres de recherche, l'opération et le schéma de sécurité |
| `POST /MedicationRequest` | oui | crée une ordonnance, ce qui la dispense |
| `GET /MedicationRequest` et `/{id}` | | les ordonnances acceptées par cette unité |
| `POST /$dispense` | oui | dispense en un seul appel, et répond avec la MedicationDispense |
| `GET /MedicationDispense` et `/{id}` | | ce que cette unité a dispensé ou refusé |
| `GET /InventoryReport` | | stock actuel, une ligne par couloir |
| `POST /InventoryReport` | oui | définit le stock à partir d'un rapport |

**La création se comporte comme une création.** Vous n'avez pas besoin de fournir
d'`id` : l'unité en attribue un si vous l'omettez, ce qu'un serveur FHIR est censé
faire. La réponse est `201` avec un en-tête `Location` pointant vers l'ordonnance
créée, un `ETag`, et la
[MedicationRequest](MedicationRequest-ActionableDarkOrder.html) créée dans le
corps. `Prefer: return=minimal` et `Prefer: return=OperationOutcome` sont tous
deux respectés. L'ordonnance est conservée, et peut donc être relue ensuite.

**La dispensation est une ressource distincte**, à
`/MedicationDispense/{id}-dispense` quand un morceau est sorti, ou à
`/MedicationDispense/{id}-declined` quand le couloir était vide. Quand ce que vous
voulez est la dispensation plutôt que l'ordonnance, utilisez l'opération :
`POST /$dispense` prend une MedicationRequest, ou des Parameters qui en
contiennent une, et répond `200` avec la
[MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.html). Une
opération rend compte d'elle-même dans la ressource qu'elle renvoie : un couloir
vide reste donc un `200`, qui porte
[une dispensation refusée](MedicationDispense-DeclinedDispenseOutOfStock.html). R5
a supprimé `MedicationDispense.statusReason` : un refus porte donc son motif dans
`notPerformedReason`, qui est un `CodeableReference`.

**Les recherches sont de vraies recherches.** Les deux magasins respectent `_id`,
`status`, `subject` et `_count`, et les dispensations respectent aussi
`authorizingPrescription`. Une référence correspond soit en entier, soit par son
seul id : `subject=Patient/123` et `subject=123` trouvent donc les mêmes
enregistrements. Les paramètres sont déclarés dans le CapabilityStatement, et le
lien self du Bundle indique ce que l'unité a compris.

**Les enregistrements survivent à un redémarrage.** Les ordonnances, les
dispensations et le stock sont conservés sur le système de fichiers de l'unité
plutôt qu'en mémoire : la redémarrer, ou la mettre à jour, n'efface donc pas ce
qu'elle a fait. Les enregistrements les plus anciens sont éliminés quand un
magasin est plein.

`GET /MedicationDispense` est aussi la façon de demander à une unité ce qu'elle a
fait. Outre les dispensations elles-mêmes, le Bundle porte une entrée dont
`search.mode` vaut `outcome` : un OperationOutcome dont la sévérité,
`issue.diagnostics` et `issue.details.text` décrivent la dernière vérification du
serveur d'ordonnances, y compris les voies que l'unité accepte et depuis combien
de temps elle a regardé.

**Les erreurs sont toujours un OperationOutcome** en `application/fhir+json`. Il
n'y a aucun second format d'erreur dans l'interface FHIR.

Le stock est rapporté sous la forme d'un
[InventoryReport](InventoryReport-SetDarkTo17.html), et peut être défini de la
même façon, soit en `snapshot`, soit en `difference`.

### Heure {#time}

Une dispensation porte `recorded`, `whenPrepared` et `whenHandedOver`, et un refus
porte `recorded`, dès que l'unité a joint un serveur NTP. Jusque-là, ces éléments
sont omis plutôt que devinés : un horodatage absent signifie que l'unité n'avait
pas d'horloge, jamais que l'événement a eu lieu à l'epoch. Il en va de même pour
`InventoryReport.reportedDateTime`.

### Mises à jour {#updates}

Le micrologiciel d'une unité et ses fichiers web sont tous deux remplaçables par
Wi-Fi, ce qui rend un distributeur distant maintenable. La puce conserve deux
emplacements d'application : un envoi est écrit dans celui qui ne s'exécute pas et
l'unité redémarre dessus ; une nouvelle image n'est marquée comme bonne qu'après
une minute de fonctionnement avec un réseau, et la précédente reste disponible
pour un retour arrière.

| Route | Signification |
|---|---|
| `GET /ota/status` | version, emplacement en cours d'exécution, taux de remplissage, disponibilité du retour arrière, horloge, dernier résultat |
| `POST /ota/firmware` | l'image du micrologiciel comme corps de la requête |
| `POST /ota/filesystem` | l'image du système de fichiers, qui transporte les fichiers web |
| `POST /ota/file?path=/index.html` | un seul fichier, sans redémarrage |
| `POST /ota/check` | récupère le manifeste de publication et indique ce qui attend |
| `POST /ota/install` | prend ce que la vérification a trouvé |
| `GET /ota/status` | indique aussi `updateAvailable`, `availableVersion` et depuis combien de temps elle a regardé |
| `POST /ota/rollback` | revient à l'image précédente |

Les versions sont publiées à côté de cette spécification, à l'adresse
[costateixeira.github.io/spenser/firmware/](https://costateixeira.github.io/spenser/firmware/),
et c'est là qu'une unité regarde par défaut. Cette page indique ce qui a changé
dans la version qu'elle sert, et propose à côté les binaires et le manifeste. Un
manifeste décrit une version pour l'unité :

```json
{ "version": "1.2.0",
  "firmware": "https://.../firmware.bin",
  "filesystem": "https://.../spiffs.bin" }
```

```
GET /setSettings?updateUrl=https://.../manifest.json&updateCheckMinutes=15
```

Une unité regarde toutes les 15 minutes par défaut, et `/ota/status` indique quand
elle a regardé pour la dernière fois et quand elle regardera de nouveau. Un
intervalle mesuré en heures ne se laisserait pas observer en train de fonctionner,
et un manifeste pèse moins d'un kilo-octet.

Regarder et prendre sont deux choses distinctes. Avec `updateMode=notify`, le
réglage par défaut, une vérification indique ce qui attend et s'arrête là :
`/ota/status` porte alors `updateAvailable` et `availableVersion`, le tableau de
bord affiche un avis indiquant "New firmware available" avec un bouton Install, et
rien ne redémarre sans qu'on l'ait demandé.

Une unité vérifie toutes les 15 minutes par défaut, et **se souvient de ce qu'elle
a trouvé**. L'avis survit à une coupure de courant, car une mise à jour qui
attendait avant qu'on débranche attend encore après, et un avis qui disparaît au
redémarrage est un avis auquel personne ne donne suite. Il s'efface de lui-même
quand une vérification ultérieure ne trouve rien de plus récent, ou dès que l'unité
exécute la version proposée.

**Le contenu d'une mise à jour peut se lire avant de la prendre.** Le manifeste
porte des notes de version ; l'unité les conserve, les sert dans `/ota/status` sous
`availableNotes` et `availableNotesUrl`, et le tableau de bord les affiche dans une
fenêtre contextuelle quand vous appuyez sur Install, avec la liste complète à un
lien de là. Installer à l'aveugle n'est pas une option qu'on devrait offrir à un
mainteneur.

Une version publiée porte le commit à partir duquel elle a été construite, sous la
forme `1.2.0+a1b2c3d`. C'est ce qui permet à une unité de distinguer une version de
la suivante, et d'en rester là une fois qu'elle en a installé une. Avec
`updateMode=install`, l'unité la prend d'elle-même, ce qui convient à une unité que
personne ne peut atteindre. Tout autre mot que le mot exact `install` compte comme
notify : un réglage mal saisi ne peut donc pas transformer un parc en unités qui se
mettent à jour sans prévenir.

Chaque unité indique ce qu'elle exécute par `software.version` dans son
CapabilityStatement et par `firmwareVersion` dans ses réglages, afin qu'on puisse
distinguer les unités d'un parc.

### Ce que Spenser demande à un serveur d'ordonnances {#what-spenser-asks-of-an-order-server}

Pointez une unité vers un serveur, et à chaque vérification elle lance deux
recherches et écrit en retour ce qui s'est passé :

```
GET  {server}/Task?status=requested&_include=Task:focus&_count=5
GET  {server}/MedicationRequest?_tag=http://terminology.hl7.org/CodeSystem/common-tags|actionable&status=active&intent=instance-order&_count=5
POST {server}/MedicationDispense
PUT  {server}/Task/{id}
PUT  {server}/MedicationRequest/{id}
```

Le `_include` compte : Spenser résout `Task.focus` à partir des entrées de ce seul
Bundle au lieu de récupérer chaque ordonnance séparément, de sorte qu'une Task dont
le focus n'est pas renvoyé avec elle est signalée comme un problème et ignorée.

`_count=5` compte pendant les tests. Seuls les cinq premiers résultats de chaque
recherche sont pris en compte par vérification : avec une file plus longue, une
ordonnance donnée peut donc ne pas être prise en charge lors d'une vérification
particulière.

`http://` et `https://` fonctionnent tous les deux. Les certificats ne sont pas
validés : traitez donc la liaison comme n'importe quel autre trafic local non
authentifié.

### Ordonnances à copier {#orders-you-can-copy}

L'IG les fournit comme exemples formels :

* [Ordonnance rendue exécutable par un tag](MedicationRequest-ActionableDarkOrder.html)
* [Ordonnance qui n'est pas exécutable à elle seule](MedicationRequest-PlainMilkOrder.html)
* [Task demandant son exécution](Task-FulfillPlainMilkOrder.html)
* [Dispensation signalée en retour](MedicationDispense-DispenseForActionableDarkOrder.html)
* [Dispensation qui n'a pas eu lieu](MedicationDispense-DeclinedDispenseOutOfStock.html)
* [Définir le stock](InventoryReport-SetDarkTo17.html) et
  [ajouter au stock](InventoryReport-Add5Milk.html)

La plus petite ordonnance utile, déposée sur le serveur d'ordonnances :

```json
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

Le même corps sans `meta.tag` est le cas négatif : Spenser doit le laisser
tranquille. Retirez le tag, ajoutez une Task qui pointe vers lui, et il
redevient exécutable par l'autre voie.

Les médicaments proviennent du
[système de codes SpenserMeds](CodeSystem-SpenserMeds.html) : `chocolate-dark` et
`chocolate-milk`, un morceau par ordonnance. R5 place le code dans
`medication.concept` ; une ordonnance envoyée directement peut aussi utiliser la
graphie R4 `medicationCodeableConcept`, que ce micrologiciel accepte encore.

### Interface non FHIR {#non-fhir-interface}

Tout ce qui suit est l'API d'administration propre à l'unité. C'est du simple JSON
ou du texte, ce n'est pas du FHIR, et ce n'est pas destiné à échanger des données
cliniques. Elle existe pour configurer une unité, la piloter pendant une
démonstration et servir le tableau de bord intégré.

| Groupe | Points de terminaison |
|---|---|
| Ordonnances | `/checkOrders` met une vérification en file et renvoie `202`, `/orders` rapporte la dernière vérification pour le tableau de bord, `/forgetOrders` efface la liste des ordonnances déjà traitées |
| Réglages | `/settings`, `/setSettings`, `/resetSettings` |
| Mises à jour | `/ota/status`, `/ota/firmware`, `/ota/filesystem`, `/ota/file`, `/ota/check`, `/ota/rollback` |
| La clé | `/key`, dans la fenêtre décrite plus haut |
| Stock et matériel | `/inventory`, `/setInventory`, `/resetInventory`, `/setServos`, `/flashServo1`, `/flashServo2`, `/setColor`, `/battery`, `/reset` |
| Wi-Fi et identité | `/`, `/scan`, `/cfg`, `/save`, `/wifi-settings`, `/wifi-reset`, `/wifi-reboot-config`, `/getMac`, `/setMac`, `/clearMac` |
| Portail captif | `/generate_204`, `/hotspot-detect.html`, `/fwlink`, `/ncsi.txt`, `/connecttest.txt` |

`/setSettings` accepte n'importe lequel des réglages `serverUrl`, `orderMode` avec
les valeurs `both`, `tag` ou `task`, `orderQuery`, `taskQuery`, `pollEnabled`,
`pollSeconds` entre 5 et 3600, `writeBack`, `giveUpOnStockEmpty`, `updateUrl`,
`updateCheckHours`, et les paramètres des servos. Il répond avec le document
complet des réglages, qui inclut la version du micrologiciel et jamais la clé.

Une unité vérifie son serveur d'ordonnances toutes les `pollSeconds`, 30 par
défaut, tant que `pollEnabled` est actif. `/checkOrders` force une vérification
immédiate. Il répond avant que le travail soit fait, car le travail HTTP se déroule
dans la boucle principale et jamais dans un gestionnaire de requête : un client
doit donc attendre la fin de la vérification plutôt que la supposer terminée.

`giveUpOnStockEmpty` décide du sort d'une ordonnance qui ne peut pas être exécutée.
Désactivé, l'ordonnance est signalée une fois en rupture de stock et laissée
ouverte : remplir le couloir permet donc de l'exécuter lors d'une vérification
ultérieure. Activé, elle est signalée une fois et abandonnée, et une Task qui
coordonne passe à `failed`.

Tout ce qui ne correspond à rien retombe sur un fichier statique du système de
fichiers de l'appareil, et c'est ainsi que le tableau de bord est servi. `OPTIONS`
renvoie `200` pour le preflight CORS.

### Interfaces qui ne sont pas HTTP {#interfaces-that-are-not-http}

* **mDNS.** L'unité s'annonce comme `spenser` avec un service HTTP sur le port 80 :
  `http://spenser.local` fonctionne donc sans connaître son adresse.
* **Point d'accès et portail captif.** Sans Wi-Fi configuré, elle sert un réseau
  ouvert et répond à tous les noms DNS, de sorte qu'un téléphone ou un ordinateur
  portable ouvre de lui-même la page de configuration.
* **Série.** Journaux à 115200 bauds, y compris chaque recherche d'ordonnances et
  chaque écriture en retour.
* **Le bouton.** Un appui court dispense. Trois secondes provoquent un redémarrage
  logiciel. Dix secondes effacent les identifiants enregistrés, et la LED passe au
  rouge pendant l'appui pour vous prévenir avant que vous ne lâchiez.

### Travailler avec un agent d'IA {#working-with-an-ai-agent}

Chaque unité sert un guide écrit pour les agents d'IA à
**`http://spenser.local/llms.txt`**. Il décrit chaque point de terminaison, les
formes exactes acceptées et produites, des exemples commentés, un test qui exerce
toute la boucle, et les erreurs qui piègent les gens. Pointez un agent vers cette
URL et il pourra écrire des exemples, des tests ou un client sans deviner, face à
l'unité que vous avez devant vous plutôt que face à une documentation qui a pu
dériver.

Il se découvre depuis FHIR : le CapabilityStatement à `/metadata` le mentionne dans
`implementation.description`, de sorte qu'un agent qui commence par le point
d'entrée FHIR le trouve.

Deux choses s'y associent bien. Le fichier `AGENTS.md` du dépôt source couvre le
dépôt lui-même, comment compiler et flasher, où se trouvent les routes, et comment
lancer les tests. La collection Bruno sous `bruno/` est une version exécutable de
cette page : elle est répartie entre le serveur d'ordonnances d'un côté et
l'appareil de l'autre, et chaque scénario vérifie du FHIR plutôt que de la prose.
