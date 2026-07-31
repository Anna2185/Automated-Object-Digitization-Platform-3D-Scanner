#Copyright © 2026 AM G. All rights reserved.
#Published strictly for portfolio demonstration. See README.md for details.

import numpy as np
import open3d as o3d
import trimesh


def generate_mesh(pcd, stl_file):
    """
    Generate a triangle mesh from an Open3D point cloud using Ball Pivoting, clean the mesh and export it as an STL file

    Args:
        pcd (o3d.geometry.PointCloud): The Open3D point cloud object
        stl_file (str): The name of the STL file to save the mesh to

    Returns: None
    """
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

    #Clean mesh 
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()

    #convert to trimesh for STL export (Open3D doesnt support direct STL export)
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.triangles)
    tri_mesh = trimesh.Trimesh( vertices=vertices, faces=faces)

    #Export STL
    tri_mesh.export(stl_file)
    print("\nSTL saved as:", stl_file)
