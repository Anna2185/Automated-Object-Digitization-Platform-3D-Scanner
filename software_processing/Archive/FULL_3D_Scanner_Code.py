#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.


import serial
import serial.tools.list_ports
import time
import numpy as np
import matplotlib.pyplot as plt
import open3d as o3d
import trimesh
from openpyxl import Workbook


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
PLY_FILE = "clean_point_cloud.ply"
STL_FILE = "scan_output.stl"


#Find the Arduino port
def find_port():
    """Find the arduino port by listing available serial ports and prompting user selection"""
    #list available serial ports and prompt user port selection
    ports = serial.tools.list_ports.comports()
    print("\nAvailable serial devices:\n")

    #print all the ports with their index, port/device name and description
    for i, port in enumerate(ports):
        print(f"[{i}] " f"{port.device} - "f"{port.description}")
    if not ports:
        return None

    #loop until a valid selection is made
    while True:
        try:
            choice = int(
                input("\nEnter the number corresponding to your Arduino: ")
            )

            #check if the choice is valid
            if 0 <= choice < len(ports):
                selected = ports[choice]
                print(f"\nSelected: " f"{selected.device}")
                return selected.device

            print("Invalid selection.")

        except ValueError:
            print("Please enter a valid number")



#SELECT PORT
port = find_port()
if not port:
    print("No serial devices found. Please connect your arduino to a port and try again")
    exit()



#SERIAL CONNECTION
ser = serial.Serial(port, BAUD_RATE, timeout=1)

#time for the serial connection to establish
time.sleep(2)

#print the connected port
print("\nConnected to:", port)

#clear old serial data if any
ser.reset_input_buffer()



#GET OBJECT HEIGHT
while True:
    try:
        #max height is 15cm due to the linear actuator's vertical limitations
        height_cm = float(input("\nEnter object height in cm (maximum 15 cm): "))

        #validate the input
        if (height_cm > 0 and height_cm <= 15):
            break

        print("Please enter a value between 0 and 15 cm")

    except ValueError:
        print("Please enter a valid number")



#START SCAN
command = (f"SCAN:{height_cm}\n")

#print the command being sent to the arduino for debugging purposes
print("\nSending:", command.strip())

#send the command to arduino to start scanning
#arduino will start scanning and sending data back to the computer
ser.write(command.encode())

print("\nscanning...\n")



#DATA COLLECTION
raw_data = []
points = []



#READ SERIAL DATA
while True:
    #read a line from the serial port, decode it and strip any whitespace or newline characters
    line = (ser.readline().decode(errors="ignore").strip())

    if not line:
        continue

    #print the line for debugging purposes
    print(line)

    #SCAN COMPELTE
    if line == "SCAN_COMPLETE":
        print("\nScan complete!")
        break

    # #ignore invalid lines that start with "[" as they are not data lines
    # if line.startswith("["):
    #     continue

    # #ignore lines that do not contain a comma as they are not valid data lines
    # if "," not in line:
    #     continue


    #PARSE DATA from arduino
    try:
        #arduino sends: height_mm, angle, distance_mm
        height_mm, angle, distance_mm = map(float, line.split(","))

    except ValueError:
        continue


    #VALIDATE DISTANCE
    if (distance_mm < MIN_SENSOR_DISTANCE_MM):
        continue

    if (distance_mm > MAX_SENSOR_DISTANCE_MM):
        continue


    #save the raw data for later use (saving to excel)
    raw_data.append([height_mm, angle, distance_mm])


    #---CONVERT ANGLE TO RADIANS
    #convert the angle from degrees to radians for trigonometric calculations based on the setup of sensor to object
    angle_rad = np.radians(angle)


    """
    SENSOR GEOMETRY
    - The sensor is 120 mm from the rotation axis
    - The sensor measures the distance from itself to the surface of the object
    - We calculate the point relative to the rotation axis
    
    IMPORTANT:
    This assumes the VL53L1X is pointed directly toward the rotation axis
    """

    sensor_x = ( SENSOR_TO_AXIS_MM * np.cos(angle_rad))
    sensor_y = (SENSOR_TO_AXIS_MM * np.sin(angle_rad))
                

    #the measured point is along the direction from the sensor toward the rotation axis
    #therefore subtract the measured distance to get the actual point's position 
    object_x = (SENSOR_TO_AXIS_MM - distance_mm)


    #convert radial measurement into the rotating frame.
    #this gives the object's surface position relative to the rotation axis
    x = (object_x * np.cos(angle_rad))
    y = (object_x * np.sin(angle_rad))


    #vertical position (negative because for some reason the scanners z-axis was inverted in the coordinate system)
    z = -height_mm


    #SAVE POINT
    points.append([x, y, z])



#CLOSE SERIAL CONNECTION
ser.close()

print("\nSerial connection closed")


#VALIDATE POINT COLLECTION
if len(points) == 0:
    print("No valid scan points were collected.")
    exit()

#print the number of valid points collected
print(f"\nCollected "f"{len(points)} "f"valid points.")


#CONVERT TO NUMPY ARRAYS
points = np.array(points, dtype=float)
raw_data = np.array(raw_data, dtype=float)


