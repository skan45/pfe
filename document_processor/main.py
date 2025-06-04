# Document Processing System with Clean Architecture & LangChain
# main.py

import os
import json
from typing import List, Dict, Any, Optional, Type, Union
import logging
import os
import sys

from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()



# Application Layer: Use cases and business rules
from application.document_processor import DocumentProcessor
from application.document_classifier import DocumentClassifier
from application.extract_service import ExtractionService
from application.chain_service import ChainService

# Infrastructure Layer: External services and implementations
from infrastructure.llm.gemini_provider import GeminiProvider
from infrastructure.llm.langchain_provider import LangChainProvider
from infrastructure.storage.file_storage import FileStorage

# Interface Layer: User interface and controllers
from interface.cli.cli_controller import CliController

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("document_processor.log")
        ]
    )

def main():
    """Main entry point for the document processing system"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Read configuration (could be from a config file)
    config = {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY"),
        "openai_api_key": os.environ.get("GEMINI_API_KEY"),
        "model_id": "gemini-2.0-flash",
        "langchain_model": "gemini-2.0-flash",
        "input_dir": "./content",
        "output_dir": "./content/output"
    }
    
    # Create dependencies
    try:
        # Infrastructure services
        file_storage = FileStorage(config["input_dir"], config["output_dir"])
        gemini_provider = GeminiProvider(api_key=config["gemini_api_key"], model_id=config["model_id"])
        langchain_provider = LangChainProvider(api_key=config["openai_api_key"], model=config["langchain_model"])
    
        # Application services
        classifier = DocumentClassifier(gemini_provider)
        extractor = ExtractionService(gemini_provider)
        chain_service = ChainService(langchain_provider)
     
        
        # Create processor with all dependencies
        processor = DocumentProcessor(
            classifier=classifier,
            extractor=extractor,
            chain_service=chain_service,
            storage=file_storage
        )
        
        # Create interface controller
        cli = CliController(processor)
        
        # Process documents
        cli.run()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()