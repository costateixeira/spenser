#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <HTTPClient.h>
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


// ---- Per-unit settings, persisted in NVS (namespace "spenser") ----
// Defaults are only used the first time a unit boots, or after /resetSettings.
struct Settings
{
  int servoDark;     // servo channel driving the dark (red) lane
  int servoMilk;     // servo channel driving the milk (blue) lane
  int angleRest;     // angle the arm sits at when idle
  int anglePush;     // angle at maximum push
  int returnDelayMs; // how long to hold the push before the arm comes back
  // --- Order client (see the COW IG: an order is actionable when it carries the
  // "actionable" tag, or when a Task asks for it to be fulfilled) ---
  String serverUrl;   // FHIR base URL of the order server, e.g. http://my-server/fhir
  String orderMode;   // "tag" = poll tagged MedicationRequests, "task" = poll Coordination Tasks
  String orderQuery;  // extra search parameters used in "tag" mode
  String taskQuery;   // extra search parameters used in "task" mode
  bool pollEnabled;   // check the server automatically
  int pollSeconds;    // seconds between automatic checks
  bool writeBack;     // report fulfilment back to the server
};

const Settings DEFAULT_SETTINGS = {
    3, 2, 0, 97, 300,
    "",
    "tag",
    "status=active&intent=instance-order&_count=5",
    "status=requested&_include=Task:focus&_count=5",
    false, 30, true};
Settings settings = DEFAULT_SETTINGS;

int inventoryDark = 15;
int inventoryMilk = 15;

void loadSettings()
{
  prefs.begin("spenser", true);
  settings.servoDark = prefs.getInt("servoDark", settings.servoDark);
  settings.servoMilk = prefs.getInt("servoMilk", settings.servoMilk);
  settings.angleRest = prefs.getInt("angleRest", settings.angleRest);
  settings.anglePush = prefs.getInt("anglePush", settings.anglePush);
  settings.returnDelayMs = prefs.getInt("returnMs", settings.returnDelayMs);
  settings.serverUrl = prefs.getString("serverUrl", settings.serverUrl);
  settings.orderMode = prefs.getString("orderMode", settings.orderMode);
  settings.orderQuery = prefs.getString("orderQuery", settings.orderQuery);
  settings.taskQuery = prefs.getString("taskQuery", settings.taskQuery);
  settings.pollEnabled = prefs.getBool("pollEnabled", settings.pollEnabled);
  settings.pollSeconds = prefs.getInt("pollSecs", settings.pollSeconds);
  settings.writeBack = prefs.getBool("writeBack", settings.writeBack);
  prefs.end();

  Serial.printf("Settings: servoDark=%d servoMilk=%d rest=%d push=%d returnMs=%d\n",
                settings.servoDark, settings.servoMilk, settings.angleRest,
                settings.anglePush, settings.returnDelayMs);
}

void saveSettings()
{
  prefs.begin("spenser", false);
  prefs.putInt("servoDark", settings.servoDark);
  prefs.putInt("servoMilk", settings.servoMilk);
  prefs.putInt("angleRest", settings.angleRest);
  prefs.putInt("anglePush", settings.anglePush);
  prefs.putInt("returnMs", settings.returnDelayMs);
  prefs.putString("serverUrl", settings.serverUrl);
  prefs.putString("orderMode", settings.orderMode);
  prefs.putString("orderQuery", settings.orderQuery);
  prefs.putString("taskQuery", settings.taskQuery);
  prefs.putBool("pollEnabled", settings.pollEnabled);
  prefs.putInt("pollSecs", settings.pollSeconds);
  prefs.putBool("writeBack", settings.writeBack);
  prefs.end();
}

String settingsJson()
{
  StaticJsonDocument<1024> doc;
  doc["servoDark"] = settings.servoDark;
  doc["servoMilk"] = settings.servoMilk;
  doc["angleRest"] = settings.angleRest;
  doc["anglePush"] = settings.anglePush;
  doc["returnDelayMs"] = settings.returnDelayMs;
  doc["serverUrl"] = settings.serverUrl;
  doc["orderMode"] = settings.orderMode;
  doc["orderQuery"] = settings.orderQuery;
  doc["taskQuery"] = settings.taskQuery;
  doc["pollEnabled"] = settings.pollEnabled;
  doc["pollSeconds"] = settings.pollSeconds;
  doc["writeBack"] = settings.writeBack;

  String out;
  serializeJson(doc, out);
  return out;
}

