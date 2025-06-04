from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Client)
admin.site.register(Comptable)
admin.site.register(Facture)
admin.site.register(Invitation)
