#include <Arduino.h>

#define EN       8  // Enable pin for stepper drivers
#define A_DIR    5  // CoreXY Motor A direction
#define B_DIR    6  // CoreXY Motor B direction
#define Z_DIR    7  // Z axis direction
#define A_STP    2  // CoreXY Motor A step
#define B_STP    3  // CoreXY Motor B step
#define Z_STP    4  // Z axis step
#define E_DIR    9  // Extruder direction
#define E_STP    10 // Extruder step

int stps_per_mm = 200;
int delayTime = 2000;  // microseconds between steps

bool absolutePositioning = true;
bool absoluteExtrusion = true;
float coord[4] = {0, 0, 0, 0}; // X, Y, Z, E
float max_coord[4] = {130, 130, 400, 100} // X, Y, Z, E

int totalLines = 0;
int linesProcessed = 0;
int lastPercentReported = -1;

void parseGCode(String gcode);
void parseMove(String gcode);
void resetCoordinates();
void homeAxes();
void enableMotors();
void disableMotors();
void reportPosition();
void moveCoreXY(float x_mm, float y_mm);
void moveZ(float z_mm);
void extrude(float e_mm);

void parseGCode(String gcode) {
  gcode.trim();
  gcode.toUpperCase();

    if (gcode.startsWith("G90")) {
      enableAbsolutePositioning();
    } else if (gcode.startsWith("G91")) {
      enableRelativePosition();
    } else if (gcode.startsWith("M82")) {
      enableAbsoluteExtrusion();
    } else if (gcode.startsWith("M83")) {
      enableRelativeExtrusion();
    } else if (gcode.startsWith("G0") || gcode.startsWith("G1")) {
      parseMove(gcode);
    } else if (gcode.startsWith("G92")) {
      resetCoordinates();
    } else if (gcode.startsWith("G28")) {
      homeAxes();
    } else if (gcode.startsWith("M17")) {
      enableMotors();
    } else if (gcode.startsWith("M18")) {
      disableMotors();
    } else if (gcode.startsWith("M114")) {
      reportPosition();
    } else if (gcode.startsWith("M100")) {
      handleM100(gcode);
    }
  

}

void parseMove(String gcode) {
  float x = NAN, y = NAN, z = NAN, e = NAN, f = NAN;
  gcode.remove(0, 2);
  gcode.trim();

  while (gcode.length() > 0) {
    int spaceIdx = gcode.indexOf(' ');
    String token = (spaceIdx == -1) ? gcode : gcode.substring(0, spaceIdx);
    if (spaceIdx != -1) gcode = gcode.substring(spaceIdx + 1);
    else gcode = "";

    char code = token.charAt(0);
    float val = token.substring(1).toFloat();

    if (code == 'X') x = val;
    else if (code == 'Y') y = val;
    else if (code == 'Z') z = val;
    else if (code == 'E') e = val;
    else if (code == 'F') f = val;
  }

  if (!isnan(x)) moveCoreXY((absolutePositioning ? x - coord[0] : x), 0);
  if (!isnan(y)) moveCoreXY(0, (absolutePositioning ? y - coord[1] : y));
  if (!isnan(z)) moveZ((absolutePositioning ? z - coord[2] : z));
  if (!isnan(e)) extrude((absoluteExtrusion ? e - coord[3] : e));

  if (!isnan(x)) coord[0] += (absolutePositioning ? x - coord[0] : x);
  if (!isnan(y)) coord[1] += (absolutePositioning ? y - coord[1] : y);
  if (!isnan(z)) coord[2] += (absolutePositioning ? z - coord[2] : z);
  if (!isnan(e)) coord[3] += (absoluteExtrusion ? e - coord[3] : e);
}

void resetCoordinates() {
  coord[0] = coord[1] = coord[2] = coord[3] = 0;
  Serial.println("Position reset to (0,0,0,0) via G92");
}


void homeAxes() {
  // Add homing code if needed
  Serial.println("Homing axes via G28");
}

void enableMotors() {
  digitalWrite(EN, LOW);
  Serial.println("Motors enabled via M17");
}

void disableMotors() {
  digitalWrite(EN, HIGH);
  Serial.println("Motors disabled via M18");
}

