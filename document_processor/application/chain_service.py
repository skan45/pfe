import logging
import json
from typing import Dict, Any

class ChainService:
    """Service responsible for generating insights using LangChain"""
    
    def __init__(self, langchain_provider):
        """Initialize with required dependencies"""
        self.logger = logging.getLogger(__name__)
        self.langchain_provider = langchain_provider
    
    def generate_insights(self, document_type: str, extracted_data: Dict[str, Any]) -> str:
        """Generate insights from extracted data using LangChain"""
        self.logger.info(f"Generating insights for document type: {document_type}")
        
        # Create or load chain for document type
        chain = self._create_chain_for_document_type(document_type)
        
        # Convert dictionary to string if needed
        # This fixes the pydantic validation error for HumanMessage
        if isinstance(extracted_data, dict):
            # Format dictionary as JSON string for the memory component
            data_str = json.dumps(extracted_data, ensure_ascii=False, indent=2)
        else:
            data_str = str(extracted_data)
        
        # Run chain with extracted data
        # Pass both the string version for memory and the dict for processing
        insights = chain.run(
            #document_type=document_type,
            extracted_data=data_str
        )
        
        self.logger.info("Successfully generated insights")
        return insights
    
    def _create_chain_for_document_type(self, document_type: str):
        """Create a specific LangChain for the document type"""
        self.logger.info(f"Creating chain for document type: {document_type}")
        
        # Define prompt templates based on document type
        templates = {
            "facture": """
            Vous êtes un expert comptable analysant une facture.
            
            Facture: {extracted_data}
            
            Tâche: 
            1. Vérifiez que les montants sont cohérents (quantité * prix unitaire = montant total produit, somme des produits + TVA = montant TTC)
            2. Identifiez les éventuelles anomalies ou points d'attention
            3. Suggérez des optimisations fiscales possibles
            4. Résumez les points clés de cette facture
            
            Fournissez ucne analyse concise et professionnelle.
            """,
            
            "bilan": """
            Vous êtes un expert comptable analysant un bilan financier.
            
            Bilan: {extracted_data}
            
            Tâche:
            1. Calculez et interprétez les ratios financiers clés (solvabilité, liquidité)
            2. Identifiez les forces et faiblesses de la structure financière
            3. Comparez avec les normes du secteur si possible
            4. Suggérez des améliorations pour la structure financière
            
            Fournissez une analyse financière concise et professionnelle.
            """,
            
            "releve_bancaire": """
            Vous êtes un expert financier analysant un relevé bancaire.
            
            Relevé: {extracted_data}
            
            Tâche:
            1. Catégorisez les principales dépenses et recettes
            2. Identifiez les tendances notables (flux récurrents, anomalies)
            3. Calculez le solde moyen et les variations importantes
            4. Suggérez des optimisations de trésorerie possibles
            
            Fournissez une analyse financière concise et pratique.
            """
        }
        
        # Get template for document type or use default
        template = templates.get(document_type, """
        Analysez les données extraites du document de type {document_type}:
        
        {extracted_data}
        
        Fournissez une analyse professionnelle et des recommandations.
        """)
        
        # Create and return chain
        return self.langchain_provider.create_chain(template)