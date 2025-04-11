import json
import os
from typing import Dict, List, Optional
import logging
from pathlib import Path
from datetime import datetime
import re
import os
import pickle
import requests
from bs4 import BeautifulSoup
import numpy as np
import faiss
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import torch
from sentence_transformers import SentenceTransformer, util
import search_engine as se


class TemplateManager:
    global label_texts, label_embeddings, model, model_template, FILE_PATH, LABELS_CARDS, labels_map, FILE_PATH, EMBEDDINGS_PATH, INDEX_PATH
    def __init__(self, templates_dir: str = "prompt"):
        self.logger = logging.getLogger(__name__)
        self.templates_dir = Path(templates_dir)
        self.templates = {}

        self._load_templates()

    
    def _load_templates(self):
        """Load all templates from the templates directory"""
        try:
            for template_file in self.templates_dir.glob("template_*.json"):
                template_number = int(template_file.stem.split("_")[1])
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.templates[template_number - 1] = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading templates: {str(e)}")
            raise

    def get_template(self, template_number: int) -> Optional[Dict]:
        """Get template by number"""
        return self.templates.get(template_number)
    
    def get_template_json(self, index):
        with open(f"prompt/template_{index + 1}.json", 'r', encoding="utf-8") as f:
            data = f.readlines()
        return json.loads(''.join(data))


    

    def validate_template_data(self, template_number: int, data: Dict) -> Dict:
        """Validate data against template requirements"""
        template = self.get_template(template_number)
        if not template:
            return {
                "is_valid": False,
                "errors": [f"Template {template_number} not found"],
                "warnings": []
            }

        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate required fields
        for field, description in template["user_input"].items():
            if field not in data.get("user_input", {}):
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False

        # Validate field formats
        for field, value in data.get("user_input", {}).items():
            if field in template["user_input"]:
                validation_result = self._validate_field(field, value)
                if not validation_result["is_valid"]:
                    validation_results["errors"].extend(validation_result["errors"])
                    validation_results["is_valid"] = False
                validation_results["warnings"].extend(validation_result["warnings"])

        return validation_results
    
    def get_template_by_message(self, message):
        """Возвращает название шаблона и соответствующий ему шаблон"""
        index = se.classify_query(message)
        print(f"ИНДЕКС {index}")
        return ("Постановление " + se.LABELS_CARDS[index], self.templates.get(index))

    def _validate_field(self, field: str, value: str) -> Dict:
        """Validate individual field value"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Date validation
        if "date" in field.lower():
            if not self._validate_date(value):
                validation_result["errors"].append(f"Invalid date format in {field}: {value}")
                validation_result["is_valid"] = False

        # IIN/BIN validation
        elif "iin" in field.lower():
            if not self._validate_iin(value):
                validation_result["errors"].append(f"Invalid IIN format in {field}: {value}")
                validation_result["is_valid"] = False
        elif "bin" in field.lower():
            if not self._validate_bin(value):
                validation_result["errors"].append(f"Invalid BIN format in {field}: {value}")
                validation_result["is_valid"] = False

        # Amount validation
        elif "amount" in field.lower() or "сумма" in field.lower():
            if not self._validate_amount(value):
                validation_result["warnings"].append(f"Unrecognized amount format in {field}: {value}")

        return validation_result

    def _validate_date(self, date_str: str) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
            return True
        except ValueError:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return True
            except ValueError:
                return False

    def _validate_iin(self, iin: str) -> bool:
        """Validate IIN format"""
        if len(iin) != 12:
            return False
        try:
            int(iin)
            return True
        except ValueError:
            return False

    def _validate_bin(self, bin: str) -> bool:
        """Validate BIN format"""
        if len(bin) != 10:
            return False
        try:
            int(bin)
            return True
        except ValueError:
            return False

    def _validate_amount(self, amount: str) -> bool:
        """Validate amount format"""
        amount_pattern = r'^\d+(?:[.,]\d{2})?\s*(?:тенге|₸|KZT)?$'
        return bool(re.match(amount_pattern, amount, re.IGNORECASE))