"""
HR OCR Parser Service
Extract text from image-based PDFs and image files using OCR
Supports: PNG, JPG, JPEG, GIF, BMP, TIFF and image-based PDFs
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import logger

# Check for OCR dependencies
OCR_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    import os
    OCR_AVAILABLE = True
    logger.info("✅ OCR support enabled (pytesseract + pillow + pdf2image)")
    
    # Set Poppler path for Windows (your specific installation + common locations)
    import platform
    if platform.system() == 'Windows':
        poppler_paths = [
            r'C:\Users\H P\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin',  # Your path
            r'C:\Program Files\poppler\Library\bin',
            r'C:\Program Files (x86)\poppler\Library\bin',
        ]
        
        for poppler_path in poppler_paths:
            if Path(poppler_path).exists():
                # Add to PATH environment variable for this process
                os.environ['PATH'] = poppler_path + os.pathsep + os.environ.get('PATH', '')
                logger.info(f"✅ Poppler found at: {poppler_path}")
                logger.info(f"✅ Poppler added to PATH for this session")
                break
        else:
            logger.warning("⚠️ Poppler not found in common locations")
            logger.warning(f"💡 Please add Poppler to PATH")
            
except ImportError as e:
    logger.warning(f"⚠️ OCR support not available: {e}")
    logger.warning("💡 Install with: pip install pytesseract pillow pdf2image")


class OCRParser:
    """Extract text from images and image-based PDFs using OCR"""
    
    def __init__(self):
        """Initialize OCR parser"""
        if OCR_AVAILABLE:
            # Set Tesseract path for Windows
            import platform
            if platform.system() == 'Windows':
                # Common Tesseract installation paths
                tesseract_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                    r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(Path.home().name)
                ]
                
                for tesseract_path in tesseract_paths:
                    if Path(tesseract_path).exists():
                        pytesseract.pytesseract.tesseract_cmd = tesseract_path
                        logger.info(f"✅ Tesseract found at: {tesseract_path}")
                        break
                else:
                    logger.warning("⚠️ Tesseract not found in common locations")
                    logger.warning("💡 Please install from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse image or image-based PDF
        
        Args:
            file_path: Path to file
        
        Returns:
            Dictionary with extracted text
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            file_ext = file_path.suffix.lower()
            
            if file_ext == '.pdf':
                return self._parse_image_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif']:
                return self._parse_image(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type for OCR: {file_ext}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'OCR parsing failed: {str(e)}'
            }
    
    def _parse_image_pdf(self, file_path: Path) -> Dict:
        """Parse image-based PDF using OCR"""
        try:
            logger.info(f"📄 Converting PDF pages to images: {file_path.name}")

            # Convert PDF pages to images (300 DPI for better OCR accuracy)
            try:
                images = pdf2image.convert_from_path(file_path, dpi=300)
            except Exception as pdf_error:
                error_msg = str(pdf_error)
                if 'poppler' in error_msg.lower() or 'unable to get page count' in error_msg.lower():
                    logger.error(f"⚠️ Poppler not installed - required for PDF OCR")
                    logger.error(f"💡 Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases")
                    logger.error(f"💡 Extract to C:\\Program Files\\poppler and add to PATH")
                    return {
                        'success': False,
                        'error': 'Poppler not installed. Install from: https://github.com/oschwartz10612/poppler-windows/releases',
                        'needs_poppler': True
                    }
                else:
                    raise pdf_error

            if not images:
                return {
                    'success': False,
                    'error': 'No pages found in PDF'
                }

            # OCR each page
            all_text = []
            for i, image in enumerate(images, 1):
                logger.info(f"🔍 OCR processing page {i}/{len(images)}...")
                text = pytesseract.image_to_string(image, lang='eng')
                all_text.append(f"--- Page {i} ---\n{text}")

            full_text = '\n\n'.join(all_text)

            total_chars = len(full_text)
            logger.info(f"✅ OCR extracted {total_chars} characters from {len(images)} pages")

            return {
                'success': True,
                'text': full_text,
                'source': f'OCR from PDF: {file_path.name}',
                'pages': len(images),
                'characters': total_chars
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'PDF OCR failed: {str(e)}'
            }
    
    def _parse_image(self, file_path: Path) -> Dict:
        """Parse image file using OCR"""
        try:
            logger.info(f"📷 Processing image: {file_path.name}")
            
            # Open image
            image = Image.open(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng')
            
            char_count = len(text)
            logger.info(f"✅ OCR extracted {char_count} characters from image")
            
            return {
                'success': True,
                'text': text,
                'source': f'OCR from image: {file_path.name}',
                'characters': char_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image OCR failed: {str(e)}'
            }
    
    def is_image_based_pdf(self, file_path: Path) -> bool:
        """
        Check if PDF is image-based (needs OCR)
        
        Returns True if PDF has no selectable text
        """
        try:
            # Try to extract text with pdfplumber first
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        return False  # Has text, not image-based
            
            return True  # No text found, likely image-based
            
        except ImportError:
            # If pdfplumber not available, assume it might need OCR
            return True
        except Exception as e:
            logger.warning(f"⚠️ Error checking PDF type: {e}")
            return True  # Assume image-based if can't check
    
    def preprocess_image(self, image_path: Path, output_path: Path = None) -> Path:
        """
        Preprocess image for better OCR results
        
        Args:
            image_path: Path to input image
            output_path: Path to save processed image (optional)
        
        Returns:
            Path to processed image
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            # Open image
            image = Image.open(image_path)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Sharpen image
            image = image.filter(ImageFilter.SHARPEN)
            
            # Save or return
            if output_path:
                image.save(output_path)
                return output_path
            else:
                # Save to temp file
                temp_path = image_path.parent / f"processed_{image_path.name}"
                image.save(temp_path)
                return temp_path
                
        except Exception as e:
            logger.error(f"❌ Image preprocessing failed: {e}")
            return image_path


# Test the OCR parser
if __name__ == "__main__":
    parser = OCRParser()
    
    print("=" * 60)
    print("OCR PARSER TEST")
    print("=" * 60)
    
    if OCR_AVAILABLE:
        print("\n✅ OCR libraries loaded successfully")
        print(f"   Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
        
        # Test with sample text image (if exists)
        test_image = Path(__file__).parent.parent.parent / "Resumes" / "test_ocr.png"
        if test_image.exists():
            print(f"\n📷 Testing with: {test_image.name}")
            result = parser.parse_file(test_image)
            
            if result['success']:
                print(f"\n✅ OCR Result:")
                print(f"   Characters: {result.get('characters', 0)}")
                print(f"   Source: {result.get('source', 'N/A')}")
                print(f"\n📄 Extracted Text (first 200 chars):")
                print(f"   {result['text'][:200]}...")
            else:
                print(f"\n❌ OCR failed: {result.get('error')}")
        else:
            print(f"\n⚠️ No test image found at: {test_image}")
            print("💡 Place a test image in Resumes/ folder to test OCR")
    else:
        print("\n❌ OCR not available")
        print("💡 Install with: pip install pytesseract pillow pdf2image")
