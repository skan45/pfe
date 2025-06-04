# interface/cli/cli_controller.py

import os
import argparse
import logging
from typing import List, Dict, Any
import json
import sys

class CliController:
    """Command Line Interface controller for document processing"""
    
    def __init__(self, document_processor):
        """Initialize with document processor service"""
        self.logger = logging.getLogger(__name__)
        self.document_processor = document_processor
    
    def run(self, args=None):
        """Run the CLI interface"""
        parser = self._create_argument_parser()
        args = parser.parse_args(args)
        
        if args.file:
            self._process_file(args.file, args.output_format)
        elif args.dir:
            self._process_directory(args.dir, args.output_format)
        elif args.text:
            self._process_text(args.text, args.doc_type, args.output_format)
        else:
            parser.print_help()
    
    def _create_argument_parser(self):
        """Create the argument parser for CLI"""
        parser = argparse.ArgumentParser(
            description="Document processing system for financial and administrative documents"
        )
        
        # Input source group
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            "-f", "--file", 
            help="Path to a document file (PDF or image) to process"
        )
        input_group.add_argument(
            "-d", "--dir", 
            help="Path to a directory containing document files to process"
        )
        input_group.add_argument(
            "-t", "--text", 
            help="Process text directly instead of a file"
        )
        
        # Output format
        parser.add_argument(
            "-o", "--output-format",
            choices=["json", "text", "all"],
            default="all",
            help="Output format (default: all)"
        )
        
        # Document type (required for text processing)
        parser.add_argument(
            "--doc-type",
            choices=["facture", "bilan", "releve_bancaire"],
            help="Document type (required when processing text)"
        )
        
        return parser
    
    def _process_file(self, file_path: str, output_format: str):
        """Process a single document file"""
        self.logger.info(f"Processing file: {file_path}")
        
        try:
            # Validate file exists
            if not os.path.isfile(file_path):
                print(f"Error: File not found: {file_path}")
                return
            
            # Process document
            result = self.document_processor.process_document(file_path)
            
            # Output results
            self._output_result(result, output_format)
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            self.logger.error(f"Error processing file: {str(e)}", exc_info=True)
    
    def _process_directory(self, dir_path: str, output_format: str):
        """Process all document files in a directory"""
        self.logger.info(f"Processing directory: {dir_path}")
        
        try:
            # Validate directory exists
            if not os.path.isdir(dir_path):
                print(f"Error: Directory not found: {dir_path}")
                return
            
            # Process all PDF and image files
            extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']
            processed_files = 0
            
            for file in os.listdir(dir_path):
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in extensions):
                    print(f"\nProcessing: {file}")
                    self._process_file(file_path, output_format)
                    processed_files += 1
            
            print(f"\nProcessed {processed_files} files from {dir_path}")
            
        except Exception as e:
            print(f"Error processing directory: {str(e)}")
            self.logger.error(f"Error processing directory: {str(e)}", exc_info=True)
    
    def _process_text(self, text: str, doc_type: str, output_format: str):
        """Process document from text"""
        self.logger.info("Processing from text input")
        
        try:
            # Validate doc_type is provided
            if not doc_type:
                print("Error: Document type (--doc-type) is required when processing text")
                return
            
            # Process text
            result = self.document_processor.process_from_text(text, doc_type)
            
            # Output results
            self._output_result(result, output_format)
            
        except Exception as e:
            print(f"Error processing text: {str(e)}")
            self.logger.error(f"Error processing text: {str(e)}", exc_info=True)
    
    def _output_result(self, result: Dict[str, Any], output_format: str):
        """Output processing result in the specified format"""
        if output_format == "json" or output_format == "all":
            print("\n===== JSON OUTPUT =====")
            print(json.dumps(result["structured_data"], indent=2, ensure_ascii=False))
        
        if output_format == "text" or output_format == "all":
            print("\n===== INSIGHTS =====")
            print(result["insights"])
            
            if "file_paths" in result:
                print("\n===== FILE PATHS =====")
                for key, path in result["file_paths"].items():
                    print(f"{key}: {path}")