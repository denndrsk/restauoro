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
