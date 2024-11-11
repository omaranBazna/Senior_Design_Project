from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from excel import makeExcel
from sql_client import InsertToSQL
import re

subjects_dic = {}

def search_for_semester(driver,semester):
    try:
        search_classes = driver.find_element(by=By.ID, value="classSearchLink")
        search_classes.click()
        driver.implicitly_wait(0.5)
        el = driver.find_element(by=By.CLASS_NAME, value="select2-arrow")
        el.click()
        search_input = driver.find_element(by=By.ID,value="s2id_autogen1_search")
        search_input.clear()
        search_input.send_keys(semester)
        search_input.send_keys(Keys.RETURN)
        driver.implicitly_wait(5)
        drop_down=driver.find_element(by=By.ID,value="select2-results-1")
        return drop_down
    except :
        print("can not search for semeter")
        return None

def click_search_button(driver,drop_down,major):
    try:
        first_option = drop_down.find_element(By.XPATH, ".//li[1]//div/div") 
        first_option.click()
        driver.implicitly_wait(5)
        continue_button = driver.find_element(by=By.ID,value="term-go")
        continue_button.click()
    except:
        print("can go to search majors")

    driver.implicitly_wait(5)
    if major != "":
        try:
            field = driver.find_element(by=By.CLASS_NAME,value="select2-choices")
            input_child = field.find_element(By.XPATH, ".//input")
            input_child.clear()
            input_child.send_keys(major)
            driver.implicitly_wait(10)
            drop_down = driver.find_element(by=By.ID,value="select2-drop")
            first_option = drop_down.find_element(By.XPATH, ".//li[1]//div/div")
            first_option.click()
            driver.implicitly_wait(10)
        except Exception:
            print("Can not search major")
    try:
        search_button = driver.find_element(by=By.ID,value="search-go")
        search_button.click()
    except Exception:
         print("search button not found")

    driver.implicitly_wait(10)

def get_driver(url):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url) 
    return driver   

def get_pages_count(driver):
    try:
        total_pages = driver.find_element(by=By.CLASS_NAME,value="total-pages").text
    except Exception:
        total_pages = "0"
    return  int(total_pages)

def open_section_details(cell):
    time.sleep(0.5)
    try:
        link = cell.find_element(By.CLASS_NAME,"section-details-link")
        link.click()
    except Exception:
       print("link not found")
    time.sleep(0.5)


def add_course_num(course_subject,driver,row_el):
    try:
        course_number = driver.find_element(By.ID,"courseNumber")
    except Exception:
        course_number = "0000"
    row_el.append(course_subject + " " +course_number.text)
    time.sleep(0.5)


def add_pre_req(driver,row_el):
    try:
        pre_req = driver.find_element(By.CSS_SELECTOR,"#preReqs a")
        pre_req.click()
    except Exception:
        print("not found")
    time.sleep(0.5)
    try:
        pre_req_el = driver.find_element(By.ID,"classDetailsContentDetailsDiv")
    except Exception:
        pre_req_el = None
    if  pre_req_el :
        pre_req_text = pre_req_el.text
        #print(pre_req_text)
        no_preq="Catalog Prerequisites\nNo prerequisite information available."
        if no_preq == pre_req_text:
            row_el.append("None")
        else:
            filtered_preq = pre_req_text.split("\n")[3:]
            filtered_preq = "\n".join(filtered_preq)
            filtered_preq = filtered_preq.replace("Course or Test: ","")
            filtered_preq = filtered_preq.replace("Minimum Grade of ","")
            filtered_preq = filtered_preq.replace(" May not be taken concurrently.","")
            result = process_req(pre_req_text)
            row_el.append(str(result))
        try:
            close_button= driver.find_element(By.CSS_SELECTOR,".ui-dialog-buttonset")
            close_button.click()
        except Exception:
            print("close button not found")
        time.sleep(0.5)
    else:
        row_el.append("None")


