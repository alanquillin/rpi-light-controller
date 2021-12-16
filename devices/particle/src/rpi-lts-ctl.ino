/*
 * Project rpi-lts-ctl
 * Description: Remote replay devices for the RPi Light Controller
 * Author: Alan Quillin
 */

#include <ArduinoJson.h>
#include <HttpClient.h>

String myDeviceId; // the manufacturer id for the device
int deviceId = 0; // device id from server
JsonObject deviceData;
String model;

// CONSTANTS
String MANUFACTURER = "Particle";
int LOOP_DELAY_MS = 40000;
String HOST = "192.168.122.9";
int PORT = 80;

http_header_t GET_HEADERS[] = {
    { "Accept" , "application/json" },
    { NULL, NULL } // NOTE: Always terminate headers will NULL
};
http_header_t POST_HEADERS[] = {
    { "Content-Type", "application/json" },
    { "Accept" , "application/json" },
    { NULL, NULL } // NOTE: Always terminate headers will NULL
};

HttpClient http_client;

http_response_t get(String path){
    http_request_t request;
    request.hostname = HOST;
    request.port = PORT;
    request.path = path;

    http_response_t response;

    Serial.print("GET http://");
    Serial.print(HOST);
    Serial.print(":");
    Serial.print(PORT);
    Serial.println(path);

    http_client.get(request, response, GET_HEADERS);

    Serial.print("Response status: ");
    Serial.println(response.status);
    Serial.print("HTTP Response Body: ");
    Serial.println(response.body);
    return response;
}

http_response_t post(String path, String data){
    http_request_t request;
    request.hostname = HOST;
    request.port = PORT;
    request.path = path;
    request.body = data;

    http_response_t response;

    Serial.print("MeasurementService>\tPOST http://");
    Serial.print(HOST);
    Serial.print(":");
    Serial.print(PORT);
    Serial.println(path);
    Serial.print("MeasurementService>\tData: ");
    Serial.println(data);

    http_client.post(request, response, POST_HEADERS);

    Serial.print("MeasurementService>\tResponse status: ");
    Serial.println(response.status);
    Serial.print("MeasurementService>\tHTTP Response Body: ");
    Serial.println(response.body);
    return response;
}

DynamicJsonDocument findDeviceData(){
    String path = "/devices?manufacturer=";
    path.concat(MANUFACTURER);
    path.concat("&model=");
    path.concat(model);
    path.concat("&manufacturer_id=");
    path.concat(myDeviceId);

    http_response_t response = get(path);
    DynamicJsonDocument doc(1024);
    if (response.status == 200){
        DeserializationError error = deserializeJson(doc, response.body.c_str());
        if (error) {
            Serial.print(F("deserializeJson() failed: "));
            // DO SOMETHING TO THROW AN ERROR 
        }
    }

    return doc;
}

DynamicJsonDocument getZoneData(int zoneId){
    String path = "/zones/";
    path.concat(zoneId);

    DynamicJsonDocument doc(1024);

    http_response_t response = get(path);
    if (response.status == 200){
        DeserializationError error = deserializeJson(doc, response.body.c_str());
        if (error) {
            Serial.print(F("deserializeJson() failed: "));
            // DO SOMETHING TO THROW AN ERROR 
        }
    }
    return doc;
}

bool ping(){
    String path = "/health";

    int cnt = 0;
    while(cnt < 5){
        http_response_t response = get(path);
        if (response.status == 200){
            return true;
        }
        cnt = cnt + 1;
    }
    return false;
}

DynamicJsonDocument Register(){
    String path = "/devices";

    DynamicJsonDocument j_data(1024);
    j_data["manufacturerId"] = myDeviceId.c_str();
    j_data["manufacturer"] = MANUFACTURER.c_str();
    j_data["model"] = model.c_str();

    char data[1024];
    serializeJson(j_data, data);

    DynamicJsonDocument doc(1024);
    int cnt = 0;
    while(cnt < 5){
        http_response_t response = post(path, data);
        if (response.status < 300){
            DeserializationError error = deserializeJson(doc, response.body.c_str());
            if (error) {
                Serial.print(F("deserializeJson() failed: "));
                // DO SOMETHING TO THROW AN ERROR 
            }
            break;
        }
        cnt = cnt + 1;
    }
    return doc;
}

