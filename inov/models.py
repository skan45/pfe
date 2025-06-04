from django.db import models
from django.contrib.auth.models import AbstractUser , User
import uuid
from datetime import date
from django.utils import timezone
class Client(models.Model):
   
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    email = models.EmailField()
    nom = models.CharField(max_length=200, null=True)
    prénom = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    CHOICES = [('Comptable', 'Comptable'),('Client', 'Client'),]
    status = models.CharField(max_length=200,choices=CHOICES,default='Client',)
    profile_pic = models.ImageField(default="profile1.png", null=True, blank=True)
    phone=models.CharField(max_length=200, null=True)
    description=models.CharField(max_length=500, null=True)
    adresse=models.CharField(max_length=500, null=True)
   

    def __str__(self):
        return self.user.username


class Comptable(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nom = models.CharField(max_length=200, null=True)
    prénom = models.CharField(max_length=200, null=True)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    CHOICES = [('Comptable', 'Comptable'),('Client', 'Client'),]
    status = models.CharField(max_length=200,choices=CHOICES,default='Comptable',)
    profile_pic = models.ImageField(default="profile1.png", null=True, blank=True)
    description=models.CharField(max_length=500, null=True)
    adresse=models.CharField(max_length=500, null=True)
    phone=models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.user.username
class Task(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),  # La date limite n'a pas encore été atteinte
        ('Passed', 'Passée'),  # La date limite est atteinte mais la tâche n'est pas faite
        ('Completed', 'Terminée')  # La tâche est complétée
    ]

    title = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(Comptable ,related_name="tasks", on_delete=models.CASCADE)
    def __str__(self):
        return self.title

    def update_status(self):
        """ Met à jour le statut en 'passed' si la date limite est dépassée et que la tâche n'est pas complétée. """
        if self.due_date and self.status != 'completed' and self.due_date < date.today():
            self.status = 'Passed'
            self.save()

class Invitation(models.Model):
    invite_code = models.UUIDField(default=uuid.uuid4, unique=True)
    from_comptable = models.ForeignKey(Comptable, on_delete=models.CASCADE)
    to_client_email = models.EmailField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted')], default='Pending')
    date_sent = models.DateTimeField(auto_now_add=True)
    date_accepted = models.DateTimeField(null=True, blank=True) 


    def __str__(self):
      return f"Invitation from {self.from_comptable.user.username} to {self.to_client_email} - Status: {self.status}"






class Folder(models.Model):
    """Model for document folders."""
    FOLDER_TYPE_CHOICES = [
        ('bilan', 'Bilan'),
        ('facture', 'Facture'),
        ('releve', 'Relevé'),
        ('mixte', 'Mixte'),
    ]
    name = models.CharField(max_length=255, verbose_name="Nom du dossier")
    color = models.CharField(max_length=20, default="#6c757d", verbose_name="Couleur")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    comptable = models.ForeignKey('Comptable', null=True, blank=True,on_delete=models.CASCADE)
    type = models.CharField(  
        max_length=10,
        choices=FOLDER_TYPE_CHOICES,
        verbose_name="Type de dossier"
    )# chaque dossier a un type selon son contenu 
    
    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def file_count(self):
        return self.files.count()

