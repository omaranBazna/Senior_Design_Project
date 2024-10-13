from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from excel import makeExcel
from sql_client import InsertToSQL
import re


def search_for_semester(driver,semester):
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


def extractData(url,semester,major):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    drop_down = search_for_semester(driver,semester):

    first_option = drop_down.find_element(By.XPATH, ".//li[1]//div/div") 
    first_option.click()
    driver.implicitly_wait(5)
    continue_button = driver.find_element(by=By.ID,value="term-go")
    continue_button.click()
    driver.implicitly_wait(5)
    field = driver.find_element(by=By.CLASS_NAME,value="select2-choices")
    input_child = field.find_element(By.XPATH, ".//input")
    input_child.clear()
    input_child.send_keys(major)
    driver.implicitly_wait(10)
    drop_down = driver.find_element(by=By.ID,value="select2-drop")
    first_option = drop_down.find_element(By.XPATH, ".//li[1]//div/div")
    first_option.click()
    driver.implicitly_wait(10)
    search_button = driver.find_element(by=By.ID,value="search-go")
    search_button.click()

    driver.implicitly_wait(10)

    count = int(driver.find_element(by=By.CLASS_NAME,value="total-pages").text)
    table_cells = []

    for i in range(count):
        time.sleep(1)
        table = driver.find_element(by=By.TAG_NAME,value="tbody")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for index_var, row in enumerate(rows):
                # Get all cells in the row
                cells = row.find_elements(By.TAG_NAME, "td")  # Use "th" if there are header cells
                row_el=[]
                index = 0
                for cell in cells:
                    if index == 0:
             
                        time.sleep(0.3)
                        link = cell.find_element(By.CLASS_NAME,"section-details-link")
                        link.click()
                        time.sleep(0.3)
                        course_number = driver.find_element(By.ID,"courseNumber")
                        row_el.append(course_number.text)
                        time.sleep(0.3)
                        pre_req = driver.find_element(By.CSS_SELECTOR,"#preReqs a")
                        pre_req.click()
                        time.sleep(0.3)
                        
                        pre_req_el = driver.find_element(By.ID,"classDetailsContentDetailsDiv")
                          
                        if  pre_req_el :
                            pre_req_text =pre_req_el.text
                            #print(pre_req_text)
                            no_preq="Catalog Prerequisites\nNo prerequisite information available."
                            if no_preq == pre_req_text:
                                row_el.append("None")
                            else:
                                filtered_preq = pre_req_text.split("\n")[3:]
                                filtered_preq = "\n".join(filtered_preq)
                                filtered_preq = filtered_preq.replace("Course or Test: ","")
                                filtered_preq = filtered_preq.replace("Minimum Grade of ","")
                                filtered_preq = filtered_preq.replace("\n May not be taken concurrently.","")
                                
                                
                                result = process_req(pre_req_text)
                                row_el.append(result)
                            close_button= driver.find_element(By.CSS_SELECTOR,".ui-dialog-buttonset")
                            close_button.click()
                            time.sleep(0.1)
                        else:
                            row_el.append("no data for pre-requests")

                    index +=1
                    
                    if index == 9:
                        divs = cell.find_elements(By.CLASS_NAME,"meeting")
                        index_2 = 0
                        times = ""
                        for div_el in divs:
                            is_class_el = div_el.find_elements(By.CSS_SELECTOR,".tooltip-row")
                            full_text = is_class_el[0].get_attribute('textContent')
                            
                            if "class" in full_text.lower():
                                highlighted = div_el.find_elements(By.CLASS_NAME,"ui-state-highlight")
                                for index_3 in range(len(highlighted)):
                                    el = highlighted[index_3]
                                    times += el.get_attribute("data-name")
                                    if index_3 < len(highlighted)-1:
                                        times +="-"
                                meeting_time_el = div_el.find_elements(By.TAG_NAME,"span")
                                meeting_time = meeting_time_el[1].text
                                times +=f" , {meeting_time}"
                                index_2 += 1
                                row_el.append(times)
                                break
                    
                    if index==1 or index == 8 or index== 11:
                        if cell and hasattr(cell, "text"):
                          text = cell.text
                          if not text == '':
                            row_el.append(text)
                        else:
                            row_el.append("")

            
                table_cells.append(row_el)
        next_button= driver.find_element(by=By.CLASS_NAME,value="next")
        next_button.click()

    makeExcel(table_cells)
    InsertToSQL(table_cells)







def process_req(input_str):

    filtered_preq = input_str.split("\n")[3:]
    filtered_preq = "\n".join(filtered_preq)
    filtered_preq = filtered_preq.replace("Course or Test: ","")
    filtered_preq = filtered_preq.replace("Minimum Grade of ","")
    input_str = filtered_preq.replace("\n May not be taken concurrently.","") 

    first_char = input_str[0]
    if first_char != "(":
        input_parts = input_str.split("\n")
        part1 = input_parts[0].strip().split(" ")[-1]
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
        course_name = course.strip().replace("(\n","").replace("\n)","")
        course_parts = course_name.split("\n")
        part1 = course_parts[0].strip().split(" ")[-1]
        part2 = course_parts[1].strip()
        course_parts = [part1,part2]
        course_name = ",".join(course_parts)
        result.append(course_name)  # Add course
        if i < len(operators):
            result.append(operators[i])  # Add operator

    # Print the result

    return result
