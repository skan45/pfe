from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files import File

from .models import (
    Client,
    Comptable,
    Facture,
    Task,
    Folder,
    File as UploadedFile,
    ExtractionConfiguration
)

# --- User & Role Forms ---

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("E-mail déjà utilisé !")
        return email


class UserRoleForm(forms.Form):
    ROLE_CHOICES = [
        ('Comptable', 'Comptable'),
        ('Client', 'Client'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# --- Client & Comptable Forms ---

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prénom', 'email', 'phone', 'description', 'adresse']


class ComptableForm(forms.ModelForm):
    class Meta:
        model = Comptable
        fields = ['nom', 'prénom', 'email', 'phone', 'description', 'adresse']

# --- Facture Forms ---

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = '__all__'

# --- Task Form ---

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Task
        fields = ["description", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

# --- Folder and File Forms ---

class FolderForm(forms.ModelForm):
   
  
    
    """Form for creating and editing folders."""
    class Meta:
        model = Folder
        fields = ['name', 'type']
        labels = {
            'type': 'Type de document',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control  custom-height',
                'placeholder': 'Nom du dossier',
                'required': True
            }),
            #ajouter le type ici 
            'type': forms.Select(attrs={
                'class': 'form-select form-select-lg custom-height',
                'required': True,
            })
            }
       

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter une option vide au début avec le texte personnalisé
        self.fields['type'].choices = [('', 'Type')] + list(self.fields['type'].choices)
class FileUploadForm(forms.Form):
    """Form for uploading files to a folder."""
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
            'class': 'form-control'
        })
    )

class FileEditForm(forms.ModelForm):
    """Form for editing file metadata."""
    class Meta:
        model = UploadedFile
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            })
        }

# --- Extraction Configuration ---

class ExtractionConfigurationForm(forms.ModelForm):
    class Meta:
        model = ExtractionConfiguration
        fields = ['type_document']

class ExtractionConfigurationForm(forms.ModelForm):
    """Formulaire pour la création et la modification de modèles d'extraction"""
    
    class Meta:
        model = ExtractionConfiguration
        fields = ['name', 'type_document', 'champs_choisis']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du modèle'}),
            'type_document': forms.Select(attrs={'class': 'form-control'}),
            'champs_choisis': forms.MultipleHiddenInput()
        }
        labels = {
            'name': 'Nom du modèle',
            'type_document': 'Type de document',
            'champs_choisis': 'Champs à extraire'
        }
        
    def clean_champs_choisis(self):
        """Validation pour s'assurer qu'au moins un champ est sélectionné"""
        champs = self.cleaned_data.get('champs_choisis')
        if not champs or len(champs) < 1:
            raise forms.ValidationError("Veuillez sélectionner au moins un champ à extraire.")
        return champs