import logging
import json
from typing import Any, Dict, Type

from pydantic import BaseModel

class ExtractionService:
    """Service responsible for extracting structured data from documents"""
    
    def __init__(self, llm_provider):
        """Initialize with required dependencies"""
        self.logger = logging.getLogger(__name__)
        self.llm_provider = llm_provider
    
    def extract_data(self, file_handle: Any, model_class: Type[BaseModel]) -> BaseModel:
        """Extract structured data from a document file"""
        self.logger.info(f"Extracting data using model: {model_class.__name__}")
        
        # Create extraction prompt
        extraction_prompt = f"Extrais les informations structurées de ce document."

        # Call LLM provider for extraction
        response = self.llm_provider.generate_content(
            prompt=extraction_prompt,
            file=file_handle,
            response_format="json",
            response_schema=model_class.model_json_schema()
        )
        
        # Parse response to model
        extracted_data = json.loads(response)


        validated_data = model_class(**extracted_data)
        
        self.logger.info(f"Successfully extracted data: {model_class.__name__}")
        return validated_data
    
    def extract_data_from_text(self, text: str, model_class: Type[BaseModel]) -> BaseModel:
        """Extract structured data from text"""
        self.logger.info(f"Extracting data from text using model: {model_class.__name__}")
        
        # Create extraction prompt
        extraction_prompt = f"""
        Vous êtes un expert comptable et vous devez extraire les informations pertinentes 
        du texte suivant en respectant la logique même si l'ordre n'est pas organisé:

        {text}
        
        Fournissez un JSON valide correspondant au schéma demandé.
        """
        
        # Call LLM provider for extraction
        response = self.llm_provider.generate_content(
            prompt=extraction_prompt,
            response_format="json",
            response_schema=model_class.model_json_schema()
        )
        
        # Parse response to model
        extracted_data = json.loads(response)
        validated_data = model_class(**extracted_data)
        
        self.logger.info(f"Successfully extracted data from text: {model_class.__name__}")
        return validated_data