class File(models.Model):
   

    """Model for files stored in folders."""
    folder = models.ForeignKey(
        Folder, 
        related_name='files', 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    file = models.FileField(upload_to='extraction_files/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name="Date d'ajout")
    extraction_status = models.CharField(max_length=20, default="pending", choices=[
        ("pending", "En attente"),
        ("processing", "En cours"),
        ("completed", "Terminé"),
        ("failed", "Échec")
    ])
    extraction_data = models.JSONField(null=True, blank=True)
   
    
    class Meta:
        verbose_name = "Fichier"
        verbose_name_plural = "Fichiers"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file.name.split('/')[-1]} ({self.folder.name})"
    
    @property
    def filename(self):
        return self.file.name.split('/')[-1]
    
    @property
    def file_extension(self):
        return self.filename.split('.')[-1].lower()
    
    @property
    def file_type(self):
        ext = self.file_extension
        if ext in ['pdf']:
            return 'pdf'
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return 'image'
        elif ext in ['doc', 'docx']:
            return 'word'
        elif ext in ['xls', 'xlsx']:
            return 'excel'
        else:
            return 'other'

#####partie modeles et extraction #######
class ContactInformation(models.Model):
    nom = models.CharField(max_length=255)
    adresse = models.TextField()
    numero_telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

def __str__(self):
        return f"{self.nom} - {self.email or 'Email non défini'}"




class Produit(models.Model):
    description = models.TextField()
    quantite = models.FloatField()
    prix_unitaire = models.FloatField()
    montant_total = models.FloatField()
def __str__(self):
        return f"{self.description} - {self.quantite} x {self.prix_unitaire} = {self.montant_total}"


def generate_default_facture_numero():
    return f"FACT-{uuid.uuid4().hex[:8]}"

class Facture(models.Model):
    date_echeance = models.CharField(max_length=100, null=True, blank=True, default="À définir")
    numero_facture = models.CharField(
        max_length=100,
        unique=True,
        default=generate_default_facture_numero
    )
    
    status = models.CharField(max_length=200, null=True, default='Non Validé')
    informations = models.ForeignKey(
        ContactInformation,
        on_delete=models.CASCADE,
        related_name="factures_emises",
        null=True,
        blank=True,
        default=None
    )

    informations_client = models.ForeignKey(
        ContactInformation,
        on_delete=models.CASCADE,
        related_name="factures_recues",
        null=True,
        blank=True,
        default=None
    )

    produits = models.ManyToManyField(Produit, related_name='factures')

    tva = models.FloatField(default=0.0)
    montant_ttc = models.FloatField(default=0.0)

    methode_de_paiement = models.CharField(max_length=100, blank=True, null=True)
    insights = models.TextField(blank=True, null=True)

    file = models.OneToOneField(
        File,
        on_delete=models.CASCADE,
        related_name="facture",
        null=True,
        blank=True,
        default=None
    )
    
    comptable = models.ForeignKey(
        Comptable,
        on_delete=models.CASCADE,
        related_name="factures",
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="factures",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Facture {self.numero_facture} pour {self.informations_client.nom if self.informations_client else 'Client inconnu'}"


class BilanComptable(models.Model):
    #date_echeance = models.DateTimeField()
    date_debut = models.CharField(max_length=100, null=True, blank=True, default="À définir") # a voir !
    date_fin = models.CharField(max_length=100, null=True, blank=True, default="À définir")
    total_actif = models.FloatField()
    total_passif = models.FloatField()
    capitaux_propres = models.FloatField()
    insights = models.TextField(blank=True, null=True) 
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name="bilan", null=True, blank=True)
    status = models.CharField(max_length=200, null=True, default='Non Validé')
    
    # New fields for Comptable and Client relationships
    comptable = models.ForeignKey(
        Comptable,
        on_delete=models.CASCADE,
        related_name="bilans",
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="bilans",
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"Bilan {self.date_debut.date() if hasattr(self.date_debut, 'date') else self.date_debut} → {self.date_fin.date() if hasattr(self.date_fin, 'date') else self.date_fin}"



class TransactionBancaire(models.Model):
    date = models.CharField(max_length=100, null=True, blank=True, default="À définir")
    date_valeur = models.CharField(max_length=100, null=True, blank=True, default="À définir")
    credit = models.FloatField()
    debit = models.FloatField()
    libelle = models.TextField()
    def __str__(self):
        return self.libelle


class ReleveBancaire(models.Model):
    titulaire_compte = models.ForeignKey(ContactInformation, on_delete=models.CASCADE, related_name="releves_bancaires")
    status = models.CharField(max_length=200, null=True, default='Non Validé')
    numero_compte = models.CharField(max_length=50)
    date_debut = models.CharField(max_length=100, null=True, blank=True, default="À définir")
    date_fin = models.CharField(max_length=100, null=True, blank=True, default="À définir")
    transactions = models.ManyToManyField(TransactionBancaire)
    solde_ouverture = models.FloatField()
    solde_cloture = models.FloatField()
    insights = models.TextField(blank=True, null=True) 
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name="releve", null=True, blank=True)
    
    # New fields for Comptable and Client relationships
    comptable = models.ForeignKey(
        Comptable,
        on_delete=models.CASCADE,
        related_name="releves",
        null=True,
        blank=True
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="releves",
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"Relevé {self.numero_compte} - {self.date_debut.date()} → {self.date_fin.date()}"




class UserPreferences(models.Model):
    """Modèle pour stocker les préférences utilisateur, y compris les modèles d'extraction par défaut"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    default_extraction_models = models.JSONField(null=True, blank=True, 
                                               help_text="Modèles d'extraction par défaut pour chaque type de document")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Préférences de {self.user.username}"

class ExtractionConfiguration(models.Model):
    """Configuration d'extraction de documents pour un utilisateur"""
    class TypeDocument(models.TextChoices):
        FACTURE = 'facture', 'Facture'
        RELEVE = 'releve', 'Relevé'
        BILAN = 'bilan', 'Bilan'
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extraction_configs', null=True, ) #null essentiel pour definir les models
    name = models.CharField(max_length=100, verbose_name="Nom du modèle")
    type_document = models.CharField(max_length=20, choices=TypeDocument.choices, verbose_name="Type de document")
    champs_choisis = models.JSONField(verbose_name="Champs sélectionnés")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration d'extraction"
        verbose_name_plural = "Configurations d'extraction"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_type_document_display()} ({self.user.username})"

    def is_default(self, user):
        """Vérifie si ce modèle est défini comme modèle par défaut pour son type"""
        try:
            prefs = user.preferences
            default_models = prefs.default_extraction_models or {}
            return str(self.id) == str(default_models.get(self.type_document))
        except UserPreferences.DoesNotExist:
            return False