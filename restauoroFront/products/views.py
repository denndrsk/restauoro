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

        # Überprüfen, ob die Datei eine unterstützte Erweiterung hat
        if original_extension not in ['.stl', '.obj']:
            return render(request, 'products/step1_upload.html', {
                'error_message': 'Nur STL- oder OBJ-Dateien sind erlaubt.'
            })

        # Ermitteln der nächsten Projekt-ID
        project_folder_base = settings.MEDIA_ROOT
        project_folders = [f for f in os.listdir(project_folder_base) if f.startswith('project_')]
        next_project_id = str(max([int(f.split('_')[1]) for f in project_folders], default=0) + 1)

        # Erstelle den Zielordner
        project_folder = os.path.join(settings.MEDIA_ROOT, f'project_{next_project_id}')
        os.makedirs(project_folder, exist_ok=True)

        # Dateiname und Pfad festlegen
        new_filename = f'raw_model_{next_project_id}.stl'
        file_path = os.path.join(project_folder, new_filename)

        # Wenn die Datei im OBJ-Format ist, konvertiere sie
        if original_extension == '.obj':
            # Lade die OBJ-Datei in Trimesh
            mesh = trimesh.load_mesh(model_file, file_type='obj')

            # Speichere die konvertierte Datei als STL
            mesh.export(file_path, file_type='stl')
        else:
            # Speichern der STL-Datei direkt
            fs = FileSystemStorage(location=project_folder)
            fs.save(new_filename, model_file)

        # Session speichern
        request.session['project_id'] = next_project_id
        align_model(next_project_id)
        # Weiterleitung zu Schritt 2
        return redirect('step2_viewer', project_id=next_project_id)

    # Übergabe der project_id an das Template
    project_id = request.session.get('project_id', None)
    return render(request, 'products/step1_upload.html', {'project_id': project_id})




def step2_viewer(request, project_id):
    model_filename = f'raw_model_{project_id}_aligned.stl'
    model_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    model_path = os.path.join(model_folder, model_filename)
    model_url = f"{settings.MEDIA_URL}project_{project_id}/{model_filename}"
    if not os.path.exists(model_path):
        return render(request, 'products/error.html', {'error_message': 'Modell nicht gefunden!'})
    return render(request, 'products/step2_viewer.html', {
        'model_url': model_url,
        'project_id': project_id
    })




