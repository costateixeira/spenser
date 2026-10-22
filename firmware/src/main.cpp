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
#include <esp_random.h>
#include <esp_ota_ops.h>
#include <Update.h>
#include <HTTPUpdate.h>
#include <time.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>
#include <functional>

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

// What this build is. Reported in /settings, in the CapabilityStatement as
// software.version, and compared against the release manifest when the unit
// checks for an update, so a unit in the field can always be identified.
//
// The publishing workflow overrides this with the base version and the commit
// it built from, e.g. "1.1.0+a1b2c3d". That matters: the unit decides whether
// to update by comparing this string with the one in the manifest, so a
// manifest published per commit needs a version that changes per commit, or a
// unit would either offer the same update forever or never notice one.
// Published builds live at https://costateixeira.github.io/spenser/firmware/
// with the notes for each one. A build from a workstation says -dev, so a
// hand-flashed unit is recognisable in a fleet.
#ifndef FIRMWARE_VERSION
#define FIRMWARE_VERSION "1.2.4-dev"
#endif
#define FIRMWARE_BUILD __DATE__ " " __TIME__

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
  // Which routes to an actionable order this unit accepts: "both" (the
  // default), or "tag"/"task" to listen on only one of them. They are not
  // alternative modes - a tag and a Task are two ways of authorizing the same
  // dispense, and the unit is happy to be told either way.
  String orderMode;   // "both", "tag" or "task"
  String orderQuery;  // extra search parameters for the MedicationRequest search
  String taskQuery;   // extra search parameters for the Task search
  bool pollEnabled;   // check the server automatically
  int pollSeconds;    // seconds between automatic checks
  bool writeBack;     // report what happened back to the server
  bool giveUpOnStockEmpty; // an order this unit cannot fill: abandon it, or retry
                           // it after a refill

  // --- Over-the-air updates. updateUrl points at a manifest, which a release
  // workflow publishes next to the binaries; see /ota/status. ---
  String updateUrl;     // manifest URL, empty to disable pull updates. The
                        // default is the published one, so a unit notices a new
                        // build without being told where to look; clear it to
                        // stop a unit checking at all.
  int updateCheckMinutes; // minutes between automatic checks, 0 = only when asked.
                          // Minutes rather than hours because an interval you
                          // cannot set shorter than an hour is one nobody can
                          // watch working, and a manifest fetch is under a
                          // kilobyte.
  String updateMode;    // "notify" (the default) reports what it found and waits
                        // for /ota/install; "install" takes it there and then
};

const Settings DEFAULT_SETTINGS = {
    3, 2, 0, 77, 300,
    "both",
    "status=active&intent=instance-order&_count=5",
    "status=requested&_include=Task:focus&_count=5",
    true, 30, true, false,
    "https://costateixeira.github.io/spenser/firmware/manifest.json", 15, "notify"};
Settings settings = DEFAULT_SETTINGS;

int inventoryDark = 15;
int inventoryMilk = 15;

// Stock is persisted: an update reboots the unit, and a dispenser that forgets
// what is in its lanes every time it restarts reports stock it does not have.
void loadInventory()
{
  prefs.begin("spenser", true);
  inventoryDark = prefs.getInt("invDark", inventoryDark);
  inventoryMilk = prefs.getInt("invMilk", inventoryMilk);
  prefs.end();
}

void saveInventory()
{
  prefs.begin("spenser", false);
  prefs.putInt("invDark", inventoryDark);
  prefs.putInt("invMilk", inventoryMilk);
  prefs.end();
}

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

// Writes to the order server that have not landed yet. Posting a dispense and
// closing the order out are both writes this unit owes the server, so both are
// queued: a close-out that is dropped on the floor leaves a Task requested
// forever while the order counts as handled.
const int RETRY_QUEUE_SIZE = 8;

struct PendingWrite
{
  String method;  // POST or PUT
  String url;     // absolute
  String body;
  String ifMatch; // version the write was based on, when the server gave one
};

PendingWrite retryQueue[RETRY_QUEUE_SIZE];
int retryCount = 0;

void queueWrite(const String &method, const String &url, const String &body, const String &ifMatch)
{
  if (retryCount >= RETRY_QUEUE_SIZE)
  {
    Serial.println("[Orders] retry queue full, dropping the oldest write");
    for (int i = 1; i < RETRY_QUEUE_SIZE; i++)
      retryQueue[i - 1] = retryQueue[i];
    retryCount = RETRY_QUEUE_SIZE - 1;
  }

  retryQueue[retryCount].method = method;
  retryQueue[retryCount].url = url;
  retryQueue[retryCount].body = body;
  retryQueue[retryCount].ifMatch = ifMatch;
  retryCount++;
}

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
  settings.updateUrl = prefs.getString("updateUrl", settings.updateUrl);
  settings.updateCheckMinutes = prefs.getInt("updateMins", settings.updateCheckMinutes);
  // Units set up before this was measured in minutes carry the old key
  if (prefs.isKey("updateHrs") && !prefs.isKey("updateMins"))
    settings.updateCheckMinutes = prefs.getInt("updateHrs", 1) * 60;
  settings.updateMode = prefs.getString("updateMode", settings.updateMode);
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
  prefs.putString("updateUrl", settings.updateUrl);
  prefs.putInt("updateMins", settings.updateCheckMinutes);
  prefs.putString("updateMode", settings.updateMode);
  prefs.end();
}

