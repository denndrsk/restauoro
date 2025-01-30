import os
from django.conf import settings
from django.http import JsonResponse
from modelling_modules.watertight import check_if_watertight
import pymeshlab

def process_3d_model_view(request, project_id):
    """
    View zur Verarbeitung eines 3D-Modells mit deinem Algorithmus.
    """
    

    try:
        # Projektverzeichnis basierend auf der Projekt-ID
        project_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
        input_file = os.path.join(project_folder, f'raw_model_{project_id}.stl')
        output_folder = os.path.join(project_folder, 'processed')
        
        # Sicherstellen, dass das Verzeichnis existiert, andernfalls erstellen
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Algorithmus starten
        result = process_model_neu(input_file, output_folder)
        
        # Ergebnis zurückgeben (als JSON oder mit einer Weiterleitung)
        if result.get("is_watertight"):
            return JsonResponse({"message": "Das Modell ist wasserdicht und wurde erfolgreich verarbeitet.", "status": "success"})
        else:
            return JsonResponse({"message": "Das Modell konnte nicht wasserdicht gemacht werden.", "status": "failed"})
    
    except Exception as e:
        return JsonResponse({"message": f"Ein Fehler ist aufgetreten: {e}", "status": "error"})


def process_model_neu(input_path, output_folder):
    """
    Angepasster Algorithmus für die Verarbeitung eines 3D-Modells.
    """
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input_path)
    print("Model loaded successfully")

    
    
    def smooth_initial_model(ms, output_folder): #изменить какая модель используется если после glätten модель больше не солид!!
        """
        Glättet das Modell und überprüft die Wasserdichtigkeit.
        Wenn das Modell nach dem Glätten nicht mehr wasserdicht ist, wird das ursprüngliche Modell wiederhergestellt.
        """
        # 1. Speichern des Modells vor der Glättung
        initial_output_path = os.path.join(output_folder, "initial_model.stl")
        ms.save_current_mesh(initial_output_path, binary=False)
        
        # 2. Pfad für das geglättete Modell
        smoothed_output_path = os.path.join(output_folder, "smoothed_model.stl")
        
        # 3. Anwenden der Laplacian-Glättung
        for i in range(4):  # Mehr Iterationen für stärkere Glättung
            ms.apply_coord_hc_laplacian_smoothing()

            # 4. Zwischenspeichern nach jedem Glättungsschritt
            ms.save_current_mesh(smoothed_output_path, binary=False)

            # 5. Überprüfen, ob das Modell nach der Glättung noch wasserdicht ist
            if check_if_watertight(smoothed_output_path):
                print(f"The model is still watertight after {i+1} iterations of smoothing.")
            else:
                print(f"The model is no longer watertight after {i+1} iterations of smoothing.")
                # 6. Falls das Modell nicht mehr wasserdicht ist, das ursprüngliche Modell wiederherstellen
                ms.load_new_mesh(initial_output_path)
                print("The original model is being restored.")
                return {"is_watertight": False, "output_file": initial_output_path}

        # 7. Falls das Modell nach der Glättung wasserdicht bleibt, speichern
        #print("The model remained watertight after smoothing.")
        return {"is_watertight": True, "output_file": smoothed_output_path}

    def save_debug_mesh(step_name, current_mesh):
        """Speichert das aktuelle Modell im projektbezogenen Verzeichnis."""
        nonlocal step
        debug_path = os.path.join(output_folder, f"step_{step}_{step_name}.stl")
        current_mesh.save_current_mesh(debug_path, binary=False)
        print(f"Intermediate result saved: step_{step}_{step_name}.stl")
        if check_if_watertight(debug_path):  # Verwende check_if_watertight statt ms.is_watertight()
            final_output_path = os.path.join(output_folder, "clean_model.stl")
            print(f"The model became waterproof after step {step_name}.")
            smooth_initial_model(ms, output_folder) #изменить какая модель используется если после glätten модель больше не солид    
            current_mesh.save_current_mesh(final_output_path, binary=False)
            return {"is_watertight": True, "output_file": final_output_path}
        step += 1
        return None
    
    if check_if_watertight(input_path):  # Wenn das Modell wasserdicht ist
        print("The model is already watertight! Finetuning the model...")
        
        # Modell glätten
        smooth_initial_model(ms, output_folder)
        
        # Speichern des geglätteten Modells
        output_file = os.path.join(output_folder, "clean_model.stl")
        ms.save_current_mesh(output_file, binary=False)
        
        return {"is_watertight": True, "output_file": output_file}

    step = 1
      
    
    # Verarbeitungsschritte
    try:
        # Geometrische Maße berechnen
        geometric_measures = ms.apply_filter('get_geometric_measures')  # Filter anwenden, um geometrische Maße zu berechnen

        # Gesamtfläche des Modells abrufen
        model_area = geometric_measures['surface_area']  # Gesamtfläche des Modells

        # Ziel: 100 Dreiecke pro Flächeneinheit
        polygons_per_unit_area = 1500
        target_face_count = int(model_area * polygons_per_unit_area)

        print(f"Total area of the model: {model_area:.2f} units²")
        print(f"Target number of polygons: {target_face_count}")
        ms.meshing_decimation_quadric_edge_collapse(
            targetfacenum=target_face_count, 
            preservetopology=True, 
            preserveboundary=True, 
            preservenormal=True, 
            qualitythr=0.3, 
            autoclean=True
        )
        result = save_debug_mesh("simplify", ms)
        if result: return result
        
                
        # 2. Doppelte Geometrien entfernen
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_duplicate_vertices()
        result = save_debug_mesh("remove_duplicates", ms)
        if result: return result
        
        # 3. Kleine Komponenten entfernen
        ms.meshing_remove_connected_component_by_diameter()
        result = save_debug_mesh("remove_small_components", ms)
        if result: return result
        
        # 4. Nicht-Manifold-Kanten reparieren
        ms.meshing_repair_non_manifold_edges()
        result = save_debug_mesh("repair_non_manifold_edges", ms)
        if result: return result
        
        # 5. Löcher schließen
        ms.apply_filter('meshing_close_holes', 
                maxholesize=50,        # Größere Löcher schließen
                selected=False,        # Alle Löcher schließen
                newfaceselected=True,  # Neu erstellte Flächen auswählen
                selfintersection=True, # Selbstüberschneidende Flächen verhindern
                refinehole=True,       # Löcher verfeinern
                refineholeedgelen=pymeshlab.PercentageValue(2))   # Feinere Triangulation

        result = save_debug_mesh("close_holes", ms)
        if result: return result

        # 6. Kleine Komponenten nach Face-Anzahl entfernen
        ms.meshing_remove_connected_component_by_face_number(mincomponentsize=25)
        result = save_debug_mesh("remove_small_components", ms)
        if result: return result
        
        # 7. Glätten des Meshes mit einer Schleife und Überprüfung, ob das Modell wasserdicht geworden ist
        for i in range(3):  # Mehr Iterationen für stärkere Glättung
            ms.apply_coord_hc_laplacian_smoothing()

            # Speichern des Modells nach der Glättung (vorübergehend)
            debug_path = os.path.join(output_folder, f"step_{step}_laplacian_smooth.stl")
            ms.save_current_mesh(debug_path, binary=False)
    
            # Überprüfen, ob das Modell nach der Glättung wasserdicht ist
            if check_if_watertight(debug_path):
                print(f"The model became watertight after {i+1} iterations of Laplacian smoothing.")
                break  # Schleife abbrechen, wenn das Modell wasserdicht ist
        
        step +=1

        # 8. Reparatur nach der Glättung
        ms.meshing_repair_non_manifold_edges()
        result = save_debug_mesh("repair_after_smoothing", ms)
        if result: return result
        
        # 9. Speichern des reparierten Modells
        final_output_path = os.path.join(output_folder, "clean_model.stl")
        ms.save_current_mesh(final_output_path, binary=False)
        
        return {"is_watertight": check_if_watertight(final_output_path), "output_file": final_output_path}
    
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        raise e

