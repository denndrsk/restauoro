import bpy
import sys

def extract_filling_piece(clean_model_path, filling_peace_path, output_path):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import meshes
    bpy.ops.import_mesh.stl(filepath=clean_model_path)
    door = bpy.context.selected_objects[0]
    door.name = "Door"

    bpy.ops.import_mesh.stl(filepath=filling_peace_path)
    filling = bpy.context.selected_objects[0]
    filling.name = "Filling_Piece"

    # Boolean operation
    bool_mod = door.modifiers.new("Bool", 'BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = filling
    bpy.context.view_layer.objects.active = door
    bpy.ops.object.modifier_apply(modifier="Bool")

    # Cleanup: Remove floating parts
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Keep the largest mesh (the filling piece)
    objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    objs.sort(key=lambda x: x.dimensions.length, reverse=True)
    for obj in objs[1:]:
        bpy.data.objects.remove(obj)

    # Step 1: Recalculate normals to fix flipped faces
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)  # Fix normals
    bpy.ops.object.mode_set(mode='OBJECT')

    # Step 2: Fill holes explicitly
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()  # Select problematic edges
    bpy.ops.mesh.fill_holes(sides=0)  # Fill holes with N-gons
    bpy.ops.mesh.quads_convert_to_tris()  # Triangulate for STL compatibility
    bpy.ops.object.mode_set(mode='OBJECT')

    # Step 3: Decimate to simplify geometry (optional)
    decimate_mod = objs[0].modifiers.new("Decimate", 'DECIMATE')
    decimate_mod.ratio = 0.5  # Reduce polygon count by 50%
    bpy.ops.object.modifier_apply(modifier="Decimate")

    # Export
    bpy.ops.export_mesh.stl(filepath=output_path)

if __name__ == "__main__":
    clean_model_path = sys.argv[-3]
    filling_peace_path = sys.argv[-2]
    output_path = sys.argv[-1]
    extract_filling_piece(clean_model_path, filling_peace_path, output_path)