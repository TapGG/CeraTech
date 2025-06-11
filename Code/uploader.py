import serial
import time
def main(filename='Gcode.txt'):
    # ---------------------
    # CONFIGURATION
    # ---------------------
    PORT = '/dev/cu.usbmodem101'        # <-- Change to your Arduino's port
    BAUDRATE = 115200    # Must match Serial.begin() on Arduino
    GCODE_FILE = 'Gcode.txt'  # Path to the received file, the received file is currently called: printingjob

    # ---------------------
    # CONNECT TO ARDUINO
    # ---------------------
    print("Connecting to Arduino...")
    arduino = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    time.sleep(2)  # Wait for Arduino to reset
    print("Connected.")

    # ---------------------
    # SEND GCODE FILE LINE BY LINE
    # ---------------------
    try:
        with open(GCODE_FILE, 'r') as file:
            start_time = time.time()
            # Get total lines for progress tracking
            total_lines = sum(1 for _ in file)
            file.seek(0)  # Reset file pointer to start

            current_line = 0
            for line in file:
                line = line.strip()
                if not line or line.startswith(';'):  # Skip comments and blanks
                    current_line += 1
                    continue

                print(f">> Sending: {line}")
                arduino.write((line + '\n').encode())

                # Calculate and print progress percentage
                current_line += 1
                progress = (current_line / total_lines) * 100
                print(f"Progress: {progress:.1f}%")  # Show 1 decimal place

                # Wait for Arduino to respond with "OK"
                while True:
                    if arduino.in_waiting:
                        response = arduino.readline().decode().strip()
                        print(f"<< Arduino: {response}")
                        print(f"Parse Time = {time.time()- start_time}")
                        start_time = time.time()
                        if response == "OK":
                            break

    except FileNotFoundError:
        print(f"Error: File '{GCODE_FILE}' not found.")
        exit(1)

    # ---------------------
    # CLEANUP
    # ---------------------
    arduino.close()
    print("Done sending G-code.")

if __name__ == '__main__':
    print('test')
    main()