DynamicJsonDocument getDeviceZones(){
    String path = "/devices/";
    path.concat(deviceId);
    path.concat("/zones");

    DynamicJsonDocument doc(1024);

    http_response_t response = get(path);
    if (response.status == 200){
        DeserializationError error = deserializeJson(doc, response.body.c_str());
        if (error) {
            Serial.print(F("deserializeJson() failed: "));
            // DO SOMETHING TO THROW AN ERROR 
        }
    }
    return doc;
}

void initDevice() {
    Serial.println("Initializing... ");
    bool success = ping();
    if(success){
        Serial.println("Service is available!!");
        DynamicJsonDocument json = findDeviceData();

        if(json.isNull() || json.as<JsonArray>().size() == 0) {
            Serial.println("Device not found on server.  Attempting to register");

            json = Register();
            deviceData = json.as<JsonObject>();
        } else {
            deviceData = json.as<JsonArray>()[0];
        }

        if(!deviceData.isNull()){
            deviceId = deviceData["id"];
        }
    
    } else {
        Serial.println("Service is currently unavailable.");
    }
    
    Serial.println("Initialization complete.");
}

void refreshAll() {
    Serial.println("Refreshing and processing all zone data");

    DynamicJsonDocument zonesDoc = getDeviceZones();

    if(zonesDoc.isNull()) {
        Serial.println("Zone data not found for some reason.");
        return; 
    }

    JsonArray zones = zonesDoc.as<JsonArray>();

    Serial.print("Zone data found!  Total found: ");
    Serial.println(zones.size());

    for(JsonObject zone : zones) {  
        refreshZone(zone);
    }
}

void refreshZone(JsonObject zone) {
    int zoneId = zone["zoneId"];
    JsonArray pins = zone["pinNums"].as<JsonArray>();

    DynamicJsonDocument zoneDoc = getZoneData(zoneId);
    JsonObject zoneDetails = zoneDoc.as<JsonObject>();

    const char* zoneName = zoneDetails["description"];
    const char* state = zoneDetails["expectedState"];
    const char* program = zoneDetails["program"];

    state = strcmp(program, "off") == 0 ? program : state;

    Serial.print("Processing Zone: ");
    Serial.print(zoneName);
    Serial.print(", Id: ");
    Serial.print(zoneId);
    Serial.print(", Program: ");
    Serial.print(program);
    Serial.print(", Expected State: ");
    Serial.println(state);

    for(int pin : pins) {
        if (pin >= 0 && pin < 7) {
            Serial.print("Setting pin ");
            Serial.print(pin);
            Serial.print(" to ");
            Serial.println(state);

            pinMode(pin, OUTPUT);
            digitalWrite(pin, strcmp(state, "on") == 0 ? HIGH : LOW);
        }
        else {
            Serial.print("Unknown/supported pin ");
            Serial.print(pin);
            Serial.println(".  Skipping.");
        }
    }
}

int alert(String arg) {
    Serial.print("Cloud 'alert' function triggered.  Refrshing all zones ");
    refreshAll();
    
    Serial.flush();
    return 0;
}

void setup() {
// PLATFORM_IDs defined here: https://github.com/particle-iot/device-os/blob/develop/hal/shared/platforms.h
    #if PLATFORM_ID == PLATFORM_PHOTON || PLATFORM_ID == PLATFORM_PHOTON_PRODUCTION
        model = "Photon";
    #endif

    #if PLATFORM_ID == PLATFORM_ELECTRON || PLATFORM_ID == PLATFORM_ELECTRON_PRODUCTION
        model = "Electron";
    #endif

    #if PLATFORM_ID == PLATFORM_ARGON
        model = "Argon";
    #endif

    #if PLATFORM_ID == PLATFORM_BORON
        model = "Boron";
    #endif

    Serial.begin(9600);

    myDeviceId = System.deviceID();

    Serial.print("My device id: ");
    Serial.println(myDeviceId);

    initDevice();

    Particle.function("alert", alert);

    Serial.flush();
}

void loop() {
    if (deviceId > 0) {
        refreshAll();
    } else {
        Serial.println("Device was never initialized... trying again");
        initDevice();
    }
    Serial.flush();
    delay(LOOP_DELAY_MS);
}