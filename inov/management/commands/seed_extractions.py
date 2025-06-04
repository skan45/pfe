from django.core.management.base import BaseCommand
from inov.models import ExtractionConfiguration

class Command(BaseCommand):
    help = 'Insère les modèles d’extraction par défaut'

    def handle(self, *args, **kwargs):
        defaults = [
            {
                'name': 'Modèle par défaut - Facture',
                'type_document': 'facture',
                'champs_choisis': [
                    "date_echeance", "numero_facture", "status", "informations",
                    "informations_client", "tva", "montant_ttc", "methode_de_paiement", "insights"
                ],
            },
            {
                'name': 'Modèle par défaut - Relevé',
                'type_document': 'releve',
                'champs_choisis': [
                    "titulaire_compte", "status", "numero_compte", "date_debut",
                    "date_fin", "solde_ouverture", "solde_cloture", "insights"
                ],
            },
            {
                'name': 'Modèle par défaut - Bilan',
                'type_document': 'bilan',
                'champs_choisis': [
                    "date_echeance", "date_debut", "date_fin", "total_actif",
                    "total_passif", "capitaux_propres", "insights", "status"
                ],
            }
        ]

        created_count = 0
        updated_count = 0

        for item in defaults:
            obj, created = ExtractionConfiguration.objects.get_or_create(
                name=item['name'],
                defaults={
                    'type_document': item['type_document'],
                    'champs_choisis': item['champs_choisis'],
                    'user': None
                }
            )
            if created:
                created_count += 1
            else:
                # Check if existing object needs updating
                needs_update = (
                    obj.type_document != item['type_document'] or
                    obj.champs_choisis != item['champs_choisis'] or
                    obj.user is not None
                )
                if needs_update:
                    obj.type_document = item['type_document']
                    obj.champs_choisis = item['champs_choisis']
                    obj.user = None
                    obj.save()
                    updated_count += 1

        message = f'Modèles d’extraction par défaut : {created_count} créés, {updated_count} mis à jour.'
        self.stdout.write(self.style.SUCCESS(message))