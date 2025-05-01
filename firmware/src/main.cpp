#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "M5AtomS3.h"
#include "M5AtomicMotion.h"
#include <Adafruit_NeoPixel.h>
#include <FS.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include <ESPAsyncWiFiManager.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <math.h>
#include "WiFiCredentials.h"

DNSServer dns;
AsyncWebServer server(80);

Preferences prefs;

const int ledPin = 35;
Adafruit_NeoPixel rgb(1, ledPin, NEO_GRB + NEO_KHZ800);
M5AtomicMotion AtomicMotion;


const int buttonPin = 41;
unsigned long lastPressTime = 0;
unsigned long debounceDelay = 200;

unsigned long lastIpReportTime = 0;
unsigned long ipReportInterval = 2000;


int dispenseAngle =  97;

int inventoryDark = 15;
int inventoryMilk = 15;

String createMedicationDispense(const String &id, const String &code, const String &patientRef)
{
  StaticJsonDocument<512> doc;
  doc["resourceType"] = "MedicationDispense";
  doc["id"] = id + "-dispense";
  doc["status"] = "completed";
  JsonObject med = doc.createNestedObject("medicationCodeableConcept");
  JsonObject coding = med.createNestedArray("coding").createNestedObject();
  coding["code"] = code;
  coding["display"] = (code == "chocolate-dark") ? "Dark Chocolate" : "Milk Chocolate";
  doc["subject"]["reference"] = patientRef;

  String output;
  serializeJson(doc, output);
  return output;
}


void setLEDColor(uint8_t r, uint8_t g, uint8_t b)
{
  rgb.setPixelColor(0, rgb.Color(r, g, b));
  rgb.show();
}

