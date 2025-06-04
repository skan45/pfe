
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from inov.backends import User
from inov.decorators import allowed_users
from inov.forms import ClientForm, FileUploadForm,ComptableForm
from inov.models import Client, Comptable, Facture, File, Invitation
from django.utils import timezone
from inov.models import Facture, BilanComptable, ReleveBancaire, Client, File, ContactInformation
from inov.utils import validate_uploaded_files

@login_required
def client(request, pk_test):
    """View details of a specific client."""
    client = get_object_or_404(Client, user_id=pk_test)
    factures = client.factures.all()
    
    # Filter handling
    statut_query = request.GET.get('statut')
    date_query = request.GET.get('dateCreation')
    
    if is_valid_queryparam(statut_query):
        factures = factures.filter(status=statut_query)
    
    if is_valid_queryparam(date_query):
        factures = factures.filter(date_created__contains=date_query)
    
    context = {
        'client': client, 
        'factures': factures, 
        'facture_count': factures.count()
    }
    return render(request, 'pages/client.html', context)


@login_required
def gerer_client(request):
    """Manage clients: display client table and handle invitations."""
    try:
        comptable = get_object_or_404(Comptable, user=request.user)
        
        # Get modal state from session or query params
        modal_open = request.session.pop('modal_open', False) or request.GET.get('modal_open', False)
        
        # Get invitations for this accountant
        invitations = Invitation.objects.filter(from_comptable=comptable)
        clients_data = []
        
        # Process existing invitations
        for invitation in invitations:
            client_info = {
                'email': invitation.to_client_email,
                'status': invitation.status,
                'nom': None,
                'prenom': None,
                'phone': None,
                'id_client': None,
                'invite_code': invitation.invite_code
            }
            
            # If invitation was accepted, get client data
            if invitation.status == 'Accepted':
                user = User.objects.filter(email=invitation.to_client_email).first()
                if user:
                    client = Client.objects.filter(user=user).first()
                    if client:
                        client_info.update({
                            'nom': client.nom,
                            'prenom': client.prénom, 
                            'phone': client.phone,
                            'id_client': client.pk
                        })
            clients_data.append(client_info)
        
        # Handle invitation form submission
        if request.method == 'POST':
            email_invité = request.POST.get('email')
            if not email_invité:
                messages.error(request, "L'email est requis.")
                return render(request, 'pages/client-list.html', {
                    'clients': clients_data,
                    'modal_open': True
                })
            
            # Check if user already exists
            if User.objects.filter(email=email_invité).exists():
                messages.warning(request, f"L'utilisateur avec l'email {email_invité} est déjà inscrit.")
                return render(request, 'pages/client-list.html', {
                    'clients': clients_data,
                    'modal_open': True
                })
                
            # Check if invitation already pending
            if Invitation.objects.filter(to_client_email=email_invité, status='Pending').exists():
                messages.warning(request, f'Une invitation est déjà en attente pour {email_invité}.')
                return render(request, 'pages/client-list.html', {
                    'clients': clients_data,
                    'modal_open': True
                })
                
            # Create invitation
            invitation = Invitation.objects.create(
                from_comptable=comptable,
                to_client_email=email_invité,
                status='Pending'
            )
            
            # Generate registration link
            invite_code = str(invitation.invite_code)
            registration_link = request.build_absolute_uri(f"/register/?code={invite_code}")
            
            # Send email
            subject = "Invitation à rejoindre notre plateforme"
            message = f"""
            Bonjour,
            
            Vous avez été invité à rejoindre notre plateforme. 
            Cliquez sur le lien ci-dessous pour vous inscrire :
            {registration_link}
            
            Cordialement,
            L'équipe Xcomtap
            """
            
            from_email = comptable.user.email
            recipient_list = [email_invité]
            
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request,f'Invitation envoyée à {email_invité}.')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")
                invitation.delete()  # Clean up the invitation if email fails
                return render(request, 'pages/client-list.html', {
                    'clients': clients_data,
                    'modal_open': True
                })
            
            # After successful invitation, re-render the page with updated data
            clients_data.append({
                'email': email_invité,
                'status': 'Pending',
                'nom': None,
                'prenom': None,
                'phone': None,
                'id_client': None,
                'invite_code': invite_code
            })
            return render(request, 'pages/client-list.html', {
                'clients': clients_data,
                'modal_open': False  # Close modal after success
            })
        
        # GET request: Render the client list
        return render(request, 'pages/client-list.html', {
            'clients': clients_data,
            'modal_open': modal_open
        })
        
    except Comptable.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré en tant que comptable.")
        return redirect('login')


