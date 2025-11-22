  #include <Arduino.h>
  #include <Servo.h>
  #include <math.h>
  #include "ServoSpinner.hpp"

  #define SERVO1_PIN 18
  #define SERVO2_PIN 19

  #define ENABLEA_FAN 15
  #define INPUT1_FAN 16
  #define INPUT2_FAN 17

  Servo servo1;
  Servo servo2;

  ServoSpinner xPivot;
  ServoSpinner yPivot;

  struct InputDelta {
      float dx;
      float dy;
  };

  InputDelta input = {0.0f, 0.0f};
  float prevDx = 0.0f;
  float prevDy = 0.0f;
  float deadzone = 0.2f;
  float sensitivity = 15.0f;
  unsigned long checkInterval = 250;
  unsigned long lastCheck = 0;
  unsigned long timeToComplete = 1000;
  int minDegree = 0;
  int maxDegree = 180;

  void handlePivot(ServoSpinner &pivot, float delta);

  void setup() {
      Serial.begin(115200);

      servo1.attach(SERVO1_PIN);
      servo2.attach(SERVO2_PIN);

      xPivot.attach(servo1);
      yPivot.attach(servo2);

      xPivot.spinTo(90, 1000);
      yPivot.spinTo(90, 1000);

      pinMode(ENABLEA_FAN, OUTPUT);
      pinMode(INPUT1_FAN, OUTPUT);
      pinMode(INPUT2_FAN, OUTPUT);

      digitalWrite(INPUT1_FAN, HIGH);
      digitalWrite(INPUT2_FAN, LOW);

      analogWrite(ENABLEA_FAN, 255); // Speed 0–255
      delay(3000);
  }

  void loop() {
    xPivot.update();
    yPivot.update();

    if (Serial.available()) {
      String data = Serial.readStringUntil('\n');
      if (data.startsWith("DX:")) {
          int dxStart = data.indexOf("DX:") + 3;
          int dyStart = data.indexOf("DY:") + 3;
          int semicolon = data.indexOf(";");

          input.dx = data.substring(dxStart, semicolon).toFloat();
          input.dy = data.substring(dyStart).toFloat();
      }
    }

    if (millis() - lastCheck >= checkInterval) {
      lastCheck = millis();

      bool dxChanged = fabs(input.dx) > deadzone;
      bool dyChanged = fabs(input.dy) > deadzone;

      if (dxChanged) {
          handlePivot(xPivot, input.dx);
          prevDx = input.dx;
      }

      if (dyChanged) {
          handlePivot(yPivot, input.dy);
          prevDy = input.dy;
      }
    }
  }


  void handlePivot(ServoSpinner &pivot, float delta) {
      if (!pivot.isActive()) {
          int current = pivot.getCurrentAngle();
          int target  = current + (int)(delta * sensitivity);
          target = constrain(target, minDegree, maxDegree);
          pivot.spinTo(target, timeToComplete);
      }
  }
