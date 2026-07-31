## Copyright
Copyright © 2026 <b>AM G.</b>. All rights reserved. 
This code is published strictly for portfolio demonstration and review purposes. No permission is granted to copy, modify, distribute or use this software for any other purpose.

# Automated Object Digitization Platform (3D-Scanner)
This project is a custom 3D scanner that uses an Arduino, a VL53L1X distance sensor, a stepper motor, and a servo motor. The stepper rotates the object while the VL53L1X measures the distance to the object. The servo then moves the sensor vertically using a linear actuator system so the object can be scanned one layer at a time.

The Arduino handles the physical scanning and sends the measurements to the computer through a serial connection. The Python program receives the data, converts it into 3D coordinates, and creates the different output files.

## Files
### hardware_control Folder
* **hardware_control.ino**: This is the arduino code. It controls the stepper motor, servo motor and VL53L1X sensor. It receives the object height from Python, performs the scan and sends the measurements back to the computer. The scanner takes a measurement every 5 degrees while rotating and moves up 1 mm after each full rotation.
### software_processing Folder
* **main.py**: This is the main Python file. It connects all of the other Python files together. It connects to the Arduino, asks for the object height, starts the scan, collects the data, and then creates the Excel file, point cloud, and STL file.
* **connection.py**: This handles the connection between the computer and Arduino. It finds the available serial ports and lets the user select whichever one is connected to the Arduino.
* **scanning.py**: This handles the scanning process on the Python side. It asks the user for the object height, sends the scan command to the arduino, and collects the measurements returned by the arduino. It also converts the distance measurements into X, Y, and Z coordinates.
* **point_cloud.py**: This handles the 3D point cloud. It displays the scanned points using Matplotlib and uses Open3D to clean up the point cloud and remove some of the noise. It also saves the cleaned point cloud as a PLY file.
* **excel_export.py**: This saves the scan data into an Excel file. The file includes the height, angle, measured distance, and calculated X, Y, and Z coordinates.
* **mesh.py**: This takes the cleaned point cloud and turns it into a 3D mesh using Open3D. The mesh is then exported as an STL file.
#### software_processing/Archive/
* **FULL_3D_Scanner_Code.py**: This file is stored in an archive folder within the software_processing folder. It includes all the functions from the main.py, connection.py, scanning.py, point_cloud.py, excel_export.py and mesh.py files. This was the original file I coded in, then once everything was working, I separated all the files into parts to have better structure with actual functions and allow proper documentation.

## Pin Setup
### Stepper Motor (ULN2003 Driver)
* **VCC** -> + (battery 2)
* **GND** -> - (battery 2)
* **IN1, IN2, IN3, IN4** -> Arduino Digital Pins **D8, D9, D10, D11**

### VL53L1X Sensor
* **VCC** -> 5V (Arduino)
* **GND** -> GND (Arduino)
* **SDA** -> SDA (Arduino I2C Bus)
* **SCL** -> SCL (Arduino I2C Bus)
* **GPIO1** -> Arduino Digital Pin **D2**
* **XSHUT** -> 3.3V

### Servo Motor
* **VCC** -> + (battery 1)
* **GND** -> - (battery 1) & GND (Arduino)
* **Signal** -> Arduino Digital Pin **D6**

## How It Works
1. **Upload**: First, the user should open `hardware_control.ino` on Arduino IDE and upload the code to the actual Arduino board (have the board connected to your laptop prior to this)
2. **Launch**: Once that's done run `main.py` and select the Arduino's serial port. You will then be asked to enter the height of the object being scanned in cm
3. **Trigger**: Python sends the height to the Arduino using a command such as `SCAN:10`
4. **Scan**: The Arduino then scans the object by taking distance measurements every 5 degrees as the stepper rotates. After one full rotation, the servo moves the sensor up by 1 mm and the process repeats until the full height of the object has been scanned
5. **Stream**: The Arduino sends each measurement back to Python in the format of "height, angle, distance"
6. **Process**: Python converts these measurements into 3D coordinates and then uses them to create the point cloud and mesh

## Output
After the scan is finished, the program creates three main files:
* **scan_data.xlsx**: Contains the scan measurements and calculated coordinates.
* **clean_point_cloud.ply**: Contains the cleaned 3D point cloud.
* **scan_output.stl**: Contains the final 3D mesh.

## Running the Project
1. First upload `hardware_control.ino` to the Arduino and connect the Arduino to the computer
2. Make sure the required Python libraries are installed, then run: `main.py`
3. Select the Arduino's serial port and enter the height of the object when prompted. The scanner will then run automatically and generate the output files when it is finished

*Note: The current scanner is set up for a maximum object height of 15 cm, with 1 mm vertical resolution and measurements taken every 5 degrees around the object*

## Author
AM G. - [https://github.com/Anna2185](https://github.com/Anna2185?tab=repositories)
