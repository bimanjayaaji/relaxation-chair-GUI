#include <HX711_ADC.h>
#if defined(ESP8266)|| defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif
#define com_rate_ms 300

const int HX711_dout = 46; 
const int HX711_sck = 44; 

HX711_ADC LoadCell(HX711_dout, HX711_sck);

const int calVal_eepromAdress = 0;
unsigned long t = 0;

unsigned long oldtime_com = 0;
float mass = 0, vol = 0;
int tare = 0;
int led_state = 0;
int x;

int pijatPower = 15, vibration = 13, heat = 17, timer = 19;
int pumpPower = 21, pumpMode = 23, pumpDown = 25, pumpUp = 27;

union val {
  struct parameter {
    float weight;
    float vol;          
  } parameter; 
  byte packet[8];
} val;

void pin_setup(){
  for(x=13;x<=27;x=x+2){
    pinMode(x,OUTPUT);
    digitalWrite(x,HIGH);
  }
}

void send_data(){
  if(millis() - oldtime_com >= com_rate_ms){
    oldtime_com = millis();
    Serial.write('#');
    Serial.write(val.packet, sizeof(val.packet));
  }
}

void setup() {
  Serial.begin(57600);
  pin_setup();
  delay(10);
  LoadCell.begin();
  
  float calibrationValue; 
  calibrationValue = 696.0; 
  #if defined(ESP8266)|| defined(ESP32)

  #endif
  EEPROM.get(calVal_eepromAdress, calibrationValue); 

  unsigned long stabilizingtime = 2000; 
  boolean _tare = true; 
  LoadCell.start(stabilizingtime, _tare);
  if (LoadCell.getTareTimeoutFlag()) {
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue);
  }

  oldtime_com = millis();
}

void loop() {
  static boolean newDataReady = 0;
  const int serialPrintInterval = 0;
  tare = 0;

  if (LoadCell.update()) newDataReady = true;

  if (newDataReady) {
    if (millis() > t + serialPrintInterval) {
      mass = LoadCell.getData();
      vol = mass*0.9998395;
      newDataReady = 0;
      t = millis();

      val.parameter.weight = mass;
      val.parameter.vol = vol;
      
      send_data();
    }
  }
  
  if (Serial.available() > 0) {
    char inByte = Serial.read();
    if (inByte == 't') LoadCell.tareNoDelay(); // TARE
    if (LoadCell.getTareStatus() == true) {
      tare = 1;
    }

    if (inByte == 's'){ // First Start
      delay(300);
      digitalWrite(pijatPower,LOW); // Pijat Power
      delay(300);
      digitalWrite(pijatPower,HIGH);
      delay(300);
      delay(300);
      digitalWrite(timer,LOW); // Timer
      delay(300);
      digitalWrite(timer,HIGH); 
    }
    
    if (inByte == 'p'){ // Pijat Power
      delay(300);
      digitalWrite(pijatPower,LOW);
      delay(300);
      digitalWrite(pijatPower,HIGH); 
    }

    if (inByte == 'v'){ // Vibration
      delay(300);
      digitalWrite(vibration,LOW);
      delay(300);
      digitalWrite(vibration,HIGH); 
    }

    if (inByte == 'h'){ // Heat
      delay(300);
      digitalWrite(heat,LOW);
      delay(300);
      digitalWrite(heat,HIGH); 
    }

    if (inByte == 'n'){ // Pump Power
      delay(100);
      digitalWrite(pumpPower,LOW);
      delay(100);
      digitalWrite(pumpPower,HIGH); 
    }

    if (inByte == 'm'){ // Pump Mode
      delay(100);
      digitalWrite(pumpMode,LOW);
      delay(100);
      digitalWrite(pumpMode,HIGH); 
    }

    if (inByte == 'd'){ // Pump Down
      delay(100);
      digitalWrite(pumpDown,LOW);
      delay(100);
      digitalWrite(pumpDown,HIGH); 
    }

    if (inByte == 'u'){ // Pump Up
      delay(100);
      digitalWrite(pumpUp,LOW);
      delay(100);
      digitalWrite(pumpUp,HIGH); 
    }
    
  }
}