String settingsJson()
{
  StaticJsonDocument<640> doc;
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
  doc["updateUrl"] = settings.updateUrl;
  doc["updateCheckMinutes"] = settings.updateCheckMinutes;
  doc["updateMode"] = settings.updateMode;
  doc["firmwareVersion"] = FIRMWARE_VERSION;

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

// ==================== Per-unit key ====================
// Everything that changes this unit - dispensing, settings, Wi-Fi, updates -
// needs this key. Reads do not, so the dashboard and the FHIR searches stay
// open. The key is generated on first boot, printed on the serial console, and
// readable over HTTP only while the unit is in setup mode or in the first few
// minutes after boot, which is the window its owner has and nobody else does.

String deviceKey;
unsigned long bootMillis = 0;
const unsigned long KEY_REVEAL_WINDOW_MS = 5UL * 60UL * 1000UL;

void loadDeviceKey()
{
  prefs.begin("spenser", false);
  deviceKey = prefs.getString("deviceKey", "");
  if (deviceKey.length() != 32)
  {
    char buf[33];
    for (int i = 0; i < 4; i++)
      snprintf(buf + i * 8, 9, "%08x", (unsigned int)esp_random());
    deviceKey = String(buf);
    prefs.putString("deviceKey", deviceKey);
    Serial.println("Generated a new device key");
  }
  prefs.end();
}

// Presented as a bearer token, as an X-Spenser-Key header, or as ?key= for a
// browser or a REST client that cannot set headers.
bool keyMatches(AsyncWebServerRequest *request)
{
  if (deviceKey.isEmpty())
    return true; // no key yet: do not lock the unit out of its own setup
  if (netMode == NET_AP)
    return true; // setup mode: the access point is the proof of proximity

  String offered;
  if (request->hasHeader("Authorization"))
  {
    offered = request->header("Authorization");
    if (offered.startsWith("Bearer "))
      offered = offered.substring(7);
  }
  if (offered.isEmpty() && request->hasHeader("X-Spenser-Key"))
    offered = request->header("X-Spenser-Key");
  if (offered.isEmpty() && request->hasParam("key"))
    offered = request->getParam("key")->value();
  if (offered.isEmpty() && request->hasParam("key", true))
    offered = request->getParam("key", true)->value();

  offered.trim();
  return offered.length() == deviceKey.length() && offered == deviceKey;
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

// ==================== Time ====================
// Without a clock a dispense record cannot say when it happened, which for a
// medication record is the part that matters. Rather than invent a timestamp,
// the resources leave the element out until the unit has heard from an NTP
// server.

bool clockReady()
{
  return time(nullptr) > 1700000000; // anything earlier is the unset epoch
}

void startClock()
{
  configTzTime("UTC0", "pool.ntp.org", "time.google.com", "time.cloudflare.com");
}

String nowIso()
{
  if (!clockReady())
    return "";

  time_t now = time(nullptr);
  struct tm utc;
  gmtime_r(&now, &utc);
  char buf[32];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &utc);
  return String(buf);
}

// ==================== OperationOutcome ====================
// Every error from a FHIR route is an OperationOutcome, which is what a client
// is entitled to expect. The admin routes answer with the same shape rather
// than a second ad hoc error format.

String outcomeJson(const char *severity, const char *code, const String &diagnostics)
{
  StaticJsonDocument<512> doc;
  doc["resourceType"] = "OperationOutcome";
  JsonObject issue = doc.createNestedArray("issue").createNestedObject();
  issue["severity"] = severity;
  issue["code"] = code;
  issue["diagnostics"] = diagnostics;

  String out;
  serializeJson(doc, out);
  return out;
}

void sendOutcome(AsyncWebServerRequest *request, int status, const char *code, const String &diagnostics)
{
  request->send(status, "application/fhir+json", outcomeJson("error", code, diagnostics));
}

// Guard for every route that changes something. Returns false when the caller
// has not presented the key, having already answered the request.
bool requireKey(AsyncWebServerRequest *request)
{
  if (keyMatches(request))
    return true;

  AsyncWebServerResponse *response = request->beginResponse(
      401, "application/fhir+json",
      outcomeJson("error", "security",
                  "This unit needs its key. Send it as Authorization: Bearer <key>, "
                  "as X-Spenser-Key, or as ?key=<key>. The key is printed on the serial "
                  "console at boot and served at /key for five minutes after a restart."));
  response->addHeader("WWW-Authenticate", "Bearer realm=\"spenser\"");
  request->send(response);
  return false;
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
  StaticJsonDocument<640> doc;
  doc["resourceType"] = "MedicationDispense";
  doc["id"] = id + "-dispense";
  doc["status"] = "completed";

  // When it happened. Left out rather than guessed when the unit has not yet
  // reached an NTP server, because a wrong time in a dispense record is worse
  // than none.
  String at = nowIso();
  if (at.length())
  {
    doc["recorded"] = at;
    doc["whenPrepared"] = at;
    doc["whenHandedOver"] = at;
  }
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
  StaticJsonDocument<768> errorDoc;
  errorDoc["resourceType"] = "MedicationDispense";
  errorDoc["id"] = id + "-declined";
  errorDoc["status"] = "declined";

  String at = nowIso();
  if (at.length())
    errorDoc["recorded"] = at;

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

// ==================== Record store ====================
// What this unit did, kept on the flash filesystem rather than in RAM, so a
// reboot - or an over-the-air update - does not erase it. One resource per
// line, oldest first. A resource whose id is already present is appended
// again; readers walk backwards and keep the first copy of each id, so the
// newest version of a record wins and no rewrite is needed.
//
// loop() writes these files while the web task reads them, and the filesystem
// makes no promise about concurrent use, so every access takes a mutex.

const char *ORDER_STORE = "/orders.ndjson";
const char *DISPENSE_STORE = "/dispenses.ndjson";
const size_t STORE_MAX_BYTES = 40960; // per file; the oldest half is dropped past this
const size_t STORE_MAX_LINE = 1536;
const int STORE_INDEX_SIZE = 120; // how many of the newest records a read can reach

SemaphoreHandle_t storeMutex = nullptr;

bool storeLock()
{
  if (!storeMutex)
    return true;
  return xSemaphoreTake(storeMutex, pdMS_TO_TICKS(2000)) == pdTRUE;
}

void storeUnlock()
{
  if (storeMutex)
    xSemaphoreGive(storeMutex);
}

// Caller holds the lock. Keeps the newer half of the file when it grows past
// the cap, so the oldest records are the ones that go.
void storeTrimLocked(const char *path)
{
  File in = SPIFFS.open(path, FILE_READ);
  if (!in)
    return;
  if (in.size() <= STORE_MAX_BYTES)
  {
    in.close();
    return;
  }

  in.seek(in.size() / 2);
  in.readStringUntil('\n'); // discard the partial line we landed in

  File out = SPIFFS.open("/store.tmp", FILE_WRITE);
  if (!out)
  {
    in.close();
    return;
  }

  while (in.available())
  {
    String line = in.readStringUntil('\n');
    line.trim();
    if (line.length())
    {
      out.print(line);
      out.print('\n');
    }
  }
  in.close();
  out.close();

  SPIFFS.remove(path);
  SPIFFS.rename("/store.tmp", path);
  Serial.printf("[Store] %s trimmed to the newest records\n", path);
}

bool storeAppend(const char *path, const String &json)
{
  if (json.length() >= STORE_MAX_LINE)
  {
    Serial.println("[Store] record too large, not kept");
    return false;
  }
  if (json.indexOf('\n') >= 0)
    return false; // one record per line, so a record may not contain one

  if (!storeLock())
    return false;

  bool ok = false;
  File f = SPIFFS.open(path, FILE_APPEND);
  if (f)
  {
    ok = f.print(json) == json.length();
    f.print('\n');
    f.close();
  }
  else
  {
    Serial.printf("[Store] could not open %s for append\n", path);
  }

  if (ok)
    storeTrimLocked(path);
  storeUnlock();
  return ok;
}

// Walk the records newest first. visit() returning false stops the walk.
void storeWalkNewest(const char *path, std::function<bool(const String &)> visit)
{
  if (!storeLock())
    return;

  File f = SPIFFS.open(path, FILE_READ);
  if (!f)
  {
    storeUnlock();
    return;
  }

  // Remember where the newest records start, in a ring so that a long file
  // leaves us holding the end of it rather than the beginning.
  static uint32_t ring[STORE_INDEX_SIZE];
  int seen = 0;
  while (f.available())
  {
    uint32_t at = f.position();
    String line = f.readStringUntil('\n');
    if (!line.length())
      break;
    ring[seen % STORE_INDEX_SIZE] = at;
    seen++;
  }

  int reachable = seen < STORE_INDEX_SIZE ? seen : STORE_INDEX_SIZE;
  for (int i = 0; i < reachable; i++)
  {
    f.seek(ring[(seen - 1 - i) % STORE_INDEX_SIZE]);
    String line = f.readStringUntil('\n');
    line.trim();
    if (line.length() && !visit(line))
      break;
  }

  f.close();
  storeUnlock();
}

// The newest stored copy of one resource, or "" when this unit has no record of it.
String storeFindById(const char *path, const String &id)
{
  String found;
  if (id.isEmpty())
    return found;

  storeWalkNewest(path, [&](const String &line) {
    StaticJsonDocument<STORE_MAX_LINE> doc;
    if (deserializeJson(doc, line))
      return true; // unreadable line, keep looking
    if (String(doc["id"] | "") == id)
    {
      found = line;
      return false;
    }
    return true;
  });
  return found;
}

void logDispense(const String &json)
{
  storeAppend(DISPENSE_STORE, json);
}

void logOrder(const String &json)
{
  storeAppend(ORDER_STORE, json);
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
    return {false, 400, outcomeJson("error", "invalid", String("The body is not readable JSON: ") + error.c_str()),
            "application/fhir+json"};
  }

  if (strcmp(doc["resourceType"] | "", "MedicationRequest") != 0)
  {
    Serial.println("Invalid resource type. Expected 'MedicationRequest'");
    return {false, 400, outcomeJson("error", "invalid", "This endpoint takes a MedicationRequest"),
            "application/fhir+json"};
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
    return {false, 400,
            outcomeJson("error", "invalid",
                        "An order needs status active or on-hold, intent instance-order, and a subject"),
            "application/fhir+json"};
  }

  if (medicationCode == "chocolate-dark")
  {
    if (inventoryDark > 0)
    {
      inventoryDark--;
      saveInventory();
      setLEDColor(128, 0, 0); // red
      dispenseServo(settings.servoDark);
      String response = createMedicationDispense(id, medicationCode, patientReference);
      setLEDColor(0, 0, 0);
      logDispense(response);
      return {true, 200, response, "application/fhir+json"};
    }
    else
    {
      String response = createDeclinedDispense(id, medicationCode, medicationDisplay, patientReference);
      logDispense(response);
      return {true, 201, response, "application/fhir+json"};
    }
  }
  else if (medicationCode == "chocolate-milk")
  {
    if (inventoryMilk > 0)
    {
      inventoryMilk--;
      saveInventory();
      setLEDColor(0, 0, 200); // blue
      dispenseServo(settings.servoMilk);
      String response = createMedicationDispense(id, medicationCode, patientReference);
      setLEDColor(0, 0, 0);
      logDispense(response);
      return {true, 200, response, "application/fhir+json"};
    }
    else
    {
      String response = createDeclinedDispense(id, medicationCode, medicationDisplay, patientReference);
      logDispense(response);
      return {true, 201, response, "application/fhir+json"};
    }
  }
  else
  {
    return {false, 400,
            outcomeJson("error", "code-invalid",
                        "This unit dispenses " MEDS_SYSTEM " chocolate-dark and chocolate-milk only"),
            "application/fhir+json"};
  }
}

// --- The device's own server role ---

// A server assigns ids; a client is not required to supply one. Random rather
// than sequential so two units never hand out the same id.
String newResourceId(const char *prefix)
{
  char buf[32];
  snprintf(buf, sizeof(buf), "%s-%08x%04x", prefix, (unsigned int)esp_random(),
           (unsigned int)(esp_random() & 0xFFFF));
  return String(buf);
}

// POST /MedicationRequest - a FHIR create that also dispenses, because posting
// an order straight at this unit is itself the decision to fill it.
//
// It behaves like a create: the id is ours to assign when the client does not
// send one, the answer is 201 with a Location, and the created resource is
// kept so it can be read back. What came out of the machine is a separate
// resource, reachable at /MedicationDispense/{id}-dispense, or in one call
// through POST /$dispense.
void handleOrderCreate(const String &body, AsyncWebServerRequest *request)
{
  DynamicJsonDocument doc(2048);
  DeserializationError error = deserializeJson(doc, body);

  if (error)
  {
    sendOutcome(request, 400, "invalid", String("The body is not readable JSON: ") + error.c_str());
    return;
  }
  if (strcmp(doc["resourceType"] | "", "MedicationRequest") != 0)
  {
    sendOutcome(request, 400, "invalid", "POST /MedicationRequest takes a MedicationRequest");
    return;
  }

  String id = doc["id"] | "";
  if (id.isEmpty())
  {
    id = newResourceId("mr");
    doc["id"] = id;
  }

  String at = nowIso();
  if (at.length())
    doc["meta"]["lastUpdated"] = at;

  String order;
  serializeJson(doc, order);

  DispenseResult result = processDispenseRequest(order);

  if (result.httpStatus == 400)
  {
    // Nothing was created, so say why and keep no record of it
    request->send(400, result.contentType, result.responseBody);
    return;
  }

  // Keep the order, with the status the work left it in. Without a Task
  // coordinating anything, a filled order is finished.
  if (result.httpStatus == 200)
    doc["status"] = "completed";
  String stored;
  serializeJson(doc, stored);
  logOrder(stored);

  String base = "http://" + request->host();
  String prefer = request->hasHeader("Prefer") ? request->header("Prefer") : String("");
  prefer.toLowerCase();

  String payload;
  String type = "application/fhir+json";
  if (prefer.indexOf("return=minimal") >= 0)
  {
    payload = "";
    type = "";
  }
  else if (prefer.indexOf("return=operationoutcome") >= 0)
  {
    payload = outcomeJson(result.httpStatus == 200 ? "information" : "warning",
                          result.httpStatus == 200 ? "informational" : "business-rule",
                          result.httpStatus == 200
                              ? "Dispensed. The dispense is MedicationDispense/" + id + "-dispense"
                              : "Created, but not dispensed: that lane is empty. See MedicationDispense/" + id + "-declined");
  }
  else
  {
    payload = stored;
  }

  AsyncWebServerResponse *response = payload.length()
                                         ? request->beginResponse(201, type, payload)
                                         : request->beginResponse(201);
  response->addHeader("Location", base + "/MedicationRequest/" + id);
  response->addHeader("ETag", "W/\"1\"");
  if (at.length())
    response->addHeader("Last-Modified", at);
  request->send(response);
}

// POST /$dispense - the one-call path. An operation may answer with whatever
// resource makes sense, so this one answers with the MedicationDispense, which
// is what a caller standing at the machine actually wants to see.
void handleDispenseOperation(const String &body, AsyncWebServerRequest *request)
{
  DynamicJsonDocument doc(2048);
  DeserializationError error = deserializeJson(doc, body);

  if (error)
  {
    sendOutcome(request, 400, "invalid", String("The body is not readable JSON: ") + error.c_str());
    return;
  }

  // Accept a bare MedicationRequest, or Parameters with the order inside it
  JsonVariant order = doc.as<JsonVariant>();
  if (strcmp(doc["resourceType"] | "", "Parameters") == 0)
  {
    for (JsonObject p : doc["parameter"].as<JsonArray>())
      if (p["resource"])
        order = p["resource"];
  }

  if (strcmp(order["resourceType"] | "", "MedicationRequest") != 0)
  {
    sendOutcome(request, 400, "invalid", "$dispense takes a MedicationRequest, or Parameters carrying one");
    return;
  }

  String id = order["id"] | "";
  if (id.isEmpty())
  {
    id = newResourceId("mr");
    order["id"] = id;
  }

  String payload;
  serializeJson(order, payload);
  DispenseResult result = processDispenseRequest(payload);

  if (result.httpStatus != 400)
  {
    if (result.httpStatus == 200)
      order["status"] = "completed";
    String stored;
    serializeJson(order, stored);
    logOrder(stored);
  }

  // An operation reports its own outcome in the resource it returns, so a
  // refusal to dispense is still a 200 with a declined MedicationDispense.
  request->send(result.httpStatus == 400 ? 400 : 200, result.contentType, result.responseBody);
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
    queueWrite("POST", url, dispenseJson, "");
  }

  http.end();
  return httpCode;
}

