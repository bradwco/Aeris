#pragma once
#include <Arduino.h>
#include <Servo.h>

class ServoSpinner {
public:
    ServoSpinner();

    void attach(Servo &s);
    void spinTo(int deg, unsigned long ms);
    void update();
    bool isActive() const;
    int getCurrentAngle() const;

private:
    Servo* servo;
    int startAngle;
    int targetAngle;
    int currentAngle;
    unsigned long startTime;
    unsigned long duration;
    bool active;
};
