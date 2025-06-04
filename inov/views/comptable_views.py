
from django.shortcuts import  redirect, render
from inov.decorators import allowed_users
from inov.forms import ComptableForm, FactureForm
from inov.models import Client, Comptable, Facture,Invitation
import os
from django.utils.dateparse import parse_date

import json
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from document_processor.domain.entities import Facture as FactureEntity
from document_processor.file_extractor import extract_info
from inov.forms import FolderForm
from inov.models import BilanComptable, ExtractionConfiguration, File, Facture, UserPreferences




def edit_extraction_data(request, file_id):
    # Récupère l'objet file
    file = get_object_or_404(File, id=file_id)

    # Vérifie que des données sont extraites
    if not file.extraction_data:
        return JsonResponse({'error': 'Aucune donnée extraite à modifier'}, status=404)

    # Si la requête est en POST, on met à jour les données extraites
    if request.method == 'POST':
        updated_data = {}
        
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                # Découper les noms des clés imbriquées (par exemple 'informations.nom')
                keys = key.split('.')
                temp = updated_data
                for part in keys[:-1]:
                    temp = temp.setdefault(part, {})
                temp[keys[-1]] = value

        # Met à jour les données extraites dans le fichier
        file.extraction_data = updated_data
        file.save()

        # Redirige après la sauvegarde des données
        return redirect('FactureComptable')  # redirige vers une page de confirmation ou liste

    # Récupère les données existantes pour l'affichage dans le formulaire
    return render(request, 'pages/formulaire-facture.html', {'file': file, 'extraction_data': file.extraction_data})

     

def get_default_models_for_file(request, file_id):
    user = request.user
    file = get_object_or_404(File, id=file_id)

    # Exemple : récupérer le type_document depuis les données extraites, sinon par défaut "facture"
    doc_type = file.extraction_data.get("type_document") if file.extraction_data else "facture"
    print("DOC_TYPE:", doc_type)

    response_data = []

    doc_models = []
    preferred_model_id = None

    user_preferences = getattr(user, 'preferences', None)
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

    # Ajout modèle global
    default_model = ExtractionConfiguration.objects.filter(user__isnull=True, type_document=doc_type).first()
    if default_model and (not preferred_model_id or default_model.id != preferred_model_id):
        doc_models.append({
            'id': default_model.id,
            'name': f"🌐 {default_model.name} | modèle global ({len(default_model.champs_choisis)} champs)",
            'champs': default_model.champs_choisis,
            'type_document': doc_type,
            'is_default': not preferred_model_id
        })

    # Modèles utilisateur
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

@allowed_users(allowed_roles=['Comptable'])
def FactureComptable(request):
    comptable = Comptable.objects.filter(user=request.user).first()

    accepted_invitations = Invitation.objects.filter(from_comptable=comptable, status='Accepted')
    client_emails = accepted_invitations.values_list('to_client_email', flat=True)
    clients = Client.objects.filter(email__in=client_emails)

    client_id = request.GET.get('client_id')
    statut = request.GET.get('statut')
    date_creation = request.GET.get('dateCreation')  # Format : YYYY-MM-DD

    factures = Facture.objects.filter(client__in=clients)

    selected_client = None
    if client_id:
        selected_client = clients.filter(id=client_id).first()
        if selected_client:
            factures = factures.filter(client=selected_client)

    if statut:
        factures = factures.filter(status=statut)

    if date_creation:
        # Convertir date en objet Python
        try:
            parsed_date = parse_date(date_creation)
            if parsed_date:
                factures = factures.filter(
                    file__uploaded_at__date=parsed_date
                )
        except ValueError:
            pass  # Mauvais format

    context = {
        'clients': clients,
        'selected_client': selected_client,
        'fact': factures,
        'selected_statut': statut,
        'selected_date': date_creation,
    }
    return render(request, 'pages/facture-comptable.html', context)




def acceuil(request):
    return render(request,'home/index.html')



#@login_required
@allowed_users(allowed_roles=['Comptable'])
def home(request):
    """Home page for accountants."""
    clients = Client.objects.all()
    
    # Collect statistics
    client_stats = []
    total_non_valide = 0
    total_valide = 0
    
    for client in clients:
        factures = client.factures.all()
        facture_count = factures.count()
        client_stats.append({
            'client': client,
            'facture_count': facture_count
        })
        
        # Count invoices by status
        total_non_valide += factures.filter(status='Non Validé').count()
        total_valide += factures.filter(status='Validé').count()

    context = {
        'client_stats': client_stats,
        'total_non_valide': total_non_valide,
        'total_valide': total_valide
    }
    
    return render(request, "pages/index.html", context)
