import serial.tools.list_ports
#Find USB Port
def find_port():  #Finds which port the arduino is plugged into
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p)
        if '0403' in p[2]: #unique to Osepp Uno (arduino clone)                
            return p[0]
find_port()