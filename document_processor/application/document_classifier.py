import logging
from typing import Any

from document_processor.domain.document_type import DocumentType

class DocumentClassifier:
    """Service responsible for classifying document types"""
    
    def __init__(self, llm_provider):
        """Initialize with required dependencies"""
        self.logger = logging.getLogger(__name__)
        self.llm_provider = llm_provider
    
    def classify_document(self, file_handle: Any) -> DocumentType:
        """Classify a document using LLM"""
        self.logger.info("Classifying document")
        
        # Create prompt for classification
        classification_prompt = """
Analyse l'image suivante et identifie le type de document.
Les types possibles sont UNIQUEMENT: 'facture', 'bilan', 'releve_bancaire'.

Exemples:
- Documents avec montants à payer, dates d'échéance, informations du fournisseur → 'facture'
- Documents avec actifs, passifs, comptes de résultat → 'bilan'
- Documents avec transactions bancaires, soldes, numéros de compte → 'releve_bancaire'

Si le document ne correspond à aucun de ces types, réponds 'autre'.
Réponds uniquement avec un des types mentionnés sans explication supplémentaire.
"""
        
        # Call LLM provider for classification
        response = self.llm_provider.generate_content(
            prompt=classification_prompt,
            file=file_handle
        )
        
        # Convert response to document type and validate
        doc_type_str = response.strip().lower()
        valid_types = ["facture", "bilan", "releve_bancaire", "autre"]
        
        if doc_type_str not in valid_types:
            self.logger.warning(f"Invalid classification response: {doc_type_str}. Defaulting to 'autre'")
            doc_type_str = "autre"
        
        doc_type = DocumentType.from_string(doc_type_str)
        
        self.logger.info(f"Document classified as: {doc_type.value}")
        return doc_type