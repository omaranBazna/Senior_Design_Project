from data import extractData
from extract_evaluation import process_student_profile

url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/classSearch/classSearch"
semester = "Winter 2024"
major = ""

extractData(url,semester,major)
