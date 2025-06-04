# pour afficher le resultat a partir de la base en transformant les données en json
from rest_framework import serializers
from inov.models import (
    ContactInformation, Produit, Facture, BilanComptable,
    TransactionBancaire, ReleveBancaire
)

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInformation
        fields = ['nom', 'adresse', 'numero_telephone', 'email']

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['description', 'quantite', 'prix_unitaire', 'montant_total']

class FactureSerializer(serializers.ModelSerializer):
    informations = ContactSerializer()
    informations_client = ContactSerializer()
    produits = ProduitSerializer(many=True)

    class Meta:
        model = Facture
        fields = [
            'date_echeance', 'numero_facture', 'tva', 'montant_ttc',
            'methode_de_paiement', 'informations', 'informations_client', 'produits','insights'
        ]
class BilanComptableSerializer(serializers.ModelSerializer):
    class Meta:
        model = BilanComptable
        fields = [
           'date_debut', 'date_fin',
            'total_actif', 'total_passif', 'capitaux_propres','insights'
        ]
class TransactionBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionBancaire
        fields = ['date', 'date_valeur', 'credit', 'debit', 'libelle']

class ReleveBancaireSerializer(serializers.ModelSerializer):
    titulaire_compte = ContactSerializer()
    transactions = TransactionBancaireSerializer(many=True)

    class Meta:
        model = ReleveBancaire
        fields = [
            'titulaire_compte', 'numero_compte',
            'date_debut', 'date_fin',
            'solde_ouverture', 'solde_cloture', 'transactions','insights'
        ]