@login_required
@allowed_users(allowed_roles=['Client'])
def homeClient(request):
    """Client home page with file upload functionality."""
    # Get the client instance
    client = get_object_or_404(Client, user=request.user)
    form = FileUploadForm()
         
    # Get client's documents
    factures = client.factures.all()
    bilans = client.bilans.all()  # Assuming relation name is 'bilans'
    releves = client.releves.all()  # Assuming relation name is 'releves'
         
    # Handle filtering for factures
    statut_query = request.GET.get('statut')
    date_query = request.GET.get('dateCreation')
 
    if is_valid_queryparam(statut_query):
        factures = factures.filter(status=statut_query)
        bilans = bilans.filter(status=statut_query)
        releves = releves.filter(status=statut_query)
 
    if is_valid_queryparam(date_query):
        factures = factures.filter(date_created__date=date_query)
        bilans = bilans.filter(date_created__date=date_query)
        releves = releves.filter(date_created__date=date_query)
 
    # Calculate counts
    facture_count_total = factures.count()
    facture_count_non_valide = factures.filter(status='Non Validé').count()
         
    bilan_count_total = bilans.count()
    bilan_count_non_valide = bilans.filter(status='Non Validé').count()
         
    releve_count_total = releves.count()
    releve_count_non_valide = releves.filter(status='Non Validé').count()
 
    # Handle file upload
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        doc_type = request.POST.get('doc_type')
                 
        errors, valid_files = validate_uploaded_files(files)
         
        if errors:
            for error in errors:
                messages.error(request, error)
        elif form.is_valid() and doc_type:
            try:
                for file in valid_files:
                    # Create file instance
                    file_instance = File.objects.create(file=file)
                                     
                    # Create appropriate document type based on selection
                    if doc_type == 'Facture':
                        document = Facture.objects.create(
                            client=client, 
                            file=file_instance
                        )
                        document_type_name = 'facture'
                    elif doc_type == 'Bilan':
                        document = BilanComptable.objects.create(
                            client=client, 
                            file=file_instance,
                            # Fournir des valeurs par défaut pour les champs obligatoires
                            total_actif=0.0,
                            total_passif=0.0,
                            capitaux_propres=0.0
                        )
                    
                        document_type_name = 'bilan'
                    elif doc_type == 'Relevé':
                        document = ReleveBancaire.objects.create(
                            client=client, 
                            file=file_instance,
                            # Fournir des valeurs par défaut pour les champs obligatoires
                            numero_compte="À définir",
                            solde_ouverture=0.0,
                            solde_cloture=0.0,
                            # titulaire_compte est obligatoire, vous devez le gérer
                            # Option 1: Créer un ContactInformation par défaut
                            # Option 2: Rendre le champ nullable dans le modèle
                            # Pour l'instant, on suppose qu'il faut le créer ou l'obtenir
                        )
                        document_type_name = 'relevé bancaire'
                    else:
                        messages.error(request, "Type de document non valide.")
                        continue
                    
                    document.save() 
                             
                messages.success(request, f"{len(valid_files)} {document_type_name}(s) uploadé(s) avec succès.")
                return redirect('homeClient')
            except Exception as e:
                messages.error(request, f"Erreur lors de la sauvegarde: {str(e)}")
        else:
            if not doc_type:
                messages.error(request, "Veuillez sélectionner un type de document.")
 
    context = {
        'form': form,
        'factures': factures,
        'bilans': bilans,
        'releves': releves,
        'facture_count_total': facture_count_total,
        'facture_count_non_valide': facture_count_non_valide,
        'bilan_count_total': bilan_count_total,
        'bilan_count_non_valide': bilan_count_non_valide,
        'releve_count_total': releve_count_total,
        'releve_count_non_valide': releve_count_non_valide,
    }
 
    return render(request, 'pages/index-client.html', context)

@login_required
@require_POST
def remove_client(request):
    """Remove a client or invitation."""
    try:
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Email manquant.")
            return redirect("table")

        # Find user, client and invitation
        user = User.objects.filter(email=email).first()
        client = None
        if user:
            client = Client.objects.filter(user=user).first()
        invitation = Invitation.objects.filter(to_client_email=email).first()

        # Deactivate client if exists
        if client and user:
            user.is_active = False
            user.save()
            messages.success(request, f"Le client {client.prénom} {client.nom} a été désactivé.")
            
            # Remove invitation if exists
            if invitation:
                invitation.delete()
                
        # Just remove invitation if no client
        elif invitation and invitation.status != "Accepted":
            invitation.delete()
            messages.success(request, f"L'invitation pour {email} a été supprimée.")
            
        else:
            messages.warning(request, "Aucun client ou invitation supprimable trouvé.")

    except Exception as e:
        messages.error(request, f"Une erreur est survenue : {str(e)}")

    return redirect("table")


def supprimer_facture(request, id):
    facture = get_object_or_404(Facture, id=id, client__user=request.user)
    facture.delete()
    messages.success(request, "Facture supprimÃ©e avec succÃ¨s.")
    return redirect('homeClient')


def is_valid_queryparam(param):
    """Utility function to check if query parameter is valid."""
    return param != '' and param is not None
@login_required
def unified_profile_view(request):
    if hasattr(request.user, 'comptable'):
        user_type = 'comptable'
        instance = get_object_or_404(Comptable, user=request.user)
        form_class = ComptableForm
        layout = 'layouts/base.html'
        redirect_url = 'home'
    elif hasattr(request.user, 'client'):
        user_type = 'client'
        instance = get_object_or_404(Client, user=request.user)
        form_class = ClientForm
        layout = 'layouts/base-client.html'
        redirect_url = 'homeClient'
    else:
        messages.error(request, "Type d'utilisateur inconnu.")
        return redirect('login')

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect(redirect_url)
    else:
        form = form_class(instance=instance)

    context = {
        'form': form,
        'layout': layout,
        'user_type': user_type,
    }

    return render(request, 'pages/user.html', context)
