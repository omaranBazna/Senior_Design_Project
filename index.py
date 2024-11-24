from flask import Flask, request, redirect, url_for, render_template
from sql_client import get_all_elements
from extract_evaluation import process_student_profile
import os
import json
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


def read_file(file_name):
    file = open(file=file_name,mode="r")
    try:
        dictionary = json.load(file)
    except Exception as e:
        print(str(e))
        
    arr =  []
    for key in dictionary:
       if key != "extracted_page" and key != "extracted_rows" :
            arr.append({"key":key,"value":dictionary[key]})
    return arr

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'html'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return "I am up and healthy 😀"

@app.route("/data")
def get_all_data():
    return get_all_elements()

@app.route("/courses")
def get_all_courses():
    return read_file("full_courses.json")


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part

    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']

    # If user does not select a file
    if file.filename == '':
        return "No selected file", 400

    if file :
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        file.save(file_path)
        return process_student_profile(file_path)
        return f"File uploaded successfully: {filename}"
    else:
        return "File not allowed", 400

if __name__ == '__main__':
    app.run(debug=True)

"""
from data import extractData
from extract_evaluation import process_student_profile

url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/classSearch"
semester = "Winter 2024"
major = ""

extractData(url,semester,major)

student_file = "test.mhtml"

process_student_profile(student_file)

"""