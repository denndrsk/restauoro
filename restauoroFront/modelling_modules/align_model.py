import os
from stl import mesh
import numpy as np
from django.conf import settings
import trimesh

def align_model(project_id):
    model_filename = f'raw_model_{project_id}.stl'
    model_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    model_path = os.path.join(model_folder, model_filename)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model {model_filename} not found!")

    # Load the STL model
    stl_mesh = trimesh.load_mesh(model_path)
    
    

    # Calculate the minimum x, y, and z values 
    min_x = np.min(stl_mesh.vertices[:, 0])  
    max_x = np.max(stl_mesh.vertices[:, 0])
    min_y = np.min(stl_mesh.vertices[:, 1]) 
    min_z = np.min(stl_mesh.vertices[:, 2])

    # Determine the center of the x-axis of the bounding box
    center_x = (min_x + max_x) / 2

    # Calculate the shift to move the center of the x-axis to x=0
    shift_x = -center_x
    shift_y = -min_y
    shift_z = -min_z

    # Shift the model's vertices
    stl_mesh.vertices += np.array([shift_x, shift_y, shift_z])

    # Save the aligned model
    aligned_model_filename = f'raw_model_{project_id}_aligned.stl'
    aligned_model_path = os.path.join(model_folder, aligned_model_filename)
    stl_mesh.export(aligned_model_path)

    print(f"Aligned model saved: {aligned_model_filename}")