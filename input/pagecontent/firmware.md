The [firmware](https://github.com/costateixeira/spenser/tree/master/firmware) runs on an **ESP32-S3-based dispenser** using the [M5Stack AtomS3 Lite](https://shop.m5stack.com/products/atoms3-lite) and [M5Stack Atomic Motion Base](https://shop.m5stack.com/products/atomic-motion), designed to dispense chocolate upon receiving FHIR `MedicationRequest`s over HTTP.

It supports:
- A local Wi-Fi configuration portal (via captive portal or button)
- RESTful endpoints for FHIR interaction
  - 📦 FHIR `InventoryReport` for reporting (GET) and adjusting (POST) inventory
  - 🏥 Accept `MedicationRequest` resources via HTTP POST and reply with `MedicationDispense`
- RESTful services for debugging and inventory management

### Usage
1. Install PlatformIO - Note: VSCode works, VSCodium doesn't
2. Connect to a USB port. On Windows, use Microsoft drivers - **DO NOT use other drivers like CH340 etc.**
3. From the `firmware` folder, run PlatformIo to compile, upload and monitor
4. **Please help improve the code - PRs are more than welcome.**


---

### 🌐 FHIR endpoints

These endpoints conform to [FHIR R5](https://hl7.org/fhir/R5):

#### `GET /metadata`
- Returns a FHIR `CapabilityStatement`
- Declares support for the FHIR resources

#### `POST /MedicationRequest`
- Accepts a FHIR `MedicationRequest` resource (JSON)
- Dispenses either dark or milk chocolate depending on the medication code
- Responds with a `MedicationDispense` resource
- If out of stock, responds with a declined `MedicationDispense`

#### `POST /InventoryReport`
- Accepts a FHIR `InventoryReport` resource
- Supports:
  - `countType: snapshot` — replace inventory
  - `countType: difference` — adjust inventory incrementally
- Validates inventory constraints (e.g. no negative values)
- Responds with the updated inventory or an error

#### `GET /InventoryReport`
- Returns a snapshot-style `InventoryReport` representing current stock
- Includes bin locations and item status

---

### ⚙️ Configuration & Debug Endpoints

These are utility endpoints for diagnostics, setup, and interactive testing.

#### Wi-Fi Configuration

| Endpoint                      | Description                                       |
|------------------------------|---------------------------------------------------|
| `GET /wifi-settings`         | Mark device to enter Wi-Fi config mode on reboot |
| `GET /wifi-reboot-config`    | Immediately reboot into config mode              |
| `GET /wifi-reset`            | Clear stored Wi-Fi credentials                   |
| `GET /startConfig`           | Trigger Wi-Fi setup mode and reboot              |
| `GET /wifi`                  | Redirect to config portal if not connected       |

#### UI & Information

| Endpoint            | Description                                      |
|---------------------|--------------------------------------------------|
| `GET /`             | Serve UI from SPIFFS or redirect in AP mode     |
| `GET /ui.html`      | Serve static UI (`index.html`)                  |
| `GET /success`      | Confirmation screen after Wi-Fi setup           |
| `GET /ip-info`      | Show IP and auto-redirect to it                 |

#### Debugging & Manual Control

| Endpoint            | Description                                     |
|---------------------|-------------------------------------------------|
| `GET /setColor`     | Change the RGB LED color via query params       |
| `GET /setServos`    | Set servo angles via query params               |
| `GET /reset`        | Reset LED and both servos to 0                  |
| `GET /flashServo1`  | Flash servo 1 to `dispenseAngle` briefly        |
| `GET /flashServo2`  | Flash servo 2 to `dispenseAngle` briefly        |
| `GET /inventory`    | Show current inventory levels in JSON           |
| `GET /resetInventory?dark=10&milk=15` | Manually set inventory counts     |
| `GET /battery`      | Report battery voltage and percentage           |

#### Captive Portal Compatibility

These endpoints redirect to `/success` to handle platform-specific captive portals:

- `/generate_204`
- `/hotspot-detect.html`
- `/fwlink`
- `/connecttest.txt`
- `/ncsi.txt`
- `/i`



---

### 🚀 Wifi and boot
When started, the firmware tries to connect to the Wi-Fi network defined in `WiFiCredentials.h`. It also creates an AP with an SSID `spenser`, and an IP `192.168.4.1`.  
So, to get started, simply connect to the `spenser` Wi-Fi network and go to [http://192.168.4.1](http://192.168.4.1).


---

### 🔋 Hardware Behavior

- **Button Pin:** GPIO 41
  - Hold 3 seconds during boot: enter Wi-Fi config mode
  - Short press during runtime: dispense one dark chocolate - **aka PANIC ! / Hit Me !!**
- **RGB LED Pin:** GPIO 35 (WS2812)
- **Servos:**
  - Servo 0: dark chocolate
  - Servo 1: milk chocolate
  - Default `dispenseAngle`: 97°

---





### 📦 Storage

- **SPIFFS** is used to serve `index.html` and UI assets.
- **Preferences** are used to persist the `forceConfig` flag for Wi-Fi setup.

---

### 🔋 Battery Monitoring

(WIP / YMMV) 
- Reads voltage from the INA226 sensor on the Atomic Motion Base.
- Estimates battery % using a polynomial fit.
- Query battery state via [`GET /battery`](#debugging--manual-control)

---

### 🧪 Manual Testing

Use these endpoints to test functionality:

- `GET /flashServo1` — Dispense dark chocolate manually
- `GET /flashServo2` — Dispense milk chocolate manually
- `GET /setColor?red=0&green=255&blue=0` — Set LED to green
- `GET /resetInventory?dark=20&milk=20` — Reset inventory

---

### ✅ Example `MedicationRequest` POST

```json
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

