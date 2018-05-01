// Wire Slave Sender
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Sends data as an I2C/TWI slave device
// Refer to the "Wire Master Reader" example for use with this

// Created 29 March 2006

// This example code is in the public domain.


#include <Wire.h>

int sensorPin = A0;    // select the input pin for the potentiometer
int ledPin = 13;      // select the pin for the LED
int sensorValue = 0;  // variable to store the value coming from the sensor
int sensorValueByte = 0;  // variable to store the value to report via i2c bus

int read = 0;         // Blink when i2c value is read

void setup() {
  // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);
  // turn the ledPin off:
  digitalWrite(ledPin, LOW);
  
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event

  // Use internal 1.1V as reference
  analogReference(INTERNAL);
  
  // initialize serial communication at 9600 bits per second:
  //Serial.begin(9600);
}

void loop() {
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);

  // Value should never reach 127 ...
  if (sensorValue > 127 ) sensorValue = 127;
  sensorValueByte = sensorValue;
  
  // print out the value you read:
  if ( read > 0 ) { 
    // turn the ledPin on
    digitalWrite(ledPin, HIGH);
    read -= 1; 
  }
  delay(10);
  if ( read == 0 ) { 
    // turn the ledPin off
    digitalWrite(ledPin, LOW);
  }
//  Serial.println(sensorValueByte);
}

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {
  Wire.write(sensorValueByte); // respond with message of 6 bytes
  read = 10;
}
