import bpy
import os
import sys

def solidify_mesh(input_mesh_path, thickness=0.1, output_folder=None, project_id=None):
    
    # Ensure Blender has no open scenes
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Enable the STL import add-on if it is not active
    if not bpy.ops.preferences.addon_enable(module="io_mesh_stl"):
        bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    
    # Import the model
    bpy.ops.import_mesh.stl(filepath=input_mesh_path)
    
    bpy.context.scene.unit_settings.system = 'METRIC'  # Sets the unit system to metric
    bpy.context.scene.unit_settings.scale_length = 1  
    
    # Select the imported model
    obj = bpy.context.selected_objects[0]
    
    # Add a Solidify Modifier
    solidify_modifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify_modifier.thickness = thickness
    
    # Apply the modifier
    bpy.ops.object.modifier_apply(modifier=solidify_modifier.name)
    
    # Set the output folder if not specified
    if output_folder is None:
        output_folder = os.path.dirname(input_mesh_path)
    os.makedirs(output_folder, exist_ok=True)
    
    # Path for the solidified model
    if not project_id:
        raise ValueError("project_id muss angegeben werden!")
    solidified_model_path = os.path.join(output_folder, f"solidified_model_{project_id}.stl")
    
    # Export the mesh as STL
    bpy.ops.export_mesh.stl(filepath=solidified_model_path)
    
    # Delete the object from the scene (optional)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    return solidified_model_path

def main():
    """
    Main function to handle arguments and run the solidify operation.
    """
    # Command line arguments: input path, output path, thickness, and project ID
    input_mesh_path = sys.argv[sys.argv.index('--') + 1]
    output_folder = sys.argv[sys.argv.index('--') + 2]
    thickness = float(sys.argv[sys.argv.index('--') + 3])
    project_id = sys.argv[sys.argv.index('--') + 4]
    
    solidified_model = solidify_mesh(input_mesh_path, thickness=thickness, output_folder=output_folder, project_id=project_id)
    print(f"The solidified model has been saved: {solidified_model}")

if __name__ == "__main__":
    main()

