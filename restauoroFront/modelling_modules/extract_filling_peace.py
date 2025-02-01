import bpy
import sys

def extract_filling_piece(clean_model_path, filling_peace_path, output_path):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import the door model
    bpy.ops.import_mesh.stl(filepath=clean_model_path)
    door = bpy.context.selected_objects[0]
    door.name = "Door"  # Explicitly name the door object

    # Import the filling piece
    bpy.ops.import_mesh.stl(filepath=filling_peace_path)
    filling = bpy.context.selected_objects[0]
    filling.name = "Filling_Piece"  # Explicitly name the filling piece

    # Apply Boolean DIFFERENCE to the DOOR (subtract filling)
    bool_mod = door.modifiers.new("Bool", 'BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = filling
    bpy.context.view_layer.objects.active = door
    bpy.ops.object.modifier_apply(modifier="Bool")

    # Cleanup: Remove floating geometry
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')  # Split into loose parts
    bpy.ops.object.mode_set(mode='OBJECT')

    # Delete small fragments (keep largest piece)
    objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    objs.sort(key=lambda x: x.dimensions.length, reverse=True)
    for obj in objs[1:]:  # Delete all but the largest
        bpy.data.objects.remove(obj)

    # Export the extracted filling piece
    bpy.ops.export_mesh.stl(filepath=output_path)

if __name__ == "__main__":
    clean_model_path = sys.argv[-3]
    filling_peace_path = sys.argv[-2]
    output_path = sys.argv[-1]
    extract_filling_piece(clean_model_path, filling_peace_path, output_path)