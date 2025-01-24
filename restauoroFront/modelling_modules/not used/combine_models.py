import numpy as np
from stl import mesh

def combine_models(model1_path, model2_path, combined_model_output_path, position_offset=(0, 0, 0)):
    # Lade beide STL-Modelle
    model1 = mesh.Mesh.from_file(model1_path)
    model2 = mesh.Mesh.from_file(model2_path)
    
    # Verschiebe das zweite Modell, um es neben dem ersten Modell anzuzeigen
    model2.x += position_offset[0]
    model2.y += position_offset[1]
    model2.z += position_offset[2]
    
    # Kombiniere die beiden Modelle
    combined = mesh.Mesh(np.concatenate([model1.data, model2.data]))
    
    # Speichere das kombinierte Modell
    combined.save(combined_model_output_path)
    return combined_model_output_path