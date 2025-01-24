from restauoroFront.modelling_modules.unused.mesh_viewer_old import show_mesh
from modelling_modules.watertight import check_if_watertight
from restauoroFront.modelling_modules.unused.erstelle_neuen_ordner import erstelle_neuen_ordner, verschiebe_datei
from restauoroFront.modelling_modules.unused.clean_up_1 import process_model
from modelling_modules.create_filling_piece import create_filling_piece
from restauoroFront.modelling_modules.unused.combine_models import combine_models
from restauoroFront.modelling_modules.unused.mesh_viewer_html import  create_renderer_html

def main():

    verschiebe_datei(input_model_path, neuer_ordner_pfad)

    process_model(f"{neuer_ordner_pfad}/rawscan6.stl", clean_model_output_path)
    #process_model(input_model_path, clean_model_output_path)
    #check_if_watertight(clean_model_output_path)
  
    if check_if_watertight(clean_model_output_path) == True:
        create_filling_piece(clean_model_output_path, filling_Piece_model_output_path, filling_dimensions, filling_position)
        #print("es kann ein Füllstück generiert werden :)")
        
    else:
        print("es kann kein Füllstück generiert werden :(")
    #try:
    #    combine_models(clean_model_output_path, filling_Piece_model_output_path, combined_model_output_path, position_offset=(0, 0, 0))
    #    print("Modelle zur Anzeige erfolgreich kombiniert und gespeichert unter:", combined_model_output_path)
    #except Exception as e:
    #   print("Fehler beim Kombinieren der Modelle:", e)
    

if __name__ == "__main__":
   
    basis_pfad = "static/models"  # Basisverzeichnis für Projekte
    input_model_path = "static/models/rawscan6.stl" # Eingabedatei (ursprüngliches Modell)
    neuer_ordner_pfad = erstelle_neuen_ordner(basis_pfad) # Einen neuen Ordner für das Projekt erstellen
     
    clean_model_output_path = f"{neuer_ordner_pfad}/cleanModel.stl" # Ausgabepfad für das bereinigte Modell
    filling_Piece_model_output_path = f"{neuer_ordner_pfad}/filling_Piece.stl" # Ausgabepfad für das Füllstück
    combined_model_output_path = f"{neuer_ordner_pfad}/combined_model.stl" # Ausgabepfad für das kombinierte Modell
    renderer_output_path = f"{neuer_ordner_pfad}/render.html"

    filling_dimensions = (0.065, 0.5, 0.55)   # Dimensionen des Füllstücks (tiefe(x), breite(y), höhe(z))  
    filling_position = (0.25, 0, 0.5)  # Position des Füllstücks im Koordinatensystem (x, y, z)
    project_folder = f"{neuer_ordner_pfad}"

    main()
    create_renderer_html(project_folder, "./cleanModel.stl", "./filling_Piece.stl")
    show_mesh(filling_Piece_model_output_path, [255,255,255])
