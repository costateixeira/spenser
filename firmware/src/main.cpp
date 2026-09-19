#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "M5AtomS3.h"
#include "M5AtomicMotion.h"
#include <Adafruit_NeoPixel.h>
#include <FS.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <math.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <esp_wifi.h>

DNSServer dns;
AsyncWebServer server(80);

Preferences prefs;

// An order is only actionable when the placer says so - either with this tag on
// the MedicationRequest, or with a Task asking for it to be fulfilled. See the
// HL7 COW IG, "Actionable orders".
#define ACTIONABLE_SYSTEM "http://terminology.hl7.org/CodeSystem/common-tags"
#define ACTIONABLE_CODE "actionable"
#define MEDS_SYSTEM "http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds"
#define NOT_PERFORMED_SYSTEM "http://hl7.org/fhir/CodeSystem/medicationdispense-status-reason"

const int ledPin = 35;
Adafruit_NeoPixel rgb(1, ledPin, NEO_GRB + NEO_KHZ800);
M5AtomicMotion AtomicMotion;

const int buttonPin = 41;

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

  // --- Order client. The server URL itself lives in orderServerUrl, which the
  // Wi-Fi portal also writes. ---
  String orderMode;   // "tag" = poll tagged MedicationRequests, "task" = poll Tasks
  String orderQuery;  // extra search parameters used in "tag" mode
  String taskQuery;   // extra search parameters used in "task" mode
  bool pollEnabled;   // check the server automatically
  int pollSeconds;    // seconds between automatic checks
  bool writeBack;     // report what happened back to the server
  bool giveUpOnStockEmpty; // an order this unit cannot fill: abandon it, or retry
                           // it after a refill
};

const Settings DEFAULT_SETTINGS = {
    3, 2, 0, 77, 300,
    "tag",
    "status=active&intent=instance-order&_count=5",
    "status=requested&_include=Task:focus&_count=5",
    true, 30, true, false};
Settings settings = DEFAULT_SETTINGS;

int inventoryDark = 15;
int inventoryMilk = 15;

// Network state
enum NetMode { NET_BOOT, NET_STA, NET_AP };
NetMode netMode = NET_BOOT;
String apSsid;                       // "Spenser-XXXX" computed from MAC
const IPAddress apIP(192, 168, 4, 1);
unsigned long apModeStartedAt = 0;
unsigned long lastStaRetryFromAp = 0;
const unsigned long staRetryFromApInterval = 5UL * 60UL * 1000UL; // retry STA every 5min while AP up

// Saved network config (Preferences namespace "wifi")
String wifiSsid;
String wifiPass;
String orderServerUrl = "";

// Retry queue for failed dispense POST-backs
const int RETRY_QUEUE_SIZE = 5;
String retryQueue[RETRY_QUEUE_SIZE];
int retryCount = 0;

// --- Dispense result struct ---

struct DispenseResult {
  bool success;        // true if dispensed or properly declined (not a parse error)
  int httpStatus;      // 200 for dispensed, 201 for declined, 400 for error
  String responseBody; // The JSON response (MedicationDispense or error)
  String contentType;  // "application/json" or "application/fhir+json"
};

// --- Helper functions ---

void setLEDColor(uint8_t r, uint8_t g, uint8_t b)
{
  rgb.setPixelColor(0, rgb.Color(r, g, b));
  rgb.show();
}

// --- Per-unit settings (Preferences namespace "spenser") ---

void loadSettings()
{
  prefs.begin("spenser", true);
  settings.servoDark = prefs.getInt("servoDark", settings.servoDark);
  settings.servoMilk = prefs.getInt("servoMilk", settings.servoMilk);
  settings.angleRest = prefs.getInt("angleRest", settings.angleRest);
  settings.anglePush = prefs.getInt("anglePush", settings.anglePush);
  settings.returnDelayMs = prefs.getInt("returnMs", settings.returnDelayMs);
  settings.orderMode = prefs.getString("orderMode", settings.orderMode);
  settings.orderQuery = prefs.getString("orderQuery", settings.orderQuery);
  settings.taskQuery = prefs.getString("taskQuery", settings.taskQuery);
  settings.pollEnabled = prefs.getBool("pollEnabled", settings.pollEnabled);
  settings.pollSeconds = prefs.getInt("pollSecs", settings.pollSeconds);
  settings.writeBack = prefs.getBool("writeBack", settings.writeBack);
  settings.giveUpOnStockEmpty = prefs.getBool("giveUpEmpty", settings.giveUpOnStockEmpty);
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
  prefs.putString("orderMode", settings.orderMode);
  prefs.putString("orderQuery", settings.orderQuery);
  prefs.putString("taskQuery", settings.taskQuery);
  prefs.putBool("pollEnabled", settings.pollEnabled);
  prefs.putInt("pollSecs", settings.pollSeconds);
  prefs.putBool("writeBack", settings.writeBack);
  prefs.putBool("giveUpEmpty", settings.giveUpOnStockEmpty);
  prefs.end();
}

