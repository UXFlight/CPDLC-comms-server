import json
import re

# Lire le fichier JSON
with open('app/database/DownLinks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def convert_response_required(value):
    """Convertit la valeur Response_required en tableau de chaînes"""
    if isinstance(value, list):
        # Déjà un tableau, s'assurer que tous les éléments sont des chaînes
        return [str(item) for item in value]
    elif isinstance(value, str):
        if value == "Y":
            return ["Y"]
        elif value == "N":
            return ["N"]
        elif value == "Y or N":
            return ["Y", "N"]
        elif value.startswith("Y "):
            # Pour les cas comme "Y UM 0 UM 1 UM 19..."
            # Diviser par les espaces et garder "Y" + tous les codes UM
            parts = value.split()
            result = ["Y"]
            for part in parts[1:]:  # Ignorer le premier "Y"
                if part and part != "+":  # Ignorer les "+" qui sont des connecteurs
                    result.append(part)
            return result
        else:
            return [value]
    else:
        return [str(value)]

# Convertir tous les objets
for obj in data:
    if 'Response_required' in obj:
        obj['Response_required'] = convert_response_required(obj['Response_required'])

# Sauvegarder le fichier modifié
with open('app/database/DownLinks.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Conversion terminée! Tous les Response_required sont maintenant des tableaux de chaînes.")