// Read an int parameter from either the query string or a posted form body.
bool paramInt(AsyncWebServerRequest *request, const char *name, int &out)
{
  if (request->hasParam(name))
  {
    out = request->getParam(name)->value().toInt();
    return true;
  }
  if (request->hasParam(name, true))
  {
    out = request->getParam(name, true)->value().toInt();
    return true;
  }
  return false;
}

// Read a string parameter from either the query string or a posted form body.
bool paramStr(AsyncWebServerRequest *request, const char *name, String &out)
{
  if (request->hasParam(name))
  {
    out = request->getParam(name)->value();
    return true;
  }
  if (request->hasParam(name, true))
  {
    out = request->getParam(name, true)->value();
    return true;
  }
  return false;
}

bool paramBool(AsyncWebServerRequest *request, const char *name, bool &out)
{
  String raw;
  if (!paramStr(request, name, raw))
    return false;
  raw.toLowerCase();
  out = (raw == "1" || raw == "true" || raw == "on" || raw == "yes");
  return true;
}

// ---- Orders already fulfilled, so a poll never dispenses the same one twice ----
// Kept as "|id1|id2|" in NVS; only the most recent SEEN_MAX ids are remembered.
const int SEEN_MAX = 20;
String seenIds = "|";

void loadSeenIds()
{
  prefs.begin("spenser", true);
  seenIds = prefs.getString("seenIds", "|");
  prefs.end();
}

int seenCount()
{
  int bars = 0;
  for (unsigned int i = 0; i < seenIds.length(); i++)
    if (seenIds[i] == '|')
      bars++;
  return bars > 0 ? bars - 1 : 0;
}

bool alreadyHandled(const String &id)
{
  return id.length() > 0 && seenIds.indexOf("|" + id + "|") >= 0;
}

void markHandled(const String &id)
{
  if (id.isEmpty() || alreadyHandled(id))
    return;

  seenIds += id + "|";
  while (seenCount() > SEEN_MAX)
  {
    int next = seenIds.indexOf('|', 1);
    if (next < 0)
      break;
    seenIds = seenIds.substring(next);
  }

  prefs.begin("spenser", false);
  prefs.putString("seenIds", seenIds);
  prefs.end();
}

void forgetHandled()
{
  seenIds = "|";
  prefs.begin("spenser", false);
  prefs.putString("seenIds", seenIds);
  prefs.end();
}

// One push-and-return cycle on the given servo channel, using the unit's settings.
void dispenseServo(int channel)
{
  AtomicMotion.setServoAngle(channel, settings.anglePush);
  delay(settings.returnDelayMs);
  AtomicMotion.setServoAngle(channel, settings.angleRest);
}

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

