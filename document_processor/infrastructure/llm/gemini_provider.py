import logging
import json
import mimetypes
from typing import Any, Dict, Optional
import os

class GeminiProvider:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self, api_key: str, model_id: str = "gemini-2.0-flash"):
        """Initialize with API key and model ID"""
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.model_id = model_id
        
        # Import here to avoid immediate dependency requirements
        try:
            from google import genai
            self.genai = genai
            # Create a client with the API key
            self.client = genai.Client(api_key=api_key)
            self.logger.info(f"Gemini client initialized with model: {model_id}")
        except ImportError:
            self.logger.error("Google Generative AI package not installed. Install with: pip install google-genai")
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-genai")
    
    def generate_content(
        self, 
        prompt: str, 
        file: Optional[Any] = None, 
        response_format: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate content using Gemini API"""
        self.logger.info(f"Generating content with prompt: {prompt[:50]}...")
        
        try:
            # Handle files differently based on what's provided
            if file is not None:
                if isinstance(file, str) and os.path.isfile(file):
                    # First, upload the file if it's a path
                    file_obj = self.upload_file(file)
                    return self._generate_with_file_obj(prompt, file_obj, response_format, response_schema)
                elif hasattr(file, 'read'):
                    # If it's a file-like object, get the path
                    file_path = getattr(file, 'name', None)
                    if file_path and os.path.isfile(file_path):
                        file_obj = self.upload_file(file_path)
                        return self._generate_with_file_obj(prompt, file_obj, response_format, response_schema)
            
            # Standard text-only generation
            content = [prompt]
            config = {}
            if response_format == "json" and response_schema is not None:
                config = {
                    'response_mime_type': 'application/json', 
                    'response_schema': response_schema
                }
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=content,
                config=config
            )
            
            result = response.text
            self.logger.info(f"Successfully generated content: {len(result)} characters")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating content with Gemini: {str(e)}")
            raise
    
    def _generate_with_file_obj(self, prompt, file_obj, response_format=None, response_schema=None):
        """Generate content with a file object"""
        try:
            # Create the multipart content
            content = [
                prompt,
                file_obj  # This should be the file object returned from upload_file
            ]
            
            # Set up config
            config = {}
            if response_format == "json" and response_schema is not None:
                config = {
                    'response_mime_type': 'application/json', 
                    'response_schema': response_schema
                }
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=content,
                config=config
            )
            
            result = response.text
            self.logger.info(f"Successfully generated content with file: {len(result)} characters")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating content with file: {str(e)}")
            raise
    
    def upload_file(self, file_path: str) -> Any:
        """Upload a file to use with the Gemini API"""
        self.logger.info(f"Uploading file: {file_path}")
        
        try:
            # Get the file's MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Default to a common image type if we can't detect it
                mime_type = "image/jpeg" if file_path.lower().endswith(('.jpg', '.jpeg')) else "image/png"
            
            # Read the file content and prepare for Gemini API
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Create file object in format expected by Gemini
            # This will depend on the exact Gemini API version you're using
            # Here are two common approaches:
            
            # Approach 1: Use files.upload if available
            try:
                file_obj = self.client.files.upload(
                    file=file_path,
                    config={'display_name': os.path.basename(file_path)}
                )
                self.logger.info(f"Successfully uploaded file: {file_path}")
                return file_obj
            except (AttributeError, TypeError) as e:
                self.logger.warning(f"Could not upload file with files.upload: {e}")
                
            # Approach 2: Create a dict with the file info
            from PIL import Image
            import io
            
            image = Image.open(file_path)
            byte_arr = io.BytesIO()
            image.save(byte_arr, format=image.format)
            
            file_obj = {
                'mime_type': mime_type,
                'data': byte_arr.getvalue()
            }
            
            self.logger.info(f"Successfully prepared file: {file_path}")
            return file_obj
            
        except Exception as e:
            self.logger.error(f"Error uploading file to Gemini: {str(e)}")
            raise