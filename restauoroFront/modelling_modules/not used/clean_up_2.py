from restauoroFront.modelling_modules.unused.mesh_viewer_old import show_mesh
from watertight import check_if_watertight
import pymeshlab

def process_model_neu(input_path, output_path):
    try:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(input_path)
        print("Originalmodell geladen.")
        
        if check_if_watertight(input_path) == False:
            # 1. Doppelte Geometrien entfernen
            ms.meshing_remove_duplicate_faces()
            print("Doppelte Flächen entfernt.")
            ms.meshing_remove_duplicate_vertices()
            print("Doppelte Knoten entfernt.")
            
            # 2. Kleine Komponenten entfernen (weniger aggressiv)
            ms.meshing_remove_connected_component_by_diameter(
                mincomponentdiag=pymeshlab.PercentageValue(1.0)  # 1% des Modell-Durchmessers
            )
            print("Kleine Komponenten entfernt.")
            
            # 3. Nicht-Manifold-Kanten reparieren (vorsichtiger)
            ms.meshing_repair_non_manifold_edges(method='Split Vertices')
            print("Nicht-manifold Kanten repariert.")
            
                    
            # 4. Löcher schließen (vorsichtiger)
            ms.meshing_close_holes(maxholesize=5)  # Versuche, größere Löcher mit einer dynamischen Methode zu schließen
            print("Kleine Löcher geschlossen.")
            
            # 5. Knoten zusammenführen, um kleine Lücken zu schließen (weniger aggressiv)
            ms.meshing_merge_close_vertices(threshold=pymeshlab.PercentageValue(0.5))  # 0.5% des Modell-Durchmessers
            print("Nahe Knoten zusammengeführt.")
            
            # 6. Uniform Remeshing für saubere und gleichmäßige Oberfläche (optional, mit feineren Zellen)
            ms.generate_resampled_uniform_mesh(cellsize=pymeshlab.PercentageValue(0.5))  # 0.5% des Modell-Durchmessers
            print("Gleichmäßiges Remeshing durchgeführt.")
            
            # 7. Optional: Oberflächenglättung (vorsichtig, um keine neuen Risse zu erzeugen)
            #ms.apply_coord_hc_laplacian_smoothing(stepsmoothnum=1)
            #print("Oberflächenglättung durchgeführt.")
        
            # 8. Modell speichern
        ms.save_current_mesh(output_path, binary=False)
        print(f"Das bereinigte Modell wurde erfolgreich unter '{output_path}' gespeichert.")
        return True
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        #raycasting 

def process_model(input_path, output_path):

    try:
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(input_path)
        
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_duplicate_vertices()
        ms.meshing_remove_connected_component_by_diameter()
        ms.meshing_repair_non_manifold_edges()
        ms.meshing_close_holes()

        #ms.meshing_remove_duplicate_faces()
        #ms.meshing_remove_connected_component_by_diameter(removeunref=True)
        #ms.meshing_repair_non_manifold_edges(method='Split Vertices')  # Alternative Reparaturmethode
        #ms.meshing_close_holes(maxholesize=30)
        #ms.generate_surface_reconstruction_ball_pivoting(clustering = 20)
        #ms.meshing_merge_close_vertices(threshold=pymeshlab.PercentageValue(1))
        #ms.generate_surface_reconstruction_screened_poisson()

        for i in range(1):
           ms.apply_coord_hc_laplacian_smoothing()
        ms.save_current_mesh(output_path, binary=False)
        print(f"Das bereinigte Modell wurde erfolgreich unter '{output_path}' gespeichert.")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")


if process_model_neu("modelling_modules/modelle_temporaer/rawscan5.stl", "modelling_modules/modelle_temporaer/cleanModel.stl") == True:
    check_if_watertight("modelling_modules/modelle_temporaer/cleanModel.stl")
    show_mesh("modelling_modules/cleanModel.stl", [255,255,255])