String settingsJson()
{
  StaticJsonDocument<256> doc;
  doc["servoDark"] = settings.servoDark;
  doc["servoMilk"] = settings.servoMilk;
  doc["angleRest"] = settings.angleRest;
  doc["anglePush"] = settings.anglePush;
  doc["returnDelayMs"] = settings.returnDelayMs;
  doc["serverUrl"] = orderServerUrl;
  doc["orderMode"] = settings.orderMode;
  doc["orderQuery"] = settings.orderQuery;
  doc["taskQuery"] = settings.taskQuery;
  doc["pollEnabled"] = settings.pollEnabled;
  doc["pollSeconds"] = settings.pollSeconds;
  doc["writeBack"] = settings.writeBack;
  doc["giveUpOnStockEmpty"] = settings.giveUpOnStockEmpty;

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

// ---- Orders this unit has already dealt with, as "|id1|id2|" ----
// seenIds is persisted, so a fulfilled order is never dispensed twice.
// reportedIds is RAM only: after a reboot an out-of-stock order may be reported
// once more, which beats posting a declined dispense on every poll.
const int SEEN_MAX = 20;
String seenIds = "|";
String reportedIds = "|";

int listCount(const String &list)
{
  int bars = 0;
  for (unsigned int i = 0; i < list.length(); i++)
    if (list[i] == '|')
      bars++;
  return bars > 0 ? bars - 1 : 0;
}

bool listHas(const String &list, const String &id)
{
  return id.length() > 0 && list.indexOf("|" + id + "|") >= 0;
}

void listAdd(String &list, const String &id)
{
  if (id.isEmpty() || listHas(list, id))
    return;

  list += id + "|";
  while (listCount(list) > SEEN_MAX)
  {
    int next = list.indexOf('|', 1);
    if (next < 0)
      break;
    list = list.substring(next);
  }
}

void loadSeenIds()
{
  prefs.begin("spenser", true);
  seenIds = prefs.getString("seenIds", "|");
  prefs.end();
}

bool alreadyHandled(const String &id)
{
  return listHas(seenIds, id);
}

void markHandled(const String &id)
{
  if (listHas(seenIds, id))
    return;

  listAdd(seenIds, id);
  prefs.begin("spenser", false);
  prefs.putString("seenIds", seenIds);
  prefs.end();
}

bool alreadyReported(const String &id)
{
  return listHas(reportedIds, id);
}

void forgetHandled()
{
  seenIds = "|";
  reportedIds = "|";
  prefs.begin("spenser", false);
  prefs.putString("seenIds", seenIds);
  prefs.end();
}

// Open a connection for either scheme. https:// is accepted without validating
// the certificate: encrypted, but not authenticated.
bool beginHttp(HTTPClient &http, WiFiClientSecure &secure, WiFiClient &plain, const String &url)
{
  if (url.startsWith("https://"))
  {
    secure.setInsecure();
    return http.begin(secure, url);
  }
  return http.begin(plain, url);
}

// One push-and-return cycle on the given servo channel, using the unit's settings.
void dispenseServo(int channel)
{
  AtomicMotion.setServoAngle(channel, settings.anglePush);
  delay(settings.returnDelayMs);
  AtomicMotion.setServoAngle(channel, settings.angleRest);
}

// --- Custom MAC override (Preferences namespace "network", key "customMAC") ---

bool customMacActive = false;

bool parseMacAddress(const String &macStr, uint8_t outMac[6])
{
  String cleaned = "";
  for (size_t i = 0; i < macStr.length(); i++) {
    char c = macStr.charAt(i);
    if (isxdigit(c)) cleaned += (char)toupper(c);
  }
  if (cleaned.length() != 12) return false;
  for (int i = 0; i < 6; i++) {
    String byteStr = cleaned.substring(i * 2, i * 2 + 2);
    outMac[i] = (uint8_t)strtol(byteStr.c_str(), nullptr, 16);
  }
  if (outMac[0] & 0x01) return false; // must be unicast
  return true;
}

String formatMacAddress(const uint8_t mac[6])
{
  char buf[18];
  snprintf(buf, sizeof(buf), "%02X:%02X:%02X:%02X:%02X:%02X",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(buf);
}

// Must be called AFTER WiFi.mode() and BEFORE WiFi.begin()
bool applyCustomMac()
{
  prefs.begin("network", true);
  String storedMac = prefs.getString("customMAC", "");
  prefs.end();

  if (storedMac.length() == 0) {
    customMacActive = false;
    return false;
  }
  uint8_t mac[6];
  if (!parseMacAddress(storedMac, mac)) {
    Serial.println("Invalid custom MAC in NVS, using factory MAC");
    customMacActive = false;
    return false;
  }
  esp_err_t result = esp_wifi_set_mac(WIFI_IF_STA, mac);
  if (result == ESP_OK) {
    customMacActive = true;
    Serial.print("Custom MAC applied: ");
    Serial.println(formatMacAddress(mac));
    return true;
  }
  Serial.printf("Failed to set custom MAC (error %d), using factory MAC\n", result);
  customMacActive = false;
  return false;
}

// --- WiFi config persistence (Preferences namespace "wifi") ---

void loadWifiConfig()
{
  prefs.begin("wifi", true);
  wifiSsid = prefs.getString("ssid", "");
  wifiPass = prefs.getString("pass", "");
  prefs.end();
}

void saveWifiConfig(const String &ssid, const String &pass)
{
  prefs.begin("wifi", false);
  prefs.putString("ssid", ssid);
  prefs.putString("pass", pass);
  prefs.end();
  wifiSsid = ssid;
  wifiPass = pass;
}

void clearWifiConfig()
{
  prefs.begin("wifi", false);
  prefs.clear();
  prefs.end();
  wifiSsid = "";
  wifiPass = "";
}

// Set a flag so next boot enters the portal without wiping creds.
void setForcePortalFlag()
{
  prefs.begin("wifi", false);
  prefs.putBool("force", true);
  prefs.end();
}

bool consumeForcePortalFlag()
{
  prefs.begin("wifi", false);
  bool v = prefs.getBool("force", false);
  if (v) prefs.remove("force");
  prefs.end();
  return v;
}

// --- Captive portal HTML ---

const char PORTAL_HTML[] PROGMEM = R"HTML(<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Spenser Wi-Fi Setup</title>
<style>
body{font-family:system-ui,sans-serif;margin:0;padding:20px;max-width:480px;background:#f4f4f4}
h1{font-size:1.3em;margin:0 0 16px}
label{display:block;margin:12px 0 4px;font-weight:600}
input,select,button{width:100%;padding:10px;font-size:1em;box-sizing:border-box;border:1px solid #ccc;border-radius:6px}
button{background:#2266cc;color:#fff;border:0;margin-top:16px;font-weight:600}
button:active{background:#1a4f9c}
small{color:#666}
.msg{padding:10px;border-radius:6px;margin-top:12px}
.ok{background:#d4f5d4}.err{background:#fdd}
</style></head><body>
<h1>Spenser Wi-Fi Setup</h1>
<form id="f">
<label>Network</label>
<select id="ssid" name="ssid"><option value="">scanning&hellip;</option></select>
<small><a href="#" onclick="rescan();return false">rescan</a> or <a href="#" onclick="manual();return false">enter manually</a></small>
<label>Password</label>
<input id="pass" name="pass" type="password" autocomplete="off">
<label>Order Server URL <small>(optional)</small></label>
<input id="url" name="url" type="url" placeholder="https://example.org/fhir">
<button type="submit">Save & Connect</button>
</form>
<div id="msg"></div>

<hr style="margin:24px 0;border:0;border-top:1px solid #ccc">
<h2 style="font-size:1.05em;margin:0 0 6px">MAC address override</h2>
<small>Optional. Use to clone another device's MAC (e.g. captive-portal bypass). Saved before connecting.</small>
<div style="font-size:0.85em;margin:10px 0 4px"><strong>Current:</strong> <span id="mac-cur">&hellip;</span></div>
<div style="font-size:0.85em;margin-bottom:8px"><strong>Stored:</strong> <span id="mac-stored">None</span></div>
<input id="macIn" placeholder="AA:BB:CC:DD:EE:FF" maxlength="17" style="font-family:monospace">
<div style="display:flex;gap:8px">
  <button type="button" onclick="saveMac()" style="margin-top:8px">Save MAC</button>
  <button type="button" onclick="clearMac()" style="margin-top:8px;background:#999">Clear</button>
</div>
<div id="macMsg"></div>

<script>
async function rescan(){
  const s=document.getElementById('ssid');
  s.innerHTML='<option value="">scanning&hellip;</option>';
  try{
    const r=await fetch('/scan');const j=await r.json();
    s.innerHTML='';
    if(!j.networks||!j.networks.length){s.innerHTML='<option value="">no networks found</option>';return}
    for(const n of j.networks){
      const o=document.createElement('option');o.value=n.ssid;
      o.textContent=n.ssid+' ('+n.rssi+'dBm'+(n.secure?' \u{1F512}':'')+')';
      s.appendChild(o);
    }
  }catch(e){s.innerHTML='<option value="">scan failed</option>'}
}
function manual(){
  const cur=document.getElementById('ssid');
  const inp=document.createElement('input');inp.id='ssid';inp.name='ssid';inp.placeholder='SSID';
  cur.replaceWith(inp);
}
async function loadCfg(){
  try{const r=await fetch('/cfg');const j=await r.json();if(j.url)document.getElementById('url').value=j.url}catch(e){}
}
document.getElementById('f').addEventListener('submit',async e=>{
  e.preventDefault();
  const m=document.getElementById('msg');
  const data=new URLSearchParams();
  data.set('ssid',document.getElementById('ssid').value);
  data.set('pass',document.getElementById('pass').value);
  data.set('url',document.getElementById('url').value);
  m.className='msg';m.textContent='Saving…';
  try{
    const r=await fetch('/save',{method:'POST',body:data});
    const j=await r.json();
    if(j.ok){m.className='msg ok';m.textContent='Saved. Device is rebooting and will join "'+j.ssid+'". You can disconnect now.'}
    else{m.className='msg err';m.textContent='Error: '+(j.error||'unknown')}
  }catch(e){m.className='msg err';m.textContent='Request failed: '+e}
});
async function loadMac(){
  try{
    const r=await fetch('/getMac');const j=await r.json();
    document.getElementById('mac-cur').textContent=j.currentMac||'unknown';
    document.getElementById('mac-stored').textContent=j.storedMac||'None (factory MAC)';
  }catch(e){}
}
async function saveMac(){
  const v=document.getElementById('macIn').value.trim();
  const m=document.getElementById('macMsg');
  if(!v){m.className='msg err';m.textContent='Enter a MAC';return}
  const c=v.replace(/[^0-9A-Fa-f]/g,'');
  if(c.length!==12){m.className='msg err';m.textContent='Need 12 hex chars';return}
  if(parseInt(c.slice(0,2),16)&1){m.className='msg err';m.textContent='First byte must be even (unicast)';return}
  try{
    const r=await fetch('/setMac?mac='+encodeURIComponent(v));const j=await r.json();
    if(r.ok){m.className='msg ok';m.textContent='Saved. Will apply on next connect.';document.getElementById('macIn').value='';loadMac()}
    else{m.className='msg err';m.textContent=j.error||'Save failed'}
  }catch(e){m.className='msg err';m.textContent='Request failed'}
}
async function clearMac(){
  const m=document.getElementById('macMsg');
  try{await fetch('/clearMac');m.className='msg ok';m.textContent='Cleared. Factory MAC on next reboot.';loadMac()}
  catch(e){m.className='msg err';m.textContent='Request failed'}
}
loadCfg();rescan();loadMac();
</script></body></html>)HTML";

// --- WiFi connect / portal ---

// WiFi event handler for debugging connection issues
void onWiFiEvent(WiFiEvent_t event, WiFiEventInfo_t info)
{
  switch (event)
  {
  case ARDUINO_EVENT_WIFI_STA_CONNECTED:
    Serial.printf("[WiFi@%lu] Connected to AP\n", millis());
    break;
  case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
    Serial.printf("[WiFi@%lu] Disconnected, reason: %d\n", millis(), info.wifi_sta_disconnected.reason);
    break;
  case ARDUINO_EVENT_WIFI_STA_GOT_IP:
    Serial.printf("[WiFi@%lu] Got IP: %s\n", millis(), WiFi.localIP().toString().c_str());
    break;
  case ARDUINO_EVENT_WIFI_STA_LOST_IP:
    Serial.printf("[WiFi@%lu] Lost IP\n", millis());
    break;
  default:
    break;
  }
}

bool tryConnectSTA(unsigned long timeoutMs)
{
  if (wifiSsid.isEmpty())
    return false;

  Serial.printf("Connecting to '%s'...\n", wifiSsid.c_str());
  WiFi.mode(WIFI_STA);
  WiFi.onEvent(onWiFiEvent); // register event handler for debugging
  applyCustomMac(); // override STA MAC if configured (after mode, before begin)
  WiFi.setHostname("spenser"); // shows up as "spenser" in the router client list
  WiFi.setSleep(false); // polling device — keep radio responsive
  WiFi.setAutoReconnect(true); // let ESP32 handle reconnections
  WiFi.setScanMethod(WIFI_ALL_CHANNEL_SCAN);    // scan all channels on reconnect
  WiFi.setSortMethod(WIFI_CONNECT_AP_BY_SIGNAL); // pick strongest BSSID on same SSID
  WiFi.begin(wifiSsid.c_str(), wifiPass.c_str());

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < timeoutMs)
  {
    delay(250);
    Serial.print('.');
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED)
  {
    netMode = NET_STA;
    Serial.print("STA connected, IP: ");
    Serial.println(WiFi.localIP());
    if (MDNS.begin("spenser"))
    {
      MDNS.addService("http", "tcp", 80);
      Serial.println("mDNS: http://spenser.local/");
    }
    else
    {
      Serial.println("mDNS start failed");
    }
    return true;
  }

  Serial.println("STA connect failed");
  WiFi.disconnect(false, false);
  return false;
}

void startAPPortal()
{
  Serial.println("Starting AP portal...");
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(apSsid.c_str()); // open network
  delay(100);

  dns.setErrorReplyCode(DNSReplyCode::NoError);
  dns.start(53, "*", apIP);

  netMode = NET_AP;
  apModeStartedAt = millis();
  lastStaRetryFromAp = millis();

  Serial.print("AP SSID: ");
  Serial.println(apSsid);
  Serial.print("Portal: http://");
  Serial.println(WiFi.softAPIP());
}

// Hard WiFi rebuild — wipes cached AP creds in NVS that cling to a bad
// supplicant state after a roam-then-AUTH_FAIL (reason 202) sequence.
void forceReconnectSTA()
{
  Serial.println("[WiFi] Forcing hard reconnect...");
  WiFi.disconnect(true, true);   // wifi off + erase cached AP creds in NVS
  delay(100);
  WiFi.mode(WIFI_OFF);
  delay(100);
  WiFi.mode(WIFI_STA);
  applyCustomMac();
  WiFi.setHostname("spenser");
  WiFi.setSleep(false);
  WiFi.setAutoReconnect(true);
  WiFi.setScanMethod(WIFI_ALL_CHANNEL_SCAN);
  WiFi.setSortMethod(WIFI_CONNECT_AP_BY_SIGNAL);
  WiFi.begin(wifiSsid.c_str(), wifiPass.c_str());
}

String createMedicationDispense(const String &id, const String &code, const String &patientRef)
{
  StaticJsonDocument<512> doc;
  doc["resourceType"] = "MedicationDispense";
  doc["id"] = id + "-dispense";
  doc["status"] = "completed";
  JsonObject med = doc.createNestedObject("medication").createNestedObject("concept");
  JsonObject coding = med.createNestedArray("coding").createNestedObject();
  coding["system"] = MEDS_SYSTEM;
  coding["code"] = code;
  coding["display"] = (code == "chocolate-dark") ? "Dark Chocolate" : "Milk Chocolate";
  doc["subject"]["reference"] = patientRef;
  doc.createNestedArray("authorizingPrescription").createNestedObject()["reference"] =
      "MedicationRequest/" + id;

  String output;
  serializeJson(doc, output);
  return output;
}

// A dispense that did not happen, because the lane is empty. R5 removed
// MedicationDispense.statusReason[x]; the reason now lives in notPerformedReason,
// which is a CodeableReference - hence the .concept. The old shape is rejected
// outright by an R5 server.
String createDeclinedDispense(const String &id, const String &medicationCode, const String &medicationDisplay, const String &patientReference)
{
  StaticJsonDocument<640> errorDoc;
  errorDoc["resourceType"] = "MedicationDispense";
  errorDoc["id"] = id + "-declined";
  errorDoc["status"] = "declined";

  JsonObject reason = errorDoc.createNestedObject("notPerformedReason").createNestedObject("concept");
  JsonObject reasonCoding = reason.createNestedArray("coding").createNestedObject();
  reasonCoding["system"] = NOT_PERFORMED_SYSTEM;
  reasonCoding["code"] = "outofstock";
  reasonCoding["display"] = "Drug not available - out of stock";

  JsonObject med = errorDoc.createNestedObject("medication").createNestedObject("concept");
  JsonObject coding = med.createNestedArray("coding").createNestedObject();
  coding["system"] = MEDS_SYSTEM;
  coding["code"] = medicationCode;
  coding["display"] = medicationDisplay;

  errorDoc["subject"]["reference"] = patientReference;
  errorDoc.createNestedArray("authorizingPrescription").createNestedObject()["reference"] =
      "MedicationRequest/" + id;

  String response;
  serializeJson(errorDoc, response);
  return response;
}

// --- Core dispensing logic (no HTTP dependency) ---

DispenseResult processDispenseRequest(const String &body)
{
  StaticJsonDocument<2048> doc;
  DeserializationError error = deserializeJson(doc, body);
  Serial.println("Processing MedicationRequest");

  if (error)
  {
    Serial.println("Failed to deserialize JSON");
    return {false, 400, "{\"status\":\"error\", \"message\":\"Invalid JSON\"}", "application/json"};
  }

  if (strcmp(doc["resourceType"], "MedicationRequest") != 0)
  {
    Serial.println("Invalid resource type. Expected 'MedicationRequest'");
    return {false, 400, "{\"status\":\"error\", \"message\":\"Invalid resource type. Expected 'MedicationRequest'\"}", "application/json"};
  }

  String id = doc["id"] | "";
  String status = doc["status"] | "";
  String intent = doc["intent"] | "";

  String medicationCode = "";
  String medicationDisplay = "";

  if (doc["medication"] && doc["medication"]["concept"] && doc["medication"]["concept"]["coding"])
  {
    medicationCode = doc["medication"]["concept"]["coding"][0]["code"] | "";
    medicationDisplay = doc["medication"]["concept"]["coding"][0]["display"] | "";
  }
  else if (doc["medicationCodeableConcept"] && doc["medicationCodeableConcept"]["coding"])
  {
    medicationCode = doc["medicationCodeableConcept"]["coding"][0]["code"] | "";
    medicationDisplay = doc["medicationCodeableConcept"]["coding"][0]["display"] | "";
  }

  String patientReference = doc["subject"]["reference"] | "";

  // Accept both "active" (direct local request) and "on-hold" (claimed from server)
  if (id.isEmpty() || (status != "active" && status != "on-hold") || intent != "instance-order" || patientReference.isEmpty())
  {
    return {false, 400, "{\"status\":\"error\", \"message\":\"Missing or invalid fields\"}", "application/json"};
  }

  if (medicationCode == "chocolate-dark")
  {
    if (inventoryDark > 0)
    {
      inventoryDark--;
      setLEDColor(128, 0, 0); // red
      dispenseServo(settings.servoDark);
      String response = createMedicationDispense(id, medicationCode, patientReference);
      setLEDColor(0, 0, 0);
      return {true, 200, response, "application/fhir+json"};
    }
    else
    {
      String response = createDeclinedDispense(id, medicationCode, medicationDisplay, patientReference);
      return {true, 201, response, "application/fhir+json"};
    }
  }
  else if (medicationCode == "chocolate-milk")
  {
    if (inventoryMilk > 0)
    {
      inventoryMilk--;
      setLEDColor(0, 0, 200); // blue
      dispenseServo(settings.servoMilk);
      String response = createMedicationDispense(id, medicationCode, patientReference);
      setLEDColor(0, 0, 0);
      return {true, 200, response, "application/fhir+json"};
    }
    else
    {
      String response = createDeclinedDispense(id, medicationCode, medicationDisplay, patientReference);
      return {true, 201, response, "application/fhir+json"};
    }
  }
  else
  {
    return {false, 400, "{\"status\":\"error\",\"message\":\"Invalid chocolate type\"}", "application/json"};
  }
}

// --- Thin wrapper for local web server ---

void handleMedicationRequest(String body, AsyncWebServerRequest *request)
{
  DispenseResult result = processDispenseRequest(body);
  request->send(result.httpStatus, result.contentType, result.responseBody);
}

// --- Remote server communication ---

// Post a dispense - completed or declined - back to the order server. Returns
// the HTTP status, and through createdId the id the server assigned, which the
// Task.output link needs. A failed post is queued for retry.
int postDispenseResult(const String &dispenseJson, String *createdId = nullptr)
{
  if (orderServerUrl.isEmpty())
    return 0;

  WiFiClientSecure secureClient;
  WiFiClient plainClient;
  HTTPClient http;
  String url = orderServerUrl + "/MedicationDispense";

  if (!beginHttp(http, secureClient, plainClient, url))
    return -1;

  const char *headerKeys[] = {"Location", "Content-Location"};
  http.collectHeaders(headerKeys, 2);
  http.addHeader("Content-Type", "application/fhir+json");
  http.addHeader("Accept", "application/fhir+json");
  http.setTimeout(8000);

  int httpCode = http.POST(dispenseJson);

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

  if (httpCode >= 200 && httpCode < 300)
  {
    Serial.println("Dispense posted to the server");
  }
  else
  {
    Serial.printf("Dispense POST failed (HTTP %d), queued for retry\n", httpCode);
    if (retryCount < RETRY_QUEUE_SIZE)
      retryQueue[retryCount++] = dispenseJson;
  }

  http.end();
  return httpCode;
}

void retryPendingDispenses()
{
  if (retryCount == 0 || orderServerUrl.isEmpty())
    return;

  WiFiClientSecure secureClient;
  WiFiClient plainClient;

  int remaining = 0;
  for (int i = 0; i < retryCount; i++)
  {
    HTTPClient http;
    String url = orderServerUrl + "/MedicationDispense";
    if (!beginHttp(http, secureClient, plainClient, url))
    {
      retryQueue[remaining++] = retryQueue[i];
      continue;
    }
    http.addHeader("Content-Type", "application/fhir+json");
    int httpCode = http.POST(retryQueue[i]);
    http.end();

    if (httpCode >= 200 && httpCode < 300)
    {
      Serial.println("Retry succeeded for queued dispense");
    }
    else
    {
      // Keep in queue
      retryQueue[remaining++] = retryQueue[i];
    }
  }
  retryCount = remaining;
}

// ==================== Order client ====================
// A FHIR request is an authorization, not an instruction. Per the COW IG
// ("Actionable orders") this unit only acts on an order when either
//   "tag"  - the MedicationRequest carries meta.tag common-tags#actionable, or
//   "task" - a Coordination Task points at it (Task.focus) asking for fulfilment.
// Whatever comes back is handed to processDispenseRequest, the same routine the
// POST /MedicationRequest endpoint uses.

const size_t ORDER_DOC_SIZE = 20480; // keep _count small: the Bundle is parsed in RAM

struct OrderCheck
{
  bool busy;
  bool everRan;
  unsigned long lastCheck; // millis() of the last finished check
  int httpStatus;          // status of the search itself
  int found;               // orders seen for the first time
  int dispensed;           // orders actually dispensed
  char message[160];       // the web task reads this while loop() writes it: keep it a plain buffer
};

OrderCheck orderCheck = {false, false, 0, 0, 0, 0, ""};
volatile bool checkRequested = false; // set by /checkOrders, serviced from loop()
unsigned long lastPollAttempt = 0;

void setOrderMessage(const String &text)
{
  strlcpy(orderCheck.message, text.c_str(), sizeof(orderCheck.message));
  Serial.println("[Orders] " + text);
}

void finishCheck()
{
  orderCheck.lastCheck = millis();
  orderCheck.busy = false;
}

String serverBase()
{
  String base = orderServerUrl;
  while (base.endsWith("/"))
    base.remove(base.length() - 1);
  return base;
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

int sendResource(const char *method, const String &url, const String &body)
{
  WiFiClientSecure secureClient;
  WiFiClient plainClient;
  HTTPClient http;

  if (!beginHttp(http, secureClient, plainClient, url))
    return -1;

  http.addHeader("Content-Type", "application/fhir+json");
  http.addHeader("Accept", "application/fhir+json");
  http.setTimeout(8000);

  int status = http.sendRequest(method, (uint8_t *)body.c_str(), body.length());
  http.end();
  return status;
}

// Close the workflow once an order has been dealt with. With a Task coordinating
// it, COW leaves the request itself to the placer, so only the Task moves - to
// completed, or to failed when this unit has given up. Without a Task there is
// nothing else to say it is done, so the request is completed instead. Giving up
// without a Task writes nothing: the order stays actionable for another unit.
String closeOrder(const String &base, JsonObject request, const String &requestId,
                  JsonObject task, const String &dispenseId, bool failed)
{
  int status = 0;

  if (!task.isNull())
  {
    task["status"] = failed ? "failed" : "completed";
    if (dispenseId.length())
    {
      JsonObject output = task.createNestedArray("output").createNestedObject();
      output.createNestedObject("type")["text"] = "MedicationDispense";
      output.createNestedObject("valueReference")["reference"] = "MedicationDispense/" + dispenseId;
    }

    String taskId = task["id"] | "";
    String body;
    serializeJson(task, body);
    status = sendResource("PUT", base + "/Task/" + taskId, body);
    Serial.printf("PUT Task/%s -> %d\n", taskId.c_str(), status);
  }
  else if (!failed)
  {
    request["status"] = "completed";
    String body;
    serializeJson(request, body);
    status = sendResource("PUT", base + "/MedicationRequest/" + requestId, body);
    Serial.printf("PUT MedicationRequest/%s -> %d\n", requestId.c_str(), status);
  }
  else
  {
    return "";
  }

  if (status >= 200 && status < 300)
    return "";

  return "Server refused the update (HTTP " + String(status) + ")";
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

  Serial.println("[Orders] GET " + url);

  WiFiClientSecure secureClient;
  WiFiClient plainClient;
  HTTPClient http;

  if (!beginHttp(http, secureClient, plainClient, url))
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

    String orderBody;
    serializeJson(request, orderBody);
    DispenseResult result = processDispenseRequest(orderBody);
    String requestId = request["id"] | "";

    if (result.httpStatus == 200) // dispensed
    {
      orderCheck.dispensed++;
      markHandled(orderId);

      if (settings.writeBack)
      {
        String dispenseId;
        int posted = postDispenseResult(result.responseBody, &dispenseId);
        String closeProblem = closeOrder(base, request, requestId, task, dispenseId, false);

        if (posted < 200 || posted >= 300)
          problem = "Dispensed, but the dispense was refused (HTTP " + String(posted) + ")";
        else if (closeProblem.length())
          problem = "Dispensed. " + closeProblem;
      }
    }
    else if (result.httpStatus == 201) // declined: that lane is empty
    {
      problem = "Out of stock for " + orderId;

      // Say so once, never on every poll.
      if (settings.writeBack && !alreadyReported(orderId))
      {
        postDispenseResult(result.responseBody);
        listAdd(reportedIds, orderId);
        problem += settings.giveUpOnStockEmpty ? " (told the server, abandoned)"
                                               : " (told the server)";
      }

      // Abandon the order so later polls skip it, or leave it for a refill.
      if (settings.giveUpOnStockEmpty)
      {
        markHandled(orderId);
        if (settings.writeBack)
          closeOrder(base, request, requestId, task, "", true);
      }
    }
    else
    {
      problem = orderId + " was not usable (HTTP " + String(result.httpStatus) + ")";
      Serial.println(problem + ": " + result.responseBody);
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
  StaticJsonDocument<1024> doc;
  doc["mode"] = settings.orderMode;
  doc["serverUrl"] = orderServerUrl;
  doc["giveUpOnStockEmpty"] = settings.giveUpOnStockEmpty;
  doc["busy"] = orderCheck.busy || checkRequested;
  doc["everRan"] = orderCheck.everRan;
  doc["secondsAgo"] = orderCheck.everRan ? (int)((millis() - orderCheck.lastCheck) / 1000) : -1;
  doc["httpStatus"] = orderCheck.httpStatus;
  doc["found"] = orderCheck.found;
  doc["dispensed"] = orderCheck.dispensed;
  doc["message"] = orderCheck.message;
  doc["handled"] = listCount(seenIds);
  doc["queuedRetries"] = retryCount;

  String out;
  serializeJson(doc, out);
  return out;
}

// --- Setup ---

void setup()
{
  Serial.begin(115200);
  delay(500);
  Serial.println("Setup starting");

  pinMode(buttonPin, INPUT_PULLUP);

  rgb.begin();
  rgb.setBrightness(50);
  rgb.show();

  setLEDColor(255, 255, 0); // Yellow = starting up

  // Initialize SPIFFS (non-fatal)
  if (!SPIFFS.begin(true))
  {
    Serial.println("SPIFFS initialization failed (continuing without it)");
  }

  // Load this unit's servo angles / timing from Preferences
  loadSettings();
  loadSeenIds();

  // Load saved server URL from Preferences
  prefs.begin("config", true);
  orderServerUrl = prefs.getString("serverUrl", "");
  prefs.end();
  Serial.println("Saved server URL: " + orderServerUrl);

  // Compute AP SSID from MAC tail
  uint8_t mac[6];
  WiFi.macAddress(mac);
  char buf[16];
  snprintf(buf, sizeof(buf), "Spenser-%02X%02X", mac[4], mac[5]);
  apSsid = String(buf);

  // Load saved Wi-Fi creds and decide STA vs AP
  loadWifiConfig();
  bool forcePortal = consumeForcePortalFlag();

  bool connected = false;
  if (!forcePortal && !wifiSsid.isEmpty())
  {
    setLEDColor(0, 0, 255); // Blue = trying STA
    connected = tryConnectSTA(15000);
  }
  if (!connected)
  {
    setLEDColor(128, 0, 128); // Purple = AP/portal mode
    startAPPortal();
  }
  else
  {
    setLEDColor(0, 255, 0); // Green = connected
  }

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

  // I2C scan for visibility (AtomicMotion @ 0x38, INA226 @ 0x40)
  Serial.println("I2C scan:");
  for (uint8_t addr = 1; addr < 127; addr++)
  {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0)
    {
      Serial.printf("  - 0x%02X\n", addr);
    }
  }
  Wire.beginTransmission(0x40); // INA226 default address
  if (Wire.endTransmission() == 0)
  {
    Serial.println("INA226 detected at 0x40");
  }
  else
  {
    Serial.println("INA226 NOT found at 0x40 — battery monitoring disabled");
  }

  // ==================== Web Server Routes ====================

  // CORS — allow tools and test pages from other origins (e.g. file://, localhost)
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Origin", "*");
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Headers", "Content-Type, Accept");

  // Root: portal page in AP mode, app UI in STA mode
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    if (netMode == NET_AP) {
      req->send_P(200, "text/html", PORTAL_HTML);
      return;
    }
    if (SPIFFS.exists("/index.html")) {
      req->send(SPIFFS, "/index.html", "text/html");
    } else {
      req->send(200, "text/plain", "Spenser is running. index.html not found in SPIFFS.");
    } });

  // Portal: SSID scan
  server.on("/scan", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    int n = WiFi.scanComplete();
    if (n == WIFI_SCAN_RUNNING) {
      req->send(200, "application/json", "{\"networks\":[],\"scanning\":true}");
      return;
    }
    if (n < 0) {
      WiFi.scanNetworks(true); // async
      req->send(200, "application/json", "{\"networks\":[],\"scanning\":true}");
      return;
    }
    String out = "{\"networks\":[";
    for (int i = 0; i < n; i++) {
      if (i) out += ',';
      out += "{\"ssid\":\"";
      String s = WiFi.SSID(i); s.replace("\\", "\\\\"); s.replace("\"", "\\\"");
      out += s;
      out += "\",\"rssi\":";
      out += String(WiFi.RSSI(i));
      out += ",\"secure\":";
      out += (WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? "false" : "true";
      out += "}";
    }
    out += "]}";
    WiFi.scanDelete();
    WiFi.scanNetworks(true); // queue next scan
    req->send(200, "application/json", out); });

  // Portal: current config (no password)
  server.on("/cfg", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    String out = "{\"ssid\":\"" + wifiSsid + "\",\"url\":\"" + orderServerUrl + "\"}";
    req->send(200, "application/json", out); });

  // Portal: save credentials and reboot into STA
  server.on("/save", HTTP_POST, [](AsyncWebServerRequest *req)
            {
    if (!req->hasParam("ssid", true)) {
      req->send(400, "application/json", "{\"ok\":false,\"error\":\"missing ssid\"}");
      return;
    }
    String ssid = req->getParam("ssid", true)->value();
    String pass = req->hasParam("pass", true) ? req->getParam("pass", true)->value() : "";
    String url  = req->hasParam("url",  true) ? req->getParam("url",  true)->value() : "";
    if (ssid.length() == 0) {
      req->send(400, "application/json", "{\"ok\":false,\"error\":\"empty ssid\"}");
      return;
    }
    if (url.endsWith("/")) url.remove(url.length() - 1);

    saveWifiConfig(ssid, pass);
    prefs.begin("config", false);
    prefs.putString("serverUrl", url);
    prefs.end();
    orderServerUrl = url;

    String resp = "{\"ok\":true,\"ssid\":\"" + ssid + "\"}";
    req->send(200, "application/json", resp);
    // Reboot shortly so the response can flush
    delay(500);
    ESP.restart(); });

  // Wi-Fi management endpoints (STA-side convenience)
  server.on("/wifi-settings", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    setForcePortalFlag();
    req->send(200, "text/html", "<p>Rebooting into Wi-Fi config mode (credentials kept)...</p>");
    delay(500);
    ESP.restart(); });

  server.on("/wifi-reset", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    clearWifiConfig();
    req->send(200, "text/html", "<p>Wi-Fi credentials cleared. Rebooting into AP mode...</p>");
    delay(500);
    ESP.restart(); });

  server.on("/wifi-reboot-config", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    setForcePortalFlag();
    req->send(200, "text/html", "<p>Rebooting into Wi-Fi config mode...</p>");
    delay(500);
    ESP.restart(); });

  // --- Custom MAC override endpoints ---

  server.on("/getMac", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    StaticJsonDocument<256> doc;
    uint8_t currentMac[6];
    WiFi.macAddress(currentMac);
    doc["currentMac"] = formatMacAddress(currentMac);
    doc["customMacActive"] = customMacActive;
    prefs.begin("network", true);
    doc["storedMac"] = prefs.getString("customMAC", "");
    prefs.end();
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response); });

  server.on("/setMac", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!request->hasParam("mac")) {
      request->send(400, "application/json", "{\"error\":\"Missing 'mac' parameter\"}");
      return;
    }
    String macStr = request->getParam("mac")->value();
    if (macStr.length() == 0) {
      prefs.begin("network", false);
      prefs.remove("customMAC");
      prefs.end();
      request->send(200, "application/json", "{\"status\":\"ok\",\"message\":\"Custom MAC cleared. Factory MAC will be used on next reboot.\"}");
      return;
    }
    uint8_t testMac[6];
    if (!parseMacAddress(macStr, testMac)) {
      request->send(400, "application/json", "{\"error\":\"Invalid MAC format. Use AA:BB:CC:DD:EE:FF. First byte must be even (unicast).\"}");
      return;
    }
    String normalizedMac = formatMacAddress(testMac);
    prefs.begin("network", false);
    prefs.putString("customMAC", normalizedMac);
    prefs.end();
    StaticJsonDocument<256> doc;
    doc["status"] = "ok";
    doc["message"] = "Custom MAC saved. Reboot to apply.";
    doc["mac"] = normalizedMac;
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response); });

  server.on("/clearMac", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    prefs.begin("network", false);
    prefs.remove("customMAC");
    prefs.end();
    request->send(200, "application/json", "{\"status\":\"ok\",\"message\":\"Custom MAC cleared. Factory MAC will be used on next reboot.\"}"); });

  // Captive portal redirects
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

  // Color control
  server.on("/setColor", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String redValue = request->getParam("red")->value();
    String greenValue = request->getParam("green")->value();
    String blueValue = request->getParam("blue")->value();

    rgb.setPixelColor(0, rgb.Color(redValue.toInt(), greenValue.toInt(), blueValue.toInt()));
    rgb.show();

    request->send(200, "text/plain", "Color updated"); });

  // Servo control
  server.on("/setServos", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (request->hasParam("servo4")) {
      int angle = request->getParam("servo4")->value().toInt();
      if (angle >= 0 && angle <= 360) {
        AtomicMotion.setServoAngle(settings.servoDark, angle);
        Serial.println("Servo 4 updated");
      }
    }
    if (request->hasParam("servo3")) {
      int angle = request->getParam("servo3")->value().toInt();
      if (angle >= 0 && angle <= 360) {
        AtomicMotion.setServoAngle(settings.servoMilk, angle);
        Serial.println("Servo 3 updated");
      }
    }
    request->send(200, "text/plain", "Servos updated"); });

  server.on("/reset", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    rgb.setPixelColor(0, rgb.Color(0, 0, 0));
    rgb.show();
    AtomicMotion.setServoAngle(settings.servoDark, settings.angleRest);
    AtomicMotion.setServoAngle(settings.servoMilk, settings.angleRest);
    request->send(200, "text/plain", "Sliders and servos reset to rest angle"); });

  server.on("/flashServo1", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    Serial.println("Flashing Servo 1");
    dispenseServo(settings.servoDark);
    request->send(200, "text/plain", "Servo 1 flashed"); });

  server.on("/flashServo2", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    Serial.println("Flashing Servo 2");
    dispenseServo(settings.servoMilk);
    request->send(200, "text/plain", "Servo 2 flashed"); });

  // Inventory
  server.on("/inventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String json = "{\"dark\":" + String(inventoryDark) + ",\"milk\":" + String(inventoryMilk) + "}";
    request->send(200, "application/json", json); });

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

    // The server URL is shared with the Wi-Fi portal, so it stays where the
    // portal put it rather than moving in with the rest of the settings.
    if (paramStr(request, "serverUrl", text)) {
      while (text.endsWith("/")) text.remove(text.length() - 1);
      orderServerUrl = text;
      prefs.begin("config", false);
      prefs.putString("serverUrl", orderServerUrl);
      prefs.end();
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
    if (paramBool(request, "giveUpOnStockEmpty", flag)) {
      settings.giveUpOnStockEmpty = flag;
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
    reportedIds = "|";
    request->send(200, "application/json", settingsJson()); });

  // Ask for a check. The HTTP call itself runs from loop(), so the async web
  // server is never blocked while this unit talks to the order server.
  server.on("/checkOrders", HTTP_GET | HTTP_POST, [](AsyncWebServerRequest *request)
            {
    checkRequested = true;
    request->send(202, "application/json", "{\"status\":\"scheduled\"}"); });

  // What the last check did
  server.on("/orders", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(200, "application/json", orderStatusJson()); });

  // Forget which orders were already dealt with, so they can be dispensed again
  server.on("/forgetOrders", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    forgetHandled();
    request->send(200, "application/json", orderStatusJson()); });

  server.on("/setInventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    bool updated = false;
    if (request->hasParam("dark")) {
      inventoryDark = request->getParam("dark")->value().toInt();
      updated = true;
    }
    if (request->hasParam("milk")) {
      inventoryMilk = request->getParam("milk")->value().toInt();
      updated = true;
    }
    if (updated) {
      request->send(200, "text/plain", "Inventory updated: Dark = " + String(inventoryDark) + ", Milk = " + String(inventoryMilk));
    } else {
      request->send(400, "text/plain", "Missing 'dark' and/or 'milk' parameters");
    } });

  server.on("/resetInventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (request->hasParam("dark")) inventoryDark = request->getParam("dark")->value().toInt();
    if (request->hasParam("milk")) inventoryMilk = request->getParam("milk")->value().toInt();
    request->send(200, "text/plain", "Inventory updated"); });

  // Battery — single-cell Li-ion via INA226 bus voltage
  server.on("/battery", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    // Sensor presence
    Wire.beginTransmission(0x40);
    if (Wire.endTransmission() != 0) {
      request->send(503, "application/json", "{\"error\":\"INA226 not present\"}");
      return;
    }

    // Power source. The INA226 sits on the pack side of the charger, so the rail
    // stays at cell voltage whether or not USB is plugged in — the direction of
    // current is what tells the two apart. On this board the raw reading is
    // positive while the pack is being drained, so CHARGE_SIGN flips it to the
    // "positive = into the pack" convention used below.
    constexpr float USB_RAIL_MIN_V = 4.35f; // above any resting or charging 1S cell
    constexpr float CHARGE_MIN_A   = 0.02f; // deadband for measurement noise
    constexpr float CHARGE_SIGN    = -1.0f;

    float voltage = AtomicMotion.ina226.readBusVoltage();
    float current = AtomicMotion.ina226.readShuntCurrent();
    String meas = "\"voltage\":" + String(voltage, 2) + ",\"current\":" + String(current, 3);

    // A 5V rail hides whatever pack sits behind it, so there is no honest
    // state-of-charge to report — only that we are on external power.
    if (voltage >= USB_RAIL_MIN_V) {
      String j = "{" + meas + ",\"percent\":null,\"state\":\"usb\",\"source\":\"usb\"}";
      request->send(200, "application/json", j);
      return;
    }

    // Below ~2.5V: no battery connected (or too dead to be safe to operate).
    // We are answering the request, so the board is being fed from elsewhere.
    if (voltage < 2.5f) {
      String j = "{" + meas + ",\"percent\":null,\"state\":\"no_battery\",\"source\":\"usb\"}";
      request->send(200, "application/json", j);
      return;
    }

    // Piecewise-linear Li-ion 1S discharge curve (resting voltage)
    static const struct { float v; float p; } curve[] = {
      {4.20f, 100.0f}, {4.10f, 90.0f}, {4.00f, 80.0f}, {3.95f, 70.0f},
      {3.85f,  60.0f}, {3.80f, 50.0f}, {3.75f, 40.0f}, {3.70f, 30.0f},
      {3.65f,  20.0f}, {3.55f, 10.0f}, {3.40f,  5.0f}, {3.20f,  0.0f},
    };
    const int N = sizeof(curve)/sizeof(curve[0]);
    float percent;
    if (voltage >= curve[0].v) {
      percent = 100.0f;
    } else if (voltage <= curve[N-1].v) {
      percent = 0.0f;
    } else {
      percent = 0.0f;
      for (int i = 0; i < N - 1; i++) {
        if (voltage <= curve[i].v && voltage >= curve[i+1].v) {
          float t = (voltage - curve[i+1].v) / (curve[i].v - curve[i+1].v);
          percent = curve[i+1].p + t * (curve[i].p - curve[i+1].p);
          break;
        }
      }
    }
    percent = constrain(round(percent), 0, 100);

    // Positive = flowing into the pack, negative = the pack is feeding the board.
    // Near-zero while we are plainly still running means neither: something else
    // is carrying the load, i.e. USB with a pack that has finished charging.
    float packCurrent = current * CHARGE_SIGN;
    const char *source = (packCurrent >  CHARGE_MIN_A) ? "charging"
                       : (packCurrent < -CHARGE_MIN_A) ? "battery"
                                                       : "usb";

    String j = "{" + meas + ",\"percent\":" + String(percent, 0) +
               ",\"state\":\"battery\",\"source\":\"" + source + "\"}";
    request->send(200, "application/json", j); });

  // FHIR CapabilityStatement
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

    JsonObject res1 = resources.createNestedObject();
    res1["type"] = "MedicationRequest";
    res1["profile"] = "http://costateixeira.github.io/spenser";
    JsonArray res1_interaction = res1.createNestedArray("interaction");
    res1_interaction.createNestedObject()["code"] = "create";

    JsonObject res2 = resources.createNestedObject();
    res2["type"] = "InventoryReport";
    JsonArray res2_interaction = res2.createNestedArray("interaction");
    res2_interaction.createNestedObject()["code"] = "read";
    res2_interaction.createNestedObject()["code"] = "create";

    // ---- client: what this unit asks of an order server ----
    JsonObject rest1 = rest.createNestedObject();
    rest1["mode"] = "client";
    rest1["documentation"] = "Polls a server for orders that have been made actionable, either by the 'actionable' tag on the MedicationRequest or by a Task asking for it to be fulfilled";

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
    cres2["documentation"] = "Coordination Task pointing at the order in Task.focus. Set to 'completed' with the dispense in Task.output, or 'failed' when this unit gives up; the status of the request itself is left to the placer";
    JsonArray cres2_interaction = cres2.createNestedArray("interaction");
    cres2_interaction.createNestedObject()["code"] = "search-type";
    cres2_interaction.createNestedObject()["code"] = "update";
    JsonObject cres2_status = cres2.createNestedArray("searchParam").createNestedObject();
    cres2_status["name"] = "status";
    cres2_status["type"] = "token";
    cres2["searchInclude"][0] = "Task:focus";

    // MedicationDispense: what this unit reports back
    JsonObject cres3 = clientResources.createNestedObject();
    cres3["type"] = "MedicationDispense";
    cres3["documentation"] = "Created on the server once an order has been dispensed or declined, referring to the order in authorizingPrescription";
    cres3.createNestedArray("interaction").createNestedObject()["code"] = "create";

    String response;
    serializeJsonPretty(doc, response);
    request->send(200, "application/fhir+json", response); });

  // FHIR InventoryReport - GET
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

  // FHIR InventoryReport - POST
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

  // FHIR MedicationRequest - POST (local)
  AsyncCallbackWebHandler *medicationHandler = new AsyncCallbackWebHandler();
  medicationHandler->setUri("/MedicationRequest");
  medicationHandler->setMethod(HTTP_POST);

  medicationHandler->onRequest([](AsyncWebServerRequest *request)
                               {
                                 // Body handled in onBody
                               });

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

  // 404 handler: fall back to static files in SPIFFS
  server.onNotFound([](AsyncWebServerRequest *request)
                    {
    if (request->method() == HTTP_OPTIONS) { // CORS preflight
      request->send(200);
      return;
    }
    if (request->method() == HTTP_GET) {
      String path = request->url();
      int q = path.indexOf('?');
      if (q >= 0) path = path.substring(0, q);
      if (SPIFFS.exists(path)) {
        const char *ct = "application/octet-stream";
        if      (path.endsWith(".html")) ct = "text/html";
        else if (path.endsWith(".js"))   ct = "application/javascript";
        else if (path.endsWith(".css"))  ct = "text/css";
        else if (path.endsWith(".png"))  ct = "image/png";
        else if (path.endsWith(".svg"))  ct = "image/svg+xml";
        else if (path.endsWith(".ico"))  ct = "image/x-icon";
        else if (path.endsWith(".json")) ct = "application/json";
        request->send(SPIFFS, path, ct);
        return;
      }
    }
    request->send(404, "text/plain", "Not found"); });

  server.begin();
  Serial.println("Web server started");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

