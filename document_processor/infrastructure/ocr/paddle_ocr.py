import logging
import os
import cv2
import numpy as np
from typing import List, Dict, Any
from PIL import Image

class PaddleOcrProvider:
    """Service for OCR using PaddleOCR"""
    
    def __init__(self):
        """Initialize PaddleOCR with required settings"""
        self.logger = logging.getLogger(__name__)
        
        # Import PaddleOCR only if available to avoid immediate dependency requirements
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                lang='fr',  # Language set to French
                table=True,
                use_angle_cls=True,  # Use angle classifier for skew correction
                ocr_version='PP-OCRv4',  # Use version 4 of OCR
                table_version='PP-STRUCTUREv2',  # Use structured table extraction
                show_log=True
            )
            self.logger.info("PaddleOCR initialized successfully")
        except ImportError:
            self.logger.error("PaddleOCR not installed. Install with: pip install paddlepaddle paddleocr")
            raise ImportError("PaddleOCR not installed. Install with: pip install paddlepaddle paddleocr")
    
    def extract_text_from_image(self, image_path: str) -> List[str]:
        """Extract text from an image file"""
        self.logger.info(f"Extracting text from image: {image_path}")
        
        try:
            # Load image
            img = cv2.imread(image_path)
 
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            
            # Process with OCR (Consider disabling classification if not needed)
            result = self.ocr.ocr(img, cls=False)  # cls=False for faster processing
            self.logger.debug(f"OCR result: {result}")
            
            # Extract text
            detected_text = self._extract_text_from_result(result)
            self.logger.info(f"Successfully extracted {len(detected_text)} text elements from image")
            return detected_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from image: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from a PDF file"""
        self.logger.info(f"Extracting text from PDF: {pdf_path}")
        
        try:
            # Import pdf2image to convert PDF to images
            from pdf2image import convert_from_path
            
            # Convert PDF to images (300 dpi for better quality)
            pages = convert_from_path(pdf_path, dpi=300, fmt='png')
            self.logger.info(f"Converted PDF to {len(pages)} images")
            
            all_text = []
            
            # Process each page
            for i, page in enumerate(pages):
                self.logger.info(f"Processing PDF page {i+1}/{len(pages)}")
                
                # Convert PIL image to OpenCV format
                img = np.array(page)
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                
                # Process with OCR
                result = self.ocr.ocr(img, cls=False)  # Use cls=False for faster processing
                
                # Extract text
                page_text = self._extract_text_from_result(result)
                all_text.extend(page_text)
            
            self.logger.info(f"Successfully extracted {len(all_text)} text elements from PDF")
            return all_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def _extract_text_from_result(self, result) -> List[str]:
        """Helper method to extract text from OCR result"""
        detected_text = []
        
        # Iterate through the OCR results
        for page_result in result:
            for line in page_result:
                # Check result type
                if isinstance(line, list):  # Detected text
                    text = line[1][0]  # Extracted text from OCR result
                    detected_text.append(text)
                
                elif isinstance(line, dict) and line.get('type') == 'table':  # Detected table
                    # Extract table cells
                    cells = line['res']['cells']
                    for cell in cells:
                        text = cell['text']  # Cell text
                        detected_text.append(text)
        
        return detected_text
