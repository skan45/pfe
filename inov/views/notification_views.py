from django.shortcuts import get_object_or_404, redirect, render
from inov.decorators import allowed_users
from django.contrib import messages
from inov.models import Invitation

@allowed_users(allowed_roles=['Comptable'])
def notifications(request):
    # Get all pending invitations
    pending_invitations = Invitation.objects.filter(status="Pending")
    
    context = {
        'invitations': pending_invitations
    }
    
    return render(request, 'pages/notifications.html', context)



def remove_invitation(request, code):
    try:
        invitation = get_object_or_404(Invitation, invite_code=code, status="Pending")
        invitation.delete()
        messages.success(request, "Invitation supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la suppression : {str(e)}")
    
    return redirect('notifications')  # Redirige vers la page des notifications (adapté à ta config)
