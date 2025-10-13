# utils/ocr_helper.py
import easyocr
import numpy as np
from PIL import Image
import io

class OCRProcessor:
    def __init__(self):
        """Initialize EasyOCR reader for text extraction"""
        # Initialize with English language
        # gpu=False for compatibility, set to True if you have GPU
        self.reader = easyocr.Reader(['en'], gpu=False)
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Optionally enhance contrast for better text detection
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        return image
    
    def extract_text(self, image_file):
        """
        Extract text from an image file using EasyOCR
        
        Args:
            image_file: Uploaded file object from Streamlit
            
        Returns:
            str: Extracted and cleaned text
        """
        try:
            # Convert uploaded file to PIL Image
            image = Image.open(image_file)
            
            # Preprocess image
            image = self.preprocess_image(image)
            
            # Convert PIL Image to numpy array
            image_np = np.array(image)
            
            # Perform OCR
            results = self.reader.readtext(image_np)
            
            # Extract text with line preservation
            if not results:
                return "[No text detected]"
            
            # Group text by vertical position to preserve structure
            lines = []
            current_y = None
            current_line = []
            
            # Sort by y-coordinate (top to bottom)
            sorted_results = sorted(results, key=lambda x: x[0][0][1])
            
            for bbox, text, confidence in sorted_results:
                # bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                y_coord = bbox[0][1]
                
                # If y changes significantly, start new line
                if current_y is not None and abs(y_coord - current_y) > 20:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = []
                
                current_y = y_coord
                current_line.append(text)
            
            # Add last line
            if current_line:
                lines.append(' '.join(current_line))
            
            # Combine lines
            extracted_text = '\n'.join(lines).strip()
            
            return extracted_text if extracted_text else "[No text detected]"
            
        except Exception as e:
            return f"[Error: {str(e)}]"
    
    def extract_text_with_metadata(self, image_file):
        """
        Extract text with confidence scores and positioning
        
        Args:
            image_file: Uploaded file object from Streamlit
            
        Returns:
            dict: Contains text, confidences, and metadata
        """
        try:
            image = Image.open(image_file)
            image = self.preprocess_image(image)
            image_np = np.array(image)
            
            results = self.reader.readtext(image_np)
            
            metadata = {
                'text': '',
                'confidence_scores': [],
                'num_words': 0,
                'avg_confidence': 0.0
            }
            
            if not results:
                return metadata
            
            texts = []
            confidences = []
            
            for bbox, text, confidence in results:
                texts.append(text)
                confidences.append(confidence)
            
            metadata['text'] = ' '.join(texts)
            metadata['confidence_scores'] = confidences
            metadata['num_words'] = len(texts)
            metadata['avg_confidence'] = np.mean(confidences) if confidences else 0.0
            
            return metadata
            
        except Exception as e:
            return {
                'text': f"[Error: {str(e)}]",
                'confidence_scores': [],
                'num_words': 0,
                'avg_confidence': 0.0
            }