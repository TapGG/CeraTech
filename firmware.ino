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
float feedrate = 1500.0;         // mm/min (default value)
float minFeedrate = 60.0;        // mm/min, to avoid divide-by-zero
float maxFeedrate = 10000.0;     // mm/min, clamp to avoid extreme speeds


bool absolutePositioning = true;
bool absoluteExtrusion = true;
float coord[4] = {0, 0, 0, 0}; // X, Y, Z, E
float max_coord[4] = {130, 130, 400, 100}; // X, Y, Z, E

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

    // if (gcode.startsWith("G90")) {
    //   enableAbsolutePositioning();
    // } else if (gcode.startsWith("G91")) {
    //   enableRelativePosition();
    // } else if (gcode.startsWith("M82")) {
    //   enableAbsoluteExtrusion();
    // } else if (gcode.startsWith("M83")) {
    //   enableRelativeExtrusion();
    // } else if (gcode.startsWith("G0") || gcode.startsWith("G1")) {
    //   parseMove(gcode);
    // } else if (gcode.startsWith("G92")) {
    //   resetCoordinates();
    // } else if (gcode.startsWith("G28")) {
    //   homeAxes();
    // } else if (gcode.startsWith("M17")) {
    //   enableMotors();
    // } else if (gcode.startsWith("M18")) {
    //   disableMotors();
    // } else if (gcode.startsWith("M114")) {
    //   reportPosition();
    // } else if (gcode.startsWith("M100")) {
    //   countGcodeLines(gcode);
    // }
    // Request next line
    Serial.println(gcode);
    Serial.println("OK");
}

void parseMove(String gcode) {
  // gcode should give the dx, dy, dz, de and feedrate values in vector form
  // check bounds
  // if bounds are ok then call the apropriate move functions update the current position
  // if bounds are not ok then send an error message and do not move, so coord[i] stay the same
  // 
  
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
if (!isnan(f)) {
  feedrate = constrain(f, minFeedrate, maxFeedrate);
  delayTime = round((60.0 * 1000000.0) / (feedrate * stps_per_mm)); // microseconds
}

  if (!isnan(x)) moveCoreXY((absolutePositioning ? x - coord[0] : x), 0);
  if (!isnan(y)) moveCoreXY(0, (absolutePositioning ? y - coord[1] : y));
  if (!isnan(z)) moveZ((absolutePositioning ? z - coord[2] : z));
  if (!isnan(e)) extrude((absoluteExtrusion ? e - coord[3] : e));

  if (!isnan(x)) coord[0] += (absolutePositioning ? x - coord[0] : x);
  if (!isnan(y)) coord[1] += (absolutePositioning ? y - coord[1] : y);
  if (!isnan(z)) coord[2] += (absolutePositioning ? z - coord[2] : z);
  if (!isnan(e)) coord[3] += (absoluteExtrusion ? e - coord[3] : e);

  // ---------------
  // Prevent moving out of bounds
  // ---------------
  float dx = 0.0;
  float dy = 0.0;
  float dz = 0.0;
  float de = 0.0;

  // Predict final coordinates
  float newX = coord[0] + dx;
  float newY = coord[1] + dy;
  float newZ = coord[2] + dz;
  float newE = coord[3] + de;

  // Check limits
  if (newX < 0 || newX > max_coord[0] ||
      newY < 0 || newY > max_coord[1] ||
      newZ < 0 || newZ > max_coord[2] ||
      newE < 0 || newE > max_coord[3]) {
    Serial.println("ERROR: Movement exceeds boundary limits. Command skipped.");
  }
  else {
  // Execute movement
  if (dx != 0 || dy != 0) moveCoreXY(dx, dy);
  if (dz != 0) moveZ(dz);
  if (de != 0) extrude(de);

  // Update coordinate state
  // here the coord update should be the something like coord[i] = coord[i] + di
  coord[0] = newX;
  coord[1] = newY;
  coord[2] = newZ;
  coord[3] = newE;
  }
}

void resetCoordinates() {
  coord[0] = coord[1] = coord[2] = coord[3] = 0;
  Serial.println("Position reset to (0,0,0,0) via G92");
}

void homeAxes() {
  // Simply reset coordinates to (0,0,0) without moving
  coord[0] = 0;  // X = 0
  coord[1] = 0;  // Y = 0
  coord[2] = 0;  // Z = 0
  Serial.println("Soft homing: Current position set to (0,0,0)");
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

void countGcodeLines(String gcode) {
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
// checking boundary (DONE)
// we need some example test gcode (Tolly)
// make parser include all the gcode commands (DONE)
// add functions for each command (DONE)
// progress of print (DONE)
// Critical missing variables: Feedrate (DONE), homing pins (DONE), and mode flags(DONE).