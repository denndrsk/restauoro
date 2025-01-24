import os
import shutil

def erstelle_neuen_ordner(basis_pfad="static/models"):
    """
    Erstellt einen neuen Ordner mit einem inkrementierenden Projektnamen im angegebenen Basisverzeichnis.

    Args:
        basis_pfad (str): Der Basisordner, in dem der neue Ordner erstellt wird.

    Returns:
        str: Der Pfad des erstellten Ordners.
    """
    os.makedirs(basis_pfad, exist_ok=True)
    vorhandene_ordner = [
        name for name in os.listdir(basis_pfad) if os.path.isdir(os.path.join(basis_pfad, name))
    ]
    projekt_nummern = [
        int(name.split("_")[1]) for name in vorhandene_ordner if name.startswith("project_") and name.split("_")[1].isdigit()
    ]
    neue_nummer = max(projekt_nummern, default=0) + 1
    neuer_ordner_name = f"project_{neue_nummer}"
    neuer_ordner_pfad = os.path.join(basis_pfad, neuer_ordner_name)
    os.makedirs(neuer_ordner_pfad, exist_ok=True)
    return neuer_ordner_pfad

def verschiebe_datei(datei_pfad, ziel_ordner):
    """
    Verschiebt eine Datei in einen Zielordner.

    Args:
        datei_pfad (str): Der Pfad zur Datei, die verschoben werden soll.
        ziel_ordner (str): Der Zielordner, in den die Datei verschoben wird.
    """
    try:
        if not os.path.exists(ziel_ordner):
            os.makedirs(ziel_ordner)
        shutil.move(datei_pfad, os.path.join(ziel_ordner, os.path.basename(datei_pfad)))
        print(f"Datei '{datei_pfad}' wurde nach '{ziel_ordner}' verschoben.")
    except Exception as e:
        print(f"Fehler beim Verschieben der Datei: {e}")