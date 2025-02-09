import trimesh
import numpy as np

def create_filling_piece(clean_model_output_path, filling_Piece_model_output_path, filling_dimensions, filling_position):
    
    # Load the door model
    door_mesh = trimesh.load_mesh(clean_model_output_path)
    
    # Tolerances for the filling piece
    model_tolerance_X = 0  
    model_tolerance_Y = -0.02
    model_tolerance_Z = 0  

    # Create the box filling piece with tolerances
    filling = trimesh.creation.box([
        filling_dimensions[0] + model_tolerance_X,  # Breite
        filling_dimensions[1] + model_tolerance_Y,  # Dicke (reduziert um Toleranz)
        filling_dimensions[2] + model_tolerance_Z   # Höhe
    ])

    # Move the filling piece so that the bottom left corner is at (0, 0, 0)
    initial_shift_x = (filling_dimensions[0]) / 2
    initial_shift_y = (filling_dimensions[1]) / 2
    initial_shift_z = (filling_dimensions[2]) / 2
    filling.apply_translation([initial_shift_x, initial_shift_y, initial_shift_z])

    # Now move the filling piece to the desired position (independent of tolerances)
    shift_x = filling_position[0]  
    shift_y = filling_position[1]  
    shift_z = filling_position[2]  
    filling.apply_translation([shift_x, shift_y, shift_z])
    # subdivide mesh (optional)
    def subdivide_mesh(mesh, iterations=3):
        # Subdivide the mesh to create smaller triangles for more detail
        for _ in range(iterations):  
            vertices, faces = trimesh.remesh.subdivide(mesh.vertices, mesh.faces)
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)  # Neues Mesh erstellen
        return mesh

    # Apply the subdivision
    filling = subdivide_mesh(filling, iterations=3)
    # Calculate the difference between the filling piece and the door model
    filling_piece = trimesh.boolean.difference([filling, door_mesh], engine='blender')

    # Save the resulting filling piece as an STL file
    filling_piece.export(filling_Piece_model_output_path)
    print(f"Füllstück gespeichert unter: {filling_Piece_model_output_path}")