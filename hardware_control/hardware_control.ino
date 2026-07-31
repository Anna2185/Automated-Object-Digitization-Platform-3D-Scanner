//Copyright © 2026 AM G. All rights reserved.
//Published strictly for portfolio demonstration. See README.md for details.

#include <Wire.h>
#include <VL53L1X.h>
#include <Stepper.h>
#include <Servo.h>
#include <math.h>

//Pin definitions (can also be found in the README.md)
/* PINS SET UP
Stepper Motor (ULN2003 Driver): 
  VCC -> + (battery 2)  
  GND -> - (battery 2)
  IN1 IN2 IN3 IN4 -> D8 D9 D10 D11 

VL53L1X Sensor: 
  VCC -> 5V (Arduino) 
  GND -> GND (Arduino)
  SDA -> SDA (Arduino I2C Bus)
  SCL -> SCL (Arduino I2C Bus)
  GPI01 -> D2
  XSHUT -> 3.3V 

Servo Motor: 
  VCC -> + (battery 1)
  GND -> - (battery 1) & GND (Arduino)
  Signal -> D6
*/
const int STEPPER_IN1 = 8;
const int STEPPER_IN2 = 9;
const int STEPPER_IN3 = 10;
const int STEPPER_IN4 = 11;
const int SERVO_PIN = 6;

//Stepper motor configuration
const int STEPS_PER_REVOLUTION = 2048;
const int ROTATION_STEPS = 28;
const float Z_RESOLUTION_MM = 1.0; //adjust this for the change in z you want it to go off of
const float MAX_HEIGHT_MM = 150.0;

//Servo configuration
const int SERVO_START_POS = 180;
const int SERVO_END_POS = 60;
//change # to whatever number of servo degrees equals exactly 1 mm of physical lift on the rig
//const float SERVO_DEGREES_PER_MM = 0.6; 
const float SERVO_DEGREES_PER_MM = 1.5; 

//Objects
Stepper turntable(STEPS_PER_REVOLUTION, STEPPER_IN1, STEPPER_IN3, STEPPER_IN2, STEPPER_IN4);
Servo linearAxis;
VL53L1X distanceSensor;

//Start state
float servoPosition = SERVO_START_POS;
int totalHeightLevels = 0;
float servoStepPerLayer = 0.0;
boolean scanning = false;
bool systemReady = false;

void setup() {
  Serial.begin(115200);
  
  //allow serial to stabilize
  delay(2000);
  Serial.println("BOOTING");
  //clear any old data
  while (Serial.available()) {
    Serial.read();
  }
  
  Wire.begin();
  Wire.setClock(400000);

  //initialize sensor
  distanceSensor.setTimeout(500);
  if (!distanceSensor.init()) {
    Serial.println("[ERR] Sensor init failed");
    while (1) {
      delay(1000);
    }
  }

  distanceSensor.setDistanceMode(VL53L1X::Short);
  distanceSensor.setMeasurementTimingBudget(20000);
  distanceSensor.startContinuous(20);

  //initialize stepper
  turntable.setSpeed(12);

  //initialize servo
  linearAxis.attach(SERVO_PIN);
  delay(500);
  servoPosition = SERVO_START_POS;
  linearAxis.write((int)servoPosition);
  delay(1000);

  //send ready signal multiple times to ensure it's received
  Serial.println("[INIT] System booted");
  delay(100);
  Serial.println("READY");
  delay(100);
  Serial.println("READY");
  
  scanning = false;
  delay(1000);
  Serial.println("READY");
  Serial.flush();
  Serial.println("READY");
  systemReady = true;
}

void loop() {
  if (!systemReady) return;
  
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    Serial.print("[CMD] ");
    Serial.println(cmd);

        if (cmd.startsWith("SCAN:")) {
      String heightStr = cmd.substring(5);
      float objectHeightCm = heightStr.toFloat();
      float objectHeightMm = objectHeightCm * 10.0;

      if (objectHeightMm <= 0 || objectHeightMm > MAX_HEIGHT_MM) {
        Serial.println("[ERR] Invalid height");
        return;
      }

      //calculate how many total levels are needed based on user input
      totalHeightLevels = (int)ceil(objectHeightMm / Z_RESOLUTION_MM);

      //ensures a consistent 2mm lift regardless of total layers
      servoStepPerLayer = Z_RESOLUTION_MM * SERVO_DEGREES_PER_MM;

      Serial.print("[DBG] Total levels calculated: ");
      Serial.println(totalHeightLevels);
      Serial.print("[DBG] Fixed Servo step degrees: ");
      Serial.println(servoStepPerLayer);

      //move to start position
      servoPosition = SERVO_START_POS;
      linearAxis.write((int)servoPosition);
      delay(1000);

      scanning = true;
      performScan();
      scanning = false;
      
      Serial.println("SCAN_COMPLETE"); 
    }
  }
}


void performScan() {
  for (int level = 0; level < totalHeightLevels; level++) {
    delay(300);

    for (int angleCount = 0; angleCount < 72; angleCount++) {
      int currentAngle = angleCount * 5;

      uint16_t readingMm = distanceSensor.read();

      if (distanceSensor.timeoutOccurred()) {
        continue;
      }

      //output data in following format: height_mm (level), angle, distance_mm
      float currentHeightMm = level * Z_RESOLUTION_MM;

      Serial.print(currentHeightMm);
      Serial.print(",");
      Serial.print(currentAngle);
      Serial.print(",");
      Serial.println(readingMm);

      turntable.step(ROTATION_STEPS);
      delay(50);
    }

    //move servo up
    if (level < (totalHeightLevels - 1)) {
      servoPosition -= servoStepPerLayer;
      
      //ensure system does not exceed the predefined physical limits
      servoPosition = constrain(servoPosition, SERVO_END_POS, SERVO_START_POS);
      
      //round() ensures smooth accurate accumulation of degrees
      Serial.print("[SERVO] ");
      Serial.println(servoPosition);
      linearAxis.write(round(servoPosition)); 
      delay(500);
    }

  }

  //return to start position
  servoPosition = SERVO_START_POS;
  linearAxis.write((int)servoPosition);
  delay(1000);

}
