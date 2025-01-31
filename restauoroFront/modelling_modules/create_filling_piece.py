import trimesh
import numpy as np

def create_filling_piece(clean_model_output_path, filling_Piece_model_output_path, filling_dimensions, filling_position):
    
    # Lade das Tür-Modell
    door_mesh = trimesh.load_mesh(clean_model_output_path)
    
    # Toleranzen für das Füllstück
    model_tolerance_X = 0  # Keine Toleranz in X-Richtung
    model_tolerance_Y = -0.02  # Reduziere die Dicke des Füllstücks in Y-Richtung
    model_tolerance_Z = 0  # Keine Toleranz in Z-Richtung

    # Erstelle das Quader-Füllstück mit Toleranzen
    # Die Toleranzen werden symmetrisch angewendet, sodass das Füllstück zentriert bleibt
    filling = trimesh.creation.box([
        filling_dimensions[0] + model_tolerance_X,  # Breite
        filling_dimensions[1] + model_tolerance_Y,  # Dicke (reduziert um Toleranz)
        filling_dimensions[2] + model_tolerance_Z   # Höhe
    ])

    # Verschiebe das Füllstück, sodass die untere linke Ecke bei (0, 0, 0) liegt
    # Die untere linke Ecke eines standardmäßig erstellten Quaders liegt bei (-width/2, -height/2, -depth/2)
    # Daher müssen wir das Füllstück um (width/2, height/2, depth/2) verschieben, um die Ecke nach (0, 0, 0) zu bringen
    initial_shift_x = (filling_dimensions[0]) / 2
    initial_shift_y = (filling_dimensions[1]) / 2 
    initial_shift_z = (filling_dimensions[2]) / 2
    filling.apply_translation([initial_shift_x, initial_shift_y, initial_shift_z])

    # Jetzt verschiebe das Füllstück in die gewünschte Position (unabhängig von Toleranzen)
    shift_x = filling_position[0]  # X-Position (unverändert)
    shift_y = filling_position[1]  # Y-Position (unverändert)
    shift_z = filling_position[2]  # Z-Position (unverändert)
    filling.apply_translation([shift_x, shift_y, shift_z])
    
    # Berechne die Differenz zwischen Füllstück und Türmodell
    filling_piece = trimesh.boolean.difference([filling, door_mesh], engine='blender')



    # Speichere das resultierende Füllstück als STL-Datei
    filling_piece.export(filling_Piece_model_output_path)
    print(f"Füllstück gespeichert unter: {filling_Piece_model_output_path}")