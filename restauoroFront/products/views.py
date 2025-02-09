from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.http import JsonResponse
from modelling_modules.clean_up import process_model_neu
from modelling_modules.align_model import align_model
from modelling_modules.scale_model import scale_model
from modelling_modules.create_filling_piece import create_filling_piece
import subprocess
import trimesh
import os



def step1_upload(request):
    if request.method == 'POST' and request.FILES.get('model_file'):
        model_file = request.FILES['model_file']
        original_extension = os.path.splitext(model_file.name)[1].lower()

        # Check if the file has a supported extension
        if original_extension not in ['.stl', '.obj']:
            return render(request, 'products/step1_upload.html', {
                'error_message': 'Only STL or OBJ files are allowed.'
            })

        # Determine the next project ID
        project_folder_base = settings.MEDIA_ROOT
        project_folders = [f for f in os.listdir(project_folder_base) if f.startswith('project_')]
        next_project_id = str(max([int(f.split('_')[1]) for f in project_folders], default=0) + 1)

        # Create the target folder
        project_folder = os.path.join(settings.MEDIA_ROOT, f'project_{next_project_id}')
        os.makedirs(project_folder, exist_ok=True)

        # Set filename and path
        new_filename = f'raw_model_{next_project_id}.stl'
        file_path = os.path.join(project_folder, new_filename)

        # If the file is in OBJ format, convert it
        if original_extension == '.obj':
            # Load the OBJ file into Trimesh
            mesh = trimesh.load_mesh(model_file, file_type='obj')

            # Save the converted file as STL
            mesh.export(file_path, file_type='stl')
        else:
            # Save the STL file directly
            fs = FileSystemStorage(location=project_folder)
            fs.save(new_filename, model_file)

        # Save session
        request.session['project_id'] = next_project_id
        align_model(next_project_id)
        # Redirect to step 2
        return redirect('step2_viewer', project_id=next_project_id)

    # Pass the project_id to the template
    project_id = request.session.get('project_id', None)
    return render(request, 'products/step1_upload.html', {'project_id': project_id})




def step2_viewer(request, project_id):
    # Define the filename for the aligned model based on the project ID
    model_filename = f'raw_model_{project_id}_aligned.stl'
    # Create the full path to the folder where the model is stored
    model_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    # Build the full file path for the model file
    model_path = os.path.join(model_folder, model_filename)
    # Create the URL path to access the model file in the media directory
    model_url = f"{settings.MEDIA_URL}project_{project_id}/{model_filename}"
    # Check if the model file exists at the specified path
    if not os.path.exists(model_path):
        # If the model file doesn't exist, render an error page with a message
        return render(request, 'products/error.html', {'error_message': 'Modell nicht gefunden!'})
     # If the model file exists, render the step2_viewer page and pass the model URL and project ID
    return render(request, 'products/step2_viewer.html', {
        'model_url': model_url,
        'project_id': project_id
    })





def step3_selection(request, project_id):
    model_filename = f'raw_model_{project_id}_aligned.stl'
    model_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    model_path = os.path.join(model_folder, model_filename)

    if not os.path.exists(model_path):
        return render(request, 'products/error.html', {'error_message': 'model not found!'})

    # URL for the model
    model_url = f"{settings.MEDIA_URL}project_{project_id}/{model_filename}"

    door_thickness = request.POST.get('door_thickness')
    scale_factor = request.POST.get('scale_factor')
    start_coordinates_x = request.POST.get('start_coordinates_x')
    start_coordinates_z = request.POST.get('start_coordinates_z')
    end_coordinates_x = request.POST.get('end_coordinates_x')
    end_coordinates_z = request.POST.get('end_coordinates_z')
    minY = request.POST.get('minY')
    maxY = request.POST.get('maxY')
    # Pass project_id and door_thickness to the template
    return render(request, 'products/step3_selection.html', {
        'model_url': model_url,
        'project_id': project_id,
        'door_thickness': door_thickness,  # Übergabe der Türdicke an das Template
        'scale_factor': scale_factor,
        'start_coordinates_x' : start_coordinates_x,
        'start_coordinates_z' : start_coordinates_z,
        'end_coordinates_x' : end_coordinates_x,
        'end_coordinates_z' : end_coordinates_z,
        'maxY' : maxY,
        'minY' : minY
    })
    



