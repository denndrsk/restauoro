import trimesh
import numpy as np

def create_filling_piece(clean_model_output_path, filling_Piece_model_output_path, filling_dimensions, filling_position):
    # Lade das Tür-Modell
    door_mesh = trimesh.load_mesh(clean_model_output_path)
    model_offset_X = 0.003 
    model_offset_Y = 0.008
    model_offset_Z = 0.003
    # Erstelle das Quader-Füllstück
    filling = trimesh.creation.box([filling_dimensions[0] + model_offset_X, filling_dimensions[1] + model_offset_Y, filling_dimensions[2] + model_offset_Z])
    
    # Berechne die Verschiebung, um die linke untere Ecke auf filling_position zu setzen
    shift_x = filling_position[0] + (filling_dimensions[0] / 2)
    shift_y = filling_position[1] + ((filling_dimensions[1] + model_offset_Y/2) / 2) 
    shift_z = filling_position[2] + (filling_dimensions[2] / 2)
    
    
    # Verschiebe das Füllstück in die richtige Position
    filling.apply_translation([shift_x, shift_y, shift_z])
    
    # Berechne die Differenz zwischen Füllstück und Türmodell
    filling_piece = filling.difference(door_mesh)
    
    # Speichere das resultierende Füllstück als STL-Datei
    filling_piece.export(filling_Piece_model_output_path)
    print(f"Füllstück gespeichert unter: {filling_Piece_model_output_path}")
