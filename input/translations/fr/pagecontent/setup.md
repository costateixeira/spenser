L'unité est assemblée, le micrologiciel est chargé et elle est sous tension. Il
reste à la mettre sur un réseau et à la diriger vers l'endroit d'où viendront
les ordonnances.

Un seul fait détermine tout le reste de cette page : **rien n'a jamais besoin de
se connecter à une unité depuis l'extérieur.** On peut l'atteindre quand le
réseau le permet, et elle va chercher le travail elle-même quand le réseau ne le
permet pas. C'est pour cela qu'un distributeur fonctionne sur le Wi-Fi d'une
conférence, là où ce genre de démonstration meurt d'habitude.

### Premier démarrage {#first-boot}

Sans identifiants enregistrés, l'unité est son propre réseau Wi-Fi ouvert. Ce
réseau s'appelle `Spenser-` suivi des deux derniers octets de son adresse MAC,
par exemple `Spenser-E3D4`, et c'est aussi le nom de l'unité partout ailleurs.

1. Rejoignez `Spenser-XXXX` depuis un téléphone ou un ordinateur portable.
   L'unité répond à tous les noms DNS qu'on lui demande, si bien que la page de
   configuration s'ouvre normalement d'elle-même. Sinon, allez à
   [http://192.168.4.1](http://192.168.4.1).
2. Choisissez un réseau dans la liste, donnez le mot de passe et enregistrez.
   L'unité redémarre et le rejoint.
3. À partir de là elle est à [http://spenser.local](http://spenser.local), ou à
   l'adresse que le routeur lui a attribuée.

**Relevez la clé avant de quitter le mode configuration.** Tout ce qui *modifie*
une unité en a besoin : dispenser, réglages, stock, Wi-Fi et mises à jour.
`GET /key` la renvoie pendant cinq minutes après un redémarrage, et à tout
moment tant que l'unité est en mode configuration. Elle est aussi écrite sur la
console série, à 115200 bauds, à chaque démarrage. Une unité qui sert son propre
point d'accès accepte tout sans clé, parce qu'il n'y a là aucun réseau à
défendre.

Maintenir le bouton trois secondes au démarrage ramène le mode configuration.
Dix secondes effacent les identifiants enregistrés ; la LED passe au rouge tant
que vous maintenez, pour vous avertir avant de relâcher.

### Quel montage choisir {#which-arrangement}

| Où se trouve l'unité | Comment les ordonnances lui parviennent |
|---|---|
| Sur votre réseau, avec un serveur d'ordonnances | Les deux : déposées directement sur l'unité, ou placées sur le serveur et récupérées |
| Sur votre réseau, sans serveur | Déposées directement sur l'unité |
| Sur son propre point d'accès | Déposées directement sur l'unité, par qui l'a rejointe |
| Sur un réseau qui isole ses clients | Placées sur un serveur d'ordonnances sur Internet, et récupérées |

#### Votre propre réseau {#your-own-network}

Maison, bureau, laboratoire. L'unité est sur le Wi-Fi, `spenser.local` se
résout, et les deux voies vous sont ouvertes : déposez un MedicationRequest
directement sur elle et un chocolat sort, ou placez des ordonnances sur un
serveur et laissez l'unité les récupérer.

C'est le montage sur lequel développer, parce qu'on y voit les deux moitiés.

#### Aucun réseau du tout {#no-network-at-all}

Laissez l'unité sur son propre point d'accès et laissez les gens rejoindre
`Spenser-XXXX`. L'unité est à `192.168.4.1`, elle n'y demande pas de clé, et les
ordonnances déposées sur elle sont dispensées sur-le-champ. L'échange complet
est [commander directement à l'unité](ExampleScenario-DirectOrderScenario.html).

Sans liaison montante, deux choses manquent. Il n'y a pas d'horloge, parce qu'il
n'y a pas de NTP, et l'unité omet donc `whenHandedOver` et ses voisins plutôt
que d'inventer une heure. Et il n'y a pas de serveur d'ordonnances, donc rien à
interroger ; coupez l'interrogation périodique avec `pollEnabled=0` pour que
l'unité cesse d'essayer.

#### Un réseau qui isole ses clients {#a-network-that-isolates-its-clients}

Le Wi-Fi des conférences, celui des hôtels et presque tous les réseaux invités
placent chaque client dans sa propre cellule. Les clients atteignent Internet et
rien d'autre. `spenser.local` ne se résoudra pas, l'adresse de l'unité ne
répondra pas, et rien ne pourra lui être déposé.

L'unité, elle, va très bien. Elle sort toujours.

Mettez un serveur d'ordonnances quelque part sur Internet, dirigez l'unité vers
lui, et laissez chacun y écrire ses ordonnances. L'unité interroge, prend le
travail qui lui est adressé, dispense, et rend compte de ce qu'elle a fait.
C'est [commander via un serveur d'ordonnances](ExampleScenario-TaskOrderScenario.html),
et l'isolation des clients est la raison d'être de ce scénario.

Vérifiez-le avant la session et non pendant : rejoignez le réseau avec deux
appareils et essayez d'atteindre l'un depuis l'autre.

#### Un partage de connexion {#a-phone-hotspot}

Comme votre propre réseau, et sous votre contrôle, à condition que le téléphone
n'isole pas lui aussi ses clients — certains le font. C'est le repli habituel
quand le Wi-Fi du lieu se révèle isolé et que le serveur d'ordonnances est déjà
sur Internet.

### Diriger l'unité vers un serveur d'ordonnances {#pointing-it-at-an-order-server}

Tout ce qui suit demande la clé.

```sh
KEY=... # de la console série, ou de GET /key

curl -H "X-Spenser-Key: $KEY" \
  "http://spenser.local/setSettings?serverUrl=https://example.org/fhir&orderMode=both&pollEnabled=1&pollSeconds=30&writeBack=1&giveUpOnStockEmpty=0"
```

* `orderMode` vaut `both` par défaut : l'unité accepte aussi bien les
  ordonnances marquées d'un tag que les Tasks. `tag` ou `task` la restreint à
  l'une des deux. Ce ne sont pas deux modes de fonctionnement, seulement deux
  façons de rendre une ordonnance exécutable.
* `pollSeconds` est compris entre 5 et 3600, 30 par défaut. `GET /checkOrders`
  force une vérification immédiate, et répond `202` avant que celle-ci soit
  terminée.
* `giveUpOnStockEmpty` désactivé laisse ouverte une ordonnance qui n'a pas pu
  être exécutée, de sorte que remplir le couloir l'exécute à une vérification
  ultérieure. Activé, elle est signalée une fois puis abandonnée.

Le tableau de bord sur `http://spenser.local` règle les mêmes choses, ainsi que
le stock, les angles des servos et les mises à jour.

### Plusieurs unités dans une même salle {#several-units-in-one-room}

Chaque unité interroge le même serveur et prendrait sinon les mêmes ordonnances.
Nommez celle qui doit exécuter une ordonnance dans `Task.requestedPerformer`, et
dans l'extension `dispensingDevice` sur l'ordonnance elle-même ; toutes les
autres unités la laissent passer.

Chaque vérification ne regarde que les cinq premiers résultats. Une file plus
longue que cela sur le serveur peut déborder une vérification, ce qu'il vaut
mieux savoir avant qu'une file se forme devant une démonstration.

### Quand cela ne marche pas {#when-it-does-not-work}

* **`spenser.local` ne se résout pas.** Utilisez l'adresse donnée par le routeur
  ou par la console série. mDNS est la pièce la plus souvent absente, pas
  l'unité.
* **Tout répond `401`.** La clé manque ou est fausse. Redémarrez l'unité et
  lisez `GET /key` dans les cinq minutes.
* **Les dispensations n'ont pas d'horodatage.** L'horloge n'est pas réglée : NTP
  n'a pas encore répondu, ou il n'y a pas de route jusqu'à lui. L'unité omet
  l'heure plutôt que de l'inventer.
* **Les ordonnances ne sont pas prises.** Vérifiez `serverUrl`, vérifiez que
  `pollEnabled` est actif, et rappelez-vous que les ordonnances déjà traitées
  sont mémorisées : `GET /forgetOrders` avant de rejouer le même scénario.
* **Un test court toujours après l'unité.** Coupez l'interrogation périodique
  avec `pollEnabled=0` pendant les tests et déclenchez les vérifications
  vous-même, puis réactivez-la.
* **La page de configuration ne s'ouvre pas d'elle-même.** Allez à
  [http://192.168.4.1](http://192.168.4.1) en étant connecté à `Spenser-XXXX`.

[Interfaces](interfaces.html) contient la référence derrière tout cela : chaque
route, ce qui demande une clé, et ce que fait chaque réglage.
