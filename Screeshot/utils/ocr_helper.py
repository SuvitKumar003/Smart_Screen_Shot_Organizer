import easyocr
import numpy as np
from PIL import Image
import io

class OCRProcessor:
    def __init__(self):
        """Initialize EasyOCR reader"""
        # Using English language, you can add more languages like ['en', 'hi']
        self.reader = easyocr.Reader(['en'], gpu=False)
    
    def extract_text(self, image_file):
        """
        Extract text from an image file
        
        Args:
            image_file: Uploaded file object from Streamlit
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Convert uploaded file to PIL Image
            image = Image.open(image_file)
            
            # Convert PIL Image to numpy array for EasyOCR
            image_np = np.array(image)
            
            # Perform OCR
            results = self.reader.readtext(image_np)
            
            # Extract just the text from results
            # results format: [(bbox, text, confidence), ...]
            extracted_text = ' '.join([text for (bbox, text, conf) in results])
            
            # Clean up the text
            extracted_text = extracted_text.strip()
            
            return extracted_text if extracted_text else "[No text detected]"
            
        except Exception as e:
            return f"[Error: {str(e)}]"
    
    def extract_text_with_confidence(self, image_file):
        """
        Extract text with confidence scores
        
        Args:
            image_file: Uploaded file object from Streamlit
            
        Returns:
            list: List of tuples (text, confidence)
        """
        try:
            image = Image.open(image_file)
            image_np = np.array(image)
            results = self.reader.readtext(image_np)
            
            # Return text with confidence scores
            return [(text, conf) for (bbox, text, conf) in results]
            
        except Exception as e:
            return [(f"Error: {str(e)}", 0.0)]