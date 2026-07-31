#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.

import numpy as np


def get_object_height():
    """
    Prompt user for object height and validate input
    
    Args: None
    
    Returns:
        float: The validated object height in cm
    """
    while True:
        try:
            #max height is 15cm due to the linear actuator's vertical limitations
            height_cm = float(input("\nEnter object height in cm (maximum 15 cm): "))

            #validate the input
            if (height_cm > 0 and height_cm <= 15):
                return height_cm

            print("Please enter a value between 0 and 15 cm")

        except ValueError:
            print("Please enter a valid number")


def start_scan(ser, height_cm):
    """
    Send the scan command to the Arduino

    Args:
        ser (serial.Serial): The serial connection object
        height_cm (float): The object height in cm

    Returns: None
    """
    command = (f"SCAN:{height_cm}\n")

    #print the command being sent to the arduino for debugging purposes
    print("\nSending:", command.strip())

    #send the command to arduino to start scanning
    #arduino will start scanning and sending data back to the computer
    ser.write(command.encode())

    print("\nscanning...\n")


def collect_data(ser, sensor_to_axis_mm, min_sensor_distance_mm, max_sensor_distance_mm):
    """
    Read serial data from Arduino and parse into raw_data and points.

    Args:
        ser (serial.Serial): The serial connection object
        sensor_to_axis_mm (float): Distance from the sensor to the rotation axis in mm
        min_sensor_distance_mm (float): Minimum valid distance from the sensor to the object in mm
        max_sensor_distance_mm (float): Maximum valid distance from the sensor to the object in mm

    Returns:
        raw_data  : list of [height_mm, angle, distance_mm]
        points    : list of [x, y, z] in mm relative to rotation axis


    SENSOR GEOMETRY
        - The sensor is 120 mm from the rotation axis
        - The sensor measures the distance from itself to the surface of the object
        - We calculate the point relative to the rotation axis
        
    IMPORTANT: 
    This assumes the VL53L1X is pointed directly toward the rotation axis, which in the setup is the case. 
    If the sensor is angled, the calculations will be incorrect.
    """
    raw_data = []
    points = []

    while True:
        #read a line from the serial port, decode it and strip any whitespace or newline characters
        line = (ser.readline().decode(errors="ignore").strip())

        if not line:
            continue

        #print the line for debugging purposes
        print(line)

        #---SCAN COMPLETE
        if line == "SCAN_COMPLETE":
            print("\nScan complete!")
            break

        # #ignore invalid lines that start with "[" as they are not data lines
        # if line.startswith("["):
        #     continue

        # #ignore lines that do not contain a comma as they are not valid data lines
        # if "," not in line:
        #     continue

        #Parse the data from the arduino
        try:
            #arduino sends: height_mm, angle, distance_mm
            height_mm, angle, distance_mm = map(float, line.split(","))

        except ValueError:
            continue

        #validate the distance 
        if (distance_mm < min_sensor_distance_mm):
            continue

        if (distance_mm > max_sensor_distance_mm):
            continue

        #save the raw data for later use (saving to excel)
        raw_data.append([height_mm, angle, distance_mm])

        #CONVERT ANGLE TO RADIANS
        #convert the angle from degrees to radians for trigonometric calculations based on the setup of sensor to object
        angle_rad = np.radians(angle)


        #CALCULATE POINTS IN 3D SPACE
        sensor_x = ( sensor_to_axis_mm * np.cos(angle_rad))
        sensor_y = (sensor_to_axis_mm * np.sin(angle_rad))

        #the measured point is along the direction from the sensor toward the rotation axis
        #therefore subtract the measured distance to get the actual point's position
        object_x = (sensor_to_axis_mm - distance_mm)

        #convert radial measurement into the rotating frame.
        #this gives the object's surface position relative to the rotation axis
        x = (object_x * np.cos(angle_rad))
        y = (object_x * np.sin(angle_rad))

        #vertical position (negative because for some reason the scanners z-axis was inverted in the coordinate system)
        z = -height_mm

        #SAVE POINT
        points.append([x, y, z])

    return raw_data, points