def add_meeting_times(cell,row_el):
    try:
        divs = cell.find_elements(By.CLASS_NAME,"meeting")
    except:
        print("can not find meetings times")
        divs = []
    index_2 = 0
    times = ""
    for div_el in divs:
        try:
            is_class_el = div_el.find_elements(By.CSS_SELECTOR,".tooltip-row")
            full_text = is_class_el[0].get_attribute('textContent')
        except Exception:
            full_text = "not found"
        if "class" in full_text.lower() or "online course" in full_text.lower():
            try:
                highlighted = div_el.find_elements(By.CLASS_NAME,"ui-state-highlight")
                for index_3 in range(len(highlighted)):
                    el = highlighted[index_3]
                    times += el.get_attribute("data-name")
                    if index_3 < len(highlighted) - 1 :
                        times +="-"
            except Exception:
                print("not found")
            try:
                meeting_time_el = div_el.find_elements(By.TAG_NAME,"span")
                meeting_time = meeting_time_el[1].text
                times +=f" , {meeting_time}"
            except Exception:
                print("not found")    
            index_2 += 1
            row_el.append(times)
            break


def add_course_name(cell,row_el):
    if cell and hasattr(cell, "text"):
        text = cell.text
        row_el.append(text)
    else:
        row_el.append("Name")

def process_table_cell(cell,index,driver,row_el,course_subject):
    if index == 0:
        
        open_section_details(cell)
        add_course_num(course_subject,driver,row_el)
        add_course_name(cell,row_el)
        add_pre_req(driver,row_el)

    if index == 8:
        add_meeting_times(cell,row_el)

def extractTableRow(row,table_cells,driver):
    try:
    # Get all cells in the row
        course_subject = row.find_element(By.CSS_SELECTOR, '[data-content="Subject"]').get_attribute("textContent")
        course_subject_description = row.find_element(By.CSS_SELECTOR, '[data-content="Subject Description"]').get_attribute("textContent")
        subjects_dic[course_subject] = course_subject_description
        time.sleep(10)
        with open("dictionary.json","w") as file:
            string = str(subjects_dic).replace("\'","\"")
            file.write(string)
            print(string)
        
        return
        cells = row.find_elements(By.TAG_NAME, "td")  # Use "th" if there are header cells
        row_el=[]
        index = 0
        for cell in cells:
            process_table_cell(cell,index,driver,row_el,course_subject)
            index += 1
        table_cells.append(row_el)
    except Exception as e:
        print(str(e))
    #print(row_el)
    #print("------")


def extractPageData(driver,table_cells ):
    time.sleep(0.5)
    try:
        table = driver.find_element(by=By.TAG_NAME,value="tbody")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for _ , row in enumerate(rows):
             extractTableRow(row,table_cells,driver)
        time.sleep(10)
        next_button = driver.find_element(by=By.CLASS_NAME,value="next")
        next_button.click()
    except Exception as e:
        print(str(e))


def extractData(url,semester,major):
    driver = get_driver(url)    
    drop_down = search_for_semester(driver,semester)
    click_search_button(driver,drop_down,major)

    count = get_pages_count(driver)
    table_cells = []

    for _ in range(count):
         extractPageData(driver,table_cells)

    print(subjects_dic)
    #makeExcel(table_cells)
    #InsertToSQL(table_cells)



def process_req(input_str):
    
    filtered_preq = input_str.split("\n")[3:]
    filtered_preq = "\n".join(filtered_preq)
    filtered_preq = filtered_preq.replace("Course or Test: ","")
    filtered_preq = filtered_preq.replace("Minimum Grade of ","")
    input_str = filtered_preq.replace(" May not be taken concurrently.","") 

    first_char = input_str[0]
    if first_char != "(":
        input_parts = input_str.split("\n")
        print(input_parts)
    
        part1 = input_parts[0].strip()
        part2 = ""
        if len(input_parts) > 1:
            part2 = input_parts[1].strip()
        input_parts = [part1,part2]
        input_str = ",".join(input_parts)
        return [input_str]
    
    course_pattern = r'\([\s\S]+?\)'  # Matches the course blocks
    operator_pattern = r'\b(?:and|or)\b'  # Matches 'and' or 'or' operations

    # Extract the courses and operators
    courses = re.findall(course_pattern, input_str)
    operators = re.findall(operator_pattern, input_str)

    # Combine the courses and operators in a list
    result = []
    for i, course in enumerate(courses):
        #print(course)
        course_name = course.strip().replace("(\n","").replace("\n)","")
        course_parts = course_name.split("\n")
        part1 = course_parts[0].strip()
        part2 = course_parts[1].strip()
        course_parts = [part1,part2]
        course_name = ",".join(course_parts)
        result.append(course_name)  # Add course
        if i < len(operators):
            result.append(operators[i])  # Add operator

    # Print the result

    return result