// Dispense one item of the given code. Returns false when the code is unknown
// or that lane is empty; the caller decides how to report that.
bool dispenseCode(const String &code)
{
  if (code == "chocolate-dark")
  {
    if (inventoryDark <= 0)
      return false;
    inventoryDark--;
    setLEDColor(128, 0, 0); // red
    dispenseServo(settings.servoDark);
  }
  else if (code == "chocolate-milk")
  {
    if (inventoryMilk <= 0)
      return false;
    inventoryMilk--;
    setLEDColor(0, 0, 200); // blue
    dispenseServo(settings.servoMilk);
  }
  else
  {
    return false;
  }

  setLEDColor(0, 0, 0);
  return true;
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
    if (dispenseCode(medicationCode))
    {
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
    if (dispenseCode(medicationCode))
    {
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

// ==================== Order client ====================
// A FHIR request is an authorization, not an instruction: per the COW IG
// ("Actionable orders") Spenser only acts on an order when either
//   "tag"  - the MedicationRequest carries meta.tag common-tags#actionable, or
//   "task" - a Coordination Task points at it (Task.focus) asking for fulfilment.
// Both are polled by the same code path; the mode is a per-unit setting.

#define ACTIONABLE_SYSTEM "http://terminology.hl7.org/CodeSystem/common-tags"
#define ACTIONABLE_CODE "actionable"
#define MEDS_SYSTEM "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds"

const size_t ORDER_DOC_SIZE = 20480; // keep _count small: the Bundle is parsed in RAM

struct OrderCheck
{
  bool busy;
  bool everRan;
  unsigned long lastCheck; // millis() of the last finished check
  int httpStatus;          // status of the search itself
  int found;               // orders seen for the first time
  int dispensed;           // orders actually dispensed
  char message[128];       // the web task reads this while loop() writes it: keep it a plain buffer
};

OrderCheck orderCheck = {false, false, 0, 0, 0, 0, ""};
volatile bool checkRequested = false; // set by /checkOrders, serviced from loop()
unsigned long lastPollAttempt = 0;

void setOrderMessage(const String &text)
{
  strlcpy(orderCheck.message, text.c_str(), sizeof(orderCheck.message));
  Serial.println("Orders: " + text);
}

void finishCheck()
{
  orderCheck.lastCheck = millis();
  orderCheck.busy = false;
}

String serverBase()
{
  String base = settings.serverUrl;
  while (base.endsWith("/"))
    base.remove(base.length() - 1);
  return base;
}

// R5 carries the code in medication.concept, R4 in medicationCodeableConcept.
String medicationCodeOf(JsonObject request)
{
  String code = request["medication"]["concept"]["coding"][0]["code"] | "";
  if (code.isEmpty())
    code = request["medicationCodeableConcept"]["coding"][0]["code"] | "";
  return code;
}

JsonObject findResource(JsonArray entries, const String &type, const String &id)
{
  for (JsonObject entry : entries)
  {
    JsonObject resource = entry["resource"];
    if (resource.isNull())
      continue;
    if (String(resource["resourceType"] | "") == type && String(resource["id"] | "") == id)
      return resource;
  }
  return JsonObject();
}

// Send a resource; report the HTTP status and, for a create, the id the server assigned.
int sendResource(const char *method, const String &url, const String &body, String *createdId = nullptr)
{
  HTTPClient http;
  if (!http.begin(url))
    return -1;

  const char *headerKeys[] = {"Location", "Content-Location"};
  http.collectHeaders(headerKeys, 2);
  http.addHeader("Content-Type", "application/fhir+json");
  http.addHeader("Accept", "application/fhir+json");
  http.setTimeout(8000);

  int status = http.sendRequest(method, (uint8_t *)body.c_str(), body.length());

  if (createdId)
  {
    String location = http.header("Location");
    if (location.isEmpty())
      location = http.header("Content-Location");

    int history = location.indexOf("/_history"); // .../MedicationDispense/7/_history/1
    if (history > 0)
      location = location.substring(0, history);
    int slash = location.lastIndexOf('/');
    *createdId = slash >= 0 ? location.substring(slash + 1) : "";
  }

  http.end();
  return status;
}

String dispenseBody(JsonObject request, const String &requestId, const String &code)
{
  StaticJsonDocument<768> doc;
  doc["resourceType"] = "MedicationDispense";
  doc["status"] = "completed";

  JsonObject medication = doc.createNestedObject("medication");
  JsonObject coding = medication.createNestedObject("concept").createNestedArray("coding").createNestedObject();
  coding["system"] = MEDS_SYSTEM;
  coding["code"] = code;
  coding["display"] = (code == "chocolate-dark") ? "Dark Chocolate" : "Milk Chocolate";

  String subject = request["subject"]["reference"] | "";
  if (subject.length())
    doc.createNestedObject("subject")["reference"] = subject;

  if (requestId.length())
    doc.createNestedArray("authorizingPrescription").createNestedObject()["reference"] =
        "MedicationRequest/" + requestId;

  String out;
  serializeJson(doc, out);
  return out;
}

// Tell the server what happened. The dispense event is always reported; what is
// completed afterwards depends on the mode. In "task" mode the COW IG leaves the
// request to the placer, so Spenser completes the Task and hands the dispense back
// in Task.output. In "tag" mode there is no Task, so the request itself is completed.
// Returns an empty String when the server accepted everything.
String reportFulfilment(const String &base, JsonObject request, const String &requestId,
                        const String &code, JsonObject task)
{
  String dispenseId;
  int dispenseStatus = sendResource("POST", base + "/MedicationDispense",
                                    dispenseBody(request, requestId, code), &dispenseId);
  Serial.printf("POST MedicationDispense -> %d\n", dispenseStatus);

  int followUp = 0;
  if (!task.isNull())
  {
    task["status"] = "completed";
    if (dispenseId.length())
    {
      JsonObject output = task.createNestedArray("output").createNestedObject();
      output.createNestedObject("type")["text"] = "MedicationDispense";
      output.createNestedObject("valueReference")["reference"] = "MedicationDispense/" + dispenseId;
    }

    String taskId = task["id"] | "";
    String body;
    serializeJson(task, body);
    followUp = sendResource("PUT", base + "/Task/" + taskId, body);
    Serial.printf("PUT Task/%s -> %d\n", taskId.c_str(), followUp);
  }
  else
  {
    request["status"] = "completed";
    String body;
    serializeJson(request, body);
    followUp = sendResource("PUT", base + "/MedicationRequest/" + requestId, body);
    Serial.printf("PUT MedicationRequest/%s -> %d\n", requestId.c_str(), followUp);
  }

  bool dispenseOk = dispenseStatus >= 200 && dispenseStatus < 300;
  bool followUpOk = followUp >= 200 && followUp < 300;
  if (dispenseOk && followUpOk)
    return "";

  return "Dispensed, but the server refused the write-back (dispense " +
         String(dispenseStatus) + ", update " + String(followUp) + ")";
}

void checkOrders()
{
  orderCheck.busy = true;
  orderCheck.everRan = true;
  orderCheck.found = 0;
  orderCheck.dispensed = 0;
  orderCheck.httpStatus = 0;

  bool taskMode = (settings.orderMode == "task");
  String base = serverBase();

  if (base.isEmpty())
  {
    setOrderMessage("No server URL configured");
    finishCheck();
    return;
  }

  if (WiFi.status() != WL_CONNECTED)
  {
    setOrderMessage("Not connected to Wi-Fi");
    finishCheck();
    return;
  }

  String url = base + (taskMode ? "/Task" : "/MedicationRequest");
  String query = taskMode ? settings.taskQuery : settings.orderQuery;
  if (!taskMode)
  {
    // Only orders the placer marked as actionable
    String tag = "_tag=" ACTIONABLE_SYSTEM "%7C" ACTIONABLE_CODE;
    query = query.length() ? tag + "&" + query : tag;
  }
  if (query.length())
    url += "?" + query;

  Serial.println("Checking for orders: " + url);

  HTTPClient http;
  if (!http.begin(url))
  {
    setOrderMessage("Could not open " + url);
    finishCheck();
    return;
  }

  http.addHeader("Accept", "application/fhir+json");
  http.setTimeout(8000);
  orderCheck.httpStatus = http.GET();

  if (orderCheck.httpStatus != 200)
  {
    http.end();
    setOrderMessage("Search failed (HTTP " + String(orderCheck.httpStatus) + ")");
    finishCheck();
    return;
  }

  DynamicJsonDocument doc(ORDER_DOC_SIZE);
  DeserializationError error = deserializeJson(doc, http.getStream());
  http.end();

  if (error)
  {
    setOrderMessage(String("Could not read the Bundle: ") + error.c_str());
    finishCheck();
    return;
  }

  JsonArray entries = doc["entry"].as<JsonArray>();
  if (entries.isNull())
  {
    setOrderMessage("No orders waiting");
    finishCheck();
    return;
  }

  String problem;
  for (JsonObject entry : entries)
  {
    JsonObject resource = entry["resource"];
    if (resource.isNull())
      continue;

    String type = resource["resourceType"] | "";
    JsonObject task;
    JsonObject request;
    String orderId;

    if (taskMode)
    {
      if (type != "Task")
        continue; // the _include brought the requests along; they are not orders by themselves

      String focus = resource["focus"]["reference"] | "";
      if (!focus.startsWith("MedicationRequest/"))
        continue;

      task = resource;
      orderId = "Task/" + String(resource["id"] | "");
      request = findResource(entries, "MedicationRequest", focus.substring(focus.indexOf('/') + 1));

      if (request.isNull())
      {
        problem = orderId + " points at " + focus + ", which the search did not return";
        Serial.println(problem);
        continue;
      }
    }
    else
    {
      if (type != "MedicationRequest")
        continue;

      request = resource;
      orderId = "MedicationRequest/" + String(resource["id"] | "");
    }

    if (alreadyHandled(orderId))
      continue;

    orderCheck.found++;
    String code = medicationCodeOf(request);

    if (!dispenseCode(code))
    {
      problem = "Cannot dispense " + (code.isEmpty() ? String("an order with no code") : code) +
                " for " + orderId;
      Serial.println(problem);
      continue; // out of stock, or not one of ours: leave it for a later check
    }

    orderCheck.dispensed++;
    markHandled(orderId);

    if (settings.writeBack)
    {
      String writeProblem = reportFulfilment(base, request, String(request["id"] | ""), code, task);
      if (writeProblem.length())
        problem = writeProblem;
    }
  }

  if (problem.length())
    setOrderMessage(problem);
  else if (orderCheck.found == 0)
    setOrderMessage("No new orders");
  else
    setOrderMessage("Dispensed " + String(orderCheck.dispensed) + " of " + String(orderCheck.found));

  finishCheck();
}

String orderStatusJson()
{
  StaticJsonDocument<768> doc;
  doc["mode"] = settings.orderMode;
  doc["serverUrl"] = settings.serverUrl;
  doc["busy"] = orderCheck.busy || checkRequested;
  doc["everRan"] = orderCheck.everRan;
  doc["secondsAgo"] = orderCheck.everRan ? (int)((millis() - orderCheck.lastCheck) / 1000) : -1;
  doc["httpStatus"] = orderCheck.httpStatus;
  doc["found"] = orderCheck.found;
  doc["dispensed"] = orderCheck.dispensed;
  doc["message"] = orderCheck.message;
  doc["handled"] = seenCount();

  String out;
  serializeJson(doc, out);
  return out;
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

  loadSettings();
  loadSeenIds();

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

    AtomicMotion.setServoAngle(settings.servoDark, settings.angleRest);
    AtomicMotion.setServoAngle(settings.servoMilk, settings.angleRest);

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
    dispenseServo(settings.servoDark);
    request->send(200, "text/plain", "Servo 1 flashed"); });

  // Define a route to handle flashing of Servo 2 (go to 180 degrees and back)
  server.on("/flashServo2", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    Serial.println("Flashing Servo 2");
    dispenseServo(settings.servoMilk);
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

  // Current per-unit settings (as stored in NVS)
  server.on("/settings", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(200, "application/json", settingsJson()); });

  // Update one or more settings and persist them on this unit.
  // e.g. /setSettings?servoDark=3&servoMilk=2&angleRest=0&anglePush=97&returnDelayMs=300
  server.on("/setSettings", HTTP_GET | HTTP_POST, [](AsyncWebServerRequest *request)
            {
      bool updated = false;
      int value = 0;

      if (paramInt(request, "servoDark", value)) {
        settings.servoDark = constrain(value, 0, 3);
        updated = true;
      }
      if (paramInt(request, "servoMilk", value)) {
        settings.servoMilk = constrain(value, 0, 3);
        updated = true;
      }
      if (paramInt(request, "angleRest", value)) {
        settings.angleRest = constrain(value, 0, 360);
        updated = true;
      }
      if (paramInt(request, "anglePush", value)) {
        settings.anglePush = constrain(value, 0, 360);
        updated = true;
      }
      if (paramInt(request, "returnDelayMs", value)) {
        settings.returnDelayMs = constrain(value, 0, 5000);
        updated = true;
      }

      String text;
      bool flag = false;

      if (paramStr(request, "serverUrl", text)) {
        settings.serverUrl = text;
        updated = true;
      }
      if (paramStr(request, "orderMode", text)) {
        settings.orderMode = (text == "task") ? "task" : "tag";
        updated = true;
      }
      if (paramStr(request, "orderQuery", text)) {
        settings.orderQuery = text;
        updated = true;
      }
      if (paramStr(request, "taskQuery", text)) {
        settings.taskQuery = text;
        updated = true;
      }
      if (paramBool(request, "pollEnabled", flag)) {
        settings.pollEnabled = flag;
        updated = true;
      }
      if (paramInt(request, "pollSeconds", value)) {
        settings.pollSeconds = constrain(value, 5, 3600);
        updated = true;
      }
      if (paramBool(request, "writeBack", flag)) {
        settings.writeBack = flag;
        updated = true;
      }

      if (!updated) {
        request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"No known setting in request\"}");
        return;
      }

      saveSettings();
      Serial.println("Settings saved: " + settingsJson());
      request->send(200, "application/json", settingsJson()); });

  // Wipe the stored settings and fall back to the compiled-in defaults
  server.on("/resetSettings", HTTP_GET, [](AsyncWebServerRequest *request)
            {
      prefs.begin("spenser", false);
      prefs.clear();
      prefs.end();
      settings = DEFAULT_SETTINGS;
      seenIds = "|";
      request->send(200, "application/json", settingsJson()); });

  // Ask for a check. The HTTP call itself runs from loop(), so the async
  // web server is never blocked while Spenser talks to the order server.
  server.on("/checkOrders", HTTP_GET | HTTP_POST, [](AsyncWebServerRequest *request)
            {
      checkRequested = true;
      request->send(202, "application/json", "{\"status\":\"scheduled\"}"); });

  // What the last check did
  server.on("/orders", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(200, "application/json", orderStatusJson()); });

  // Forget which orders were already fulfilled, so they can be dispensed again
  server.on("/forgetOrders", HTTP_GET, [](AsyncWebServerRequest *request)
            {
      forgetHandled();
      request->send(200, "application/json", orderStatusJson()); });

  server.on("/metadata", HTTP_GET, [](AsyncWebServerRequest *request)
            {
        DynamicJsonDocument doc(8192);
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
      
        // ---- client: what Spenser asks of an order server ----
        JsonObject rest1 = rest.createNestedObject();
        rest1["mode"] = "client";
        rest1["documentation"] = "Spenser polls a server for orders that have been made actionable, either by the 'actionable' tag on the MedicationRequest or by a Task asking for it to be fulfilled";

        JsonArray clientResources = rest1.createNestedArray("resource");

        // MedicationRequest: the order to dispense
        JsonObject cres1 = clientResources.createNestedObject();
        cres1["type"] = "MedicationRequest";
        cres1["documentation"] = "Searched for orders tagged as actionable. Set to 'completed' after dispensing, when no Task is coordinating the work";
        JsonArray cres1_interaction = cres1.createNestedArray("interaction");
        cres1_interaction.createNestedObject()["code"] = "search-type";
        cres1_interaction.createNestedObject()["code"] = "update";
        JsonArray cres1_params = cres1.createNestedArray("searchParam");
        JsonObject cres1_tag = cres1_params.createNestedObject();
        cres1_tag["name"] = "_tag";
        cres1_tag["type"] = "token";
        cres1_tag["documentation"] = "Selects orders tagged " ACTIONABLE_SYSTEM "#" ACTIONABLE_CODE;
        JsonObject cres1_status = cres1_params.createNestedObject();
        cres1_status["name"] = "status";
        cres1_status["type"] = "token";
        JsonObject cres1_intent = cres1_params.createNestedObject();
        cres1_intent["name"] = "intent";
        cres1_intent["type"] = "token";

        // Task: the Coordination Task asking for fulfilment
        JsonObject cres2 = clientResources.createNestedObject();
        cres2["type"] = "Task";
        cres2["documentation"] = "Coordination Task pointing at the order in Task.focus. Set to 'completed' with the dispense in Task.output; the status of the request itself is left to the placer";
        JsonArray cres2_interaction = cres2.createNestedArray("interaction");
        cres2_interaction.createNestedObject()["code"] = "search-type";
        cres2_interaction.createNestedObject()["code"] = "update";
        JsonObject cres2_status = cres2.createNestedArray("searchParam").createNestedObject();
        cres2_status["name"] = "status";
        cres2_status["type"] = "token";
        cres2["searchInclude"][0] = "Task:focus";

        // MedicationDispense: what Spenser reports back
        JsonObject cres3 = clientResources.createNestedObject();
        cres3["type"] = "MedicationDispense";
        cres3["documentation"] = "Created on the server once an order has been dispensed, referring to the order in authorizingPrescription";
        cres3.createNestedArray("interaction").createNestedObject()["code"] = "create";

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
        dispenseServo(settings.servoDark);
        rgb.setPixelColor(0, rgb.Color(0, 0, 0)); // LED off
        rgb.show();
      }
      else
      {
        Serial.println("Out of dark chocolate!");
      }
    }
  }

  // Order polling. The blocking HTTP work happens here in loop(), never inside
  // an async web handler, which only raises the checkRequested flag.
  unsigned long nowMs = millis();
  bool pollDue = settings.pollEnabled && settings.pollSeconds > 0 &&
                 (nowMs - lastPollAttempt >= (unsigned long)settings.pollSeconds * 1000UL);

  if (checkRequested || pollDue)
  {
    checkRequested = false;
    lastPollAttempt = nowMs;
    checkOrders();
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
