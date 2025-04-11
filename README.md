# Legal Document Processing System

A comprehensive system for processing legal documents with OCR, template matching, and document generation capabilities.

## Features

- OCR processing with Tesseract for Cyrillic text
- Document structure analysis
- Entity recognition (names, dates, IIN/BIN, amounts)
- Template management and validation
- Document generation with docxtpl
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- Tesseract OCR with Russian language support
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-rus`
- macOS: `brew install tesseract tesseract-lang`

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```


## Configuration

1. Set Tesseract path in `ocr_processor.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# or
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux/macOS
```

2. Configure upload folder in `app.py`:
```python
UPLOAD_FOLDER = 'uploads'
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Access the web interface at `http://localhost:5000`

### API Endpoints

- `POST /api/search/template` - Search for templates based on query
- `POST /api/document/create` - Create a document from template data
- `POST /api/document/upload` - Upload and process a document
- `GET /api/template/<number>` - Get template by number
- `POST /api/template/validate` - Validate template data

## Security Considerations

- All uploaded files are automatically deleted after processing
- File size is limited to 20MB
- Only allowed file types (PDF, PNG, JPG, JPEG) are accepted
- Input validation is performed on all endpoints

## Error Handling

The system provides detailed error messages for:
- Invalid file types
- File size limits
- OCR processing errors
- Template validation failures
- Document generation issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 