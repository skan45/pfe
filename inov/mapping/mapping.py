

from inov.models import BilanComptable as BilanModel
from document_processor.domain.entities import BilanComptable as BilanEntity
from datetime import datetime
from inov.models import ContactInformation as ContactModel, Facture as FactureModel, Produit as ProduitModel
from document_processor.domain.entities import Facture
from inov.models import ReleveBancaire as ReleveModel, TransactionBancaire as TransactionModel, ContactInformation as ContactModel
from document_processor.domain.entities import ReleveBancaire as ReleveEntity, TransactionBancaire as TransactionEntity

def map_facture_entity_to_model(entity: Facture, insights: str = "") -> FactureModel: #ajouter insights comme entréé puisque elle nexiste pas dans entities 
    # Créer et sauvegarder le modèle Contact pour informations émetteur
    informations = ContactModel.objects.create(
        nom=entity.informations.nom,
        adresse=entity.informations.adresse,
        numero_telephone=entity.informations.numero_telephone,
        email=entity.informations.email
    )

    # Créer et sauvegarder le modèle Contact pour client
    informations_client = ContactModel.objects.create(
        nom=entity.informations_client.nom,
        adresse=entity.informations_client.adresse,
        numero_telephone=entity.informations_client.numero_telephone,
        email=entity.informations_client.email
    )

    # Créer la facture sans les produits d'abord
 
    facture = FactureModel.objects.create(
        date_echeance=entity.date_echeance,
        numero_facture=entity.numero_facture,
        informations=informations,
        informations_client=informations_client,
        tva=entity.tva,
        montant_ttc=entity.montant_ttc,
        methode_de_paiement=entity.methode_de_paiement,
        insights=insights 
    )

    # Créer et ajouter les produits à la facture
    for produit in entity.produits:
        produit_model = ProduitModel.objects.create(
            description=produit.description,
            quantite=produit.quantite,
            prix_unitaire=produit.prix_unitaire,
            montant_total=produit.montant_total
        )
        facture.produits.add(produit_model)

    return facture




def map_bilan_entity_to_model(entity: BilanEntity, insights: str = "") -> BilanModel:
    return BilanModel.objects.create(
        
        date_debut=entity.date_debut, 
        date_fin=entity.date_fin, 
        total_actif=entity.total_actif,
        total_passif=entity.total_passif,
        capitaux_propres=entity.capitaux_propres,
        insights=insights
    )

 

def map_releve_entity_to_model(entity: ReleveEntity, insights: str = "") -> ReleveModel:
    titulaire, _ = ContactModel.objects.get_or_create(
        nom=entity.titulaire_compte,
        defaults={"adresse": "", "numero_telephone": None, "email": None}
    )

    releve = ReleveModel.objects.create(
        titulaire_compte=titulaire,
        numero_compte=entity.numero_compte,
        date_debut=entity.date_debut,
        date_fin=entity.date_fin,
        solde_ouverture=entity.solde_ouverture,
        solde_cloture=entity.solde_cloture,
        insights=insights
    )

    for transaction in entity.transactions:
        transaction_model = TransactionModel.objects.create(
            date=entity.date,
            date_valeur=entity.date_valeur,
            credit=transaction.credit,
            debit=transaction.debit,
            libelle=transaction.libelle
        )
        releve.transactions.add(transaction_model)

    return releve
