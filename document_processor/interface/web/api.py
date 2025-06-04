# interface/web/api.py

import os
import logging
import tempfile
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from domain.document_type import DocumentType
from application.document_processor import DocumentProcessor
from application.document_classifier import DocumentClassifier
from application.extract_service import ExtractionService
from application.chain_service import ChainService
from infrastructure.ocr.paddle_ocr import PaddleOcrProvider
from infrastructure.llm.gemini_provider import GeminiProvider
from infrastructure.llm.langchain_provider import LangChainProvider
from infrastructure.storage.file_storage import FileStorage

class WebApi:
    """Web API for document processing system"""
    
    def __init__(self, document_processor):
        """Initialize with document processor service"""
        self.logger = logging.getLogger(__name__)
        self.document_processor = document_processor
        self.app = Flask(__name__)
        self._configure_routes()
    
    def _configure_routes(self):
        """Configure API routes"""
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({"status": "healthy"})
        
        @self.app.route('/process', methods=['POST'])
        def process_document():
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            try:
                # Save uploaded file to temporary location
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, secure_filename(file.filename))
                file.save(file_path)
                
                # Process document
                result = self.document_processor.process_document(file_path)
                
                # Clean up temporary file
                os.unlink(file_path)
                os.rmdir(temp_dir)
                
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"Error processing document: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/process-text', methods=['POST'])
        def process_text():
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            text = data.get('text')
            doc_type = data.get('document_type')
            
            if not text:
                return jsonify({"error": "No text provided"}), 400
            
            if not doc_type:
                return jsonify({"error": "No document type provided"}), 400
            
            try:
                # Process text
                result = self.document_processor.process_from_text(text, doc_type)
                return jsonify(result)
                
            except Exception as e:
                self.logger.error(f"Error processing text: {str(e)}", exc_info=True)
                return jsonify({"error": str(e)}), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Create and configure Flask application"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Get API keys from environment
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        openai_api_key = os.environ.get("GEMINI_API_KEY")
        
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY environment variable not set")
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Create infrastructure services
        file_storage = FileStorage("/tmp/input", "/tmp/output")
        gemini_provider = GeminiProvider(api_key=gemini_api_key, model_id="gemini-2.0-flash")
        langchain_provider = LangChainProvider(api_key=openai_api_key, model="gemini-2.0-flash")
        
        # Create application services
        classifier = DocumentClassifier(gemini_provider)
        extractor = ExtractionService(gemini_provider)
        chain_service = ChainService(langchain_provider)
        
        # Create document processor
        processor = DocumentProcessor(
            classifier=classifier,
            extractor=extractor,
            chain_service=chain_service,
            storage=file_storage
        )
        
        # Create web API
        api = WebApi(processor)
        return api.app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}", exc_info=True)
        raise

# For direct execution
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)