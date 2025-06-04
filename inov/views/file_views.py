import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render



from inov.decorators import allowed_users
from inov.models import Facture, File, Folder
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



def folder_files(request, folder_id):
    """View for displaying files within a specific folder."""
    folder = get_object_or_404(Folder, id=folder_id)
    
    context = {
        'folder': folder,
    }
    return render(request, 'pages/folder_files.html', context)

def upload_files(request, folder_id):
    """Handle file uploads to a specific folder."""
    folder = get_object_or_404(Folder, id=folder_id)
    
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')
        
        for uploaded_file in files:
            File.objects.create(folder=folder, file=uploaded_file)
        
        messages.success(request, f'{len(files)} fichiers ajoutés au dossier {folder.name}!')
    
    return redirect('folder_files', folder_id=folder_id)

def delete_folder(request, folder_id):
    """Delete folder and all its files."""
    folder = get_object_or_404(Folder, id=folder_id)
    
    if request.method == 'POST':
        folder_name = folder.name
        folder.delete()
        messages.success(request, f'Le dossier "{folder_name}" a été supprimé avec succès!')
    
    return redirect('extraction')

def delete_file(request, file_id):
    """Delete a specific file."""
    file = get_object_or_404(File, id=file_id)
    folder_id = file.folder.id
    
    if request.method == 'POST':
        file_name = file.file.name.split('/')[-1]
        file.delete()
        messages.success(request, f'Le fichier "{file_name}" a été supprimé avec succès!')
    
    return redirect('folder_files', folder_id=folder_id)

def edit_file(request, file_id):
    """Edit file metadata."""
    file = get_object_or_404(File, id=file_id)
   
    # Implement edit logic here
    # This is just a placeholder
    
    return redirect('folder_files', folder_id=file.folder.id)


#@login_required(login_url='login')
@allowed_users(allowed_roles=['Comptable'])

def ChoixFile(request,pk):
    facture = Facture.objects.get(id=pk)
    context={'factur': facture}
    return render(request, 'pages/choix.html',context)


@csrf_exempt
@require_POST
def update_folder_color(request):
    """Update folder color via AJAX."""
    data = json.loads(request.body)
    folder_id = data.get('folder_id')
    color = data.get('color')
    
    folder = get_object_or_404(Folder, id=folder_id)
    folder.color = color
    folder.save()
    
    return JsonResponse({'status': 'success'})