'''!pip install flask
!pip install Pillow
!pip install pytesseract
!pip install pdf2image
!apt-get install poppler-utils
!apt-get install tesseract-ocr
!apt-get install tesseract-ocr-eng'''


print("Script is running!")

from flask import Flask, jsonify, request
from PIL import Image
import pytesseract
import json
import re
from pdf2image import convert_from_path
from pathlib import Path

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_text(img):
    return pytesseract.image_to_string(img)

def clean_text(text):
    replacements = {
        '\u2014': '-',
        '\u2013': '-',
        '\u2018': "'",
        '\u2019': "'",
        '\u201C': '"',
        '\u201D': '"',
        '\u00A0': ' ',
        '\u2022': '*',
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    text = text.replace('\n', ' ')
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    return text

def process_pdf(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        extracted_text = []

        for img in images:
            text = extract_text(img)
            clean = clean_text(text)
            extracted_text.append(clean)

        return {
            "status": "success",
            "text": extracted_text
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


question_data = {}


@app.route('/api/questions', methods=['GET'])
def get_questions():
    return jsonify({
        "status": "success",
        "data": question_data
    })


@app.route('/api/data/input', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file part in the request"
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": "No file selected"
        }), 400

    if file and file.filename.endswith('.pdf'):

        pdf_path = Path(f"temp_{file.filename}")
        file.save(pdf_path)


        result = process_pdf(pdf_path)


        pdf_path.unlink()

        if result["status"] == "success":

            question_data[file.filename] = result["text"]



            return jsonify({
                "status": "success",
                "message": "PDF processed successfully",
                "extracted_text": result["text"]
            }), 200
        else:
            return jsonify(result), 500
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid file format. Please upload a PDF"
        }), 400

def main():

    for year in ['2022.pdf', '2023.pdf', '2024.pdf']:
        pdf_path = Path(year)
        if pdf_path.exists():
            result = process_pdf(pdf_path)
            if result["status"] == "success":
                question_data[year] = result["text"]


    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()