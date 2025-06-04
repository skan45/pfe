from django.utils import timezone 

from django.shortcuts import get_object_or_404, redirect, render
from inov.forms import TaskForm
from inov.models import Task
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.contrib import messages


def todolist(request):
    """ Affiche la liste des tâches du comptable connecté et permet d'en ajouter une nouvelle """
    
    # Récupérer les tâches du comptable connecté
    comptable = request.user.comptable  # Assurez-vous que l'utilisateur est bien un comptable
    tasks = Task.objects.filter(assigned_to=comptable)

    # Vérifier et mettre à jour le statut des tâches
    update_task_status(request)

    # Traitement du formulaire d'ajout de tâche
    if request.method == "POST":

    
        description = request.POST.get("description")
        due_date_str = request.POST.get("due_date")  # exemple: 2025-04-03T14:00
      
         
        if description and due_date_str:
            parsed_date = parse_datetime(due_date_str)
            if parsed_date is not None:
                aware_due_date = make_aware(parsed_date)  # Pour éviter l’erreur naive/aware
                if aware_due_date < timezone.now() :
                  messages.error(request,"choisir une date convenable")
                  return redirect("todolist")

                Task.objects.create(
                    description=description,
                    due_date=aware_due_date,
                    assigned_to=comptable,
                )
                messages.success(request, "Tâche ajoutée avec succès.")
                return redirect("todolist")
            else:
                messages.error(request, "Format de date invalide.")
    else:
        form = TaskForm()

    return render(request, "pages/todo-list.html", {"tasks": tasks, "form": form})

   


def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.description = request.POST.get('description')
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status')
        task.save()
        return redirect('todolist')


def update_task_status(request):
    comptable = request.user.comptable  
    tasks = Task.objects.filter(assigned_to=comptable)
    """Met à jour le statut des tâches selon leur due_date (datetime)"""
    now = timezone.now()
    for task in tasks:
        if task.status == "Active" and task.due_date < now :
            task.status = "Passed"
            task.save()


def delete_task(request, task_id):
    print(f"🔍 Requête reçue pour supprimer la tâche {task_id}")
    """ Supprime une tâche """
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect("todolist")