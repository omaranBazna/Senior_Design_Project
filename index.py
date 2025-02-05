from flask import Flask, request, redirect, url_for, render_template, send_file
from sql_client import clear_all, get_all_elements,find_element,find_element_by_attr_only,get_attr_list_elements
from extract_evaluation import process_student_profile,check_if_pre_req_met
import os
import json
from flask_cors import CORS
from flask_cors import cross_origin
app = Flask(__name__)
from data import extractData
import shutil
CORS(app, resources={r"/*": {"origins": ["https://stellular-axolotl-d0a978.netlify.app","https://thunderous-tartufo-7ce2f7.netlify.app", "https://senior-design-project.onrender.com","https://astounding-baklava-6ad077.netlify.app","http://localhost:3000","http://localhost:8000","https://lovely-nasturtium-ed889c.netlify.app"]}})




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
def home():
    return render_template('index.html')  # Renders the HTML file

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


@app.route('/create_db', methods=['POST'])
def create_db():
    year = request.form.get('year')
    semester = request.form.get('semester')
    startPage= request.form.get("startPage")
    endPage = request.form.get("endPage")
    
    url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/classSearch"
    major = ""

    extractData(url,semester+" "+year,major,startPage,endPage)
    return {"msg":"success"}

@app.route('/clear_temp_db', methods=['GET'])
def clear_temp_db():
    clear_all()
    return {"msg":"success"}



@app.route('/download_db', methods=['GET'])
def download_temp_db():
    file_path = "./temp.db"  # Ensure this file exists
    return send_file(file_path, as_attachment=True)





@app.route('/upload_db', methods=['POST'])
def upload_db():
    if 'dbFile' not in request.files:
        return "No file part", 400

    file = request.files['dbFile']
    if file.filename == '':
        return "No selected file", 400

    file_path = "persistant.db"  # Save as persistent.db in the root folder
    file.save(file_path)
    
    return "Database file uploaded successfully as persistent.db"

@app.route("/reset_2024", methods=["GET"])
def reset_2024():
    source_file = "database_2.db"
    destination_file = "persistant.db"

    try:
        shutil.copy(source_file, destination_file)
        return "Database reset successfully.", 200
    except FileNotFoundError:
        return "Source database file not found.", 404
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/get-attr-list",methods=["GET"])

def get_attr_list():

    return get_attr_list_elements()

if __name__ == '__main__':
    app.run(debug=True,port=port,host="0.0.0.0")
