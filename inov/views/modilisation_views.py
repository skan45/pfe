from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Q

from inov.models import BilanComptable, ExtractionConfiguration, Facture, ReleveBancaire, UserPreferences

MODEL_MAP = {
    'facture': Facture,
    'releve': ReleveBancaire,
    'bilan': BilanComptable
}

@login_required
def modelisation_view(request):
    """Vue pour créer un nouveau modèle d'extraction"""
    if request.method == "POST":
        return save_extraction_model(request)

    doc_type = request.GET.get('document_type', '')
    context = {
        'title': 'Créer un modèle d\'extraction',
        'doc_type': doc_type,
    }
    return render(request, 'pages/modelisation.html', context)

@login_required
def get_fields(request):
    """Récupère les champs pour un type de document spécifique"""
    doc_type = request.GET.get('document_type')

    if doc_type in MODEL_MAP:
        model = MODEL_MAP[doc_type]
        fields = [
            f.name for f in model._meta.fields + model._meta.many_to_many
            if f.name != 'id'
        ]
        return JsonResponse({'fields': fields})

    return JsonResponse({'error': 'Type non valide'}, status=400)

@login_required
@require_POST
def save_extraction_model(request):
    """Sauvegarde un nouveau modèle d'extraction"""
    name = request.POST.get("model_name", "Modèle sans nom")
    type_document = request.POST.get("document_type")
    fields = request.POST.getlist("fields")

    if not type_document or not fields:
        return JsonResponse({
            "status": "error",
            "message": "Veuillez sélectionner un type de document et au moins un champ."
        })

    model = ExtractionConfiguration.objects.create(
        user=request.user,
        name=name,
        type_document=type_document,
        champs_choisis=fields
    )
    return JsonResponse({
        "status": "success",
        "message": "Modèle enregistré avec succès !"
    })

@login_required
def liste_modeles(request):
    """Liste tous les modèles d'extraction de l'utilisateur et les modèles génériques"""
    type_filter = request.GET.get('type', '')

    models = ExtractionConfiguration.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    )

    if type_filter:
        models = models.filter(type_document=type_filter)

    preferred_models = {}     
    if hasattr(request.user, 'preferences'):  
     preferred_models = getattr(request.user.preferences, 'default_extraction_models', {}) or {}
    print(request.user)

    for model in models:
        if preferred_models.get(model.type_document) == model.id:
            model.name = f"⭐ {model.name}"

    context = {
        'title': 'Mes modèles d\'extraction',
        'models': models,
        'type_filter': type_filter,
        'types': ExtractionConfiguration.TypeDocument.choices
    }
    return render(request, 'pages/liste_modeles.html', context)

@login_required
def detail_modele(request, pk):
    """Affiche les détails d'un modèle d'extraction (personnel ou générique)"""
    model = get_object_or_404(
        ExtractionConfiguration,
        Q(pk=pk) & (Q(user=request.user) | Q(user__isnull=True))
    )

    field_labels = {}
    if model.type_document in MODEL_MAP:
        model_class = MODEL_MAP[model.type_document]
        valid_fields = {f.name: f.verbose_name for f in model_class._meta.fields}
        for champ in model.champs_choisis:
            if champ in valid_fields:
                field_labels[champ] = valid_fields[champ]

    context = {
        'title': f'Détails du modèle : {model.name}',
        'model': model,
        'field_labels': field_labels
    }
    return render(request, 'pages/detail_modele.html', context)

@login_required
@require_POST
def supprimer_modele(request, pk):
    """Supprime un modèle d'extraction (seulement s'il appartient à l'utilisateur)"""
    model = get_object_or_404(ExtractionConfiguration, pk=pk)

    if model.user is None:
        return render(request, 'pages/message.html', {
            "title": "Suppression impossible",
            "message": "Ce modèle est générique et ne peut pas être supprimé."
        })

    if model.user != request.user:
        return render(request, 'pages/message.html', {
            "title": "Accès refusé",
            "message": "Vous n'avez pas les droits pour supprimer ce modèle."
        })

    model.delete()
    return redirect('liste_modeles')

@login_required
@require_POST
def set_default_model(request, pk):
    """Définit un modèle comme modèle par défaut (seulement s'il appartient à l'utilisateur)"""
    model = get_object_or_404(ExtractionConfiguration, pk=pk)

    if model.user is None:
        return JsonResponse({
            "status": "error",
            "message": "Ce modèle est générique et ne peut pas être défini comme modèle par défaut."
        }, status=403)

    if model.user != request.user:
        return JsonResponse({
            "status": "error",
            "message": "Vous n'avez pas les droits pour définir ce modèle par défaut."
        }, status=403)

    user_prefs, _ = UserPreferences.objects.get_or_create(user=request.user)

    if not isinstance(user_prefs.default_extraction_models, dict):
        user_prefs.default_extraction_models = {}

    user_prefs.default_extraction_models[model.type_document] = model.id
    user_prefs.save()

    return JsonResponse({
        "status": "success",
        "message": f"{model.name} défini comme modèle par défaut pour {model.get_type_document_display()}."
    })
