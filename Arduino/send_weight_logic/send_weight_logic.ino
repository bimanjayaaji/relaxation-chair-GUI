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

union val {
  struct parameter {
    float weight;
    float vol;          
  } parameter; 
  byte packet[8];
} val;

void pin_setup(){
  pinMode(12,OUTPUT);
  pinMode(14,OUTPUT);
  pinMode(16,OUTPUT);
  pinMode(18,OUTPUT);
  digitalWrite(12,HIGH);
  digitalWrite(14,HIGH);
  digitalWrite(16,HIGH);
  digitalWrite(18,HIGH);
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
    if (inByte == 't') LoadCell.tareNoDelay();
    if (LoadCell.getTareStatus() == true) {
      tare = 1;
    }

    if (inByte == 's'){
      delay(50);
      digitalWrite(12,LOW);
      delay(50);
      digitalWrite(12,HIGH);
      delay(300);
      delay(50);
      digitalWrite(14,LOW);
      delay(50);
      digitalWrite(14,HIGH); 
    }
    
    if (inByte == 'p'){
      delay(50);
      digitalWrite(12,LOW);
      delay(50);
      digitalWrite(12,HIGH); 
    }

    if (inByte == 'v'){
      delay(50);
      digitalWrite(16,LOW);
      delay(50);
      digitalWrite(16,HIGH); 
    }

    if (inByte == 'h'){
      delay(50);
      digitalWrite(18,LOW);
      delay(50);
      digitalWrite(18,HIGH); 
    }
  }
}