// Declared here, defined once sendResource is available further down.
int sendResource(const char *method, const String &url, const String &body, const String &ifMatch = "");

void retryPendingWrites()
{
  if (retryCount == 0 || orderServerUrl.isEmpty())
    return;

  int remaining = 0;
  for (int i = 0; i < retryCount; i++)
  {
    PendingWrite &w = retryQueue[i];
    int status = sendResource(w.method.c_str(), w.url, w.body, w.ifMatch);

    // A version conflict means somebody else moved the resource on. Our write
    // is still the newer truth about what the machine did, so try once more
    // without the precondition rather than hold it forever.
    if ((status == 409 || status == 412) && w.ifMatch.length())
    {
      w.ifMatch = "";
      status = sendResource(w.method.c_str(), w.url, w.body, "");
    }

    if (status >= 200 && status < 300)
    {
      Serial.printf("[Orders] queued %s to %s landed\n", w.method.c_str(), w.url.c_str());
    }
    else
    {
      if (remaining != i)
        retryQueue[remaining] = retryQueue[i];
      remaining++;
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
  char severity[12];       // OperationOutcome.issue.severity for the message: information, warning or error
};

OrderCheck orderCheck = {false, false, 0, 0, 0, 0, "", "information"};
volatile bool checkRequested = false; // set by /checkOrders, serviced from loop()
unsigned long lastPollAttempt = 0;

void setOrderMessage(const String &text, const char *severity = "error")
{
  strlcpy(orderCheck.message, text.c_str(), sizeof(orderCheck.message));
  strlcpy(orderCheck.severity, severity, sizeof(orderCheck.severity));
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

int sendResource(const char *method, const String &url, const String &body, const String &ifMatch)
{
  WiFiClientSecure secureClient;
  WiFiClient plainClient;
  HTTPClient http;

  if (!beginHttp(http, secureClient, plainClient, url))
    return -1;

  http.addHeader("Content-Type", "application/fhir+json");
  http.addHeader("Accept", "application/fhir+json");
  // An update based on a version we read should not silently overwrite a newer
  // one, so say which version we saw.
  if (ifMatch.length())
    http.addHeader("If-Match", "W/\"" + ifMatch + "\"");
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
    String version = task["meta"]["versionId"] | "";
    String body;
    serializeJson(task, body);
    String url = base + "/Task/" + taskId;
    status = sendResource("PUT", url, body, version);
    Serial.printf("PUT Task/%s -> %d\n", taskId.c_str(), status);

    if ((status == 409 || status == 412) && version.length())
      status = sendResource("PUT", url, body, "");

    if (status < 200 || status >= 300)
      queueWrite("PUT", url, body, "");
  }
  else if (!failed)
  {
    request["status"] = "completed";
    String version = request["meta"]["versionId"] | "";
    String body;
    serializeJson(request, body);
    String url = base + "/MedicationRequest/" + requestId;
    status = sendResource("PUT", url, body, version);
    Serial.printf("PUT MedicationRequest/%s -> %d\n", requestId.c_str(), status);

    if ((status == 409 || status == 412) && version.length())
      status = sendResource("PUT", url, body, "");

    if (status < 200 || status >= 300)
      queueWrite("PUT", url, body, "");
  }
  else
  {
    return "";
  }

  if (status >= 200 && status < 300)
    return "";

  return "Server refused the update (HTTP " + String(status) + "), queued for retry";
}

// A tag and a Task are two ways of saying the same thing - this order may be
// acted on - not two modes of operation. This unit accepts both by default;
// settings.orderMode narrows that to one of them when a demo needs it.
bool acceptsTagged() { return settings.orderMode != "task"; }
bool acceptsTasks() { return settings.orderMode != "tag"; }

String acceptedLanes()
{
  if (settings.orderMode == "tag")
    return "tagged orders";
  if (settings.orderMode == "task")
    return "tasks";
  return "tagged orders and tasks";
}

// Remember an order so later polls skip it. Handling a Task also stands in for
// the request it points at, so the tag lane will not dispense the same order a
// second time.
void rememberHandled(const String &orderId, bool taskLane, const String &requestId)
{
  markHandled(orderId);
  if (taskLane && requestId.length())
    markHandled("MedicationRequest/" + requestId);
}

// One lane of a check: either the search for MedicationRequests the placer
// tagged actionable, or the search for Tasks asking for an order to be
// fulfilled. Adds to the shared counters, appends anything worth reporting to
// "problem", and returns false when the search itself did not come back.
// How many pages of one search this unit will walk in a single check. A search
// is capped by _count, and without following the Bundle's next link a backlog
// longer than one page would never be reached.
const int MAX_SEARCH_PAGES = 5;

bool runOrderPage(const String &base, bool taskLane, String &problem, const String &pageUrl,
                  int page, String &nextUrl)
{
  String url = pageUrl;
  if (url.isEmpty())
  {
    url = base + (taskLane ? "/Task" : "/MedicationRequest");
    String query = taskLane ? settings.taskQuery : settings.orderQuery;
    if (!taskLane)
    {
      // Only orders the placer marked as actionable
      String tag = "_tag=" ACTIONABLE_SYSTEM "%7C" ACTIONABLE_CODE;
      query = query.length() ? tag + "&" + query : tag;
    }
    if (query.length())
      url += "?" + query;
  }

  Serial.printf("[Orders] GET (page %d) ", page);
  Serial.println(url);

  WiFiClientSecure secureClient;
  WiFiClient plainClient;
  HTTPClient http;

  if (!beginHttp(http, secureClient, plainClient, url))
  {
    problem = "Could not open " + url;
    return false;
  }

  http.addHeader("Accept", "application/fhir+json");
  http.setTimeout(8000);
  int status = http.GET();

  // A failure in either lane is what the status ends up reporting
  if (orderCheck.httpStatus == 0 || orderCheck.httpStatus == 200)
    orderCheck.httpStatus = status;

  if (status != 200)
  {
    http.end();
    problem = String(taskLane ? "Task" : "Order") + " search failed (HTTP " + String(status) + ")";
    return false;
  }

  // getString(), never getStream(): a FHIR server is free to answer with
  // Transfer-Encoding: chunked (fhir-candle behind Caddy always does), and
  // HTTPClient only unwraps the chunk framing on the writeToStream() path that
  // getString() uses. getStream() hands back the raw socket, so ArduinoJson
  // reads the hex chunk-size line as if it were the Bundle and fails with
  // InvalidInput. Keep _count small and this stays a couple of KB.
  String payload = http.getString();
  http.end();

  DynamicJsonDocument doc(ORDER_DOC_SIZE);
  DeserializationError error = deserializeJson(doc, payload);

  if (error)
  {
    problem = String("Could not read the Bundle: ") + error.c_str() +
              " (" + String(payload.length()) + " bytes)";
    return false;
  }

  JsonArray entries = doc["entry"].as<JsonArray>();
  if (entries.isNull())
    return true; // nothing waiting in this lane

  for (JsonObject entry : entries)
  {
    JsonObject resource = entry["resource"];
    if (resource.isNull())
      continue;

    String type = resource["resourceType"] | "";
    JsonObject task;
    JsonObject request;
    String orderId;

    if (taskLane)
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

    // An order that carries the tag AND has a Task pointing at it turns up in
    // both lanes. The Task lane runs first and remembers the request as well as
    // the Task, so the tag lane skips it below. The reverse guard covers an
    // order dispensed on an earlier poll that only later gained a Task: the
    // work is already done, so the Task is left alone rather than repeated.
    if (alreadyHandled(orderId) ||
        (taskLane && alreadyHandled("MedicationRequest/" + String(request["id"] | ""))))
      continue;

    orderCheck.found++;

    String orderBody;
    serializeJson(request, orderBody);
    DispenseResult result = processDispenseRequest(orderBody);
    String requestId = request["id"] | "";

    if (result.httpStatus == 200) // dispensed
    {
      orderCheck.dispensed++;
      rememberHandled(orderId, taskLane, requestId);

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
        rememberHandled(orderId, taskLane, requestId);
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

  // Hand the caller the server's next link, if it offered one.
  for (JsonObject link : doc["link"].as<JsonArray>())
    if (String(link["relation"] | "") == "next")
      nextUrl = String(link["url"] | "");

  return true;
}

// One lane of a check, across as many pages as the server offers up to the cap.
// Each page is fetched, processed and freed before the next one, so a backlog
// costs time rather than memory.
bool runOrderLane(const String &base, bool taskLane, String &problem)
{
  String url = "";
  for (int page = 1; page <= MAX_SEARCH_PAGES; page++)
  {
    String next;
    if (!runOrderPage(base, taskLane, problem, url, page, next))
      return false;
    if (next.isEmpty())
      return true;
    url = next;
    if (page == MAX_SEARCH_PAGES)
      Serial.println("[Orders] stopping at the page cap; the rest waits for the next check");
  }
  return true;
}

void checkOrders()
{
  orderCheck.busy = true;
  orderCheck.everRan = true;
  orderCheck.found = 0;
  orderCheck.dispensed = 0;
  orderCheck.httpStatus = 0;

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

  // Both lanes run on every check unless the settings narrow it down. The Task
  // lane goes first: when an order is both tagged and pointed at by a Task, the
  // Task is the stronger statement - it names a filler and expects the dispense
  // back in Task.output - so that is the route taken, and the order is
  // dispensed once.
  String problem;
  bool searchFailed = false;

  if (acceptsTasks())
    searchFailed = !runOrderLane(base, true, problem);

  if (acceptsTagged())
  {
    String tagProblem;
    if (!runOrderLane(base, false, tagProblem))
      searchFailed = true;
    if (tagProblem.length())
      problem = problem.length() ? problem + "; " + tagProblem : tagProblem;
  }

  if (problem.length())
    setOrderMessage(problem, searchFailed ? "error" : "warning");
  else if (orderCheck.found == 0)
    setOrderMessage("No new orders", "information");
  else
    setOrderMessage("Dispensed " + String(orderCheck.dispensed) + " of " + String(orderCheck.found), "information");

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

String jsonString(const JsonDocument &doc)
{
  String out;
  serializeJson(doc, out);
  return out;
}

// The last check of the order server as an OperationOutcome. It rides along in
// the /MedicationDispense searchset with search.mode "outcome", which is where
// FHIR puts "here is why the list looks the way it does".
String checkOutcomeJson()
{
  StaticJsonDocument<1024> doc;
  doc["resourceType"] = "OperationOutcome";
  JsonArray issues = doc.createNestedArray("issue");

  if (orderCheck.busy || checkRequested)
  {
    JsonObject busy = issues.createNestedObject();
    busy["severity"] = "information";
    busy["code"] = "informational";
    busy["diagnostics"] = "A check of the order server is in progress";
  }

  JsonObject issue = issues.createNestedObject();
  if (!orderCheck.everRan)
  {
    issue["severity"] = "information";
    issue["code"] = "informational";
    issue["diagnostics"] = "This unit has not checked the order server yet";
    return jsonString(doc);
  }

  const char *severity = orderCheck.severity;
  issue["severity"] = severity;
  issue["code"] = (strcmp(severity, "error") == 0)     ? "exception"
                  : (strcmp(severity, "warning") == 0) ? "processing"
                                                       : "informational";
  issue["diagnostics"] = orderCheck.message;
  issue["details"]["text"] =
      "Last check of " + orderServerUrl + " (accepting " + acceptedLanes() + ") " +
      String((millis() - orderCheck.lastCheck) / 1000) + " s ago: search HTTP " +
      String(orderCheck.httpStatus) + ", " + String(orderCheck.found) + " new, " +
      String(orderCheck.dispensed) + " dispensed";

  return jsonString(doc);
}

// A searchset over one of the stores. The entries are already JSON, so the
// Bundle is assembled as text rather than parsed into a document and back.
//
// Supported parameters are the ones a client actually needs to ask this device
// a question, and they are declared in the CapabilityStatement: _id, status,
// subject, _count, and for dispenses authorizingPrescription. Anything else is
// ignored rather than refused, which is what FHIR asks of a server, and the
// self link records what was understood.

struct SearchQuery
{
  String id;
  String status;
  String subject;
  String prescription;
  int count;
};

SearchQuery readSearchQuery(AsyncWebServerRequest *request)
{
  SearchQuery q;
  q.count = 20;

  if (request->hasParam("_id"))
    q.id = request->getParam("_id")->value();
  if (request->hasParam("status"))
    q.status = request->getParam("status")->value();
  if (request->hasParam("subject"))
    q.subject = request->getParam("subject")->value();
  if (request->hasParam("patient"))
    q.subject = request->getParam("patient")->value();
  if (request->hasParam("authorizingPrescription"))
    q.prescription = request->getParam("authorizingPrescription")->value();
  if (request->hasParam("prescription"))
    q.prescription = request->getParam("prescription")->value();
  if (request->hasParam("_count"))
    q.count = constrain(request->getParam("_count")->value().toInt(), 0, 50);

  return q;
}

// A reference matches either in full or by its id alone, so both
// subject=Patient/123 and subject=123 find the same records.
bool referenceMatches(const String &wanted, const String &actual)
{
  if (wanted.isEmpty())
    return true;
  if (actual == wanted)
    return true;
  int slash = actual.lastIndexOf('/');
  return slash >= 0 && actual.substring(slash + 1) == wanted;
}

String searchBundleJson(const char *path, const char *resourceType,
                        const String &base, const SearchQuery &q,
                        const String &selfQuery, bool withCheckOutcome)
{
  String entries;
  String handled = "|"; // ids already emitted, so an updated record appears once
  int matched = 0;

  storeWalkNewest(path, [&](const String &line) {
    StaticJsonDocument<STORE_MAX_LINE> doc;
    if (deserializeJson(doc, line))
      return true;

    String id = doc["id"] | "";
    if (id.isEmpty() || handled.indexOf("|" + id + "|") >= 0)
      return true;
    handled += id + "|"; // not listAdd: that caps its list, and a search must
                         // not start emitting duplicates once it passes the cap

    if (!q.id.isEmpty() && q.id != id)
      return true;
    if (!q.status.isEmpty() && String(doc["status"] | "") != q.status)
      return true;
    if (!referenceMatches(q.subject, String(doc["subject"]["reference"] | "")))
      return true;
    if (!q.prescription.isEmpty() &&
        !referenceMatches(q.prescription, String(doc["authorizingPrescription"][0]["reference"] | "")))
      return true;

    matched++;
    if (matched > q.count)
      return false;

    entries += "{\"fullUrl\":\"" + base + "/" + resourceType + "/" + id + "\",\"resource\":";
    entries += line;
    entries += ",\"search\":{\"mode\":\"match\"}},";
    return true;
  });

  int total = matched > q.count ? q.count : matched;

  String out;
  out.reserve(entries.length() + 1024);
  out += "{\"resourceType\":\"Bundle\",\"type\":\"searchset\",\"total\":" + String(total);
  String stamp = nowIso();
  if (stamp.length())
    out += ",\"timestamp\":\"" + stamp + "\"";
  out += ",\"link\":[{\"relation\":\"self\",\"url\":\"" + base + "/" + resourceType +
         (selfQuery.length() ? "?" + selfQuery : "") + "\"}],\"entry\":[";
  out += entries;

  if (withCheckOutcome)
    out += "{\"resource\":" + checkOutcomeJson() + ",\"search\":{\"mode\":\"outcome\"}},";

  if (out.endsWith(","))
    out.remove(out.length() - 1);
  out += "]}";
  return out;
}

// The query string as this unit understood it, for the Bundle's self link.
String selfQueryOf(AsyncWebServerRequest *request, const SearchQuery &q)
{
  String self;
  if (q.id.length())
    self += "_id=" + q.id + "&";
  if (q.status.length())
    self += "status=" + q.status + "&";
  if (q.subject.length())
    self += "subject=" + q.subject + "&";
  if (q.prescription.length())
    self += "authorizingPrescription=" + q.prescription + "&";
  self += "_count=" + String(q.count);
  return self;
}

// ==================== Over-the-air updates ====================
// The firmware and the web files are both replaceable over Wi-Fi. The chip
// keeps two application slots, so an upload is written to the one that is not
// running and the unit reboots into it; the filesystem has its own partition
// and the same mechanism. A single page can also be replaced on its own, which
// is how the dashboard is iterated on without rebuilding anything.
//
// Everything here needs the unit's key. An update endpoint without one is a
// standing invitation to run code on somebody else's dispenser.

struct OtaState
{
  bool active;
  bool fileMode;
  String filePath;
  File file;
  size_t expected;
  String error;
};

OtaState ota = {false, false, "", File(), 0, ""};
unsigned long restartAt = 0;          // loop() restarts the unit when this passes
volatile bool updateCheckRequested = false;
volatile bool updateInstallRequested = false;
unsigned long lastUpdateCheck = 0;
String lastUpdateResult = "never checked";

// What the last check found waiting, if anything. Kept so that looking and
// taking are two separate decisions, and persisted so that the notice does not
// quietly disappear when the unit is power cycled: an update that was waiting
// before the plug came out is still waiting afterwards.
String availableVersion;
String availableFirmwareUrl;
String availableFilesystemUrl;
String availableNotes;    // what changed, short enough to read on a phone
String availableNotesUrl; // the whole thing, for anyone who wants it
String availableReleased; // when it was published
long availableBytes = 0;  // what installing it will pull down

// Keep the notes small: they are held in RAM, persisted to NVS and served in
// every /ota/status. Anything longer belongs behind availableNotesUrl.
const size_t NOTES_MAX = 600;

void loadUpdateState()
{
  prefs.begin("spenser", true);
  availableVersion = prefs.getString("availVer", "");
  availableFirmwareUrl = prefs.getString("availFw", "");
  availableFilesystemUrl = prefs.getString("availFs", "");
  availableNotes = prefs.getString("availNotes", "");
  availableNotesUrl = prefs.getString("availNoteU", "");
  availableReleased = prefs.getString("availWhen", "");
  availableBytes = prefs.getLong("availSize", 0);
  prefs.end();

  if (availableVersion.length())
  {
    if (availableVersion == FIRMWARE_VERSION)
    {
      // We are now running what was offered, so there is nothing to announce
      availableVersion = "";
      availableFirmwareUrl = "";
      availableFilesystemUrl = "";
      availableNotes = "";
      availableNotesUrl = "";
      availableReleased = "";
      availableBytes = 0;
      prefs.begin("spenser", false);
      prefs.remove("availVer");
      prefs.remove("availFw");
      prefs.remove("availFs");
      prefs.remove("availNotes");
      prefs.remove("availNoteU");
      prefs.end();
    }
    else
    {
      lastUpdateResult = availableVersion + " is available, this unit runs " FIRMWARE_VERSION;
      Serial.println("[OTA] still waiting: " + lastUpdateResult);
    }
  }
}

void saveUpdateState()
{
  prefs.begin("spenser", false);
  if (availableVersion.length())
  {
    prefs.putString("availVer", availableVersion);
    prefs.putString("availFw", availableFirmwareUrl);
    prefs.putString("availFs", availableFilesystemUrl);
    prefs.putString("availNotes", availableNotes);
    prefs.putString("availNoteU", availableNotesUrl);
    prefs.putString("availWhen", availableReleased);
    prefs.putLong("availSize", availableBytes);
  }
  else
  {
    prefs.remove("availVer");
    prefs.remove("availFw");
    prefs.remove("availFs");
    prefs.remove("availNotes");
    prefs.remove("availNoteU");
    prefs.remove("availWhen");
    prefs.remove("availSize");
  }
  prefs.end();
}
bool appMarkedValid = false;

void scheduleRestart(unsigned long inMs)
{
  restartAt = millis() + inMs;
}

// Once a new build has proved it can boot, reach the network and answer, the
// slot it came from is worth keeping. Until then the previous slot stays as
// the way back.
void markRunningAppValid()
{
  if (appMarkedValid)
    return;
  appMarkedValid = true;
  esp_err_t err = esp_ota_mark_app_valid_cancel_rollback();
  Serial.printf("[OTA] running image marked valid (%s)\n", esp_err_to_name(err));
}

String otaStatusJson()
{
  DynamicJsonDocument doc(1536);
  doc["firmwareVersion"] = FIRMWARE_VERSION;
  doc["build"] = FIRMWARE_BUILD;

  const esp_partition_t *running = esp_ota_get_running_partition();
  if (running)
  {
    doc["runningSlot"] = running->label;
    doc["slotBytes"] = running->size;
  }
  doc["canRollback"] = Update.canRollBack();
  doc["markedValid"] = appMarkedValid; // false until this image has proved itself
  doc["uptimeSeconds"] = (millis() - bootMillis) / 1000;
  doc["sketchBytes"] = ESP.getSketchSize();
  doc["updateUrl"] = settings.updateUrl;
  doc["updateCheckMinutes"] = settings.updateCheckMinutes;
  doc["updateMode"] = settings.updateMode;
  doc["updateAvailable"] = availableVersion.length() > 0;
  if (availableVersion.length())
  {
    doc["availableVersion"] = availableVersion;
    doc["availableFirmwareUrl"] = availableFirmwareUrl;
    doc["availableNotes"] = availableNotes;
    doc["availableNotesUrl"] = availableNotesUrl;
    doc["availableReleased"] = availableReleased;
    doc["availableBytes"] = availableBytes;
  }
  doc["lastCheckSecondsAgo"] = lastUpdateCheck ? (int)((millis() - lastUpdateCheck) / 1000) : -1;

  // When it will look again, so an absent notice reads as "has not looked yet"
  // rather than "looked and found nothing".
  int nextIn = -1;
  if (settings.updateCheckMinutes > 0 && settings.updateUrl.length())
  {
    unsigned long period = (unsigned long)settings.updateCheckMinutes * 60UL * 1000UL;
    unsigned long since = millis() - lastUpdateCheck;
    nextIn = lastUpdateCheck == 0 ? 0 : (since >= period ? 0 : (int)((period - since) / 1000));
  }
  doc["nextCheckSeconds"] = nextIn;
  doc["lastResult"] = lastUpdateResult;
  doc["clock"] = clockReady() ? nowIso() : "unset";

  String out;
  serializeJson(doc, out);
  return out;
}

// A unit can fetch its own updates from a manifest that a release workflow
// publishes beside the binaries:
//   { "version": "1.2.0",
//     "firmware": "https://.../firmware.bin",
//     "filesystem": "https://.../spiffs.bin" }
//
// Looking and taking are deliberately separate. A check reports what is
// waiting and stops there, because a dispenser that reboots itself in the
// middle of somebody's afternoon is not a well behaved appliance. Set
// updateMode=install for a unit you would rather not visit at all.

bool fetchManifest(String &version, String &firmwareUrl, String &filesystemUrl,
                   String &notes, String &notesUrl, String &released, long &bytes)
{
  if (settings.updateUrl.isEmpty())
  {
    lastUpdateResult = "no manifest URL configured";
    return false;
  }
  if (WiFi.status() != WL_CONNECTED)
  {
    lastUpdateResult = "no network";
    return false;
  }

  WiFiClientSecure secureClient;
  WiFiClient plainClient;
  HTTPClient http;

  if (!beginHttp(http, secureClient, plainClient, settings.updateUrl))
  {
    lastUpdateResult = "could not open the manifest URL";
    return false;
  }

  http.addHeader("Accept", "application/json");
  http.setTimeout(8000);
  // A release asset is served from a redirect, so both the manifest and the
  // binaries below have to be followed rather than reported as a 302.
  http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
  int status = http.GET();

  if (status != 200)
  {
    http.end();
    lastUpdateResult = "manifest HTTP " + String(status);
    Serial.println("[OTA] " + lastUpdateResult);
    return false;
  }

  String payload = http.getString();
  http.end();

  DynamicJsonDocument manifest(2048);
  if (deserializeJson(manifest, payload))
  {
    lastUpdateResult = "manifest is not readable JSON";
    return false;
  }

  version = String(manifest["version"] | "");
  firmwareUrl = String(manifest["firmware"] | "");
  filesystemUrl = String(manifest["filesystem"] | "");
  notes = String(manifest["notes"] | "");
  notesUrl = String(manifest["notesUrl"] | "");
  released = String(manifest["released"] | "");
  // What pressing Install will actually pull over the air
  bytes = (long)(manifest["firmwareBytes"] | 0) + (long)(manifest["filesystemBytes"] | 0);
  if (notes.length() > NOTES_MAX)
    notes = notes.substring(0, NOTES_MAX) + "...";

  if (version.isEmpty())
  {
    lastUpdateResult = "manifest has no version";
    return false;
  }
  return true;
}

// Look only. Records what is waiting, and installs it only when this unit has
// been told to do that for itself.
void runUpdateCheck()
{
  String version, firmwareUrl, filesystemUrl, notes, notesUrl, released;
  long bytes = 0;
  if (!fetchManifest(version, firmwareUrl, filesystemUrl, notes, notesUrl, released, bytes))
  {
    Serial.println("[OTA] " + lastUpdateResult);
    return;
  }

  if (version == FIRMWARE_VERSION)
  {
    availableVersion = "";
    availableFirmwareUrl = "";
    availableFilesystemUrl = "";
    availableNotes = "";
    availableNotesUrl = "";
    availableReleased = "";
    availableBytes = 0;
    saveUpdateState();
    lastUpdateResult = "up to date at " + version;
    Serial.println("[OTA] " + lastUpdateResult);
    return;
  }

  availableVersion = version;
  availableFirmwareUrl = firmwareUrl;
  availableFilesystemUrl = filesystemUrl;
  availableNotes = notes;
  availableNotesUrl = notesUrl;
  availableReleased = released;
  availableBytes = bytes;
  saveUpdateState();
  lastUpdateResult = version + " is available, this unit runs " FIRMWARE_VERSION;
  Serial.println("[OTA] " + lastUpdateResult);

  if (settings.updateMode == "install")
  {
    Serial.println("[OTA] updateMode=install, taking it now");
    updateInstallRequested = true;
  }
}

// Take what the last check found. The filesystem goes first: a new dashboard
// served by old firmware is a smaller problem than new firmware looking for
// files that are not there.
void runUpdateInstall()
{
  if (availableVersion.isEmpty())
  {
    // Nothing known yet, so look before refusing: /ota/install on a unit that
    // has never checked should still do the obvious thing.
    String version, firmwareUrl, filesystemUrl, notes, notesUrl, released;
    long bytes = 0;
    if (!fetchManifest(version, firmwareUrl, filesystemUrl, notes, notesUrl, released, bytes))
    {
      Serial.println("[OTA] " + lastUpdateResult);
      return;
    }
    if (version == FIRMWARE_VERSION)
    {
      lastUpdateResult = "up to date at " + version + ", nothing to install";
      Serial.println("[OTA] " + lastUpdateResult);
      return;
    }
    availableVersion = version;
    availableFirmwareUrl = firmwareUrl;
    availableFilesystemUrl = filesystemUrl;
    availableNotes = notes;
    availableNotesUrl = notesUrl;
    availableReleased = released;
    availableBytes = bytes;
    saveUpdateState();
  }

  String version = availableVersion;
  Serial.println("[OTA] installing " + version);

  httpUpdate.rebootOnUpdate(false);
  httpUpdate.setLedPin(-1, LOW);
  httpUpdate.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);

  if (availableFilesystemUrl.length())
  {
    WiFiClientSecure fsSecure;
    WiFiClient fsPlain;
    WiFiClient &client = availableFilesystemUrl.startsWith("https://")
                             ? (fsSecure.setInsecure(), (WiFiClient &)fsSecure)
                             : (WiFiClient &)fsPlain;
    SPIFFS.end();
    t_httpUpdate_return r = httpUpdate.updateSpiffs(client, availableFilesystemUrl);
    if (r == HTTP_UPDATE_FAILED)
    {
      lastUpdateResult = "filesystem update failed: " + httpUpdate.getLastErrorString();
      Serial.println("[OTA] " + lastUpdateResult);
      SPIFFS.begin(true);
      return;
    }
    Serial.println("[OTA] filesystem updated");
  }

  if (availableFirmwareUrl.length())
  {
    WiFiClientSecure fwSecure;
    WiFiClient fwPlain;
    WiFiClient &client = availableFirmwareUrl.startsWith("https://")
                             ? (fwSecure.setInsecure(), (WiFiClient &)fwSecure)
                             : (WiFiClient &)fwPlain;
    t_httpUpdate_return r = httpUpdate.update(client, availableFirmwareUrl);
    if (r == HTTP_UPDATE_FAILED)
    {
      lastUpdateResult = "firmware update failed: " + httpUpdate.getLastErrorString();
      Serial.println("[OTA] " + lastUpdateResult);
      return;
    }
  }

  lastUpdateResult = "updated to " + version + ", restarting";
  Serial.println("[OTA] " + lastUpdateResult);
  scheduleRestart(500);
}

// --- Setup ---

void setup()
{
  Serial.begin(115200);
  delay(500);
  bootMillis = millis();
  Serial.println("Setup starting");
  Serial.println("Spenser firmware " FIRMWARE_VERSION " (" FIRMWARE_BUILD ")");

  // The stores are read by the web task while loop() writes them
  storeMutex = xSemaphoreCreateMutex();

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
  loadInventory();
  loadDeviceKey();
  loadUpdateState();

  // The one place the key is always available to whoever can reach the board
  Serial.println("----------------------------------------------------------");
  Serial.println("Device key: " + deviceKey);
  Serial.println("Needed by everything that changes this unit. Also at GET /key");
  Serial.println("for five minutes after this boot, or any time in setup mode.");
  Serial.println("----------------------------------------------------------");

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
    startClock(); // dispense records are worth nothing without a real time
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
    if (!requireKey(req)) return;
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
    if (!requireKey(req)) return;
    setForcePortalFlag();
    req->send(200, "text/html", "<p>Rebooting into Wi-Fi config mode (credentials kept)...</p>");
    delay(500);
    ESP.restart(); });

  server.on("/wifi-reset", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    if (!requireKey(req)) return;
    clearWifiConfig();
    req->send(200, "text/html", "<p>Wi-Fi credentials cleared. Rebooting into AP mode...</p>");
    delay(500);
    ESP.restart(); });

  server.on("/wifi-reboot-config", HTTP_GET, [](AsyncWebServerRequest *req)
            {
    if (!requireKey(req)) return;
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
    if (!requireKey(request)) return;
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
    if (!requireKey(request)) return;
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
    if (!requireKey(request)) return;
    String redValue = request->getParam("red")->value();
    String greenValue = request->getParam("green")->value();
    String blueValue = request->getParam("blue")->value();

    rgb.setPixelColor(0, rgb.Color(redValue.toInt(), greenValue.toInt(), blueValue.toInt()));
    rgb.show();

    request->send(200, "text/plain", "Color updated"); });

  // Servo control
  server.on("/setServos", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
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
    if (!requireKey(request)) return;
    rgb.setPixelColor(0, rgb.Color(0, 0, 0));
    rgb.show();
    AtomicMotion.setServoAngle(settings.servoDark, settings.angleRest);
    AtomicMotion.setServoAngle(settings.servoMilk, settings.angleRest);
    request->send(200, "text/plain", "Sliders and servos reset to rest angle"); });

  server.on("/flashServo1", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    Serial.println("Flashing Servo 1");
    dispenseServo(settings.servoDark);
    request->send(200, "text/plain", "Servo 1 flashed"); });

  server.on("/flashServo2", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
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
    if (!requireKey(request)) return;
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
      // Anything that is not one of the two narrowing values means "accept
      // either", so orderMode=both, =either or an empty value all widen it.
      settings.orderMode = (text == "task") ? "task" : (text == "tag") ? "tag"
                                                                       : "both";
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
    if (paramStr(request, "updateUrl", text)) {
      settings.updateUrl = text;
      updated = true;
    }
    if (paramInt(request, "updateCheckMinutes", value)) {
      settings.updateCheckMinutes = constrain(value, 0, 7 * 24 * 60);
      updated = true;
    }
    // Still accepted, because it is in the published documentation and in
    // whatever anyone has already scripted
    if (paramInt(request, "updateCheckHours", value)) {
      settings.updateCheckMinutes = constrain(value * 60, 0, 7 * 24 * 60);
      updated = true;
    }
    if (paramStr(request, "updateMode", text)) {
      // Anything that is not an explicit "install" means notify, so a typo
      // cannot turn a fleet into one that reboots itself unannounced.
      settings.updateMode = (text == "install") ? "install" : "notify";
      updated = true;
    }

    if (!updated) {
      sendOutcome(request, 400, "invalid", "No setting this unit recognises was in the request");
      return;
    }

    saveSettings();
    Serial.println("Settings saved: " + settingsJson());
    request->send(200, "application/json", settingsJson()); });

  // Wipe the stored settings and fall back to the compiled-in defaults
  server.on("/resetSettings", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    prefs.begin("spenser", false);
    prefs.clear();

    // Two things survive a settings reset, because neither is a setting.
    //
    // The key is this unit's identity. Wiping it locked out whoever was
    // holding it, silently: a new one is generated at the next boot, and
    // everything that writes starts answering 401 for no visible reason.
    //
    // The stock count is a fact about the physical world. Resetting the
    // configuration does not empty the lanes, and a unit that comes back
    // claiming fifteen of each is lying to its order server.
    prefs.putString("deviceKey", deviceKey);
    prefs.putInt("invDark", inventoryDark);
    prefs.putInt("invMilk", inventoryMilk);
    prefs.end();

    settings = DEFAULT_SETTINGS;
    seenIds = "|";
    reportedIds = "|";
    availableVersion = "";
    availableFirmwareUrl = "";
    availableFilesystemUrl = "";
    availableNotes = "";
    availableNotesUrl = "";
    request->send(200, "application/json", settingsJson()); });

  // Ask for a check. The HTTP call itself runs from loop(), so the async web
  // server is never blocked while this unit talks to the order server.
  server.on("/checkOrders", HTTP_GET | HTTP_POST, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    checkRequested = true;
    request->send(202, "application/json", "{\"status\":\"scheduled\"}"); });

  // This unit's key, which everything that changes it needs. Readable only
  // while the unit is in setup mode or in the first few minutes after a
  // restart: whoever just powered it on is its owner, and anybody later is
  // not. It is also printed on the serial console at every boot.
  server.on("/key", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    bool fresh = (millis() - bootMillis) < KEY_REVEAL_WINDOW_MS;
    if (!fresh && netMode != NET_AP && !keyMatches(request)) {
      sendOutcome(request, 403, "forbidden",
                  "The key is only readable in setup mode or within five minutes of a restart. "
                  "Restart this unit, or read it from the serial console.");
      return;
    }

    StaticJsonDocument<192> doc;
    doc["key"] = deviceKey;
    doc["firmwareVersion"] = FIRMWARE_VERSION;
    String out;
    serializeJson(doc, out);
    request->send(200, "application/json", out); });

  // What the last check did, for the device's own dashboard (not FHIR - the
  // FHIR view of the same thing is GET /MedicationDispense below)
  server.on("/orders", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(200, "application/json", orderStatusJson()); });

  // FHIR MedicationDispense: what this unit did, as the resources it produced,
  // from its own store rather than from memory. A search honours _id, status,
  // subject, authorizingPrescription and _count, and the searchset carries an
  // OperationOutcome about the last check of the order server. The same
  // handler serves /MedicationDispense/{id}, which is a plain read.
  server.on("/MedicationDispense", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String base = "http://" + request->host();
    String path = request->url();
    const String prefix = "/MedicationDispense/";

    if (path.startsWith(prefix)) {
      String id = path.substring(prefix.length());
      String found = storeFindById(DISPENSE_STORE, id);
      if (found.length()) {
        request->send(200, "application/fhir+json", found);
        return;
      }
      sendOutcome(request, 404, "not-found", "MedicationDispense/" + id + " is not in this unit's record");
      return;
    }

    SearchQuery q = readSearchQuery(request);
    request->send(200, "application/fhir+json",
                  searchBundleJson(DISPENSE_STORE, "MedicationDispense", base, q,
                                   selfQueryOf(request, q), true)); });

  // FHIR MedicationRequest: the orders this unit accepted. A dispenser that
  // keeps no orders cannot answer for what it did, so a created order is
  // readable afterwards, and searchable by _id, status, subject and _count.
  server.on("/MedicationRequest", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    String base = "http://" + request->host();
    String path = request->url();
    const String prefix = "/MedicationRequest/";

    if (path.startsWith(prefix)) {
      String id = path.substring(prefix.length());
      String found = storeFindById(ORDER_STORE, id);
      if (found.length()) {
        request->send(200, "application/fhir+json", found);
        return;
      }
      sendOutcome(request, 404, "not-found",
                  "MedicationRequest/" + id + " is not in this unit's record. It keeps the orders "
                  "posted to it, not the ones it polled from a server.");
      return;
    }

    SearchQuery q = readSearchQuery(request);
    request->send(200, "application/fhir+json",
                  searchBundleJson(ORDER_STORE, "MedicationRequest", base, q,
                                   selfQueryOf(request, q), false)); });

  // ---- Over-the-air updates ----

  server.on("/ota/status", HTTP_GET, [](AsyncWebServerRequest *request)
            { request->send(200, "application/json", otaStatusJson()); });

  server.on("/ota/rollback", HTTP_POST | HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    if (!Update.canRollBack()) {
      sendOutcome(request, 409, "not-supported", "This unit has no previous image to go back to");
      return;
    }
    if (!Update.rollBack()) {
      sendOutcome(request, 500, "exception", "The rollback was refused");
      return;
    }
    request->send(200, "application/json", "{\"status\":\"rolling back\",\"restarting\":true}");
    scheduleRestart(1200); });

  // Look. Reports what is waiting in /ota/status; installs it only when this
  // unit is set to updateMode=install.
  server.on("/ota/check", HTTP_POST | HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    if (settings.updateUrl.isEmpty()) {
      sendOutcome(request, 400, "required", "Set updateUrl first, e.g. /setSettings?updateUrl=https://.../manifest.json");
      return;
    }
    updateCheckRequested = true;
    request->send(202, "application/json", "{\"status\":\"checking\"}"); });

  // Take. A unit that has never checked looks first, so this does the obvious
  // thing either way.
  server.on("/ota/install", HTTP_POST | HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    if (settings.updateUrl.isEmpty()) {
      sendOutcome(request, 400, "required", "Set updateUrl first, e.g. /setSettings?updateUrl=https://.../manifest.json");
      return;
    }
    if (orderCheck.busy) {
      sendOutcome(request, 409, "lock-error", "This unit is mid-check; try again in a moment");
      return;
    }

    updateInstallRequested = true;
    StaticJsonDocument<192> doc;
    doc["status"] = "installing";
    doc["version"] = availableVersion.length() ? availableVersion : String("whatever the manifest offers");
    String out;
    serializeJson(doc, out);
    request->send(202, "application/json", out); });

  // Whole images: the firmware, or the filesystem that holds the web files.
  // The body is the .bin itself, streamed straight into the spare slot.
  auto receiveImage = [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
  {
    bool filesystem = request->url().endsWith("/filesystem");

    if (index == 0)
    {
      if (!requireKey(request))
        return;
      if (orderCheck.busy)
      {
        sendOutcome(request, 409, "lock-error", "This unit is mid-check; try again in a moment");
        return;
      }
      if (total == 0)
      {
        sendOutcome(request, 400, "invalid", "Send the image as the request body");
        return;
      }

      if (filesystem)
        SPIFFS.end(); // the partition is about to be rewritten underneath it

      if (!Update.begin(total, filesystem ? U_SPIFFS : U_FLASH))
      {
        String why = Update.errorString();
        if (filesystem)
          SPIFFS.begin(true);
        sendOutcome(request, 507, "exception", "Could not start the update: " + why);
        return;
      }

      ota.active = true;
      ota.fileMode = false;
      ota.expected = total;
      ota.error = "";
      Serial.printf("[OTA] receiving %u bytes of %s\n", (unsigned)total,
                    filesystem ? "filesystem" : "firmware");
    }

    if (!ota.active)
      return; // refused above, or already failed

    if (Update.write(data, len) != len)
    {
      ota.error = Update.errorString();
      Update.abort();
      ota.active = false;
      if (filesystem)
        SPIFFS.begin(true);
      sendOutcome(request, 500, "exception", "The upload failed: " + ota.error);
      return;
    }

    if (index + len == total)
    {
      bool ok = Update.end(true);
      ota.active = false;

      if (!ok)
      {
        String why = Update.errorString();
        if (filesystem)
          SPIFFS.begin(true);
        sendOutcome(request, 500, "exception", "The image was not accepted: " + why);
        return;
      }

      Serial.println("[OTA] image accepted, restarting");
      request->send(200, "application/json",
                    String("{\"status\":\"updated\",\"target\":\"") +
                        (filesystem ? "filesystem" : "firmware") + "\",\"restarting\":true}");
      scheduleRestart(1200);
    }
  };

  AsyncCallbackWebHandler *otaFirmware = new AsyncCallbackWebHandler();
  otaFirmware->setUri("/ota/firmware");
  otaFirmware->setMethod(HTTP_POST);
  otaFirmware->onRequest([](AsyncWebServerRequest *request) {});
  otaFirmware->onBody(receiveImage);
  server.addHandler(otaFirmware);

  AsyncCallbackWebHandler *otaFilesystem = new AsyncCallbackWebHandler();
  otaFilesystem->setUri("/ota/filesystem");
  otaFilesystem->setMethod(HTTP_POST);
  otaFilesystem->onRequest([](AsyncWebServerRequest *request) {});
  otaFilesystem->onBody(receiveImage);
  server.addHandler(otaFilesystem);

  // One file at a time, which is all a dashboard tweak needs. Written to a
  // temporary name and moved into place at the end, so an upload that stops
  // half way cannot leave a half-written page behind.
  AsyncCallbackWebHandler *otaFile = new AsyncCallbackWebHandler();
  otaFile->setUri("/ota/file");
  otaFile->setMethod(HTTP_POST);
  otaFile->onRequest([](AsyncWebServerRequest *request) {});
  otaFile->onBody([](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
                  {
    if (index == 0)
    {
      if (!requireKey(request))
        return;

      String path;
      if (request->hasParam("path"))
        path = request->getParam("path")->value();
      if (!path.startsWith("/") || path.indexOf("..") >= 0 || path.length() > 31)
      {
        sendOutcome(request, 400, "invalid", "Give an absolute path on the device filesystem, e.g. ?path=/index.html");
        return;
      }

      ota.file = SPIFFS.open("/upload.tmp", FILE_WRITE);
      if (!ota.file)
      {
        sendOutcome(request, 507, "exception", "Could not open a temporary file");
        return;
      }
      ota.active = true;
      ota.fileMode = true;
      ota.filePath = path;
      Serial.printf("[OTA] receiving %u bytes for %s\n", (unsigned)total, path.c_str());
    }

    if (!ota.active || !ota.fileMode)
      return;

    if (ota.file.write(data, len) != len)
    {
      ota.file.close();
      SPIFFS.remove("/upload.tmp");
      ota.active = false;
      sendOutcome(request, 507, "exception", "The device filesystem is full");
      return;
    }

    if (index + len == total)
    {
      ota.file.close();
      ota.active = false;

      SPIFFS.remove(ota.filePath);
      if (!SPIFFS.rename("/upload.tmp", ota.filePath))
      {
        SPIFFS.remove("/upload.tmp");
        sendOutcome(request, 500, "exception", "Could not move the file into place");
        return;
      }

      StaticJsonDocument<192> out;
      out["status"] = "written";
      out["path"] = ota.filePath;
      out["bytes"] = total;
      String body;
      serializeJson(out, body);
      request->send(200, "application/json", body);
    } });
  server.addHandler(otaFile);

  // Forget which orders were already dealt with, so they can be dispensed again
  server.on("/forgetOrders", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
    forgetHandled();
    request->send(200, "application/json", orderStatusJson()); });

  server.on("/setInventory", HTTP_GET, [](AsyncWebServerRequest *request)
            {
    if (!requireKey(request)) return;
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
    if (!requireKey(request)) return;
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
    // Headroom: the documentation strings below are copied into this pool,
    // and an overflowing document serializes as truncated JSON rather than
    // failing loudly.
    DynamicJsonDocument doc(12288);
    doc["resourceType"] = "CapabilityStatement";
    doc["status"] = "active";
    doc["date"] = "2025-04-18";
    doc["publisher"] = "Spenser";
    doc["kind"] = "instance";
    doc["fhirVersion"] = "5.0.0";
    doc["format"][0] = "json";
    doc["software"]["name"] = "Spenser";
    doc["software"]["version"] = FIRMWARE_VERSION;

    // Where a reader, human or agent, goes next. /llms.txt is this unit's own
    // guide: every endpoint, the shapes it accepts, worked examples and the
    // traps, written to be read by an AI agent writing examples or tests.
    String selfBase = "http://" + request->host();
    doc["implementation"]["description"] = "Spenser chocolate dispenser. Agent guide with examples at " + selfBase + "/llms.txt";
    doc["implementation"]["url"] = selfBase;
    doc["implementationGuide"][0] = "http://costateixeira.github.io/spenser/ImplementationGuide/jct.fhir.spenser";

    JsonArray rest = doc.createNestedArray("rest");
    JsonObject rest0 = rest.createNestedObject();
    rest0["mode"] = "server";
    rest0["documentation"] = "Orders posted straight at this unit are dispensed on the spot: posting here is itself the authorization. See " + selfBase + "/llms.txt";
    rest0["security"]["description"] =
        "Reads are open. Everything that changes this unit needs its per-unit key, as "
        "Authorization: Bearer <key>, as X-Spenser-Key, or as ?key=<key>. The key is printed on "
        "the serial console at boot and served at /key for five minutes afterwards.";

    JsonArray resources = rest0.createNestedArray("resource");

    JsonObject res1 = resources.createNestedObject();
    res1["type"] = "MedicationRequest";
    res1["profile"] = "http://costateixeira.github.io/spenser/StructureDefinition/SpenserRequest";
    res1["documentation"] = "A create dispenses on the spot and is kept, so the order can be read back. "
                            "The id is assigned here when the client does not supply one, and the answer "
                            "is 201 with a Location. $dispense does the same in one call and answers with "
                            "the MedicationDispense instead.";
    JsonArray res1_interaction = res1.createNestedArray("interaction");
    res1_interaction.createNestedObject()["code"] = "create";
    res1_interaction.createNestedObject()["code"] = "read";
    res1_interaction.createNestedObject()["code"] = "search-type";
    JsonArray res1_params = res1.createNestedArray("searchParam");
    JsonObject p1a = res1_params.createNestedObject();
    p1a["name"] = "_id";
    p1a["type"] = "token";
    JsonObject p1b = res1_params.createNestedObject();
    p1b["name"] = "status";
    p1b["type"] = "token";
    JsonObject p1c = res1_params.createNestedObject();
    p1c["name"] = "subject";
    p1c["type"] = "reference";
    JsonObject op1 = res1.createNestedArray("operation").createNestedObject();
    op1["name"] = "dispense";
    op1["definition"] = "http://costateixeira.github.io/spenser/OperationDefinition/dispense";
    op1["documentation"] = "POST a MedicationRequest to /$dispense and the MedicationDispense comes back.";

    JsonObject res2 = resources.createNestedObject();
    res2["type"] = "InventoryReport";
    JsonArray res2_interaction = res2.createNestedArray("interaction");
    res2_interaction.createNestedObject()["code"] = "read";
    res2_interaction.createNestedObject()["code"] = "create";

    JsonObject res3 = resources.createNestedObject();
    res3["type"] = "MedicationDispense";
    res3["documentation"] = "What this unit dispensed or refused to dispense, newest first, kept on its "
                            "filesystem so a restart does not erase it. The searchset carries an "
                            "OperationOutcome (search.mode 'outcome') describing the last check of the order server";
    JsonArray res3_interaction = res3.createNestedArray("interaction");
    res3_interaction.createNestedObject()["code"] = "read";
    res3_interaction.createNestedObject()["code"] = "search-type";
    JsonArray res3_params = res3.createNestedArray("searchParam");
    JsonObject p3a = res3_params.createNestedObject();
    p3a["name"] = "_id";
    p3a["type"] = "token";
    JsonObject p3b = res3_params.createNestedObject();
    p3b["name"] = "status";
    p3b["type"] = "token";
    JsonObject p3c = res3_params.createNestedObject();
    p3c["name"] = "subject";
    p3c["type"] = "reference";
    JsonObject p3d = res3_params.createNestedObject();
    p3d["name"] = "authorizingPrescription";
    p3d["type"] = "reference";

    // ---- client: what this unit asks of an order server ----
    JsonObject rest1 = rest.createNestedObject();
    rest1["mode"] = "client";
    rest1["documentation"] = "Polls a server for orders that have been made actionable, either by the 'actionable' tag on the MedicationRequest or by a Task asking for it to be fulfilled. Both routes are accepted on every check; a Task takes precedence when an order arrives by both. The orderMode setting narrows this to one route when a demo calls for it";

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
    // reportedDateTime, not reportedDate, and the real time rather than a
    // date frozen into the firmware. The epoch is what an unset clock looks
    // like, which is at least unmistakable.
    String at = nowIso();
    doc["reportedDateTime"] = at.length() ? at : "1970-01-01T00:00:00Z";

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

      if (!requireKey(request))
        return;

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
        sendOutcome(request, 400, "invalid", "POST /InventoryReport takes an InventoryReport");
        return;
      }

      String countType = doc["countType"] | "snapshot";
      if (!doc.containsKey("inventoryListing")) {
        sendOutcome(request, 400, "required", "An InventoryReport needs at least one inventoryListing");
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
  // POST /MedicationRequest is a create, and POST /MedicationRequest/$dispense
  // or POST /$dispense is the one-call operation. One body collector serves
  // all three, because a plain-path handler also matches paths beneath it.
  auto collectAndRun = [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
  {
    if (!index) {
      if (!requireKey(request))
        return;
      request->_tempObject = new String();
      ((String *)request->_tempObject)->reserve(total);
    }
    if (!request->_tempObject)
      return; // refused above

    ((String *)request->_tempObject)->concat((const char *)data, len);

    if (index + len == total) {
      String body = *((String *)request->_tempObject);
      delete (String *)request->_tempObject;
      request->_tempObject = nullptr;

      if (request->url().endsWith("/$dispense"))
        handleDispenseOperation(body, request);
      else
        handleOrderCreate(body, request);
    }
  };

  AsyncCallbackWebHandler *medicationHandler = new AsyncCallbackWebHandler();
  medicationHandler->setUri("/MedicationRequest");
  medicationHandler->setMethod(HTTP_POST);
  medicationHandler->onRequest([](AsyncWebServerRequest *request) {});
  medicationHandler->onBody(collectAndRun);
  server.addHandler(medicationHandler);

  AsyncCallbackWebHandler *dispenseOperation = new AsyncCallbackWebHandler();
  dispenseOperation->setUri("/$dispense");
  dispenseOperation->setMethod(HTTP_POST);
  dispenseOperation->onRequest([](AsyncWebServerRequest *request) {});
  dispenseOperation->onBody(collectAndRun);
  server.addHandler(dispenseOperation);

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
        else if (path.endsWith(".txt"))  ct = "text/plain";
        else if (path.endsWith(".md"))   ct = "text/markdown";
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
      retryPendingWrites();
  }

  // Updates, like order polling, are blocking HTTP work and belong here rather
  // than in a request handler.
  bool updateDue = settings.updateCheckMinutes > 0 && !settings.updateUrl.isEmpty() &&
                   (lastUpdateCheck == 0 ||
                    now - lastUpdateCheck >= (unsigned long)settings.updateCheckMinutes * 60UL * 1000UL);

  if (updateCheckRequested || (WiFi.status() == WL_CONNECTED && updateDue))
  {
    updateCheckRequested = false;
    lastUpdateCheck = now;
    runUpdateCheck();
  }

  if (updateInstallRequested && WiFi.status() == WL_CONNECTED)
  {
    updateInstallRequested = false;
    runUpdateInstall();
  }

  // A build that has been up for a minute with a network and a web server is
  // working. Until then the previous image stays available to roll back to.
  if (!appMarkedValid && WiFi.status() == WL_CONNECTED && now - bootMillis > 60000UL)
    markRunningAppValid();

  // Restart after an update, once the response has had time to go out.
  if (restartAt != 0 && (long)(now - restartAt) >= 0)
  {
    Serial.println("Restarting");
    delay(100);
    ESP.restart();
  }
}
