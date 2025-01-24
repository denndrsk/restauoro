import pymeshlab
from modelling_modules.watertight import check_if_watertight
def process_model(input_path, output_path):

    try:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(input_path)
        
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_duplicate_vertices()
        ms.meshing_remove_connected_component_by_diameter()
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_close_holes()

        for i in range(2):
           ms.apply_coord_hc_laplacian_smoothing()
        ms.save_current_mesh(output_path, binary=False)
        check_if_watertight(output_path)
        print(f"Das bereinigte Modell wurde erfolgreich unter '{output_path}' gespeichert.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

