import serial
import time

# Global variable to store the Arduino connection
arduino = None

# Configuration constants
PORT = '/dev/cu.usbmodem101'  # <-- Change to your Arduino's port
BAUDRATE = 115200  # Must match Serial.begin() on Arduino

def connect_arduino():
    """Establish connection to Arduino"""
    global arduino
    
    if arduino is not None:
        print("Arduino already connected.")
        return True
    
    try:
        print("Connecting to Arduino...")
        arduino = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print("Connected.")
        return True
    except Exception as e:
        print(f'Could not connect to arduino: {e}')
        return False

def start_print(filename='Gcode.txt'):
    global arduino
    
    # Auto-connect if not connected
    if arduino is None:
        if not connect_arduino():
            return
        
    # ---------------------
    # SEND GCODE FILE LINE BY LINE
    # ---------------------
    try:
        with open(filename, 'r') as file:
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
                        print(f"Parse Time = {time.time() - start_time}")
                        start_time = time.time()
                        if response == "OK":
                            break
                            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    
    # ---------------------
    # CLEANUP
    # ---------------------
    arduino.close()
    arduino = None
    print("Done sending G-code.")

def send_gcode(gcode):
    """
    Send a single line of G-code to the Arduino
    Auto-connects if not already connected.
    
    Args:
        gcode (str): The G-code command to send
    
    Returns:
        str: The response from Arduino, or None if error
    """
    global arduino
    
    # Auto-connect if not connected
    if arduino is None:
        if not connect_arduino():
            return None
    
    # Skip empty lines and comments
    gcode = gcode.strip()
    if not gcode or gcode.startswith(';'):
        print("Skipping empty line or comment")
        return None
    
    try:
        print(f">> Sending: {gcode}")
        arduino.write((gcode + '\n').encode())
        
        # Wait for Arduino to respond
        while True:
            if arduino.in_waiting:
                response = arduino.readline().decode().strip()
                print(f"<< Arduino: {response}")
                return response
                
    except Exception as e:
        print(f"Error sending G-code: {e}")
        return None

def close_connection():
    """Close the Arduino connection"""
    global arduino
    if arduino:
        arduino.close()
        arduino = None
        print("Arduino connection closed.")

def is_connected():
    """Check if Arduino is connected"""
    return arduino is not None and arduino.is_open

if __name__ == '__main__':
    print('test')
    connect_arduino()
    
    # Example usage of send_gcode:
    # send_gcode("G28")  # Home all axes
    # send_gcode("G1 X10 Y10 F1500")  # Move to position
    # close_connection()  # Clean up when done