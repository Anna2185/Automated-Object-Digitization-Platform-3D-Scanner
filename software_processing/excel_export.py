#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.

import numpy as np
from openpyxl import Workbook


def save_to_excel(raw_data, sensor_to_axis_mm, filename):
    """
    Save raw scan data and computed XYZ coordinates to an Excel file
    
    Args:
        raw_data (np.ndarray): Raw scan data containing height, angle, and distance
        sensor_to_axis_mm (float): Distance from the sensor to the rotation axis in mm
        filename (str): The name of the Excel file to save the data to

    Returns: None
    """
    print("\nsaving Excel file...")
    wb = Workbook() #create a new workbook
    ws = wb.active #get the active worksheet
    ws.title = "Scan Data" #set the title of the worksheet

    headers = [
        "Height (mm)",
        "Angle (degrees)",
        "Distance (mm)",
        "X (mm)",
        "Y (mm)",
        "Z (mm)"
    ]

    #add the headers to the first row of the Excel sheet
    ws.append(headers)

    for i in range(len(raw_data)):
        #formulas for each header column
        height_mm = (raw_data[i, 0])                        #height in mm
        angle = (raw_data[i, 1])                            #angle in degrees
        distance_mm = (raw_data[i, 2])                      #distance in mm
        angle_rad = np.radians(angle)                       #angle in radians
        object_x = (sensor_to_axis_mm - distance_mm)        #objects x position relative to the rotation axis
        x = (object_x * np.cos(angle_rad))                  #x position in the scanner coordinate system
        y = (object_x * np.sin(angle_rad))                  #y position in the scanner coordinate system
        z = height_mm                                       #z position in the scanner coordinate system

        ws.append(
            [
                height_mm,
                angle,
                distance_mm,
                x,
                y,
                z
            ]
        )

    #save the excel file with the collected data
    wb.save(filename)
    print("Excel saved as:", filename)