def step3_selection(request, project_id):
    model_filename = f'raw_model_{project_id}_aligned.stl'
    model_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    model_path = os.path.join(model_folder, model_filename)

    if not os.path.exists(model_path):
        return render(request, 'products/error.html', {'error_message': 'Modell nicht gefunden!'})

    # URL für das Modell
    model_url = f"{settings.MEDIA_URL}project_{project_id}/{model_filename}"

    # Türdicke aus dem Formular (Standardwert 0.4)
     # Standardwerte für Eingabefelder
    door_thickness = request.POST.get('door_thickness')
    scale_factor = request.POST.get('scale_factor')
    start_coordinates_x = request.POST.get('start_coordinates_x')
    start_coordinates_z = request.POST.get('start_coordinates_z')
    end_coordinates_x = request.POST.get('end_coordinates_x')
    end_coordinates_z = request.POST.get('end_coordinates_z')
    minY = request.POST.get('minY')
    maxY = request.POST.get('maxY')
    # Übergabe von project_id und door_thickness an das Template
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
    # Verzeichnisse und Pfade
    project_folder = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}')
    raw_model_path = os.path.join(project_folder, f'raw_model_{project_id}_aligned.stl')
    processed_folder = os.path.join(project_folder, 'processed')
    solidified_model_path = os.path.join(processed_folder, f"solidified_model_{project_id}.stl")
    scaled_model_path = os.path.join(project_folder, f'raw_model_{project_id}_scaled.stl')
    # Überprüfen, ob das Rohmodell existiert
    if not os.path.exists(raw_model_path):
        return render(request, 'products/error.html', {'error_message': 'Rohmodell nicht gefunden!'})
    # Sicherstellen, dass der Ordner für die verarbeiteten Modelle existiert
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
    door_thickness = float(request.POST.get('door_thickness', 0.1)) / 100 #(maxY-minY)*scale_factor

    print(door_thickness)

    # Blender-Skript-Pfad
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
    # Blender-Befehl
    command = [
        '/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--python', blender_script,
        '--', scaled_model_path, processed_folder, door_thickness_str, project_id
    ]

    try:
         #Starte Blender im Hintergrund
        subprocess.run(command, check=True)
        print(f"Solidified Modell gespeichert: {os.path.join(processed_folder, f'solidified_model_{project_id}.stl')}")
    except subprocess.CalledProcessError as e:
        return render(request, 'products/error.html', {'error_message': f"Fehler beim Solidifizieren des Modells: {e}"})

    # Bereinigung des solidifizierten Modells durchführen
    solidified_model_path = os.path.join(processed_folder, f"solidified_model_{project_id}.stl")
    result = process_model_neu(solidified_model_path, processed_folder)

    # URL des bereinigten Modells erstellen
    processed_model_url = f"{settings.MEDIA_URL}/project_{project_id}/processed/clean_model.stl"
    request.session['clean_model'] = processed_model_url

    # Überprüfen, ob das bereinigte Modell wasserdicht ist
    is_watertight = result.get("is_watertight", False)
    
    # Übergabe an das Template
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
    #für trimesh
    processed_model_url = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}/processed/clean_model.stl')
    filling_piece_url = os.path.join(settings.MEDIA_ROOT, f'project_{project_id}/processed/filling_piece.stl')


    scale_factor = float(request.session.get('scale_factor'))
    
    start_coordinates_x = float(request.session.get('start_coordinates_x', 0)) * scale_factor
    start_coordinates_z = float(request.session.get('start_coordinates_z', 0))* scale_factor
    end_coordinates_x = float(request.session.get('end_coordinates_x', 0)) * scale_factor
    end_coordinates_z = float(request.session.get('end_coordinates_z', 0)) * scale_factor
    
    maxY = float(request.session.get('maxY', 0))
    minY = float(request.session.get('minY', 0))
    door_thickness = (maxY - minY)*scale_factor
    #door_thickness = float(request.session.get('door_thickness'))
    #print("scale by:", scale_factor)
    #print("start coords*scaled", start_coordinates_x,start_coordinates_z)
    #print("minY:", minY)
    #print("maxY:", maxY)
    #print("end coords*scaled", end_coordinates_x,end_coordinates_z)
    #print(door_thickness)
    
    
    #for threejs
    model_url = f"{settings.MEDIA_URL}project_{project_id}/processed/clean_model.stl"
    threejs_filling_piece_url = f"{settings.MEDIA_URL}project_{project_id}/processed/filling_piece.stl"


    # Berechnung der Dimensionen des Füllstücks
    filling_dimensions = (
        abs(end_coordinates_x - start_coordinates_x),  # Breite des Rechtecks
        door_thickness,  # Die Dicke des Füllstücks
        abs(end_coordinates_z - start_coordinates_z)  # Höhe des Rechtecks
    )
    
    # Berechnung der Position des Füllstücks
    filling_position = (
        min(start_coordinates_x, end_coordinates_x),  # X-Position
        minY, 
        min(start_coordinates_z, end_coordinates_z)  # Z-Position
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
        #subprocess.run(command, check=True)
        threejs_filling_piece_url = f"{settings.MEDIA_URL}project_{project_id}/processed/filling_piece.stl"
        return render(request, 'products/step6_filling_piece_viewer.html', {
            'project_id': project_id,
            'filling_piece_url': threejs_filling_piece_url
        })
    
    except subprocess.CalledProcessError as e:
        return render(request, 'products/error.html', {'error_message': f"Fehler beim Ausführen des Extraktionsskripts: {e}"})