#PRINT POINT CLOUD DIMENSIONS
print("\nPoint cloud dimensions:")

#print the minimum and maximum values for each axis in the point cloud
print("X:", points[:, 0].min(),"to", points[:, 0].max(),"mm")
print("Y:", points[:, 1].min(),"to", points[:, 1].max(),"mm")
print("Z:", points[:, 2].min(),"to", points[:, 2].max(),"mm")


#SAVE TO EXCEL
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
    height_mm = (raw_data[i, 0])                    #height in mm
    angle = (raw_data[i, 1])                        #angle in degrees
    distance_mm = (raw_data[i, 2])                  #distance in mm
    angle_rad = np.radians(angle)                   #angle in radians
    object_x = (SENSOR_TO_AXIS_MM - distance_mm)    #objects x position relative to the rotation axis
    x = (object_x * np.cos(angle_rad))              #x position in the scanner coordinate system
    y = (object_x * np.sin(angle_rad))              #y position in the scanner coordinate system
    z = height_mm                                   #z position in the scanner coordinate system 


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
wb.save(EXCEL_FILE)
print("Excel saved as:", EXCEL_FILE)


#PLOT POINT CLOUD
print("\nOpening point cloud...")

#plot the collected points in a 3D scatter plot using matplotlib
fig = plt.figure(figsize=(10, 8))
#add a 3D subplot to the figure
ax = fig.add_subplot( 111, projection="3d")

#plot the points in 3D space with a small size for better visibility
ax.scatter(
    points[:, 0],
    points[:, 1],
    points[:, 2],
    s=2
)

#set labels accordingly for each axis
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_zlabel("Z (mm)")
ax.set_title("3D Scanner Point Cloud")


#SET EQUAL ASPECT RATIO

#get the range of values for each axis to determine the maximum range
x_range = (points[:, 0].max()- points[:, 0].min())
y_range = (points[:, 1].max()- points[:, 1].min())
z_range = (points[:, 2].max()- points[:, 2].min())

#set the maximum range to make sure there is equal aspect ratio across all the axes
max_range = max(x_range, y_range, z_range)

#calculate the midpoints for each axis to center the plot
#divide by 2 to get the midpoint between the min and max values for each axis
mid_x = (points[:, 0].max() + points[:, 0].min()) / 2
mid_y = (points[:, 1].max() + points[:, 1].min()) / 2
mid_z = (points[:, 2].max() + points[:, 2].min()) / 2

#set the limits for each axis based on the midpoints and maximum range to ensure equal aspect ratio
ax.set_xlim(mid_x - max_range / 2, mid_x + max_range / 2)
ax.set_ylim(mid_y - max_range / 2, mid_y + max_range / 2)
ax.set_zlim(mid_z - max_range / 2, mid_z + max_range / 2)

plt.show()


#CREATE OPEN3D POINT CLOUD
#using Open3D to create a point cloud object from the collected points for further processing and mesh generation
print("\nCreating Open3D point cloud...")

pcd = o3d.geometry.PointCloud()
pcd.points = (o3d.utility.Vector3dVector(points))

#remove noise/outliers to improve mesh quality
print("Removing noise...")
#remove statistical outliers from the point cloud using Open3D's built-in function
pcd, ind = (pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0))
#convert the cleaned point cloud back to a numpy array for further processing or analysis
clean_points = np.asarray(pcd.points)

print("Remaining points:", len(clean_points))



#EXPORT CLEAN POINT CLOUD
#save the cleaned point cloud to a PLY file for later use or visualization
o3d.io.write_point_cloud(PLY_FILE, pcd)


print("Clean point cloud saved as:", PLY_FILE)


#ESTIMATE NORMALS
print("Estimating normals...")

#estimate the normals of the point cloud using Open3D's built in function
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=5.0,max_nn=30))
#orient the normals to be consistent with the tangent plane of the point cloud for better mesh generation
pcd.orient_normals_consistent_tangent_plane(10)



#MESH GENERATION
print("Generating mesh...")


#The point spacing is approximately: 1 mm vertically (per scanning level)
#and the horizontal spacing is based on: 5 degrees per rotation
#start with small radii and adjust as needed

#the radii for the Ball Pivoting algorithm, which determines how the mesh is generated from the point cloud
radii = o3d.utility.DoubleVector(
    [2.0, 3.0, 5.0, 8.0]
)

#mesh generation using Open3D's Ball Pivoting algorithm to create a mesh from the point cloud
mesh = (o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, radii))


#CLEAN MESH
mesh.remove_degenerate_triangles()
mesh.remove_duplicated_triangles()
mesh.remove_duplicated_vertices()
mesh.remove_non_manifold_edges()


#CONVERT TO TRIMESH
vertices = np.asarray(mesh.vertices)
faces = np.asarray(mesh.triangles)
tri_mesh = trimesh.Trimesh( vertices=vertices, faces=faces)


#EXPORT STL
tri_mesh.export(STL_FILE)
print("\nSTL saved as:", STL_FILE)
print("\nDONE")