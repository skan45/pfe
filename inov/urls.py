from django.urls import path

# Import views from their new locations
from .views.auth_views import register_view, login_view, logout_view
from .views.client_views import homeClient, client, gerer_client, remove_client, supprimer_facture,unified_profile_view
from .views.comptable_views import FactureComptable,  acceuil,home
from .views.file_views import (
    ChoixFile, folder_files, upload_files, delete_file, 
    edit_file, update_folder_color, delete_folder
)
from .views.task_views import todolist, delete_task, edit_task
from .views.extraction_views import (
    extraction_view,
    extract_folder_files, extract_data,get_default_models
)
from .views.notification_views import notifications, remove_invitation

from .views.comptable_views import  (get_default_models_for_file, edit_extraction_data)
from .views.modilisation_views  import(modelisation_view,get_fields,liste_modeles,detail_modele,supprimer_modele,set_default_model)

urlpatterns = [
    # Authentication URLs
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/<uuid:invite_code>/', register_view, name='register_with_invite'),
    
    # Client URLs
   
    path('acceuil/', home, name="home"),
    path('client/<str:pk_test>/', client, name="client"),
    path('table/', gerer_client, name="table"),
    path('remove_client/', remove_client, name="remove_client"),

    path('facture/supprimer/<int:id>/', supprimer_facture, name='supprimer_facture'),
    # Comptable URLs
    path('home/', homeClient, name="homeClient"),
    path('Facture/', FactureComptable, name="FactureComptable"),
    
    
    path('user-profil/', unified_profile_view, name="unified_profile_view"),
    path('', acceuil, name="acceuil"),
    
    # Notification URLs
    path('notifications/', notifications, name="notifications"),
    path('remove_invitation/<uuid:code>/', remove_invitation, name="remove_invitation"),
    
    # File Management URLs
    path('donwload/<str:pk>/', ChoixFile, name="ChoixFile"),
    path('delete-folder/<int:folder_id>/', delete_folder, name='delete_folder'),
    path('folder/<int:folder_id>/files/', folder_files, name='folder_files'),
    path('upload-files/<int:folder_id>/', upload_files, name='upload_files'),
    path('delete-file/<int:file_id>/', delete_file, name='delete_file'),
    path('edit-file/<int:file_id>/', edit_file, name='edit_file'),
    path('update-folder-color/', update_folder_color, name='update_folder_color'),
    
    # Task Management URLs
    path('todolist/', todolist, name="todolist"),
    path("delete-task/<int:task_id>/", delete_task, name="delete_task"),
    path("edit-task/<int:task_id>/", edit_task, name="edit_task"),
    
    # Extraction URLs
    path('extraction/', extraction_view, name='extraction'),
    path('extract-data/<int:file_id>/', extract_data, name='extract_data'),
    path('extract-folder/', extract_folder_files, name='extract_folder_files'),
    path('get-default-models/<int:folder_id>/', get_default_models, name='get_default_models'),#for folder

    path('get-default-models-for-file/<int:file_id>/', get_default_models_for_file, name='get_default_models_for_file'),#for file
    path('edit-extraction-data/<int:file_id>/', edit_extraction_data, name='edit_extraction_data'),
   
   



    # URLs pour la gestion des modèles d'extraction
    path('extraction_template/', modelisation_view, name='extraction_template'),
    path('get-fields/', get_fields, name='get_fields'),
    path('modeles/', liste_modeles, name='liste_modeles'),
    path('modeles/<int:pk>/', detail_modele, name='detail_modele'),
    path('modeles/<int:pk>/supprimer/', supprimer_modele, name='supprimer_modele'),
    path('modeles/<int:pk>/default/', set_default_model, name='set_default_model'),

    
    

]