from enum import Enum
from typing import Dict, Type
from pydantic import BaseModel

from document_processor.domain.entities import Facture, BilanComptable, ReleveBancaire


class DocumentType(Enum):
    """Enumeration of document types supported by the system"""
    FACTURE = "facture"
    BILAN = "bilan"
    RELEVE_BANCAIRE = "releve_bancaire"
    UNKNOWN = "unknown"
    
    @staticmethod
    def get_model_mapping() -> Dict[str, Type[BaseModel]]:
        """Get mapping of document types to their corresponding
        Pydantic models"""
        return {
            DocumentType.FACTURE.value: Facture,
            DocumentType.BILAN.value: BilanComptable,
            DocumentType.RELEVE_BANCAIRE.value: ReleveBancaire
        }
    
    @staticmethod
    def from_string(doc_type: str) -> 'DocumentType':
        """Convert string representation to DocumentType"""
        try:
            return DocumentType(doc_type.lower())
        except ValueError:
            return DocumentType.UNKNOWN
    def to_folder_type(self) -> str:
        """Convert DocumentType to the expected folder.type"""
        if self == DocumentType.RELEVE_BANCAIRE:
            return "releve"
        if self == DocumentType.FACTURE:
            return "facture"
        if self == DocumentType.BILAN:
            return "bilan"
        return "unknown"