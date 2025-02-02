import bpy
import sys

def extract_filling_piece(clean_model_path, filling_piece_path, output_path):
    # Import door shell and filling piece
    bpy.ops.import_mesh.stl(filepath=clean_model_path)
    door = bpy.context.selected_objects[0]
    door.name = "Door"

    bpy.ops.import_mesh.stl(filepath=filling_piece_path)
    filling = bpy.context.selected_objects[0]
    filling.name = "Filling_Piece"

    # Switch to edit mode for the filling piece
    bpy.context.view_layer.objects.active = filling
    bpy.ops.object.mode_set(mode='EDIT')

    # Select loose geometry (assumed to be internal filling piece)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_loose()

    # Separate the internal geometry
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Rename and clean the new separated object
    extracted_piece = bpy.context.selected_objects[-1]
    extracted_piece.name = "Extracted_Filling_Piece"

    # Optional: Make sure the extracted piece is watertight
    bpy.context.view_layer.objects.active = extracted_piece
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    bpy.context.object.modifiers["Solidify"].thickness = 0.01  # Adjust thickness as needed
    bpy.ops.object.modifier_apply(modifier="Solidify")

    # Export the cleaned filling piece
    bpy.ops.export_mesh.stl(filepath=output_path, use_selection=True)
    print(f"Extracted filling piece saved to {output_path}")

# Example call
extract_filling_piece('/path/to/clean_model.stl', '/path/to/filling_piece.stl', '/path/to/output_filling_piece.stl')

if __name__ == "__main__":
    clean_model_path = sys.argv[-3]
    filling_piece_path = sys.argv[-2]
    output_path = sys.argv[-1]
    extract_filling_piece(clean_model_path, filling_piece_path, output_path)