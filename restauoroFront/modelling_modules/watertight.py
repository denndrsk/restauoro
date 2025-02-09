import trimesh
import os
def check_if_watertight(model_path):
    # Load the model
    mesh = trimesh.load_mesh(model_path)
    
    # Check if the model is watertight
    if mesh.is_watertight:
        return (True)
    else:
        print(f"{os.path.basename(model_path)} is not watertight...")
        return (False)