void handleMedicationRequest(String body, AsyncWebServerRequest *request)
{
  StaticJsonDocument<2048> doc;
  DeserializationError error = deserializeJson(doc, body);
  Serial.println("Handling MedicationRequest");

  if (error)
  {
    Serial.println("Failed to deserialize JSON");
    request->send(400, "application/json", "{\"status\":\"error\", \"message\":\"Invalid JSON\"}");
    return;
  }

  if (strcmp(doc["resourceType"], "MedicationRequest") != 0)
  {
    Serial.println("Invalid resource type. Expected 'MedicationRequest'");
    request->send(400, "application/json", "{\"status\":\"error\", \"message\":\"Invalid resource type. Expected 'MedicationRequest'\"}");
    return;
  }

  String id = doc["id"] | "";
  String status = doc["status"] | "";
  String intent = doc["intent"] | "";
  String medicationCode = doc["medicationCodeableConcept"]["coding"][0]["code"] | "";
  String medicationDisplay = doc["medicationCodeableConcept"]["coding"][0]["display"] | "";
  String dosageText = doc["dosageInstruction"][0]["text"] | "";
  String patientReference = doc["subject"]["reference"] | "";

  if (id.isEmpty() || status != "active" || intent != "instance-order" || patientReference.isEmpty())
  {
    request->send(400, "application/json", "{\"status\":\"error\", \"message\":\"Missing or invalid fields\"}");
    return;
  }

  if (medicationCode == "chocolate-dark")
  {
    if (inventoryDark > 0)
    {
      inventoryDark--;
      rgb.setPixelColor(0, rgb.Color(128, 0, 0)); // red
      rgb.show();
      AtomicMotion.setServoAngle(3, dispenseAngle);
      delay(300);
      AtomicMotion.setServoAngle(3, 0);
      String response = createMedicationDispense(id, medicationCode, patientReference);
      request->send(200, "application/json", response);
    }
    else
    {

      StaticJsonDocument<512> errorDoc;
      errorDoc["resourceType"] = "MedicationDispense";
      errorDoc["id"] = id + "-declined";
      errorDoc["status"] = "declined";

      JsonObject reason = errorDoc.createNestedObject("statusReason");
      JsonObject coding = reason.createNestedArray("coding").createNestedObject();
      coding["system"] = "http://hl7.org/fhir/CodeSystem/medicationdispense-status-reason";
      coding["code"] = "outofstock";
      coding["display"] = "Out of Stock";

      errorDoc["medicationCodeableConcept"]["coding"][0]["code"] = medicationCode;
      errorDoc["medicationCodeableConcept"]["coding"][0]["display"] = medicationDisplay;
      errorDoc["subject"]["reference"] = patientReference;

      String declinedResponse;
      serializeJson(errorDoc, declinedResponse);
      request->send(201, "application/fhir+json", declinedResponse);

      //      request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"Out of dark chocolate stock\"}");
    }
  }
  else if (medicationCode == "chocolate-milk")
  {
    if (inventoryMilk > 0)
    {
      inventoryMilk--;
      rgb.setPixelColor(0, rgb.Color(0, 0, 200)); // blue
      rgb.show();
      AtomicMotion.setServoAngle(2, dispenseAngle);
      delay(300);
      AtomicMotion.setServoAngle(2, 0);
      String response = createMedicationDispense(id, medicationCode, patientReference);
      request->send(200, "application/json", response);
    }
    else
    {
      StaticJsonDocument<512> errorDoc;
      errorDoc["resourceType"] = "MedicationDispense";
      errorDoc["id"] = id + "-declined";
      errorDoc["status"] = "declined";

      JsonObject reason = errorDoc.createNestedObject("statusReason");
      JsonObject coding = reason.createNestedArray("coding").createNestedObject();
      coding["system"] = "http://hl7.org/fhir/CodeSystem/medicationdispense-status-reason";
      coding["code"] = "outofstock";
      coding["display"] = "Out of Stock";

      errorDoc["medicationCodeableConcept"]["coding"][0]["code"] = medicationCode;
      errorDoc["medicationCodeableConcept"]["coding"][0]["display"] = medicationDisplay;
      errorDoc["subject"]["reference"] = patientReference;

      String declinedResponse;
      serializeJson(errorDoc, declinedResponse);
      request->send(201, "application/fhir+json", declinedResponse);

      //      request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"Out of milk chocolate stock\"}");
    }
  }
  else
  {
    request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"Invalid chocolate type\"}");
  }
  rgb.setPixelColor(0, rgb.Color(0, 0, 0));
  rgb.show();
}

bool isAPMode()
{
  return WiFi.getMode() == WIFI_AP || WiFi.status() != WL_CONNECTED;
}