void reportPosition() {
  Serial.print("X:"); Serial.print(coord[0]);
  Serial.print(" Y:"); Serial.print(coord[1]);
  Serial.print(" Z:"); Serial.print(coord[2]);
  Serial.print(" E:"); Serial.println(coord[3]);
}

void moveCoreXY(float x_mm, float y_mm) {
  int x_steps = round(x_mm * stps_per_mm);
  int y_steps = round(y_mm * stps_per_mm);
  int a_steps = x_steps + y_steps;
  int b_steps = x_steps - y_steps;

  boolean a_dir = (a_steps >= 0);
  boolean b_dir = (b_steps >= 0);

  a_steps = abs(a_steps);
  b_steps = abs(b_steps);

  digitalWrite(A_DIR, a_dir);
  digitalWrite(B_DIR, b_dir);

  for (int i = 0; i < max(a_steps, b_steps); i++) {
    if (i < a_steps) digitalWrite(A_STP, HIGH);
    if (i < b_steps) digitalWrite(B_STP, HIGH);
    delayMicroseconds(delayTime);
    if (i < a_steps) digitalWrite(A_STP, LOW);
    if (i < b_steps) digitalWrite(B_STP, LOW);
    delayMicroseconds(delayTime);
  }
}

void moveZ(float z_mm) {
  boolean up = z_mm >= 0;
  int steps = abs(round(z_mm * stps_per_mm));
  digitalWrite(Z_DIR, !up);
  for (int i = 0; i < steps; i++) {
    digitalWrite(Z_STP, HIGH);
    delayMicroseconds(delayTime);
    digitalWrite(Z_STP, LOW);
    delayMicroseconds(delayTime);
  }
}

void extrude(float e_mm) {
  boolean dir = (e_mm >= 0);
  int steps = abs(round(e_mm * stps_per_mm));
  digitalWrite(E_DIR, dir);
  for (int i = 0; i < steps; i++) {
    digitalWrite(E_STP, HIGH);
    delayMicroseconds(delayTime);
    digitalWrite(E_STP, LOW);
    delayMicroseconds(delayTime);
  }
}

// --- G-code Handlers ---
void enableAbsolutePositioning() {
  absolutePositioning = true;
  Serial.println("Switched to Absolute Positioning (G90)");
}

void enableRelativePosition() {
  absolutePositioning = false;
  Serial.println("Switched to Relative Positioning (G91)");
}

void enableAbsoluteExtrusion() {
  absoluteExtrusion = true;
  Serial.println("Switched to Absolute Extrusion (M82)");
}

void enableRelativeExtrusion() {
  absoluteExtrusion = false;
  Serial.println("Switched to Relative Extrusion (M83)");
}



void handleM100(String gcode) {
  int sIndex = gcode.indexOf('S');
  if (sIndex != -1) {
    int total = gcode.substring(sIndex + 1).toInt();
    setTotalLines(total);
  }
}

void setTotalLines(int total) {
  totalLines = total;
  linesProcessed = 0;
  lastPercentReported = -1;
  Serial.print("Total lines set: ");
  Serial.println(totalLines);
}

void updateProgress() {
  if (totalLines <= 0) return;

  int percent = (100 * linesProcessed) / totalLines;
  if (percent != lastPercentReported && percent % 5 == 0) {
    Serial.print("Progress: ");
    Serial.print(percent);
    Serial.println("%");
    lastPercentReported = percent;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(A_DIR, OUTPUT); pinMode(A_STP, OUTPUT);
  pinMode(B_DIR, OUTPUT); pinMode(B_STP, OUTPUT);
  pinMode(Z_DIR, OUTPUT); pinMode(Z_STP, OUTPUT);
  pinMode(E_DIR, OUTPUT); pinMode(E_STP, OUTPUT);
  pinMode(EN, OUTPUT);
  digitalWrite(EN, LOW);
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    parseGCode(line);
    linesProcessed++;
    updateProgress();
  }
}
// check serial.print is recieved by python 
// commands to implement: 
// must update gcode compiler with the functions move to coord
// checking boundary (VZ)
// we need some example test gcode (Tolly)
// make parser include all the gcode commands (DONE)
// add functions for each command (DONE)
// progress of print (DONE)
// Critical missing variables: Feedrate, homing pins, and mode flags.