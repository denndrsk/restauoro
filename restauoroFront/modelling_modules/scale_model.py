import sys
import trimesh
import os

def scale_model(raw_model_path, scale_factor, output_path):
    """
    Skaliert das Modell basierend auf dem gegebenen Scale-Faktor.
    
    :param raw_model_path: Pfad zur Raw-Modell-STL-Datei
    :param scale_factor: Der Skalierungsfaktor
    :param output_path: Pfad, wo das skalierte Modell gespeichert werden soll
    """
    # Lade das Modell
    model = trimesh.load_mesh(raw_model_path)
    print("Scale factor:", scale_factor)
    # Skaliere das Modell
    model.apply_scale(scale_factor)
    
    # Speichere das skalierte Modell
    model.export(output_path)
    print(f"Skaliertes Modell gespeichert unter: {output_path}")

if __name__ == "__main__":
    # Übernehme Argumente aus der Kommandozeile
    raw_model_path = sys.argv[1]  # Pfad zum Rohmodell
    scale_factor = float(sys.argv[2])  # Skalierungsfaktor
    output_path = sys.argv[3]  # Zielpfad für das skalierte Modell

    # Modell skalieren
    scale_model(raw_model_path, scale_factor, output_path)
