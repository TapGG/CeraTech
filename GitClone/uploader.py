import serial
import time
import threading

# Global variable to store the Arduino connection
arduino = None

# Pause/Resume control
is_paused = False
pause_lock = threading.Lock()
print_thread = None
stop_printing = False

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

def main(filename='Gcode.txt'):
    """Legacy function - now just calls connect_arduino"""
    return connect_arduino()

def start_print(filename='Gcode.txt'):
    """Start printing G-code file in a separate thread"""
    global print_thread, stop_printing
    
    # Auto-connect if not connected
    if arduino is None:
        if not connect_arduino():
            return False
    
    # Check if already printing
    if print_thread and print_thread.is_alive():
        print("Print already in progress. Stop current print first.")
        return False
    
    # Reset control flags
    stop_printing = False
    
    # Start printing in separate thread
    print_thread = threading.Thread(target=_print_worker, args=(filename,))
    print_thread.daemon = True
    print_thread.start()
    return True

def _print_worker(filename):
    """Worker function that runs in separate thread for printing"""
    global is_paused, stop_printing
    
    try:
        with open(filename, 'r') as file:
            start_time = time.time()
            # Get total lines for progress tracking
            total_lines = sum(1 for _ in file)
            file.seek(0)  # Reset file pointer to start
            current_line = 0
            
            for line in file:
                # Check if we should stop
                if stop_printing:
                    print("Print stopped by user.")
                    break
                
                # Handle pause
                while is_paused and not stop_printing:
                    time.sleep(0.1)  # Small delay while paused
                
                
                line = line.strip()
                if not line or line.startswith(';'):  # Skip comments and blanks
                    current_line += 1
                    continue
                
                print(f">> Sending: {line}")
                arduino.write((line + '\n').encode())
                
                # Calculate and print progress percentage
                current_line += 1
                progress = (current_line / total_lines) * 100
                print(f"Progress: {progress:.1f}%")
                
                # Wait for Arduino to respond with "OK"
                while True:
                    if stop_printing:
                        break
                    
                    if arduino.in_waiting:
                        response = arduino.readline().decode().strip()
                        print(f"<< Arduino: {response}")
                        print(f"Parse Time = {time.time() - start_time}")
                        start_time = time.time()
                        if response == "OK":
                            break
                
                if stop_printing:
                    break
                    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return
    except Exception as e:
        print(f"Error during printing: {e}")
        return
    
    if not stop_printing:
        print("Print completed successfully!")
    
def pause_print():
    """Pause the current print job"""
    global is_paused
    with pause_lock:
        if not is_paused:
            is_paused = True
            print("Print paused.")
            return True
        else:
            print("Print is already paused.")
            return False

def resume_print():
    """Resume the paused print job"""
    global is_paused
    with pause_lock:
        if is_paused:
            is_paused = False
            print("Print resumed.")
            return True
        else:
            print("Print is not paused.")
            return False

def stop_print():
    """Stop the current print job"""
    global stop_printing, is_paused
    stop_printing = True
    is_paused = False  # Unpause so the thread can exit
    print("Stopping print...")
    
    # Wait for thread to finish
    if print_thread and print_thread.is_alive():
        print_thread.join(timeout=5)  # Wait up to 5 seconds
    
    return True

def get_print_status():
    """Get current print status"""
    if print_thread and print_thread.is_alive():
        if is_paused:
            return "paused"
        else:
            return "printing"
    else:
        return "idle"

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
    
    # Stop any ongoing print first
    if get_print_status() != "idle":
        stop_print()
    
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
    
    # Example usage:
    # start_print("Gcode.txt")  # Start printing
    # time.sleep(5)
    # pause_print()  # Pause after 5 seconds
    # time.sleep(3)
    # resume_print()  # Resume after 3 seconds
    # 
    # Or send individual commands:
    # send_gcode("G28")  # Home all axes
    # send_gcode("G1 X10 Y10 F1500")  # Move to position
    # 
    # close_connection()  # Clean up when done