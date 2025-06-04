# utils.py
from django.apps import apps
ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
MAX_FILE_SIZE_MB = 5
MAX_FILES_UPLOAD = 10

def validate_uploaded_files(files, allowed_ext=None, max_size_mb=None, max_files=None):
    """
    Valide une liste de fichiers uploadés.
    Retourne une liste d’erreurs et les fichiers valides.
    """
    allowed_ext = allowed_ext or ALLOWED_EXTENSIONS
    max_size_mb = max_size_mb or MAX_FILE_SIZE_MB
    max_files = max_files or MAX_FILES_UPLOAD

    errors = []
    valid_files = []

    if len(files) > max_files:
        errors.append(f"Vous ne pouvez uploader que {max_files} fichiers à la fois.")
        return errors, []

    for file in files:
        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_ext:
            errors.append(f"Type de fichier non autorisé : {file.name}")
        elif file.size > max_size_mb * 1024 * 1024:
            errors.append(f"Fichier trop volumineux ({file.name}) : max {max_size_mb} Mo.")
        else:
            valid_files.append(file)

    return errors, valid_files



