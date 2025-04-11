import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging
from pathlib import Path
import tempfile
import os
import sys
import re

class OCRProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configure Tesseract paths
        self._configure_tesseract()
        
        # Use Russian language model for better accuracy with Cyrillic text
        self.custom_config = r'--oem 1 --psm 6 -l rus'
        
    def _configure_tesseract(self):
        """Configure Tesseract paths and verify installation"""
        try:
            # Set Tesseract executable path
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Set TESSDATA_PREFIX if not already set
            if 'TESSDATA_PREFIX' not in os.environ:
                tessdata_path = r'C:\Program Files\Tesseract-OCR\tessdata'
                if os.path.exists(tessdata_path):
                    os.environ['TESSDATA_PREFIX'] = tessdata_path
                else:
                    raise FileNotFoundError(f"Tesseract data directory not found at {tessdata_path}")
            
            # Verify Russian language data file exists
            rus_data_path = os.path.join(os.environ['TESSDATA_PREFIX'], 'rus.traineddata')
            if not os.path.exists(rus_data_path):
                raise FileNotFoundError(f"Russian language data file not found at {rus_data_path}")
            
            # Test Tesseract configuration
            try:
                pytesseract.get_tesseract_version()
            except Exception as e:
                raise RuntimeError(f"Tesseract configuration test failed: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Tesseract configuration error: {str(e)}")
            raise
        


    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results while preserving original quality"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image at {image_path}")

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply very light noise reduction (preserve details)
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Enhance contrast slightly
            alpha = 1.2  # Contrast control (subtle enhancement)
            beta = 5     # Brightness control (subtle)
            enhanced = cv2.convertScaleAbs(denoised, alpha=alpha, beta=beta)
            
            # Apply a very mild adaptive threshold only if needed for text areas
            # that might have slight variations in brightness
            max_value = 255
            block_size = 15
            c = 2
            adaptive = cv2.adaptiveThreshold(
                enhanced, max_value, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, block_size, c
            )
            
            # Resize for better OCR - modest scaling that won't degrade quality
            scale_factor = 1.5
            resized = cv2.resize(adaptive, None, fx=scale_factor, fy=scale_factor, 
                            interpolation=cv2.INTER_CUBIC)
            
            # No morphological operations that could damage character shapes
            
            return img

        except Exception as e:
            self.logger.error(f"Error in image preprocessing: {str(e)}")
            raise

    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR optimized for Russian language"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Save preprocessed image for debugging if needed
            debug_dir = Path("debug_images")
            debug_dir.mkdir(exist_ok=True)
            debug_path = debug_dir / f"preprocessed_{Path(image_path).stem}.png"
            cv2.imwrite(str(debug_path), processed_image)
            
            # Try multiple page segmentation modes optimized for different document layouts
            configs = [
                r'--oem 1 --psm 6 -l rus',  # Единый блок текста
                r'--oem 1 --psm 4 -l rus',  # Один столбец текста
                r'--oem 1 --psm 3 -l rus',  # Полностью автоматическая сегментация
                r'--oem 1 --psm 1 -l rus',  # Автоматическая сегментация с определением ориентации
                r'--oem 1 --psm 11 -l rus', # Разреженный текст
                r'--oem 1 --psm 12 -l rus'  # Разреженный текст с OSD
            ]
            
            best_text = ""
            best_confidence = 0
            best_config = ""
            
            for config in configs:
                try:
                    # Convert numpy array to PIL Image for pytesseract
                    pil_image = Image.fromarray(processed_image)
                    
                    # Perform OCR with current configuration
                    text = pytesseract.image_to_string(pil_image, config=config)
                    
                    # Get confidence scores
                    data = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT)
                    conf_values = [float(x) for x in data['conf'] if x != '-1']
                    
                    if conf_values:
                        avg_confidence = np.mean(conf_values)
                        
                        # Log confidence for debugging
                        self.logger.debug(f"Config {config}: confidence {avg_confidence:.2f}%")
                        
                        if avg_confidence > best_confidence:
                            best_confidence = avg_confidence
                            best_text = text
                            best_config = config
                except Exception as e:
                    self.logger.warning(f"Failed to process with config {config}: {str(e)}")
                    continue
            
            if not best_text:
                raise ValueError("No text could be extracted with any configuration")
            
            self.logger.info(f"Selected config: {best_config} with confidence: {best_confidence:.2f}%")
            
            # Clean up the text: remove excess whitespace and normalize line endings
            best_text = '\n'.join([line.strip() for line in best_text.splitlines() if line.strip()])
            print(best_text)
            
            return best_text
        except Exception as e:
            self.logger.error(f"Error in text extraction: {str(e)}")
            raise

    def process_document(self, file_path: str) -> Dict:
        """Process document and extract structured information"""
        try:
            # Extract raw text
            raw_text = self.extract_text(file_path)
            
            if not raw_text or len(raw_text.strip()) == 0:
                raise ValueError("No text could be extracted from the document")
            
            # Process with image to get confidence data
            processed_image = self.preprocess_image(file_path)
            pil_image = Image.fromarray(processed_image)
            confidence_data = pytesseract.image_to_data(
                pil_image, 
                config=self.custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            conf_values = [float(x) for x in confidence_data['conf'] if x != '-1']
            avg_confidence = np.mean(conf_values) if conf_values else 0.0
            
            # Extract structure information
            paragraphs = [p for p in raw_text.split('\n\n') if p.strip()]
            sentences = []
            for paragraph in paragraphs:
                # Разбиение предложений по знакам препинания
                for sent in re.split(r'(?<=[.!?])\s+', paragraph):
                    if sent.strip():
                        sentences.append(sent.strip())
            
            return {
                "raw_text": raw_text,
                "structure": {
                    "sentences": len(sentences),
                    "paragraphs": len(paragraphs),
                    "structure": {
                        "sentences": sentences,
                        "paragraphs": paragraphs
                    }
                },
                "entities": [],  # Для извлечения сущностей можно добавить дополнительную обработку
                "confidence": avg_confidence,
                "validation_results": self.validate_document({
                    "raw_text": raw_text,
                    "confidence": avg_confidence
                })
            }
        except Exception as e:
            self.logger.error(f"Error in document processing: {str(e)}")
            return {
                "raw_text": "",
                "structure": {
                    "sentences": 0,
                    "paragraphs": 0,
                    "structure": {
                        "sentences": [],
                        "paragraphs": []
                    }
                },
                "entities": [],
                "confidence": 0.0,
                "validation_results": {
                    "is_valid": False,
                    "message": str(e),
                    "details": []
                }
            }

    def validate_document(self, extracted_data: Dict) -> Dict:
        """Validate extracted document data"""
        try:
            if not extracted_data.get("raw_text"):
                return {
                    "is_valid": False,
                    "message": "No text was extracted from the document",
                    "details": []
                }
            
            confidence = extracted_data.get("confidence", 0.0)
            
            # Более мягкий порог доверия для кириллического текста
            if confidence < 40.0:
                return {
                    "is_valid": False,
                    "message": f"Low confidence in text extraction: {confidence:.2f}%",
                    "details": []
                }
            
            # Проверка на наличие кириллических символов
            raw_text = extracted_data.get("raw_text", "")
            if not re.search(r'[А-Яа-я]', raw_text):
                return {
                    "is_valid": False,
                    "message": "No Cyrillic characters found in extracted text",
                    "details": []
                }
            
            return {
                "is_valid": True,
                "message": "Document validation successful",
                "details": []
            }
        except Exception as e:
            self.logger.error(f"Error in document validation: {str(e)}")
            return {
                "is_valid": False,
                "message": str(e),
                "details": []
            }


