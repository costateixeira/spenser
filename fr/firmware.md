# Micrologiciel - Spenser - a developer's companion v1.0.0

## Micrologiciel

 
Cette page comprend des traductions de la langue source originale dans laquelle le guide a été rédigé. Des informations sur ces traductions et des instructions sur la manière de fournir un retour d'information sur les traductions sont disponibles [ici](translationinfo.md). 

Le [micrologiciel](https://github.com/costateixeira/spenser/tree/master/firmware) s'exécute sur un **distributeur à base d'ESP32-S3** utilisant le [M5Stack AtomS3 Lite](https://shop.m5stack.com/products/atoms3-lite) et la [M5Stack Atomic Motion Base](https://shop.m5stack.com/products/atomic-motion), conçu pour dispenser du chocolat à la réception de `MedicationRequest` FHIR par HTTP.

Il prend en charge :

* Un portail local de configuration Wi-Fi (par portail captif ou par bouton)
* Des points de terminaison RESTful pour l'interaction FHIR 
* 📦 `InventoryReport` FHIR pour rapporter (GET) et ajuster (POST) le stock
* 🏥 Acceptation de ressources `MedicationRequest` par HTTP POST, avec réponse par `MedicationDispense`
 
* Des services RESTful pour le débogage et la gestion du stock

### Utilisation

1. Installez PlatformIO - Remarque : VSCode fonctionne, VSCodium non
1. Branchez sur un port USB. Sous Windows, utilisez les pilotes Microsoft -**N'UTILISEZ PAS d'autres pilotes comme CH340, etc.**
1. Depuis le dossier`firmware`, lancez PlatformIo pour compiler, téléverser et surveiller
1. **Merci d'aider à améliorer le code - les PR sont plus que bienvenues.**

-------

### 🌐 Points de terminaison FHIR

Ces points de terminaison sont conformes à [FHIR R5](https://hl7.org/fhir/R5) :

#### GET /metadata

* Renvoie un `CapabilityStatement` FHIR
* Déclare la prise en charge des ressources FHIR

#### POST /MedicationRequest

* Accepte une ressource FHIR `MedicationRequest` (JSON)
* Dispense du chocolat noir ou au lait selon le code du médicament
* Répond avec une ressource `MedicationDispense`
* En cas de rupture de stock, répond avec une `MedicationDispense` refusée

#### POST /InventoryReport

* Accepte une ressource FHIR `InventoryReport`
* Prend en charge : 
* `countType: snapshot` — remplace le stock
* `countType: difference` — ajuste le stock par incréments
 
* Valide les contraintes de stock (par exemple, pas de valeurs négatives)
* Répond avec le stock mis à jour ou une erreur

#### GET /InventoryReport

* Renvoie un `InventoryReport` de type instantané représentant le stock actuel
* Inclut les emplacements et l'état des articles

-------

### ⚙️ Points de terminaison de configuration et de débogage

Ce sont des points de terminaison utilitaires pour le diagnostic, la mise en place et les tests interactifs.

#### Configuration Wi-Fi

| | |
| :--- | :--- |
| `GET /wifi-settings` | Marque l'appareil pour qu'il passe en mode de configuration Wi-Fi au redémarrage |
| `GET /wifi-reboot-config` | Redémarre immédiatement en mode de configuration |
| `GET /wifi-reset` | Efface les identifiants Wi-Fi enregistrés |
| `GET /startConfig` | Déclenche le mode de configuration Wi-Fi et redémarre |
| `GET /wifi` | Redirige vers le portail de configuration si non connecté |

#### Interface utilisateur et informations

| | |
| :--- | :--- |
| `GET /` | Sert l'interface depuis SPIFFS ou redirige en mode AP |
| `GET /ui.html` | Sert l'interface statique (`index.html`) |
| `GET /success` | Écran de confirmation après la configuration Wi-Fi |
| `GET /ip-info` | Affiche l'IP et y redirige automatiquement |

#### Débogage et contrôle manuel

| | |
| :--- | :--- |
| `GET /setColor` | Change la couleur de la LED RGB via les paramètres de requête |
| `GET /setServos` | Définit les angles des servos via les paramètres de requête |
| `GET /reset` | Remet la LED et les deux servos à 0 |
| `GET /flashServo1` | Amène brièvement le servo 1 à`dispenseAngle` |
| `GET /flashServo2` | Amène brièvement le servo 2 à`dispenseAngle` |
| `GET /inventory` | Affiche les niveaux de stock actuels en JSON |
| `GET /resetInventory?dark=10&milk=15` | Définit manuellement les quantités en stock |
| `GET /battery` | Indique la tension et le pourcentage de la batterie |

#### Compatibilité avec les portails captifs

Ces points de terminaison redirigent vers `/success` pour gérer les portails captifs propres à chaque plateforme :

* `/generate_204`
* `/hotspot-detect.html`
* `/fwlink`
* `/connecttest.txt`
* `/ncsi.txt`
* `/i`

-------

### 🚀 Wi-Fi et démarrage

Sans identifiants enregistrés, le micrologiciel sert son propre point d'accès ouvert, nommé `Spenser-` suivi des deux derniers octets de son adresse MAC, à l'adresse `192.168.4.1`. En rejoignant ce réseau, la page de configuration s'ouvre d'elle-même ; on y indique à l'unité le réseau à rejoindre, et ces identifiants sont conservés d'un démarrage à l'autre.
 Une fois sur un réseau, elle est joignable à [http://spenser.local](http://spenser.local), qu'elle annonce en mDNS sous le nom `spenser`.
 Voir [Configurer une unité](setup.md).

-------

### 🔋 Comportement du matériel

* **Broche du bouton :** GPIO 41 
* Maintien de 3 secondes au démarrage : passage en mode de configuration Wi-Fi
* Appui court en fonctionnement : dispense un chocolat noir - **alias PANIC ! / Hit Me !!**
 
* **Broche de la LED RGB :** GPIO 35 (WS2812)
* **Servos :** 
* Servo 0 : chocolat noir
* Servo 1 : chocolat au lait
* `dispenseAngle` par défaut : 97°
 

-------

### 📦 Stockage

* **SPIFFS** sert à fournir `index.html` et les ressources de l'interface.
* **Preferences** sert à conserver l'indicateur `forceConfig` pour la configuration Wi-Fi.

-------

### 🔋 Surveillance de la batterie

(En cours de développement / vos résultats peuvent varier)

* Lit la tension sur le capteur INA226 de l'Atomic Motion Base.
* Estime le pourcentage de batterie par un ajustement polynomial.
* Interrogez l'état de la batterie via [`GET /battery`](#debugging--manual-control)

-------

### 🧪 Tests manuels

Utilisez ces points de terminaison pour tester le fonctionnement :

* `GET /flashServo1` — Dispense manuellement du chocolat noir
* `GET /flashServo2` — Dispense manuellement du chocolat au lait
* `GET /setColor?red=0&green=255&blue=0` — Met la LED au vert
* `GET /resetInventory?dark=20&milk=20` — Réinitialise le stock

-------

### ✅ Exemple de POST de MedicationRequest

```
{
  "resourceType": "MedicationRequest",
  "id": "req-123",
  "status": "active",
  "intent": "instance-order",
  "medicationCodeableConcept": {
    "coding": [
      {
        "code": "chocolate-dark",
        "display": "Dark Chocolate"
      }
    ]
  },
  "dosageInstruction": [
    { "text": "Dispense one dark chocolate" }
  ],
  "subject": { "reference": "Patient/example" }
}

```

