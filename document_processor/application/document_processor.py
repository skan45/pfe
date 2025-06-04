import logging
from typing import  Dict, Any,Union
import os

from document_processor.domain.document_type import DocumentType


class DocumentProcessor:
    """Main application service orchestrating the document processing workflow"""
    
    def __init__(self, classifier, extractor, chain_service, storage):
        """Initialize with required dependencies"""
        self.logger = logging.getLogger(__name__)
        self.classifier = classifier
        self.extractor = extractor
        self.chain_service = chain_service
        self.storage = storage
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document file and extract structured information"""
        self.logger.info(f"Processing document: {file_path}")
      
        
        # Check if file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        
        # Upload file to LLM provider for classification
        file_handle = self.storage.get_file_handle(file_path)
      
        
        # Classify document type
        doc_type = self.classifier.classify_document(file_handle)
        self.logger.info(f"Document classified as: {doc_type.value}")
        
        if doc_type == DocumentType.UNKNOWN:
            raise ValueError(f"Unable to classify document: {file_path}")
        
        # Extract structured data based on document type
        model_class = DocumentType.get_model_mapping().get(doc_type.value)
        

        structured_data = self.extractor.extract_data(file_handle, model_class)
        
        jsonData =  structured_data.model_dump()
        
        
        # Generate additional insights using LangChain
        insights = self.chain_service.generate_insights(
            doc_type.value, 
            jsonData
           
        )
    
        # Return complete results
        return {
            "document_type": doc_type.value,
            "structured_data":jsonData,
            "insights": insights,
        }
    
    def process_from_text(self, text: str, doc_type: Union[str, DocumentType]) -> Dict[str, Any]:
        """Process document from already extracted text"""
        self.logger.info("Processing from extracted text")
        
        # Convert string to enum if needed
        if isinstance(doc_type, str):
            doc_type = DocumentType.from_string(doc_type)
        
        if doc_type == DocumentType.UNKNOWN:
            raise ValueError(f"Invalid document type: {doc_type}")
        
        # Get model class
        model_class = DocumentType.get_model_mapping().get(doc_type.value)
        
        # Extract structured data from text
        structured_data = self.extractor.extract_data_from_text(text, model_class)
        
        # Generate insights
        insights = self.chain_service.generate_insights(
            doc_type.value,
            structured_data.model_dump()
        )
        
        # Return results
        return {
            "document_type": doc_type.value,
            "structured_data": structured_data.model_dump(),
            "insights": insights
        }