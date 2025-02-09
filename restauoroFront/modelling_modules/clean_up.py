import os
from django.conf import settings
from django.http import JsonResponse
from modelling_modules.watertight import check_if_watertight
import pymeshlab

def process_model_neu(input_path, output_folder):
    
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(input_path)
    print("Model loaded successfully")
    
    def smooth_initial_model(ms, output_folder):
        # 1. Saving the model before smoothing
        initial_output_path = os.path.join(output_folder, "initial_model.stl")
        ms.save_current_mesh(initial_output_path, binary=False)
        
        # 2. Path for the smoothed model
        smoothed_output_path = os.path.join(output_folder, "smoothed_model.stl")
        
        # 3. Applying Laplacian smoothing
        for i in range(2):  
            ms.apply_coord_hc_laplacian_smoothing()

            # 4. Save intermediate result after each smoothing step
            ms.save_current_mesh(smoothed_output_path, binary=False)

            # 5. Check if the model is still watertight after smoothing
            if check_if_watertight(smoothed_output_path):
                print(f"The model is still watertight after {i+1} iterations of smoothing.")
            else:
                print(f"The model is no longer watertight after {i+1} iterations of smoothing.")
                # 6. If the model is no longer watertight, restore the original model
                ms.load_new_mesh(initial_output_path)
                print("The original model is being restored.")
                return {"is_watertight": False, "output_file": initial_output_path}

        # 7. If the model remains watertight after smoothing, save it
        return {"is_watertight": True, "output_file": smoothed_output_path}

    def save_debug_mesh(step_name, current_mesh):
        nonlocal step
        debug_path = os.path.join(output_folder, f"step_{step}_{step_name}.stl")
        current_mesh.save_current_mesh(debug_path, binary=False)
        print(f"Intermediate result saved: step_{step}_{step_name}.stl")
        if check_if_watertight(debug_path):  
            final_output_path = os.path.join(output_folder, "clean_model.stl")
            print(f"The model became waterproof after step {step_name}.")
            smooth_initial_model(ms, output_folder)
            current_mesh.save_current_mesh(final_output_path, binary=False)
            return {"is_watertight": True, "output_file": final_output_path}
        step += 1
        return None
    
    if check_if_watertight(input_path):  # Check whethter the model is already watertight
        print("The model is already watertight! Finetuning the model...")
        
        # Smooth the model
        smooth_initial_model(ms, output_folder)
        
        # Save the smoothed model
        output_file = os.path.join(output_folder, "clean_model.stl")
        ms.save_current_mesh(output_file, binary=False)
        
        return {"is_watertight": True, "output_file": output_file}

    step = 1
      
    
    try:
        # Calculate geometric measures
        geometric_measures = ms.apply_filter('get_geometric_measures') 

        # Retrieve the total surface area of the model
        model_area = geometric_measures['surface_area']

        # the target number of polygons per unit area should be adjusted
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
        autoclean=True)
        result = save_debug_mesh("simplify", ms)
        if result: return result
        
                
        # 2. Remove duplicate geometries
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_duplicate_vertices()
        result = save_debug_mesh("remove_duplicates", ms)
        if result: return result
        
        # 3. Remove small components
        ms.meshing_remove_connected_component_by_diameter()
        result = save_debug_mesh("remove_small_components", ms)
        if result: return result
        
        # 4. Repair non-manifold edges
        ms.meshing_repair_non_manifold_edges()
        result = save_debug_mesh("repair_non_manifold_edges", ms)
        if result: return result
        
        # 5. Close holes
        ms.apply_filter('meshing_close_holes', 
                maxholesize=50, 
                selected=False,
                newfaceselected=True,
                selfintersection=True,
                refinehole=True,
                refineholeedgelen=pymeshlab.PercentageValue(2))

        result = save_debug_mesh("close_holes", ms)
        if result: return result

        # 6. Remove small components by face count
        ms.meshing_remove_connected_component_by_face_number(mincomponentsize=25)
        result = save_debug_mesh("remove_small_components", ms)
        if result: return result
        
        # 7. Smoothing the mesh with a loop and checking if the model has become watertight
        for i in range(3):
            ms.apply_coord_hc_laplacian_smoothing()

            # Save the model after smoothing (temporarily)
            debug_path = os.path.join(output_folder, f"step_{step}_laplacian_smooth.stl")
            ms.save_current_mesh(debug_path, binary=False)
    
            # Check if the model is watertight after smoothing
            if check_if_watertight(debug_path):
                print(f"The model became watertight after {i+1} iterations of Laplacian smoothing.")
                break 
        
        step +=1

                
        # 8. Saving the repaired model
        final_output_path = os.path.join(output_folder, "clean_model.stl")
        ms.save_current_mesh(final_output_path, binary=False)
        
        return {"is_watertight": check_if_watertight(final_output_path), "output_file": final_output_path}
    
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        raise e
