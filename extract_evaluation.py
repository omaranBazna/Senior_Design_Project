import base64
from email import message_from_binary_file
from bs4 import BeautifulSoup

def get_content(cell,index):
    cell_content = cell.decode_contents()
   
    if index == 0:
        if "Yes" in cell_content: return "Yes" 
        return "No"

    cell_soup = BeautifulSoup(cell_content, 'lxml')
    remaining_text = cell_soup.div.next_sibling

    return remaining_text.strip()




# Path to your MHTML file
mhtml_file = "evaluation.mhtml"

# Step 1: Read and parse the MHTML file
with open(mhtml_file, 'rb') as file:
    msg = message_from_binary_file(file)

# Step 2: Find and decode the HTML part
html_part = None
for part in msg.walk():
    if part.get_content_type() == "text/html":
        html_part = part.get_payload(decode=True)
        break

if html_part is None:
    print("No HTML part found in the MHTML file.")
else:
    # Decode HTML content if it is base64-encoded
    try:
        html_content = base64.b64decode(html_part).decode('utf-8')
    except:
        html_content = html_part.decode('utf-8')

    # Step 3: Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')


    # Example: Find all elements with class 'intro'
    tables = soup.find_all(class_="datadisplaytable udm_capp_table DETAILS xe-table xe-table-xs")
    
    table = tables[0]
    eles = table.find_all(class_="odd udm_capp_tr DETAIL_REQUIREMENT")
    for ele in eles:
        cells = ele.find_all("td")
        index = 0 
        row_el = []
        for cell in cells:
            cell_content =  get_content(cell,index)
            if index == 0  or index == 1 or index == 7: 
                row_el.append(cell_content)
            index += 1
        print(row_el)
        print("\n--------------\n")

