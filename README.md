-   firmware.ino is uploaded to the arduino
-   uploader.py sets up a two way connection between the arduino and the computer
-   it reads the Gcode from the file named Gcode.txt
-   it sends the lines of Gcode (one at a time / all at once)
-   firmware.ino parses that Gcode and executes it
-   serialprint() in firmware.ino sends progress updates to the python code which displays these updates
    in the terminal / GUI
