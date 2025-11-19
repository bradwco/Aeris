#include <Arduino.h>
#include <Servo.h>
#include <iostream>

#define SERVO1_PIN 26
#define SERVO2_PIN 27

Servo servo1;
Servo servo2;

void xPivot(int deg, int minSpeed, int elapsedTime);
void yPivot(int deg, int minSpeed, int elapsedTime);

void setup() {
  Serial.begin(115200);
  servo1.attach(SERVO1_PIN); 
  servo2.attach(SERVO2_PIN);
}

char input;
bool stopLoop = false;

void loop() {
  if (Serial.available() > 0) {
    input = Serial.read();
    if (input == 'S' || input == 's') {
      stopLoop = true;
      Serial.println("Stopped");
    }
    if (input == 'G' || input == 'g') {
      stopLoop = false;
      Serial.println("Go");
    }
    Serial.print("Input: ");
    Serial.println(input);
  }
  if (!stopLoop) {
    servo1.write(0);   
    delay(1000);
    servo1.write(180);
    delay(1000);
  }
  delay(50); 
}

void xPivot(int deg, int minSpeed, int elapsedTime) {

}

void yPivot(int deg, int minSpeed, int elapsedTime) {

} 