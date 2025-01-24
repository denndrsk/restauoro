import trimesh

def show_mesh(model, modelcolor):
    """
    Display a 3D model with custom colors in a viewer.

    Args:
        model (str): Path to the 3D model file.
    """
    # Load the mesh
    mesh = trimesh.load_mesh(model)

    # Apply the mesh color (white)
    mesh.visual.vertex_colors = modelcolor  # White in RGBA

    # Create a scene with the mesh
    scene = trimesh.Scene(mesh)

    # Show the scene with a custom viewer configuration
    scene.show(
        viewer="gl",  # OpenGL-based viewer
        background=(51, 51, 51),  # Dark gray in RGB
    )

