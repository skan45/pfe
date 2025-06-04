import os
import json
import logging
from typing import List, Dict, Any, Union, BinaryIO

class FileStorage:
    """Service for file storage operations"""
    
    def __init__(self, input_dir: str = "input", output_dir: str = "output"):
        """Initialize with input and output directories"""
        self.logger = logging.getLogger(__name__)
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.logger.info(f"FileStorage initialized with input_dir: {input_dir}, output_dir: {output_dir}")
    
    def save_text(self, text: Union[str, List[str]], filename: str) -> str:
        """Save text content to a file"""
        filepath = os.path.join(self.output_dir, filename)
        self.logger.info(f"Saving text to: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(text, list):
                    for line in text:
                        f.write(f"{line}\n")
                else:
                    f.write(text)
            
            self.logger.info(f"Successfully saved text to: {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error saving text: {str(e)}")
            raise
    
    def save_json(self, data: Dict[str, Any], filename: str) -> str:
        """Save JSON data to a file"""
        filepath = os.path.join(self.output_dir, filename)
        self.logger.info(f"Saving JSON to: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Successfully saved JSON to: {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error saving JSON: {str(e)}")
            raise
    
    def load_text(self, filename: str) -> str:
        """Load text from a file"""
        filepath = os.path.join(self.input_dir, filename)
        self.logger.info(f"Loading text from: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"Successfully loaded text from: {filepath}")
            return content
        
        except Exception as e:
            self.logger.error(f"Error loading text: {str(e)}")
            raise
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON from a file"""
        filepath = os.path.join(self.input_dir, filename)
        self.logger.info(f"Loading JSON from: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Successfully loaded JSON from: {filepath}")
            return data
        
        except Exception as e:
            self.logger.error(f"Error loading JSON: {str(e)}")
            raise
    
    def get_file_handle(self, file_path: str) -> BinaryIO:
        """Get a file handle for a file"""
        self.logger.info(f"Getting file handle for: {file_path}")
        
        try:
            return open(file_path, 'rb')
        except Exception as e:
            self.logger.error(f"Error getting file handle: {str(e)}")
            raise
    
    def list_files(self, directory: str = None, extension: str = None) -> List[str]:
        """List files in a directory with optional extension filter"""
        dir_path = directory if directory else self.input_dir
        self.logger.info(f"Listing files in: {dir_path}")
        
        try:
            files = os.listdir(dir_path)
            
            if extension:
                files = [f for f in files if f.endswith(extension)]
            
            self.logger.info(f"Found {len(files)} files in: {dir_path}")
            return files
        
        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            raise