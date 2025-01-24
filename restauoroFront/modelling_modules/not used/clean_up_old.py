import pymeshlab
from restauoroFront.modelling_modules.unused.mesh_viewer_old import show_mesh
def process_model(input_path, output_path):
    try:
        # Neues MeshLab-Projekt erstellen
        ms = pymeshlab.MeshSet()

        # Modell laden
        ms.load_new_mesh(input_path)
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_connected_component_by_diameter()
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_close_holes()
        # Screened Poisson Surface Reconstruction ausführen
        #ms.apply_coord_laplacian_smoothing(stepsmoothnum=3)
        for i in range(3):
            ms.apply_coord_hc_laplacian_smoothing()
        #ms.generate_surface_reconstruction_screened_poisson(preclean=True, depth=7)

        # Ergebnis speichern
        ms.save_current_mesh(output_path, binary=False)
        print(f"Das bereinigte Modell wurde erfolgreich unter '{output_path}' gespeichert.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        

if __name__ == "__main__":
    # Eingabe- und Ausgabe-Pfade
    input_model_path = "static/models/brokendoor.stl"
    output_model_path = "static/models/cleanModel.stl"

    # Prozess ausführen
    process_model(input_model_path, output_model_path)

show_mesh(output_model_path)