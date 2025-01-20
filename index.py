from flask import Flask, request, redirect, url_for, render_template
from sql_client import get_all_elements,find_element,find_element_by_attr_only,get_attr_list_elements
from extract_evaluation import process_student_profile,check_if_pre_req_met
import os
import json
from flask_cors import CORS
from flask_cors import cross_origin
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["https://thunderous-tartufo-7ce2f7.netlify.app", "https://senior-design-project.onrender.com"]}})




port = os.getenv("PORT", 8000)

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
    print("get all data")
    return []
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


def is_valid_course_code(course_string):
    import re
    # Regular expression for course code and number
    print(course_string)
    pattern = r'^[A-Z]{2,4}\s+\d{4}$'
    return bool(re.match(pattern, course_string))

@app.route("/check_course",methods=["POST"])

def check_course():
    data = request.get_json()
    
    course = data["data"]
    if not is_valid_course_code(course):
        return {"error":True, "msg":"not valid course"}

    if not "token" in data:
        return {"error":True, "msg":"missing token courses"}
    
    rows = find_element(course)
    if(len(rows)==0):
        return {"msg":"Not in winter"}
    msg = "Not met"
    result = []
    for i in range(len(rows)):
        row = rows[i]
        if check_if_pre_req_met(data["token"],row):
            result.append(row)
    msg = ""
    return {"msg":msg,"rows":result}

@app.route("/check_attr",methods=["POST"])

def check_attr():
    data = request.get_json()
    attr = data["data"]
    print(attr)
    if not "token" in data:
        return {"error":True, "msg":"missing token courses"}
    
    result = []

    rows = find_element_by_attr_only(attr)
    for i in range(len(rows)):
        row = rows[i]
        if(check_if_pre_req_met(data["token"],row)):
            result.append(row)


    return {"rows":result,"msg":""}


@app.route("/get-attr-list",methods=["GET"])

def get_attr_list():

    return get_attr_list_elements()

if __name__ == '__main__':
    app.run(debug=True,port=port,host="0.0.0.0")
