#include "ServoSpinner.hpp"

ServoSpinner::ServoSpinner()
    : servo(nullptr), startAngle(0), targetAngle(0),
      currentAngle(0), startTime(0), duration(0), active(false) {}

void ServoSpinner::attach(Servo &s) {
    servo = &s;
    currentAngle = servo->read();
}

void ServoSpinner::spinTo(int deg, unsigned long ms) {
    if (!servo) return;

    startAngle = servo->read();
    targetAngle = deg;
    startTime = millis();
    duration = ms;
    active = true;
}

void ServoSpinner::update() {
    if (!active) return;

    unsigned long now = millis();
    float t = float(now - startTime) / duration;

    if (t >= 1.0f) {
        servo->write(targetAngle);
        currentAngle = targetAngle;
        active = false;
        return;
    }

    currentAngle = startAngle +
                   (targetAngle - startAngle) * t;
    servo->write(currentAngle);
}

bool ServoSpinner::isActive() const {
    return active;
}
int ServoSpinner::getCurrentAngle() const {
    return currentAngle;
}
