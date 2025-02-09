import sys
import trimesh
import os

def scale_model(raw_model_path, scale_factor, output_path):
   
    # Load the model
    model = trimesh.load_mesh(raw_model_path)
    print("Scale factor:", scale_factor)
    # Scale the model
    model.apply_scale(scale_factor)
    
    # Save the scaled model
    model.export(output_path)
    print(f"Skaliertes Modell gespeichert unter: {output_path}")

if __name__ == "__main__":
    # Take arguments from the command line
    raw_model_path = sys.argv[1]  
    scale_factor = float(sys.argv[2])
    output_path = sys.argv[3]

    # Scale the model
    scale_model(raw_model_path, scale_factor, output_path)
