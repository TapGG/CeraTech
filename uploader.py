import serial
import time

# ---------------------
# CONFIGURATION
# ---------------------
PORT = 'COM3'        # <-- Change to your Arduino's port
BAUDRATE = 115200    # Must match Serial.begin() on Arduino
GCODE_FILE = 'printjob.gcode'  # Path to the received file, the received file is currently called: printingjob

# ---------------------
# CONNECT TO ARDUINO
# ---------------------
print("Connecting to Arduino...")
arduino = serial.Serial(PORT, BAUDRATE)
time.sleep(2)  # Wait for Arduino to reset
print("Connected.")

# ---------------------
# SEND GCODE FILE LINE BY LINE
# ---------------------
with open(GCODE_FILE, 'r') as file:
    for line in file:
        line = line.strip()
        if not line or line.startswith(';'):  # Skip comments and blanks
            continue
        print(f">> Sending: {line}")
        arduino.write((line + '\n').encode())

        # Optional: wait for Arduino to finish command
        time.sleep(0.1)  # Tune this depending on your command duration

        # Optional: read response
        while arduino.in_waiting:
            response = arduino.readline().decode().strip()
            print(f"<< Arduino: {response}")


# ---------------------
# RECIEVE STATUS UPDATES
# ---------------------



# ---------------------
# CLEANUP
# ---------------------
arduino.close()
print("Done sending G-code.")
