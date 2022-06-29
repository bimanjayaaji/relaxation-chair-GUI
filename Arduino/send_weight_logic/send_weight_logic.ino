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
  digitalWrite(12,HIGH);
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
    //Serial.println("Timeout, check MCU>HX711 wiring and pin designations");
    while (1);
  }
  else {
    LoadCell.setCalFactor(calibrationValue);
    //Serial.println("Startup is complete");
  }

  oldtime_com = millis();
}

void loop() {
  static boolean newDataReady = 0;
  const int serialPrintInterval = 0; //increase value to slow down serial print activity
  tare = 0;

  // check for new data/start next conversion:
  if (LoadCell.update()) newDataReady = true;

  // get smoothed value from the dataset:
  if (newDataReady) {
    if (millis() > t + serialPrintInterval) {
      mass = LoadCell.getData();
      vol = mass*0.9998395;
      //Serial.print("Mass : ");
      //Serial.println(mass);
//      Serial.print(" | ");
//      Serial.print("Vol : ");
//      Serial.println(vol);
      newDataReady = 0;
      t = millis();

      val.parameter.weight = mass;
      val.parameter.vol = vol;
      //val.parameter.tare = tare;
      
      send_data();
    }
  }
  
  // receive command from serial terminal, send 't' to initiate tare operation:
  if (Serial.available() > 0) {
    char inByte = Serial.read();
    if (inByte == 't') LoadCell.tareNoDelay();

    // check if last tare operation is complete:
    if (LoadCell.getTareStatus() == true) {
      //Serial.println("Tare complete");
      tare = 1;
    }

    if (inByte == 'l') digitalWrite(10, HIGH);
    if (inByte == 'o') digitalWrite(10, LOW);
    if (inByte == 'r'){
      delay(50);
      digitalWrite(12,LOW);
      delay(50);
      digitalWrite(12,HIGH); 
    }
  }

//  delay(1000);
//  digitalWrite(12, LOW);
//  delay(1000);
//  digitalWrite(12,HIGH);
}
