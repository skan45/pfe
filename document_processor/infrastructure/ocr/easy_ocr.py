import logging
import os
import cv2
import numpy as np
from typing import List
from PIL import Image
import easyocr

class EasyOcrProvider:
    """Service for OCR using EasyOCR"""

    def __init__(self):
        """Initialize EasyOCR model with required settings"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize EasyOCR Reader
        self.reader = easyocr.Reader(['en'])  # Specify the language(s) for OCR
        self.logger.info("EasyOCR model initialized successfully")

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess the image to the format expected by EasyOCR"""
        self.logger.info(f"Processing image for OCR: {image_path}")
        
        # Load image using OpenCV
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert image to grayscale (not strictly necessary for EasyOCR, but good for some images)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize the image (optional, but ensures consistent input size)
        resized_img = cv2.resize(gray_img, (1280, 720))  # Example resizing to 720p resolution

        self.logger.debug(f"Preprocessed image shape: {resized_img.shape}")
        return resized_img

    def extract_text_from_image(self, image_path: str) -> List[str]:
        """Extract text from an image file using EasyOCR"""
        self.logger.info(f"Extracting text from image: {image_path}")
        
        try:
            # Preprocess image to suitable format (though EasyOCR can handle various formats)
            preprocessed_image = self.preprocess_image(image_path)

            # Use EasyOCR to extract text
            result = self.reader.readtext(preprocessed_image)

            # Extract the detected text from the result (EasyOCR returns a list of tuples)
            text = [item[1] for item in result]  # item[1] contains the extracted text

            self.logger.info(f"Successfully extracted text: {text}")
            return text
            
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
                
                # Process with OCR using EasyOCR
                result = self.extract_text_from_image(img)
                all_text.extend(result)
            
            self.logger.info(f"Successfully extracted {len(all_text)} text elements from PDF")
            return all_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