def step4_clean_up(request, project_id):
    """
    Bereinigt das Modell, solidifiziert es und speichert das Ergebnis.
    """
    # Directories and paths
    project_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    raw_model_path = os.path.join(project_folder, f'raw_model_{project_id}_aligned.stl')
    processed_folder = os.path.join(project_folder, 'processed')
    solidified_model_path = os.path.join(processed_folder, f"solidified_model_{project_id}.stl")
    scaled_model_path = os.path.join(project_folder, f'raw_model_{project_id}_scaled.stl')
    # Check if the raw model exists
    if not os.path.exists(raw_model_path):
        return render(request, 'products/error.html', {'error_message': 'Raw model not found!'})
    # Ensure that the folder for processed models exists
    os.makedirs(processed_folder, exist_ok=True)
    scale_factor = float(request.POST.get('scale_factor', 1.0))
    start_coordinates_x = request.POST.get('start_coordinates_x')
    start_coordinates_z = request.POST.get('start_coordinates_z')
    end_coordinates_x = request.POST.get('end_coordinates_x')
    end_coordinates_z = request.POST.get('end_coordinates_z')
    minY = float(request.POST.get('minY'))
    maxY = float(request.POST.get('maxY'))
    print(minY, maxY)
    scale_model(raw_model_path,scale_factor, scaled_model_path)
    door_thickness = float(request.POST.get('door_thickness', 0.1)) / 100 #(maxY-minY)/2*scale_factor could be used instead

    # Blender script path
    request.session['minY'] = minY
    request.session['maxY'] = maxY
    request.session['door_thickness'] = door_thickness
    request.session['scale_factor'] = scale_factor
    request.session['start_coordinates_x'] = start_coordinates_x
    request.session['start_coordinates_z'] = start_coordinates_z
    request.session['end_coordinates_x'] = end_coordinates_x
    request.session['end_coordinates_z'] = end_coordinates_z
    blender_script = os.path.join(settings.BASE_DIR, 'restauoroFront/modelling_modules/solidify_model.py')  
    door_thickness_str = str(door_thickness)
    # Blender command
    command = [
        '/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--python', blender_script,
        '--', scaled_model_path, processed_folder, door_thickness_str, project_id
    ]

    try:
        # Start Blender in the background
        subprocess.run(command, check=True)
        print(f"Solidified Modell gespeichert: {os.path.join(processed_folder, f'solidified_model_{project_id}.stl')}")
    except subprocess.CalledProcessError as e:
        return render(request, 'products/error.html', {'error_message': f"Fehler beim Solidifizieren des Modells: {e}"})

    # Perform cleanup of the solidified model
    solidified_model_path = os.path.join(processed_folder, f"solidified_model_{project_id}.stl")
    result = process_model_neu(solidified_model_path, processed_folder)

    # Create URL of the cleaned model
    processed_model_url = f"{settings.MEDIA_URL}/project_{project_id}/processed/clean_model.stl"
    request.session['clean_model'] = processed_model_url

    # Check if the cleaned model is watertight
    is_watertight = result.get("is_watertight", False)
    
    # Pass to the template
    return render(request, 'products/step4_clean_up.html', {
        'model_url': processed_model_url,
        'project_id': project_id,
        'door_thickness': door_thickness,
        'is_watertight': is_watertight,
        'scale_factor': scale_factor,
        'start_coordinates_x' : start_coordinates_x,
        'start_coordinates_z' : start_coordinates_z,
        'end_coordinates_x' : end_coordinates_x,
        'end_coordinates_z' : end_coordinates_z,
        'maxY' : maxY,
        'minY' : minY
    })


