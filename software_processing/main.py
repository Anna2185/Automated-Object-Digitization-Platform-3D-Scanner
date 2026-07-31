#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.

import numpy as np
from connection   import find_port, connect
from scanning     import get_object_height, start_scan, collect_data
from excel_export import save_to_excel
from point_cloud  import plot_point_cloud, build_open3d_cloud
from mesh         import generate_mesh


#SETTINGS
#has to match the baud rate set in the Arduino code
BAUD_RATE = 115200

#PHYSICAL SCANNER GEOMETRY
#distance in mm from the Rotation axis to the VL53L1X sensor
#rotation axis center---distance--> Sensor
SENSOR_TO_AXIS_MM = 120.0

#Vertical scanning resolution, arduino moves the sensor 1 mm per level
Z_RESOLUTION_MM = 1.0

#maximum sensor reading distance (in mm)
MAX_SENSOR_DISTANCE_MM = 400.0

#minimum sensor reading distance (in mm)
MIN_SENSOR_DISTANCE_MM = 1.0


#OUTPUT FILES
#output files names for the data
EXCEL_FILE = "scan_data.xlsx"
PLY_FILE   = "clean_point_cloud.ply"
STL_FILE   = "scan_output.stl"


#MAIN FUNCTION
def main():
    """
    The main function of the program which calls on the proper functions for the scanning process and data handling
    Steps: 
        1. Find the Arduino port
        2. Connect to the Arduino via serial
        3. Get the object height from the user
        4. Start the scanning process
        5. Collect raw data and valid points
        6. Close the serial connection
        7. Validate point collection
        8. Save raw data to Excel
        9. Plot the point cloud
        10. Build an Open3D point cloud and export to PLY
        11. Generate a mesh and export to STL
    """
    #1.Select Port
    port = find_port()
    if not port:
        print("No serial devices found. Please connect your arduino to a port and try again")
        return
 
    #2.Serial Connection
    ser = connect(port, BAUD_RATE)
 
    #3.Get Object height
    height_cm = get_object_height()
 
    #4.Start Scan
    start_scan(ser, height_cm)
 
    #5.Data Collection
    raw_data, points = collect_data(
        ser,
        SENSOR_TO_AXIS_MM,
        MIN_SENSOR_DISTANCE_MM,
        MAX_SENSOR_DISTANCE_MM
    )
 
    #6.Close Serial Connection
    ser.close()
    print("\nSerial connection closed")
 
    #7.Validate Point Collection
    if len(points) == 0:
        print("No valid scan points were collected.")
        return
 
    #print the number of valid points collected
    print(f"\nCollected "f"{len(points)} "f"valid points.")
 
    #Convert to numpy arrays for easier processing
    points   = np.array(points,   dtype=float)
    raw_data = np.array(raw_data, dtype=float)
 
    #Print point cloud dimensions
    print("\nPoint cloud dimensions:")
    print("X:", points[:, 0].min(),"to", points[:, 0].max(),"mm")
    print("Y:", points[:, 1].min(),"to", points[:, 1].max(),"mm")
    print("Z:", points[:, 2].min(),"to", points[:, 2].max(),"mm")
 
    #8.Save to Excel
    save_to_excel(raw_data, SENSOR_TO_AXIS_MM, EXCEL_FILE)
 
    #9.Plot Point Cloud
    plot_point_cloud(points)
 
    #10.Build Open3D Cloud (cleaning, normals, PLY export)
    pcd = build_open3d_cloud(points, PLY_FILE)
 
    #11.Generate Mesh (STL export)
    generate_mesh(pcd, STL_FILE)
 
    print("\nDONE")
 
 
if __name__ == "__main__":
    main()
