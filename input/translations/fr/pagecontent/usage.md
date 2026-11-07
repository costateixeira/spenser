Spenser dispense du chocolat, et il traite le chocolat comme un médicament. Vous
n'appuyez donc pas sur un bouton pour en obtenir. Vous déposez une ordonnance, et
le distributeur décide s'il a le droit d'y donner suite.

Cette page parcourt le tout de l'extérieur vers l'intérieur. La page
[Interfaces](interfaces.html) en est la référence.

### Où va l'ordonnance

On peut parler directement à une unité posée sur votre bureau. Pas à une unité
située ailleurs : le montage qui compte est donc celui où les ordonnances résident
sur un serveur FHIR et où le distributeur vient les chercher.

Le distributeur interroge son serveur d'ordonnances toutes les trente secondes.
Vous y déposez une ordonnance, et dans la demi-minute environ un morceau de
chocolat tombe de la machine. Rien n'envoie quoi que ce soit au distributeur, et
personne n'a besoin de savoir où il se trouve.

### L'ordonnance

Envoyez une MedicationRequest au serveur d'ordonnances, avec les codes
[SpenserMeds](CodeSystem-SpenserMeds.html) : `chocolate-dark` ou
`chocolate-milk`. Un morceau à la fois, seule quantité que le profil
[SpenserRequest](StructureDefinition-SpenserRequest.html) autorise.

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

L'exemple complet se trouve
[ici](MedicationRequest-ActionableDarkOrder.html). La partie qui fait le travail
est `meta.tag`.

### Pourquoi le tag

Une MedicationRequest est une autorisation, pas une instruction. Quelqu'un peut
avoir une ordonnance au dossier sans que personne n'entende la faire exécuter
tout de suite, et un distributeur qui se vide dans la pièce à chaque ordonnance
rédigée ne rend pas vraiment service.

Spenser attend donc qu'on lui dise qu'une ordonnance est prête à être traitée, ce
que le guide Clinical Orders Workflow appelle une ordonnance exécutable
(*actionable order*). Retirez le tag de l'exemple ci-dessus et vous obtenez
[une ordonnance que Spenser ignorera](MedicationRequest-PlainMilkOrder.html) :
toujours parfaitement valide, simplement personne n'a demandé qu'on l'exécute.

### L'autre façon de le dire

Il arrive que l'ordonnance soit rédigée par une personne et que la demande
d'exécution vienne plus tard, ou d'ailleurs. C'est à cela que sert une Task.
Laissez l'ordonnance telle quelle, et envoyez
[une Task qui pointe vers elle](Task-FulfillPlainMilkOrder.html) avec le statut
`requested` et l'ordonnance dans `Task.focus`.

Les deux voies fonctionnent, et le distributeur cherche les deux à chaque
interrogation. Vous ne le configurez pas dans un mode ou dans l'autre. Si une
ordonnance se présente avec un tag et une Task en même temps, elle n'est
quand même dispensée qu'une fois.

La différence apparaît ensuite, dans qui clôture quoi :

| comment l'ordonnance a été rendue exécutable | ce que Spenser définit | ce qu'il vous laisse |
|---|---|---|
| le tag | l'ordonnance à `completed` | rien |
| une Task | la Task à `completed`, avec la dispensation dans `Task.output` | l'ordonnance, qui reste `active` |

La seconde ligne est délibérée. Quand une Task coordonne le travail, terminer
l'ordonnance est l'affaire de son émetteur, et une Task terminée est le signal
pour le faire.

### Ce qui revient

Chaque morceau de chocolat produit une
[MedicationDispense](MedicationDispense-DispenseForActionableDarkOrder.html) sur
le serveur, qui renvoie à l'ordonnance par `authorizingPrescription`. C'est la
trace qu'il s'est physiquement passé quelque chose, et c'est ce qu'il faut
chercher pour savoir si votre ordonnance a été exécutée :

```
GET {server}/MedicationDispense?_count=20
```

### Quand il ne peut pas

Un couloir finit par se vider. Spenser le dit au lieu de se taire : il envoie
[une dispensation qui n'a pas eu lieu](MedicationDispense-DeclinedDispenseOutOfStock.html),
avec le statut `declined` et le motif dans `notPerformedReason`. Il le signale
une fois, pas à chaque interrogation.

Ce qu'il advient alors de l'ordonnance est un réglage. Par défaut, l'ordonnance
reste ouverte : remplir le couloir permet de l'exécuter lors d'une interrogation
ultérieure, sans que personne ne renvoie quoi que ce soit. L'autre choix est de
l'abandonner, et si une Task coordonnait le travail, cette Task passe à `failed`.

### Observer une unité

Le distributeur tient son propre registre de ce qu'il a fait, en FHIR, que
l'ordonnance soit venue d'un serveur ou lui ait été remise directement :

```
GET http://spenser.local/MedicationDispense
```

Le Bundle contient ses dispensations récentes, les plus récentes d'abord. Il
porte aussi une entrée dont le `search.mode` vaut `outcome` : un OperationOutcome
qui indique comment s'est passée la dernière interrogation, à quel serveur elle
s'est adressée, il y a combien de temps, combien d'ordonnances elle a trouvées et
combien elle en a exécutées. Si rien ne sort, lisez d'abord cette entrée. Elle dit
généralement pourquoi, et elle distingue un distributeur qui n'arrive pas à
joindre son serveur d'un distributeur qui fonctionne correctement et à qui on n'a
simplement rien donné qu'il ait le droit de traiter.

L'écran du distributeur affiche les deux mêmes choses, qui sont les deux qui
comptent : ce qu'il y a dans chaque couloir, et ce qu'a donné la dernière
vérification.

Rien de ce qui précède ne demande d'autorisation. Modifier une unité, si :
dispenser à la main, les réglages, le stock, le Wi-Fi et les mises à jour
nécessitent tous la clé de cette unité, qu'elle affiche sur sa console série au
démarrage et qu'elle remet pendant cinq minutes après un redémarrage. Lire ce
qu'elle a fait ne la demande jamais.

### Les réglages qui comptent

L'essentiel de la configuration d'une unité concerne les servos, le Wi-Fi et les
LED. Voici ceux qui changent le comportement des ordonnances (les libellés sont
ceux du tableau de bord, qui reste en anglais) :

| Réglage | Ce qu'il décide |
|---|---|
| Order server | l'URL de base FHIR qu'elle interroge |
| Voies acceptées (Accept orders made actionable by) | à la fois un tag et une Task, ce qui est le réglage par défaut, ou une seule des deux pour montrer la différence |
| Check every | secondes entre les interrogations, 30 par défaut |
| Report back | si elle écrit la dispensation et la clôture sur le serveur |
| Give up when the lane is empty | abandonner une ordonnance impossible à exécuter, ou la garder ouverte en attendant un remplissage |

### Quand vous êtes juste à côté

Vous pouvez envoyer une ordonnance directement au distributeur. Il n'y a alors ni
tag ni Task, car l'envoyer à la main est en soi la décision de dispenser, et
il répond avec la MedicationDispense :

```
POST http://spenser.local/MedicationRequest
```

Et il y a le bouton en façade, qui dispense sans aucun FHIR.

Une unité hors de portée reste maintenable : son micrologiciel et ses fichiers web
peuvent tous deux être remplacés par Wi-Fi, et elle peut se tenir à jour à partir
d'une version publiée. La page [Interfaces](interfaces.html) donne les détails.

**En cas d'urgence, Spenser dispose d'un bouton "Hit me" pour dispenser un peu de chocolat.**  
**Cette fonction est à utiliser avec prudence.**  
{:.stu-note}
