"""
Script pour corriger l'encodage des fichiers JSON
"""

import json
import os

def fix_json_encoding(file_path):
    """
    Lit un fichier JSON en essayant différents encodages et le réécrit en UTF-8
    """
    # Liste des encodages à essayer
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']
    
    # Essayer chaque encodage jusqu'à ce qu'un fonctionne
    data = None
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                print(f"Essai de lecture avec l'encodage {encoding}...")
                data = json.load(f)
            print(f"Succès avec l'encodage {encoding}")
            break
        except UnicodeDecodeError:
            print(f"Échec avec l'encodage {encoding}")
            continue
        except json.JSONDecodeError:
            print(f"Fichier valide en {encoding} mais pas un JSON valide")
            continue
    
    # Si aucun encodage ne fonctionne
    if data is None:
        print("Impossible de lire le fichier avec les encodages essayés")
        return False
    
    # Sauvegarder le fichier en UTF-8
    try:
        with open(file_path + '.bak', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Renommer les fichiers
        os.rename(file_path, file_path + '.old')
        os.rename(file_path + '.bak', file_path)
        print(f"Fichier {file_path} converti et sauvegardé en UTF-8")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return False

if __name__ == "__main__":
    # Chemin du fichier users.json
    users_file = os.path.join("user_data", "users.json")
    
    if os.path.exists(users_file):
        print(f"Correction de l'encodage de {users_file}...")
        fix_json_encoding(users_file)
    else:
        print(f"Le fichier {users_file} n'existe pas.")
