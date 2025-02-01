import bpy
import os
import sys

def solidify_mesh(input_mesh_path, thickness=0.1, output_folder=None, project_id=None):
    """
    Solidify a mesh by adding a thickness along the surface normals using Blender's Solidify modifier.
    
    :param input_mesh_path: Path to the input mesh file (STL)
    :param thickness: The thickness to be added to the mesh
    :param output_folder: The folder where the solidified mesh will be saved
    :param project_id: ID of the project for naming the output file
    :return: Path to the solidified mesh file
    """
    # Sicherstellen, dass Blender keine offenen Szenen hat
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Aktivieren des STL-Import-Add-ons, falls es nicht aktiv ist
    if not bpy.ops.preferences.addon_enable(module="io_mesh_stl"):
        bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    
    # Importiere das Modell
    bpy.ops.import_mesh.stl(filepath=input_mesh_path)
    
    bpy.context.scene.unit_settings.system = 'METRIC'  # Setzt das Einheitensystem auf metrisch
    bpy.context.scene.unit_settings.scale_length = 1  # Skaliert die Längeneinheit auf Meter
    
    # Das importierte Modell auswählen
    obj = bpy.context.selected_objects[0]
    
    # Einen Solidify Modifier hinzufügen
    solidify_modifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify_modifier.thickness = thickness
    
    # Anwenden des Modifiers
    bpy.ops.object.modifier_apply(modifier=solidify_modifier.name)
    
    # Setze den Ausgabeordner, falls nicht angegeben
    if output_folder is None:
        output_folder = os.path.dirname(input_mesh_path)  # Speichern im gleichen Ordner wie das Eingabemodell
    
    # Sicherstellen, dass der Ausgabeordner existiert
    os.makedirs(output_folder, exist_ok=True)
    
    # Pfad für das solidifizierte Modell
    if not project_id:
        raise ValueError("project_id muss angegeben werden!")
    solidified_model_path = os.path.join(output_folder, f"solidified_model_{project_id}.stl")
    
    # Exportiere das Mesh als STL
    bpy.ops.export_mesh.stl(filepath=solidified_model_path)
    
    # Lösche das Objekt aus der Szene (optional)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    return solidified_model_path

def main():
    """
    Main function to handle arguments and run the solidify operation.
    """
    # Kommandozeilenargumente: Eingabepfad, Ausgabepfad, Dicke und Projekt-ID
    input_mesh_path = sys.argv[sys.argv.index('--') + 1]
    output_folder = sys.argv[sys.argv.index('--') + 2]
    thickness = float(sys.argv[sys.argv.index('--') + 3])
    project_id = sys.argv[sys.argv.index('--') + 4]
    
    solidified_model = solidify_mesh(input_mesh_path, thickness=thickness, output_folder=output_folder, project_id=project_id)
    print(f"The solidified model has been saved: {solidified_model}")

if __name__ == "__main__":
    main()

import trimesh

def hollow_to_solid(input_path, output_path, wall_thickness):
    """Convert hollow door scan to solid volume while preserving details"""
    try:
        mesh = trimesh.load(input_path)
        
        if not mesh.is_watertight:
            print("Fixing non-watertight mesh...")
            mesh.fill_holes()
            mesh.fix_normals()

        # Create parallel inward/outward shells
        print("Creating solid volume...")
        outward = mesh.copy()
        outward.apply_translation([0, wall_thickness / 2, 0])

        inward = mesh.copy()
        inward.apply_translation([0, -wall_thickness / 2, 0])

        # Combine shells without simplification
        combined = trimesh.util.concatenate([mesh, outward, inward])

        # Use voxel-based filling for precision
        voxel = combined.voxelized(pitch=wall_thickness / 5)  # High resolution
        solid = voxel.fill().marching_cubes

        # Validate result
        if not solid.is_watertight or solid.volume < 1e-6:
            raise ValueError("Failed to create valid solid mesh")

        # Export
        solid.export(output_path)
        print(f"Successfully created detailed solid mesh: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error in hollow_to_solid: {str(e)}")
        # Fallback to manual extrusion
        print("Attempting fallback method...")

        try:
            mesh = trimesh.load(input_path)
            solid = mesh.extrude(height=wall_thickness)  # For 2D meshes
        except AttributeError:
            # Simple translation as a fallback
            solid = mesh.copy()
            solid.apply_translation([0, 0, wall_thickness])

        solid.export(output_path)
        print(f"Fallback solid mesh created: {output_path}")
        return output_path