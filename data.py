from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from excel import makeExcel
from sql_client import InsertToSQL



def extractData(url,semester,major):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)


    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)

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
    #select2-results-1
    drop_down=driver.find_element(by=By.ID,value="select2-results-1")
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
                        time.sleep(0.1)
                        time.sleep(0.1)
                        link = cell.find_element(By.CLASS_NAME,"section-details-link")
                        link.click()
                        course_number = driver.find_element(By.ID,"courseNumber")
                        row_el.append(course_number.text)

                        pre_req = driver.find_element(By.CSS_SELECTOR,"#preReqs a")
                        pre_req.click()
                        time.sleep(0.1)
                        
                        pre_req_el = driver.find_element(By.ID,"classDetailsContentDetailsDiv")
                          
                        if  pre_req_el :
                            pre_req_text =pre_req_el.text
                            row_el.append(pre_req_text)
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

                print(row_el)
                table_cells.append(row_el)
        next_button= driver.find_element(by=By.CLASS_NAME,value="next")
        next_button.click()
    print(table_cells)
    makeExcel(table_cells)
    InsertToSQL(table_cells)