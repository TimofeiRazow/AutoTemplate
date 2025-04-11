from flask import Flask, jsonify, request, render_template, send_file
import json
import os
from werkzeug.utils import secure_filename
import logging
from pathlib import Path

from ocr_processor import OCRProcessor
from document_analyzer import DocumentAnalyzer
from template_manager import TemplateManager
import search_engine as se
import parser as p

app = Flask(__name__)
app.secret_key = 'r3bFSgsrbdJGUqFYUYemSGGi'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
ocr_processor = OCRProcessor()
document_analyzer = DocumentAnalyzer()
template_manager = TemplateManager()

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/search/template", methods=["POST"])
def get_data():
    data = request.get_json()
    message = data.get("message", "Нет данных")
    name, template = template_manager.get_template_by_message(message)
    json_data = {
        "response": name,
        "info": template
    }
    return jsonify(json_data)

@app.route("/api/document/create", methods=["POST"])
def get_document_url():
    data = request.get_json()
    logger.info(f"Received document creation request: {data}")
    
    try:
        data = p.declensionText(data)
        p.renderDocument(p.flatten_json(data))
        url = request.host_url + "static/generic/document.docx"
        return jsonify({"url": url})
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/document/upload", methods=["POST"])
def upload_document():
    if 'file' not in request.files:
        print("No file part")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(file.filename):
        print("File type not allowed")
        return jsonify({"error": "File type not allowed"}), 400
    
    if request.content_length and request.content_length > MAX_FILE_SIZE:
        print("File too large")
        return jsonify({"error": "File too large"}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process document with OCR
        ocr_result = ocr_processor.process_document(filepath)
        template = template_manager.get_template_by_message(" ".join(ocr_result["raw_text"].split()[0:10]))
        # Analyze document structure
        structure = document_analyzer.analyze_structure(ocr_result["raw_text"])
        
        # Extract entities using the new NER implementation
        entities = document_analyzer.extract_entities(ocr_result["raw_text"])
        
        # Validate entities
        validation_result = document_analyzer.validate_entities(entities)
        print(template)
        print(entities)
        return jsonify({
            "structure": structure,
            "entities": validation_result,
            "template": template,
            "raw_text": ocr_result["raw_text"]
        })
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route("/api/templates/search", methods=["POST"])
def search_templates():
    data = request.get_json()
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    try:
        # Get all templates
        templates = []
        for i in range(1, 41):  # Assuming we have templates from 1 to 40
            template = template_manager.get_template(i)
            if template:
                templates.append({
                    "id": i,
                    "name": template.get("template", ""),
                    "description": template.get("advices", {}).get("brief_info", "")
                })
        
        # Filter templates based on search query
        matching_templates = []
        for template in templates:
            if query.lower() in template["name"].lower() or \
               query.lower() in template["description"].lower():
                matching_templates.append(template)
        
        return jsonify({
            "templates": matching_templates,
            "count": len(matching_templates)
        })
    except Exception as e:
        logger.error(f"Error searching templates: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/template/<int:template_number>", methods=["GET"])
def get_template(template_number):
    try:
        template = template_manager.get_template(template_number)
        if not template:
            return jsonify({"error": f"Template {template_number} not found"}), 404
        
        return jsonify({
            "id": template_number,
            "name": template.get("template", ""),
            "description": template.get("advices", {}).get("brief_info", ""),
            "fields": template.get("user_input", {}),
            "settings": template.get("settings", {})
        })
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/template/validate", methods=["POST"])
def validate_template_data():
    data = request.get_json()
    template_number = data.get("number_of_template")
    
    if not template_number:
        return jsonify({"error": "Template number is required"}), 400
    
    validation_result = template_manager.validate_template_data(template_number, data)
    return jsonify(validation_result)

if __name__ == "__main__":
    se.init()
    app.run(debug=True)