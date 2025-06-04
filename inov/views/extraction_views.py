import os
import json
import tempfile
import zipfile
import shutil
import concurrent.futures
import csv
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from document_processor.domain.entities import Facture as FactureEntity
from document_processor.file_extractor import extract_info
from inov.forms import FolderForm
from inov.mapping.mapping import map_bilan_entity_to_model, map_facture_entity_to_model, map_releve_entity_to_model
from inov.mapping.serializers import BilanComptableSerializer, FactureSerializer, ReleveBancaireSerializer
from inov.models import BilanComptable, ExtractionConfiguration, File, Folder, ReleveBancaire, Facture, UserPreferences

from document_processor.file_extractor import classify_file
def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary into a single-level dictionary with dot-separated keys.
    """
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def get_flattened_headers(champs_choisis, filtered_data_example=None):
    """
    Generate CSV headers by flattening champs_choisis fields.
    If filtered_data_example is provided, ensure all nested fields are included.
    """
    headers = []
    for field in champs_choisis:
        if filtered_data_example and isinstance(filtered_data_example.get(field), dict):
            nested_dict = filtered_data_example.get(field, {})
            flattened = flatten_dict(nested_dict)
            headers.extend([f"{field}.{k}" for k in flattened.keys()])
        else:
            headers.append(field)
    return headers

def process_extraction(file_path, file_instance, extraction_model):
    """
    Process a file to extract and filter data based on the extraction model's chosen fields.
    Returns only the filtered data (dictionary of chosen fields).
    """
    try:
        result = extract_info(file_path)
        structured_data = result.get('structured_data', {})
        document_type = result.get('document_type', 'unknown')
        insights = result.get('insights', '')

        champs_choisis = extraction_model.champs_choisis if extraction_model else []
        filtered_data = {field: structured_data.get(field) for field in champs_choisis if field in structured_data}
        print("🔍 Données filtrées pour le type", document_type, ":", json.dumps(filtered_data, indent=2, ensure_ascii=False))

        if document_type == "facture" and filtered_data:
            try:
                facture_entity = FactureEntity(**structured_data)
                facture_model = map_facture_entity_to_model(facture_entity, insights)
                facture_model.file = file_instance
                facture_model.save()
            except IntegrityError as e:
                if 'duplicate key value violates unique constraint' in str(e):
                    pass
                else:
                    raise

        elif document_type == "bilan" and filtered_data:
            try:
                entity = BilanComptable(**structured_data)
                model_instance = map_bilan_entity_to_model(entity, insights)
                model_instance.file = file_instance
                model_instance.save()
            except IntegrityError as e:
                if 'duplicate key value violates unique constraint' in str(e):
                    pass
                else:
                    raise

        elif document_type == "releve" and filtered_data:
            try:
                entity = ReleveBancaire(**structured_data)
                model_instance = map_releve_entity_to_model(entity, insights)
                model_instance.file = file_instance
                model_instance.save()
            except IntegrityError as e:
                if 'duplicate key value violates unique constraint' in str(e):
                    pass
                else:
                    raise

        return filtered_data

    except Exception as e:
        print(f"Erreur lors de l'extraction: {str(e)}")
        return {}



def export_to_csv(data_list, doc_type, champs_choisis, temp_dir, folder_name):
    """
    Export extracted data to a CSV file with flattened champs_choisis fields.
    Uses 'N/A' for None or missing values and replaces newlines with spaces.
    """
    if not data_list:
        return None, None

    csv_filename = f'extraction_{doc_type}_{folder_name.replace(" ", "_")}.csv'
    csv_path = os.path.join(temp_dir, csv_filename)

    # Use the first data item to determine nested fields
    filtered_data_example = data_list[0].get('filtered_data', {}) if data_list else {}
    headers = get_flattened_headers(champs_choisis, filtered_data_example)

    with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()

        for data in data_list:
            filtered_data = data.get('filtered_data', {})
            flattened_data = flatten_dict(filtered_data)
            # Use 'N/A' for None/missing and replace newlines with spaces
            row = {
                key: 'N/A' if key not in flattened_data or flattened_data[key] is None else str(flattened_data[key]).replace('\n', ' ').replace('\r', ' ')
                for key in headers
            }
            writer.writerow(row)

    return csv_filename, csv_path

def extract_and_write(file, temp_dir, model_mapping, folder_type, output_format='json'):
    try:
        file_path = file.file.path
        doc_type = folder_type or 'unknown'
        extraction_model = model_mapping.get(doc_type)

        filtered_data = process_extraction(file_path, file, extraction_model)
        
        if output_format == 'json':
            json_filename = f'extraction_{file.id}_{file.filename}.json'
            json_path = os.path.join(temp_dir, json_filename)

            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(filtered_data, json_file, ensure_ascii=False, indent=2)

            return ('success', json_filename, json_path, {'filtered_data': filtered_data, 'document_type': doc_type})
        else:  # csv
            return ('success', None, None, {'filtered_data': filtered_data, 'document_type': doc_type})

    except Exception as e:
        error_filename = f'error_{file.id}_{file.filename}.json'
        error_path = os.path.join(temp_dir, error_filename)
        error_data = {'error': str(e)}
        with open(error_path, 'w', encoding='utf-8') as error_file:
            json.dump(error_data, error_file, ensure_ascii=False, indent=2)

        return ('error', error_filename, error_path, None)

@csrf_exempt
def extract_folder_files(request):
    try:
        folder_id = request.POST.get('folder_id')
        selected_model_ids = request.POST.getlist('models[]')
        output_format = request.POST.get('format', 'json')

        if not folder_id:
            return JsonResponse({'error': 'Aucun dossier spécifié'}, status=400)

        folder = get_object_or_404(Folder, id=folder_id)
        folder_type = folder.type

        files = File.objects.filter(folder=folder)
        if not files.exists():
            return JsonResponse({'error': 'Aucun fichier trouvé dans ce dossier'}, status=404)

        model_mapping = {}
        for model_id in selected_model_ids:
            model = ExtractionConfiguration.objects.filter(id=model_id).first()
            if model:
                model_mapping[model.type_document] = model

        temp_dir = tempfile.mkdtemp()
        zip_filename = f'extractions_{folder.name.replace(" ", "_")}.zip'
        zip_path = os.path.join(temp_dir, zip_filename)

        results = []
        csv_data = {'facture': [], 'bilan': [], 'releve': []}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(extract_and_write, file, temp_dir, model_mapping, folder_type, output_format) for file in files]
            for future in concurrent.futures.as_completed(futures):
                status, filename, path, data = future.result()
                results.append((status, filename, path))
                if output_format == 'csv' and status == 'success' and data:
                    doc_type = data.get('document_type')
                    if doc_type in csv_data:
                        csv_data[doc_type].append(data)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if output_format == 'json':
                for status, filename, path in results:
                    if filename and path:
                        zip_file.write(path, filename)
            else:
                for doc_type in csv_data:
                    if csv_data[doc_type]:
                        extraction_model = model_mapping.get(doc_type)
                        champs_choisis = extraction_model.champs_choisis if extraction_model else []
                        csv_filename, csv_path = export_to_csv(csv_data[doc_type], doc_type, champs_choisis, temp_dir, folder.name)
                        if csv_filename and csv_path:
                            zip_file.write(csv_path, csv_filename)

        response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        shutil.rmtree(temp_dir, ignore_errors=True)
        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def extraction_view(request):
   

   

    comptable = getattr(request.user, 'comptable', None)
    folders = Folder.objects.filter(comptable=comptable)
    folder_form = FolderForm()

    context = {
        'folders': folders,
        'folder_form': folder_form,
        'successes': [],
        'errors': []
    }

    if request.method == 'POST':
        if 'name' in request.POST:
            folder_form = FolderForm(request.POST)
            if folder_form.is_valid():
                new_folder = folder_form.save(commit=False)
                new_folder.comptable = comptable
                new_folder.save()
                context['successes'].append('Dossier créé avec succès!')
                return render(request, 'pages/extraction.html', context)

        elif 'folder_id' in request.POST and request.FILES.getlist('files'):
          folder = get_object_or_404(Folder, id=request.POST.get('folder_id'), comptable=comptable)
          files = request.FILES.getlist('files')
 
          fichiers_valides = []

          for uploaded_file in files:
               result = classify_file(uploaded_file, expected_type=folder.type)
               if result["valid"]:
                  fichiers_valides.append(uploaded_file)
               else:
                  context['errors'].append(result["error"])

          for f in fichiers_valides:
           File.objects.create(folder=folder, file=f)

          if fichiers_valides:
              context['successes'].append(
              f"{len(fichiers_valides)} fichiers ajoutés avec succès à {folder.name}."
        )

    return render(request, 'pages/extraction.html', context)



def get_default_models(request, folder_id):  
    user = request.user

    try:
        folder = Folder.objects.get(id=folder_id)
    except Folder.DoesNotExist:
        return JsonResponse({'error': 'Dossier non trouvé'}, status=404)

    folder_type = folder.type
    user_preferences = getattr(user, 'preferences', None)
    response_data = []

    types_to_check = ['facture', 'bilan', 'releve'] if folder_type == 'mixte' else [folder_type]

    for doc_type in types_to_check:
        doc_models = []
        preferred_model_id = None

        if user_preferences and user_preferences.default_extraction_models:
            preferred_model_id = user_preferences.default_extraction_models.get(doc_type)

        if preferred_model_id:
            preferred_model = ExtractionConfiguration.objects.filter(id=preferred_model_id).first()
            if preferred_model:
                doc_models.append({
                    'id': preferred_model.id,
                    'name': f"⭐ {preferred_model.name} | modèle préféré ({len(preferred_model.champs_choisis)} champs)",
                    'champs': preferred_model.champs_choisis,
                    'type_document': doc_type,
                    'is_default': True
                })

        default_model = ExtractionConfiguration.objects.filter(user__isnull=True, type_document=doc_type).first()
        if default_model and (not preferred_model_id or default_model.id != preferred_model_id):
            doc_models.append({
                'id': default_model.id,
                'name': f"🌐 {default_model.name} | modèle global par défaut ({len(default_model.champs_choisis)} champs)",
                'champs': default_model.champs_choisis,
                'type_document': doc_type,
                'is_default': folder_type == 'mixte' and not preferred_model_id
            })

        user_models = ExtractionConfiguration.objects.filter(user=user, type_document=doc_type).exclude(id=preferred_model_id)
        for model in user_models:
            nb_champs = len(model.champs_choisis)
            doc_models.append({
                'id': model.id,
                'name': f"{model.name} ({nb_champs} champs)",
                'champs': model.champs_choisis,
                'type_document': doc_type,
                'is_default': False
            })

        response_data.append({
            'type_document': doc_type,
            'models': doc_models
        })

    return JsonResponse({'data': response_data})



@csrf_exempt
def extract_data(request, file_id):
    """
    Extrait les données d'un fichier unique avec un modèle donné (uniquement JSON)
    """
    file = get_object_or_404(File, id=file_id)

    try:
        file_path = file.file.path
        model_id = request.POST.get('model_id')

        if not model_id:
            return JsonResponse({'error': 'Aucun modèle fourni'}, status=400)

        extraction_model = ExtractionConfiguration.objects.filter(id=model_id).first()
        if not extraction_model:
            return JsonResponse({'error': 'Modèle introuvable'}, status=404)

        output_data = process_extraction(file_path, file, extraction_model)
         # ✅ Sauvegarde des données extraites dans la base pour q'on puisse apres faire la validation
        file.extraction_data = output_data
        file.save()
        json_data = json.dumps(output_data, ensure_ascii=False, indent=2)

        return HttpResponse(
            json_data,
            content_type='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=extraction_{file_id}.json'
            }
        )

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
