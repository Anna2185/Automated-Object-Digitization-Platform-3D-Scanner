#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.

import numpy as np
import matplotlib.pyplot as plt
import open3d as o3d


def plot_point_cloud(points):
    """
    Plot the collected points in a 3D scatter plot using matplotlib
    
    Args:
        points (np.ndarray): A 2D array of shape (N, 3) containing the XYZ coordinates of the points
    
    Returns: None but a plot window will be displayed
    """
    print("\nOpening point cloud...")

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

    #Set equal aspect ratio for all axes to ensure the point cloud is not distorted
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


def build_open3d_cloud(points, ply_file):
    """
    Create an Open3D point cloud from points, remove outliers, estimate normals and save to a PLY file

    Args:
        points (np.ndarray): A 2D array of shape (N, 3) containing the XYZ coordinates of the points
        ply_file (str): The name of the PLY file to save the cleaned point cloud to

    Returns:
        o3d.geometry.PointCloud: The cleaned Open3D point cloud object with estimated normals
    """
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

    #EXPORT THE CLEAN POINT CLOUD
    #save the cleaned point cloud to a PLY file for later use or visualization
    o3d.io.write_point_cloud(ply_file, pcd)
    print("Clean point cloud saved as:", ply_file)

    #Estimate normals for better mesh generation
    print("Estimating normals...")

    #estimate the normals of the point cloud using Open3D's built in function
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=5.0,max_nn=30))
    #orient the normals to be consistent with the tangent plane of the point cloud for better mesh generation
    pcd.orient_normals_consistent_tangent_plane(10)

    return pcd
