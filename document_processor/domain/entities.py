from pydantic import BaseModel, Field

from typing import List, Optional


class ContactInformation(BaseModel):
    """Entity representing contact information"""
    nom: str = Field(description="Nom du client ou de l'entreprise")
    adresse: str = Field(description="Adresse complète")
    numero_telephone: Optional[str] = Field(default=None, description="Numéro de téléphone")
    email: Optional[str] = Field(default=None, description="Adresse e-mail")


class Produit(BaseModel):
    """Entity representing a product or service"""
    description: str = Field(description="Description du produit")
    quantite: float = Field(description="Quantité du produit")
    prix_unitaire: float = Field(description="Prix unitaire du produit")
    montant_total: float = Field(description="Montant total (quantité * prix unitaire)")


class Facture(BaseModel):
    """Entity representing an invoice"""
    date_echeance: str = Field(description="Date limite de paiement de la facture")
    numero_facture: str = Field(description="Numéro de facture unique")
    informations: ContactInformation = Field(description="Informations de l'entreprise")
    informations_client: ContactInformation = Field(description="Informations du client")
    produits: List[Produit] = Field(description="Liste des produits ou services")
    tva: float = Field(description="Montant de la TVA")
    montant_ttc: float = Field(description="Montant total avec taxes")
    methode_de_paiement: Optional[str] = Field(default=None, description="Méthode de paiement (ex: virement, PayPal)")


class BilanComptable(BaseModel):
    """Entity representing a financial statement"""
   # date_echeance: str = Field(description="Date d'échéance du bilan")
    date_debut: str= Field(description="Date de début de la période du bilan")
    date_fin: str = Field(description="Date de fin de la période du bilan")
    total_actif: float = Field(description="Total des actifs")
    total_passif: float = Field(description="Total des passifs")
    capitaux_propres: float = Field(description="Capitaux propres")


class TransactionBancaire(BaseModel):
    """Entity representing a bank transaction"""
    date: str = Field(description="Date de la transaction")
    date_valeur: str = Field(description="Date de la transaction")
    credit: float = Field(description="Montant crédité (0 si pas de crédit)")
    debit: float = Field(description="Montant débité (0 si pas de débit)")
    libelle: str = Field(description="Description ou libellé de la transaction")
 
 
 
class ReleveBancaire(BaseModel):
    """Entity representing a bank statement"""
    titulaire_compte: str = Field(description="Nom du titulaire du compte")
    numero_compte: str = Field(description="Numéro du compte bancaire")
    date_debut: str = Field(description="Date de début du relevé au format 'YYYY-MM-DD'")
    date_fin: str = Field(description="Date de fin du relevé au format 'YYYY-MM-DD'")
    transactions: List[TransactionBancaire] = Field(description="Liste des transactions effectuées pendant la période")
    solde_ouverture: float = Field(description="Solde d'ouverture du compte")
    solde_cloture: float = Field(description="Solde de clôture du compte")