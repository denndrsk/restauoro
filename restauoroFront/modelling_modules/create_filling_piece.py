import trimesh
import numpy as np


def create_filling_piece(clean_model_output_path, filling_Piece_model_output_path, filling_dimensions, filling_position):
    # Lade das Tür-Modell
    door_mesh = trimesh.load_mesh(clean_model_output_path)
    
    # Erstelle das Quader-Füllstück
    filling = trimesh.creation.box(filling_dimensions)
    
    # Verschiebe das Füllstück in die richtige Position
    filling.apply_translation(filling_position)
    
    # Berechne die Differenz zwischen Füllstück und Türmodell
    filling_piece = filling.difference(door_mesh)
    
    # Speichere das resultierende Füllstück als STL-Datei
    filling_piece.export(filling_Piece_model_output_path)
    print(f"Füllstück gespeichert unter: {filling_Piece_model_output_path}")