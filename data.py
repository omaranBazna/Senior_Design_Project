from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

import time
from excel import makeExcel
from sql_client import InsertToSQL
import re
import json

subjects_dic = {}

with open("dictionary.json","r") as file:
    subjects_dic = json.load(file)

  
def add_log_window(driver):
    driver.execute_script("""
    // Create the log window
    var logWindow = document.createElement('div');
    logWindow.id = 'logWindow';
    logWindow.style.position = 'fixed';
    logWindow.style.bottom = '0';
    logWindow.style.right = '0';
    logWindow.style.width = '500px';
    logWindow.style.height = '500px';
    logWindow.style.overflowY = 'auto';
    logWindow.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    logWindow.style.color = 'white';
    logWindow.style.fontFamily = 'monospace';
    logWindow.style.fontSize = '12px';
    logWindow.style.padding = '15px';
    logWindow.style.zIndex = '10000';
    logWindow.style.border = '2px solid white';
    document.body.appendChild(logWindow);

    // Add a logMessage function to log messages
    window.logMessage = function(message) {
        var logEntry = document.createElement('div');
        logEntry.textContent = message;
        logEntry.style.margin = "15px"
        logEntry.style.padding = "15px"
        logEntry.style.border = "2px solid white"
        logWindow.appendChild(logEntry);
        logWindow.scrollTop = logWindow.scrollHeight; // Auto-scroll to the bottom
    };
    """)

def log_message(driver,message):
    print(message)
    driver.execute_script(f"logMessage(`{message}`);")

def set_per_page(driver):
    dropdown_element = driver.find_element(By.CLASS_NAME,"page-size-select")
    dropdown = Select(dropdown_element)
    dropdown.select_by_visible_text("50")

def go_to_page(driver,page_number):
    input_element = driver.find_element(By.CLASS_NAME, "page-number")  # Replace with the actual ID

    # Use JavaScript to set the value
    driver.execute_script("arguments[0].value = '12'; arguments[0].dispatchEvent(new Event('input'));", input_element)

    # Simulate pressing the Return key
    input_element.send_keys("\n")


def highlight_element(driver, element, color="yellow"):
    driver.execute_script("arguments[0].setAttribute('style', arguments[0].getAttribute('style') + '; background-color: {};')".format(color), element)
    driver.execute_script("arguments[0].setAttribute('style', arguments[0].getAttribute('style') + '; font-weight:800;')", element)

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

def open_section_details(driver,cell):
    time.sleep(1)
    try:
        link = cell.find_element(By.CLASS_NAME,"section-details-link")
        highlight_element(driver,link,color="red")
        link.click()
    except Exception:
       print("link not found")
    time.sleep(1)


def add_course_num(course_subject,driver,row_el):
    try:
        course_number = driver.find_element(By.ID,"courseNumber")
        highlight_element(driver,course_number,color="green")
    except Exception:
        course_number = "0000"
    row_el.append(course_subject + " " +course_number.text)
    time.sleep(1)


def add_pre_req(driver,row_el):
    try:
        time.sleep(1)
        pre_req = driver.find_element(By.CSS_SELECTOR,"#preReqs a")
        highlight_element(driver,pre_req,color="orange")
        pre_req.click()
    except Exception:
        print("not found")
    time.sleep(1)
    
    try:
        pre_req_el = driver.find_element(By.ID,"classDetailsContentDetailsDiv")
        highlight_element(driver,pre_req_el,color="orange")
        time.sleep(1)
        highlight_element(driver,pre_req_el,color="white")
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
        time.sleep(1)
    else:
        row_el.append("None")


def add_meeting_times(driver,cell,row_el):
    try:
        divs = cell.find_elements(By.CLASS_NAME,"meeting")

    except Exception as e:
        print(str(e))
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
            highlight_element(driver,div_el,color="green")
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


def add_course_name(driver,cell,row_el):
    if cell and hasattr(cell, "text"):
        highlight_element(driver,cell,"green")
        time.sleep(1)
        text = cell.text
        row_el.append(text)
    else:
        log_message(driver,"does not find the cell")
        row_el.append("Name")

def process_table_cell(cell,index,driver,row_el,course_subject):
    if index == 0:
        
        open_section_details(driver,cell)
        add_course_num(course_subject,driver,row_el)
        add_course_name(driver,cell,row_el)
        time.sleep(1)
        add_pre_req(driver,row_el)

    if index == 8:
        add_meeting_times(driver,cell,row_el)

def extractTableRow(row,table_cells,driver,extracted_rows):
    try:
    # Get all cells in the row
        """
        course_subject_element = row.find_element(By.CSS_SELECTOR, '[data-content="Subject"]')
        course_subject = course_subject_element.get_attribute("textContent")
  

        highlight_element(driver, course_subject_element)
        course_subject_description_element = row.find_element(By.CSS_SELECTOR, '[data-content="Subject Description"]')
        course_subject_description = course_subject_description_element.get_attribute("textContent")
       
        highlight_element(driver, course_subject_description_element) 
       
        subjects_dic[course_subject] = course_subject_description
        time.sleep(1)
        print(extracted_rows)
        with open("dictionary.json","w") as file:
            
            subjects_dic["extracted_rows"] = extracted_rows
           
            log_message(driver,str(subjects_dic))
            string = str(subjects_dic).replace("\'","\"")
            file.write(string)
        """
        course_subject_element = row.find_element(By.CSS_SELECTOR, '[data-content="Subject"]')
        course_subject = course_subject_element.get_attribute("textContent")
        cells = row.find_elements(By.TAG_NAME, "td")  # Use "th" if there are header cells
        row_el=[]
        index = 0
        for cell in cells:
            highlight_element(driver, cell)
            process_table_cell(cell,index,driver,row_el,course_subject)
            index += 1
        log_message(driver,str(row_el))
        table_cells.append(row_el)
    except Exception as e:
        print(str(e))
    #print(row_el)
    #print("------")


def extractPageData(driver,table_cells ,extracted_row,extracted_page):
    time.sleep(1)
    try:
        table = driver.find_element(by=By.TAG_NAME,value="tbody")
        rows = table.find_elements(By.TAG_NAME, "tr")
        subjects_dic["extracted_page"] = extracted_page[0]
        extracted_page[0] += 1
        if(extracted_page[0]>3):
            for _ , row in enumerate(rows):
                 extractTableRow(row,table_cells,driver,extracted_row[0])
                 extracted_row[0] += 1
        time.sleep(1)
        next_button = driver.find_element(by=By.CLASS_NAME,value="next")
        next_button.click()
    except Exception as e:
        print(str(e))


def extractData(url,semester,major):
    driver = get_driver(url)    
    drop_down = search_for_semester(driver,semester)
    click_search_button(driver,drop_down,major)
    set_per_page(driver)
    time.sleep(1)
    add_log_window(driver )
    count = get_pages_count(driver)
    table_cells = []
    extracted_row = [0]
    extracted_page = [0]
    for _ in range(count):
        time.sleep(1)
        extractPageData(driver,table_cells,extracted_row,extracted_page)

    #print(subjects_dic)
    makeExcel(table_cells)
    InsertToSQL(table_cells)



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