// --- Main loop ---

void loop()
{
  // Button handling
  // - short tap (50–1000 ms): dispense one dark chocolate
  // - 3 s hold: reboot into AP/portal, KEEP credentials (lets user reconfigure)
  // - 10 s hold: WIPE credentials + URL, reboot into AP (factory reset)
  static bool buttonPressed = false;
  static unsigned long buttonPressStart = 0;
  static bool wipeFeedbackShown = false;
  const unsigned long shortPressMinDuration = 50;
  const unsigned long shortPressMaxDuration = 1000;
  const unsigned long softResetDuration    = 3000;
  const unsigned long factoryResetDuration = 10000;

  bool buttonState = digitalRead(buttonPin) == LOW;

  if (buttonState && !buttonPressed)
  {
    buttonPressed = true;
    buttonPressStart = millis();
    wipeFeedbackShown = false;
  }

  // While button is held: visual feedback when crossing the 10 s threshold
  if (buttonState && buttonPressed && !wipeFeedbackShown &&
      millis() - buttonPressStart >= factoryResetDuration)
  {
    setLEDColor(255, 0, 0); // red = will wipe creds on release
    wipeFeedbackShown = true;
  }

  if (!buttonState && buttonPressed)
  {
    unsigned long pressDuration = millis() - buttonPressStart;
    buttonPressed = false;

    if (pressDuration >= factoryResetDuration)
    {
      Serial.println("10s hold — wiping Wi-Fi creds + server URL, rebooting...");
      clearWifiConfig();
      prefs.begin("config", false);
      prefs.remove("serverUrl");
      prefs.end();
      delay(500);
      ESP.restart();
    }
    else if (pressDuration >= softResetDuration)
    {
      Serial.println("3s hold — rebooting into AP portal (credentials kept)...");
      setForcePortalFlag();
      delay(500);
      ESP.restart();
    }
    else if (pressDuration >= shortPressMinDuration && pressDuration <= shortPressMaxDuration)
    {
      Serial.println("Short press detected — dispensing one dark chocolate.");
      if (inventoryDark > 0)
      {
        inventoryDark--;
        setLEDColor(128, 0, 0);
        dispenseServo(settings.servoDark);
        setLEDColor(netMode == NET_AP ? 128 : 0, 0, netMode == NET_AP ? 128 : 0);
      }
      else
      {
        Serial.println("Out of dark chocolate!");
      }
    }
  }

  unsigned long now = millis();

  // AP mode: keep DNS captive portal alive; periodically retry STA
  if (netMode == NET_AP)
  {
    dns.processNextRequest();
    if (!wifiSsid.isEmpty() && now - lastStaRetryFromAp >= staRetryFromApInterval)
    {
      lastStaRetryFromAp = now;
      Serial.println("Retrying STA from AP...");
      WiFi.softAPdisconnect(false);
      dns.stop();
      if (tryConnectSTA(15000))
      {
        setLEDColor(0, 255, 0);
      }
      else
      {
        startAPPortal();
        setLEDColor(128, 0, 128);
      }
    }
    return; // skip STA-only work below
  }

  // STA mode: check if still connected, handle reconnection
  static unsigned long lastStaCheck = 0;
  static unsigned long staDisconnectedSince = 0;
  static bool staWasConnected = true;
  static bool staInitialized = false;
  static bool forcedReconnectTried = false;
  const unsigned long staCheckInterval = 2000;
  const unsigned long staForceReconnectAfter = 5000;   // hard reconnect after 5s
  const unsigned long staReconnectTimeout = 30000;     // fall back to AP after 30s
  const unsigned long staGracePeriod = 5000;

  if (now - lastStaCheck >= staCheckInterval)
  {
    lastStaCheck = now;

    // Skip checks during grace period after boot
    if (!staInitialized && now < staGracePeriod)
    {
      return;
    }
    staInitialized = true;

    if (WiFi.status() == WL_CONNECTED)
    {
      staDisconnectedSince = 0;
      forcedReconnectTried = false;
      if (!staWasConnected)
      {
        setLEDColor(0, 255, 0);
        Serial.println("WiFi reconnected");
        staWasConnected = true;
      }
    }
    else
    {
      // WiFi dropped
      if (staWasConnected)
      {
        Serial.println("WiFi connection lost, waiting for auto-reconnect...");
        setLEDColor(255, 165, 0); // Orange = reconnecting
        staDisconnectedSince = now;
        staWasConnected = false;
        forcedReconnectTried = false;
      }

      // After 5s still down, do one hard reconnect attempt
      if (!forcedReconnectTried && staDisconnectedSince > 0 &&
          now - staDisconnectedSince >= staForceReconnectAfter)
      {
        forcedReconnectTried = true;
        forceReconnectSTA();
      }

      // If disconnected too long, fall back to AP
      if (staDisconnectedSince > 0 && now - staDisconnectedSince >= staReconnectTimeout)
      {
        Serial.println("WiFi reconnect timeout, starting AP portal...");
        startAPPortal();
        setLEDColor(128, 0, 128);
        return;
      }
    }
  }

  // Report IP periodically (only if connected)
  static unsigned long lastIpReport = 0;
  if (now - lastIpReport >= ipReportInterval)
  {
    lastIpReport = now;
    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("[%lu] IP: %s\n", now, WiFi.localIP().toString().c_str());
    } else {
      Serial.printf("[%lu] WiFi.status()=%d (not connected)\n", now, WiFi.status());
    }
  }

  // Order polling. The blocking HTTP work happens here in loop(), never inside
  // an async web handler, which only raises the checkRequested flag.
  bool pollDue = settings.pollEnabled && settings.pollSeconds > 0 &&
                 (now - lastPollAttempt >= (unsigned long)settings.pollSeconds * 1000UL);

  if (checkRequested || (WiFi.status() == WL_CONNECTED && pollDue))
  {
    checkRequested = false;
    lastPollAttempt = now;
    checkOrders(); // reports the Wi-Fi state itself when there is no connection

    if (WiFi.status() == WL_CONNECTED)
      retryPendingDispenses();
  }
}
