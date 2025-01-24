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
        raise FileNotFoundError(f"Modell {model_filename} nicht gefunden!")

    # Lade das STL-Modell
    stl_mesh = trimesh.load_mesh(model_path)
    
    # Überprüfe die Dimensionen der Punkte
    print(f"Form der Punkte im Modell: {stl_mesh.vertices.shape}")

    # Berechne die minimalen x-, y- und z-Werte (maximale Werte sind auch nützlich)
    min_x = np.min(stl_mesh.vertices[:, 0])  # Minimale x-Koordinate
    max_x = np.max(stl_mesh.vertices[:, 0])
    min_y = np.min(stl_mesh.vertices[:, 1])  # Minimale y-Koordinate
    min_z = np.min(stl_mesh.vertices[:, 2])  # Minimale z-Koordinate

   # Bestimme den Mittelpunkt der x-Achse der Bounding-Box
    center_x = (min_x + max_x) / 2

    # Berechne die Verschiebung, um den Mittelpunkt der x-Achse auf x=0 zu verschieben
    shift_x = -center_x
    shift_y = -min_y
    shift_z = -min_z

    # Verschiebe die Punkte des Modells
    stl_mesh.vertices += np.array([shift_x, shift_y, shift_z])

    # Speichern des ausgerichteten Modells
    aligned_model_filename = f'raw_model_{project_id}_aligned.stl'
    aligned_model_path = os.path.join(model_folder, aligned_model_filename)
    stl_mesh.export(aligned_model_path)

    print(f"Ausgerichtetes Modell gespeichert: {aligned_model_filename}")