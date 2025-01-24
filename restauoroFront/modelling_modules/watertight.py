import trimesh
import os
def check_if_watertight(model_path):
    # Lade das Modell
    mesh = trimesh.load_mesh(model_path)
    
    # Überprüfen, ob das Modell wasserdicht ist
    if mesh.is_watertight:
        #print(f"{os.path.basename(model_path)} is watertight! ")
        return (True)
    else:
        print(f"{os.path.basename(model_path)} is not watertight...")
        return (False)

