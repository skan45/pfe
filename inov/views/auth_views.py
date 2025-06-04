from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.utils import timezone
from inov.decorators import unauthenticated_user
from inov.forms import CustomUserCreationForm, UserRoleForm
from inov.models import Client, Comptable, Invitation
import logging

logger = logging.getLogger(__name__)

@unauthenticated_user
def register_view(request):
    user_form = CustomUserCreationForm(prefix='infos')
    role_form = UserRoleForm(prefix='status')

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, prefix='infos')
        role_form = UserRoleForm(request.POST, prefix='status')


        if user_form.is_valid() and role_form.is_valid():
            email = user_form.cleaned_data['email']
            last_name = user_form.cleaned_data['last_name']
            first_name = user_form.cleaned_data['first_name']
            role = role_form.cleaned_data['role']

            try:
                group, created = Group.objects.get_or_create(name=role)
                if created:
                    logger.info(f"Group '{role}' created.")
            except IntegrityError:
                logger.error(f"Error while creating group '{role}'.")
                return redirect('register')

            user = user_form.save(commit=False)
            user.username = email  # Assure uniqueness
            user.save()
            user.groups.add(group)

            if role == 'Client':
                try:
                    invitation = Invitation.objects.get(to_client_email=email, status='Pending')
                    invitation.status = 'Accepted'
                    invitation.date_accepted = timezone.now()
                    invitation.save()
                except Invitation.DoesNotExist:
                    pass

                Client.objects.create(user=user, status='Client', email=email, prénom=first_name, nom=last_name)

            elif role == 'Comptable':
                Comptable.objects.create(user=user, status='Comptable', email=email, prénom=first_name, nom=last_name)

            messages.success(request, f"Le compte a bien été créé pour {last_name}")
            return redirect('login')

    
    context = {'form': user_form, 'form_2': role_form}
    return render(request, 'pages/register.html', context)


#@unauthenticated_user
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        logger.debug(f"Authentication attempt: {user}")

        if user is not None and user.groups.exists():
            group = user.groups.first().name
            login(request, user)
            if group == 'Client':
                return redirect('homeClient')
            elif group == 'Comptable':
                return redirect('home')
        else:
            messages.warning(request, 'Email ou mot de passe incorrect')

    return render(request, 'pages/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
