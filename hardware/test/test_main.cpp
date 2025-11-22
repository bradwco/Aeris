// #include <Arduino.h>
// #include <AccelStepper.h>

// #define STEPPER_ENABLE_A_PIN 15
// #define STEPPER_ENABLE_B_PIN 21

// #define STEPPER_INPUT_1_PIN 18
// #define STEPPER_INPUT_2_PIN 19
// #define STEPPER_INPUT_3_PIN 22
// #define STEPPER_INPUT_4_PIN 23

// AccelStepper stepper(
//     AccelStepper::FULL4WIRE,
//     STEPPER_INPUT_1_PIN,
//     STEPPER_INPUT_3_PIN,
//     STEPPER_INPUT_2_PIN,
//     STEPPER_INPUT_4_PIN
// );

// char input;
// bool running = true;
// int moveDirection = 1000000;

// void setup() {
//     Serial.begin(115200);

//     pinMode(STEPPER_ENABLE_A_PIN, OUTPUT);
//     pinMode(STEPPER_ENABLE_B_PIN, OUTPUT);

//     digitalWrite(STEPPER_ENABLE_A_PIN, LOW);
//     digitalWrite(STEPPER_ENABLE_B_PIN, LOW);

//     stepper.setMaxSpeed(600);
//     stepper.setAcceleration(300);
// }

// void loop() {

//     if (Serial.available() > 0) {
//         input = Serial.read();

//         if (input == 'S' || input == 's') {
//             running = false;
//             stepper.stop();
//             digitalWrite(STEPPER_ENABLE_A_PIN, HIGH);
//             digitalWrite(STEPPER_ENABLE_B_PIN, HIGH);
//             Serial.println("Stepper Stopped");
//         }

//         if (input == 'G' || input == 'g') {
//             running = true;
//             digitalWrite(STEPPER_ENABLE_A_PIN, LOW);
//             digitalWrite(STEPPER_ENABLE_B_PIN, LOW);
//             stepper.moveTo(moveDirection);
//             Serial.println("Stepper Running");
//         }

//         if (input == 'R' || input == 'r') {
//             moveDirection = -moveDirection;
//             if (running) {
//                 stepper.moveTo(moveDirection);
//             }
//             Serial.println("Stepper Reverse");
//         }
//     }

//     if (running) {
//         stepper.run();
//     }
// }