def step5_filling_piece(request, project_id):
    #paths for trimesh
    processed_model_url = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}/processed/clean_model.stl')
    filling_piece_url = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}/processed/filling_piece.stl')


    scale_factor = float(request.session.get('scale_factor'))
    
    start_coordinates_x = float(request.session.get('start_coordinates_x', 0)) * scale_factor
    start_coordinates_z = float(request.session.get('start_coordinates_z', 0))* scale_factor
    end_coordinates_x = float(request.session.get('end_coordinates_x', 0)) * scale_factor
    end_coordinates_z = float(request.session.get('end_coordinates_z', 0)) * scale_factor
    
    maxY = float(request.session.get('maxY', 0))
    minY = float(request.session.get('minY', 0))
    #door_thickness = (maxY - minY)*scale_factor #this can be used instead of the following line
    door_thickness = float(request.session.get('door_thickness'))   
   
    #path for threejs has to be created differently
    model_url = f"{settings.MEDIA_URL}project_{project_id}/processed/clean_model.stl"
    threejs_filling_piece_url = f"{settings.MEDIA_URL}project_{project_id}/processed/filling_piece.stl"

    # Calculation of the dimensions of the filling piece
    filling_dimensions = (
        abs(end_coordinates_x - start_coordinates_x),
        door_thickness,  # Die Dicke des Füllstücks
        abs(end_coordinates_z - start_coordinates_z) 
    )
    
    # Calculation of the position of the filling piece
    filling_position = (
        min(start_coordinates_x, end_coordinates_x), 
        minY, 
        min(start_coordinates_z, end_coordinates_z)  
    )
    create_filling_piece(processed_model_url, filling_piece_url, filling_dimensions, filling_position)

    return render(request, 'products/step5_filling_piece.html', {
        'model_url': model_url,
        'project_id': project_id,
        'filling_piece_url': threejs_filling_piece_url,
        'door_thickness': door_thickness,
        'scale_factor': scale_factor,
        'start_coordinates_x' : start_coordinates_x,
        'start_coordinates_z' : start_coordinates_z,
        'end_coordinates_x' : end_coordinates_x,
        'end_coordinates_z' : end_coordinates_z})


def step6_filling_piece_viewer(request, project_id):
    project_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    processed_folder = os.path.join(project_folder, 'processed')

    extract_filling_piece_script = os.path.join(settings.BASE_DIR, 'restauoroFront/modelling_modules/extract_filling_piece.py')

    clean_model_path = os.path.join(processed_folder, 'clean_model.stl')
    filling_piece_path = os.path.join(processed_folder, 'filling_piece.stl')
    output_path = os.path.join(processed_folder, 'extracted_filling_piece.stl')
    if not os.path.exists(clean_model_path):
        return render(request, 'products/error.html', {'error_message': 'Das bereinigte Modell wurde nicht gefunden!'})

    # Get parameters from session
    minY = float(request.session.get('minY'))
    maxY = float(request.session.get('maxY'))
    start_x = float(request.session.get('start_coordinates_x'))
    end_x = float(request.session.get('end_coordinates_x'))
    start_z = float(request.session.get('start_coordinates_z'))
    end_z = float(request.session.get('end_coordinates_z'))
    #attempt to extract the filling piece from the shell geometry, not working yet
    command = [
        'blender',
        '--background',
        '--python', extract_filling_piece_script,
        '--', 
        clean_model_path,
        filling_piece_path,
        output_path
    ]

    try:
        #turned off for now
        #subprocess.run(command, check=True)
        threejs_filling_piece_url = f"{settings.MEDIA_URL}project_{project_id}/processed/filling_piece.stl"
        return render(request, 'products/step6_filling_piece_viewer.html', {
            'project_id': project_id,
            'filling_piece_url': threejs_filling_piece_url
        })
    
    except subprocess.CalledProcessError as e:
        return render(request, 'products/error.html', {'error_message': f"error when running script: {e}"})