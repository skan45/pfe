import os
from document_processor.application.document_classifier import DocumentClassifier
from document_processor.application.extract_service import ExtractionService
from document_processor.application.document_processor import DocumentProcessor
from document_processor.application.chain_service import ChainService

from document_processor.infrastructure.storage.file_storage import FileStorage
from document_processor.infrastructure.llm.gemini_provider import GeminiProvider
from document_processor.infrastructure.llm.langchain_provider import LangChainProvider
from document_processor.domain.document_type import DocumentType  
from dotenv import load_dotenv
from tempfile import NamedTemporaryFile
load_dotenv()


config = {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY"),
        "openai_api_key": os.environ.get("GEMINI_API_KEY"),
        "model_id": "gemini-2.0-flash",
        "langchain_model": "gemini-2.0-flash",
        "input_dir": "./media/uploads",
        "output_dir": "./media/outputs"
    }


file_storage = FileStorage(config["input_dir"], config["output_dir"])
gemini_provider = GeminiProvider(api_key=config["gemini_api_key"], model_id=config["model_id"])
langchain_provider = LangChainProvider(api_key=config["openai_api_key"], model=config["langchain_model"])

classifier = DocumentClassifier(gemini_provider)
extractor = ExtractionService(gemini_provider)
chain_service = ChainService(langchain_provider)
processor = DocumentProcessor(classifier, extractor, chain_service, file_storage)

def extract_info(file_path):
   
    # Traitement réel du document
    result = processor.process_document(file_path)
    return result


def classify_file(uploaded_file, expected_type=None):
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        document_type = classifier.classify_document(tmp_path)
        folder_type = document_type.to_folder_type()

        if expected_type and expected_type != 'mixte' and folder_type != expected_type:
            return {
                "valid": False,
                "error": f"❌ {uploaded_file.name} est classifié comme {document_type.value} "
                         f"et ne correspond pas au type du dossier ({expected_type})"
            }

        return {
            "valid": True,
            "type": document_type.value
        }

    except Exception as e:
        return {
            "valid": False,
            "error": f"Erreur lors de l'analyse de {uploaded_file.name} : {str(e)}"
        }

    finally:
        os.remove(tmp_path)