void setup()
{

  Serial.begin(115200);
  delay(500);
  Serial.println("Setup starting");

  pinMode(buttonPin, INPUT_PULLUP);
  bool resetWiFi = false;

  rgb.begin();
  rgb.setBrightness(50);
  rgb.show();

  setLEDColor(255, 255, 0);

  unsigned long startCheck = millis();
  while (millis() - startCheck < 3000)
  {
    if (digitalRead(buttonPin) == LOW)
    {
      setLEDColor(255, 255, 0);
      delay(300);
      setLEDColor(0, 0, 0);
      delay(300);
    }
    else
    {
      break;
    }
  }

  if (digitalRead(buttonPin) == LOW)
  {
    Serial.println("Button held for 3s — resetting WiFi settings");
    resetWiFi = true;
  }

  // Initialize SPIFFS
  if (!SPIFFS.begin(true))
  {
    Serial.println("SPIFFS initialization failed!");
    return;
  }

  WiFi.mode(WIFI_STA);

  server.on("/wifi-settings", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    prefs.begin("config", false);
    prefs.putBool("forceConfig", true);
    prefs.end();
  
    req->send(200, "text/html", "<p>Rebooting into Wi-Fi config mode...</p>");
    delay(1000);
    ESP.restart(); });

    prefs.begin("config", false);
    bool forceConfig = prefs.getBool("forceConfig", false);
    prefs.end();
    
    AsyncWiFiManager wifiManager(&server, &dns);
    
    bool connected = false;
    if (!forceConfig) {
      Serial.print("Trying to connect to ");
      Serial.println(ssid);
      WiFi.begin(ssid, password);
    
      unsigned long startAttempt = millis();
      while (millis() - startAttempt < 10000)
      {
        if (WiFi.status() == WL_CONNECTED) {
          connected = true;
          break;
        }
        delay(500);
        Serial.print(".");
      }
    
      if (connected) {
        Serial.println("\nConnected using hardcoded credentials.");
      } else {
        Serial.println("\nHardcoded credentials failed. Enabling config mode...");
        forceConfig = true;
        prefs.begin("config", false);
        prefs.putBool("forceConfig", true);
        prefs.end();
        ESP.restart();  // enter config mode next boot
      }
    }
    

    if (forceConfig) {
      Serial.println("Starting Wi-Fi configuration portal...");
      wifiManager.setConfigPortalTimeout(180);
      wifiManager.setBreakAfterConfig(true);
      if (!wifiManager.autoConnect("Spenser")) {
        Serial.println("Config failed. Rebooting...");
        delay(2000);
        ESP.restart();
      }
    
      // Success: clear forceConfig and reboot
      prefs.begin("config", false);
      prefs.remove("forceConfig");
      prefs.end();
    
      Serial.println("WiFi credentials received. Rebooting...");
      delay(1000);
      ESP.restart();
    }
    

  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  WiFi.softAP("Spenser");
  setLEDColor(0, 255, 0); // Green = Connected
  WiFi.setSleep(true);

  server.begin();

  //////////////////////////

  // Your handler FIRST — this must be before WiFiManager starts the portal
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    if (isAPMode()) {
      req->redirect("/ui.html");
    } else {
      if (SPIFFS.exists("/index.html")) {
        req->send(SPIFFS, "/index.html", "text/html");
      } else {
        req->send(200, "text/plain", "index.html not found in SPIFFS");
      }
    } });

  server.on("/ui.html", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    if (SPIFFS.exists("/index.html")) {
      req->send(SPIFFS, "/index.html", "text/html");
    } else {
      req->send(500, "text/plain", "index.html not found");
    } });

  // Launch Wi-Fi settings (captive portal) without disconnecting

  // Forget current Wi-Fi credentials (no immediate disconnect or reboot)
  server.on("/wifi-reset", HTTP_GET, [](AsyncWebServerRequest *req)
            {
  prefs.begin("config", false);
  prefs.putBool("forceConfig", true); // next boot starts config
  prefs.end();
  req->send(200, "text/html", "<p>Wi-Fi credentials cleared. Will enter config mode on reboot.</p>"); });

  // Reboot immediately into Wi-Fi configuration mode
  server.on("/wifi-reboot-config", HTTP_GET, [](AsyncWebServerRequest *req)
            {
  prefs.begin("config", false);
  prefs.putBool("forceConfig", true);
  prefs.end();
  req->send(200, "text/html", "<p>Rebooting into Wi-Fi config mode...</p>");
  delay(1000);
  ESP.restart(); });

  // Add this to trigger WiFi config manually:
  server.on("/startConfig", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    prefs.begin("config", false);
    prefs.putBool("forceConfig", true);
    prefs.end();
  
    // Disconnect and forget current WiFi before reboot
    WiFi.disconnect(true, true);  // <- This clears credentials
    delay(500);
    req->send(200, "text/html", "<p>Rebooting to config mode…</p>");
    delay(1000);
    ESP.restart(); });

  // wifiManager.setCaptivePortalEnable(false);

  server.on("/generate_204", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/"); });
  server.on("/hotspot-detect.html", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/"); });
  server.on("/fwlink", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/"); });
  server.on("/ncsi.txt", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/"); });
  server.on("/connecttest.txt", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/"); });

  
  server.on("/success", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String ip = WiFi.localIP().toString();
    String page = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>";
    page += "</head><body>";
    page += "<h2>Wi-Fi Configured!</h2>";
    page += "<p>ESP is now connected to Wi-Fi.</p>";
    page += "<p><strong>IP Address:</strong> " + ip + "</p>";
    page += "<p>You can now reconnect to your Wi-Fi and visit:</p>";
    page += "<p><a href='http://" + ip + "'>http://" + ip + "</a></p>";
    page += "</body></html>";
    request->send(200, "text/html", page); });

  if (WiFi.status() == WL_CONNECTED)
  {
    setLEDColor(0, 255, 0); // green
    WiFi.setSleep(true);    // Enable modem sleep
    Serial.println("Modem Sleep enabled");
  }
  else
  {
    setLEDColor(0, 0, 255); // still blue
  }

  // Serve a page showing the connected IP address
  server.on("/ip-info", HTTP_GET, [](AsyncWebServerRequest *request)
            {
  String ip = WiFi.localIP().toString();
  String page = "<!DOCTYPE html><html><head><meta http-equiv='refresh' content='5; url=http://" + ip + "'></head><body>";
  page += "<h2>Connected!</h2>";
  page += "<p>Redirecting you to <a href='http://" + ip + "'>" + ip + "</a>...</p>";
  page += "</body></html>";
  request->send(200, "text/html", page); });

  delay(100);

  server.on("/wifi", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (WiFi.status() == WL_CONNECTED) {
      request->redirect("/startConfig");  // trigger reconfig
    } else {
      request->redirect("http://192.168.4.1");  // config portal root
    } });

  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi not connected. Restarting AP for config...");
    WiFi.softAP("Spenser");
    setLEDColor(0, 0, 255); // Blue LED = AP Mode
  }
  else
  {
    Serial.println("WiFi connected. IP: " + WiFi.localIP().toString());
    setLEDColor(0, 255, 0); // Green LED = Connected
    WiFi.setSleep(true);    // Enable modem sleep
    Serial.println("Modem Sleep enabled");
  }

  delay(5000); // Give user time to load the page
  //  ESP.restart(); // reboot after user sees info
  Serial.println("Setup complete. Waiting for user to reconnect to their WiFi.");

  // Redirect to a page that shows IP
  Serial.println("Redirecting user to /ip-info page");

  // Initialize M5 Atom
  auto cfg = M5.config();
  AtomS3.begin(cfg);

  // Setup Atomic Motion Library
  bool atomicOk = AtomicMotion.begin(&Wire, M5_ATOMIC_MOTION_I2C_ADDR, 38, 39, 100000);
  if (atomicOk)
  {
    Serial.println("Atomic Motion initialized");
  }
  else
  {
    Serial.println("Atomic Motion initialization failed");
  }

  Wire.beginTransmission(M5_ATOMIC_MOTION_I2C_ADDR);
  byte error = Wire.endTransmission();
  if (error == 0)
  {
    Serial.println("INA226 connected!");
  }
  else
  {
    Serial.printf("INA226 not found (error %d)\n", error);
  }


  // Print the ESP32's IP address
  Serial.print("ESP32 Web Server's IP address: ");
  Serial.println(WiFi.localIP());


  // Define a route to handle color updates
  server.on("/setColor", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String redValue = request->getParam("red")->value();
    String greenValue = request->getParam("green")->value();
    String blueValue = request->getParam("blue")->value();

    int red = redValue.toInt();
    int green = greenValue.toInt();
    int blue = blueValue.toInt();

    // Update RGB LED with the selected color
    rgb.setPixelColor(0, rgb.Color(red, green, blue));
    rgb.show();

    request->send(200, "text/plain", "Color updated"); });

  // Define a route to handle servo updates (only the one changed)
  server.on("/setServos", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (request->hasParam("servo4")) {
      String servo1Value = request->getParam("servo4")->value();
      int servo1Angle = servo1Value.toInt();
      if (servo1Angle >= 0 && servo1Angle <= 360) {
        AtomicMotion.setServoAngle(3, servo1Angle);  // Move Servo 1
        Serial.println("Servo 4 updated");
      }
    }

    if (request->hasParam("servo3")) {
      String servo2Value = request->getParam("servo3")->value();
      int servo2Angle = servo2Value.toInt();
      if (servo2Angle >= 0 && servo2Angle <= 360) {
        AtomicMotion.setServoAngle(2, servo2Angle);  // Move Servo 2
        Serial.println("Servo 3 updated");
      }
    }

    request->send(200, "text/plain", "Servos updated"); });

  // Define a route to reset all sliders and servos to 0
  server.on("/reset", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    rgb.setPixelColor(0, rgb.Color(0, 0, 0));  // Turn off the LED
    rgb.show();

    AtomicMotion.setServoAngle(3, 0);  // Reset Servo 1 to 0 degrees
    AtomicMotion.setServoAngle(2, 0);  // Reset Servo 2 to 0 degrees

    request->send(200, "text/plain", "Sliders and servos reset to 0"); });

  server.on("/i", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/success"); });

  server.on("/hotspot-detect.html", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/success"); });

  server.on("/generate_204", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->redirect("/success"); });

  // Define a route to handle flashing of Servo 1 (go to 180 degrees and back)
  server.on("/flashServo1", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    Serial.println("Flashing Servo 1");
    AtomicMotion.setServoAngle(3, dispenseAngle);  // Move servo to 180 degrees
    delay(500);       // Wait for 1 second
    AtomicMotion.setServoAngle(3, 0);   // Move servo back to 0 degrees
    request->send(200, "text/plain", "Servo 1 flashed"); });

  // Define a route to handle flashing of Servo 2 (go to 180 degrees and back)
  server.on("/flashServo2", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    Serial.println("Flashing Servo 2");
    AtomicMotion.setServoAngle(2, dispenseAngle);  // Move servo to 180 degrees
    delay(500);       // Wait for 1 second
    AtomicMotion.setServoAngle(2, 0);   // Move servo back to 0 degrees
    request->send(200, "text/plain", "Servo 2 flashed"); });

  server.on("/inventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
      String json = "{\"dark\":" + String(inventoryDark) + ",\"milk\":" + String(inventoryMilk) + "}";
      request->send(200, "application/json", json); });

  server.on("/battery", HTTP_GET, [](AsyncWebServerRequest *request)
            {
        float voltage = AtomicMotion.ina226.readBusVoltage();
        if (voltage < 1.0) {  // too low, likely failed read
          request->send(500, "application/json", "{\"error\":\"Could not read battery voltage\"}");
          return;
        }
      
        float percent = 
          -706.0 * pow(voltage, 5) +
           8800.0 * pow(voltage, 4) -
          44100.0 * pow(voltage, 3) +
         110000.0 * pow(voltage, 2) -
         134000.0 * voltage +
          64300.0;
      
        percent = constrain(round(percent), 0, 100);
      
        String json = "{\"voltage\":" + String(voltage, 2) + ",\"percent\":" + String(percent, 0) + "}";
        request->send(200, "application/json", json); });

  server.on("/setInventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
      bool updated = false;
      if (request->hasParam("dark")) {
        inventoryDark = request->getParam("dark")->value().toInt();
        Serial.printf("Dark chocolate inventory set to %d\n", inventoryDark);
        updated = true;
      }
      if (request->hasParam("milk")) {
        inventoryMilk = request->getParam("milk")->value().toInt();
        Serial.printf("Milk chocolate inventory set to %d\n", inventoryMilk);
        updated = true;
      }
    
      if (updated) {
        request->send(200, "text/plain", "Inventory updated: Dark = " + String(inventoryDark) + ", Milk = " + String(inventoryMilk));
      } else {
        request->send(400, "text/plain", "Missing 'dark' and/or 'milk' parameters");
      } });

  server.on("/metadata", HTTP_GET, [](AsyncWebServerRequest *request)
            {
        StaticJsonDocument<4096> doc;
        doc["resourceType"] = "CapabilityStatement";
        doc["status"] = "active";
        doc["date"] = "2025-04-18";
        doc["publisher"] = "Spenser";
        doc["kind"] = "instance";
        doc["fhirVersion"] = "5.0.0";
        doc["format"][0] = "json";
      
        JsonArray rest = doc.createNestedArray("rest");
        JsonObject rest0 = rest.createNestedObject();
        rest0["mode"] = "server";
      
        JsonArray resources = rest0.createNestedArray("resource");
      
        // MedicationRequest resource
        JsonObject res1 = resources.createNestedObject();
        res1["type"] = "MedicationRequest";
        JsonArray res1_interaction = res1.createNestedArray("interaction");
        JsonObject res1_create = res1_interaction.createNestedObject();
        res1_create["code"] = "create";
        // JsonArray res1_ops = res1.createNestedArray("operation");
        // JsonObject res1_op = res1_ops.createNestedObject();
        // res1_op["name"] = "responds-with-medicationdispense";
      
        // InventoryReport resource
        JsonObject res2 = resources.createNestedObject();
        res2["type"] = "InventoryReport";
        JsonArray res2_interaction = res2.createNestedArray("interaction");
      
        JsonObject res2_read = res2_interaction.createNestedObject();
        res2_read["code"] = "read";
      
        JsonObject res2_create = res2_interaction.createNestedObject();
        res2_create["code"] = "create";
      
        // JsonArray res2_ops = res2.createNestedArray("operation");
      
        // JsonObject op_snapshot = res2_ops.createNestedObject();
        // op_snapshot["name"] = "supports-snapshot-update";
        // op_snapshot["definition"] = "http://example.org/fhir/OperationDefinition/inventory-snapshot";
      
        // JsonObject op_difference = res2_ops.createNestedObject();
        // op_difference["name"] = "supports-difference-update";
        // op_difference["definition"] = "http://example.org/fhir/OperationDefinition/inventory-difference";
      
        String response;
        serializeJsonPretty(doc, response);
        request->send(200, "application/fhir+json", response); });

  // New handler to reset inventory via GET /resetInventory?dark=10&milk=15
  server.on("/resetInventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
  if (request->hasParam("dark")) inventoryDark = request->getParam("dark")->value().toInt();
  if (request->hasParam("milk")) inventoryMilk = request->getParam("milk")->value().toInt();
  request->send(200, "text/plain", "Inventory updated"); });

  server.on("/InventoryReport", HTTP_POST, [](AsyncWebServerRequest *request) {}, nullptr, [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
            {
    if (index == 0) {
      request->_tempObject = new String();
      ((String *)request->_tempObject)->reserve(total);
    }
    ((String *)request->_tempObject)->concat((const char *)data, len);
  
    if (index + len == total) {
      String body = *((String *)request->_tempObject);
      delete (String *)request->_tempObject;
      request->_tempObject = nullptr;
  
      StaticJsonDocument<2048> doc;
      DeserializationError error = deserializeJson(doc, body);
      if (error) {
        StaticJsonDocument<256> out;
        out["resourceType"] = "OperationOutcome";
        JsonObject issue = out.createNestedArray("issue").createNestedObject();
        issue["severity"] = "error";
        issue["code"] = "invalid";
        issue["diagnostics"] = "Invalid JSON";
        String err;
        serializeJson(out, err);
        request->send(400, "application/fhir+json", err);
        return;
      }
  
      if (doc["resourceType"] != "InventoryReport") {
        request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"Expected InventoryReport\"}");
        return;
      }
  
      String countType = doc["countType"] | "snapshot";
      if (!doc.containsKey("inventoryListing")) {
        request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"Missing inventoryListing\"}");
        return;
      }
  
      JsonArray inventory = doc["inventoryListing"];
      bool ok = true;
      String failReason = "";
  
      for (JsonObject entry : inventory) {
        JsonArray items = entry["item"];
        for (JsonObject item : items) {
          String code = item["item"]["coding"][0]["code"] | "";
          int value = item["quantity"]["value"] | 0;
  
          if (countType == "difference") {
            if (code == "chocolate-dark" && inventoryDark + value < 0) {
              ok = false; failReason = "Negative dark chocolate inventory";
            }
            if (code == "chocolate-milk" && inventoryMilk + value < 0) {
              ok = false; failReason = "Negative milk chocolate inventory";
            }
          }
        }
      }
  
      if (!ok) {
        StaticJsonDocument<256> out;
        out["resourceType"] = "OperationOutcome";
        JsonObject issue = out.createNestedArray("issue").createNestedObject();
        issue["severity"] = "error";
        issue["code"] = "business-rule";
        issue["diagnostics"] = failReason;
        String err;
        serializeJson(out, err);
        request->send(400, "application/fhir+json", err);
        return;
      }
  
      for (JsonObject entry : inventory) {
        JsonArray items = entry["item"];
        for (JsonObject item : items) {
          String code = item["item"]["coding"][0]["code"] | "";
          int value = item["quantity"]["value"] | 0;
  
          if (countType == "snapshot") {
            if (code == "chocolate-dark") inventoryDark = value;
            else if (code == "chocolate-milk") inventoryMilk = value;
          } else if (countType == "difference") {
            if (code == "chocolate-dark") inventoryDark += value;
            else if (code == "chocolate-milk") inventoryMilk += value;
          }
        }
      }
  
      inventoryDark = max(inventoryDark, 0);
      inventoryMilk = max(inventoryMilk, 0);
  
      String response;
      serializeJsonPretty(doc, response);
      request->send(201, "application/fhir+json", response);
    } });

  // New handler to serve FHIR R5 InventoryReport
  server.on("/InventoryReport", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    StaticJsonDocument<1024> doc;
  
    doc["resourceType"] = "InventoryReport";
    doc["id"] = "choco-inventory";
    doc["status"] = "current";
    doc["countType"] = "snapshot";
    doc["reportedDate"] = "2025-04-18T12:00:00Z";
  
    JsonArray inventoryListing = doc.createNestedArray("inventoryListing");
  
    // Dark chocolate in Bin 1
    JsonObject dark = inventoryListing.createNestedObject();
    dark["location"]["display"] = "Bin 1";
    JsonObject darkItem = dark.createNestedArray("item").createNestedObject();
    darkItem["item"]["coding"][0]["system"] = "http://example.org/choco-codes";
    darkItem["item"]["coding"][0]["code"] = "chocolate-dark";
    darkItem["item"]["coding"][0]["display"] = "Dark Chocolate";
    darkItem["quantity"]["value"] = inventoryDark;
    darkItem["quantity"]["unit"] = "pieces";
    darkItem["itemStatus"] = "available";
  
    // Milk chocolate in Bin 2
    JsonObject milk = inventoryListing.createNestedObject();
    milk["location"]["display"] = "Bin 2";
    JsonObject milkItem = milk.createNestedArray("item").createNestedObject();
    milkItem["item"]["coding"][0]["system"] = "http://example.org/choco-codes";
    milkItem["item"]["coding"][0]["code"] = "chocolate-milk";
    milkItem["item"]["coding"][0]["display"] = "Milk Chocolate";
    milkItem["quantity"]["value"] = inventoryMilk;
    milkItem["quantity"]["unit"] = "pieces";
    milkItem["itemStatus"] = "available";
  
    String output;
    serializeJsonPretty(doc, output);
    request->send(200, "application/fhir+json", output); });

  AsyncCallbackWebHandler *medicationHandler = new AsyncCallbackWebHandler();
  medicationHandler->setUri("/MedicationRequest");
  medicationHandler->setMethod(HTTP_POST);

  // optional: just mark as handled
  medicationHandler->onRequest([](AsyncWebServerRequest *request)
                               {
                                 // Do nothing here, we handle response in onBody
                               });

  // handle body
  medicationHandler->onBody([](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
                            {
      if (!index) {
        request->_tempObject = new String();
        ((String*)request->_tempObject)->reserve(total);
        Serial.println("Start receiving MedicationRequest body...");
      }
    
      ((String*)request->_tempObject)->concat((const char*)data, len);
    
      if (index + len == total) {
        Serial.println("Full MedicationRequest body received.");
        String body = *((String*)request->_tempObject);
        delete (String*)request->_tempObject;
        request->_tempObject = nullptr;
        handleMedicationRequest(body, request);
      } });

  server.addHandler(medicationHandler);


  // server.on("/MedicationRequest", HTTP_POST, [](AsyncWebServerRequest *request)
  //           {
  //             Serial.println("MedicationRequest received");
  //             // Body will be handled in onRequestBody
  //           });

  server.onRequestBody([](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
                       {
      if (request->url() == "/MedicationRequest" && request->method() == HTTP_POST) {
          if (!index) {
              request->_tempObject = new String();
              ((String *)request->_tempObject)->reserve(total);
          }
          Serial.println("MedicationRequest Body received");

          ((String *)request->_tempObject)->concat((const char *)data, len);
  
          if (index + len == total) {
              String body = *((String *)request->_tempObject);
              delete (String *)request->_tempObject;
              request->_tempObject = nullptr;
  
              // Now send a response from here
              handleMedicationRequest(body, request);  // This will call request->send(...)
          }
      } });

  server.onNotFound([](AsyncWebServerRequest *request)
                    {
        if (WiFi.status() == WL_CONNECTED) {
          String ip = WiFi.localIP().toString();
          String page = "<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=http://" + ip + "'></head><body>";
          page += "<p>Redirecting to <a href='http://" + ip + "'>" + ip + "</a>...</p>";
          page += "</body></html>";
          request->send(200, "text/html", page);
        } else {
          request->send(404, "text/plain", "Page not found");
        } });
}

void loop()
{
  static bool buttonHeld = false;
  static bool buttonPressed = false;
  static unsigned long buttonPressStart = 0;
  const unsigned long longPressDuration = 3000;
  const unsigned long shortPressMinDuration = 50;
  const unsigned long shortPressMaxDuration = 1000;

  bool buttonState = digitalRead(buttonPin) == LOW;

  if (buttonState && !buttonPressed)
  {
    buttonPressed = true;
    buttonPressStart = millis();
  }

  if (!buttonState && buttonPressed)
  {
    unsigned long pressDuration = millis() - buttonPressStart;
    buttonPressed = false;

    if (pressDuration >= longPressDuration)
    {
      Serial.println("Long press detected. Enabling config mode...");

      prefs.begin("config", false);
      prefs.putBool("forceConfig", true);
      prefs.end();

      WiFi.disconnect(true);
      delay(1000);
      ESP.restart();
    }
    else if (pressDuration >= shortPressMinDuration && pressDuration <= shortPressMaxDuration)
    {
      Serial.println("Short press detected — dispensing one dark chocolate.");
      if (inventoryDark > 0)
      {
        inventoryDark--;
        rgb.setPixelColor(0, rgb.Color(128, 0, 0)); // red
        rgb.show();
        AtomicMotion.setServoAngle(3, dispenseAngle);
        delay(300);
        AtomicMotion.setServoAngle(3, 0);
        rgb.setPixelColor(0, rgb.Color(0, 0, 0)); // LED off
        rgb.show();
      }
      else
      {
        Serial.println("Out of dark chocolate!");
      }
    }
  }

  // Optional: report IP periodically
  static unsigned long lastIpReport = 0;
  unsigned long now = millis();
  if (now - lastIpReport >= ipReportInterval )
  {
    lastIpReport = now;
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  }
}
