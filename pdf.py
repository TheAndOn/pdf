from genericpath import exists
import os
import pdfplumber
import os
import shutil
import sys

workspace = os.getcwd()
input_folder = os.path.join(workspace, 'in')
log_folder = os.path.join(workspace, 'logs')
output_folder = os.path.join(workspace, 'out')

match_due_date = "Förfallodatum: "
match_cost = "Att betala: "
match_row_before_name = 'NR/MEDDELANDE ANGES:'

class pdf_object():
    '''
        Class defining the properties of a PDF
    '''
    def __init__(self):
        self.original_name = ''
        self.path = ''
        self.due_date = ''
        self.name_person = ''
        self.amount = 0


    def save_log(self, text):
        log = open(os.path.join(log_folder, self.log_name), 'w')
        log.write(text)
        log.close()

    def open_log(self):
        return open(os.path.join(log_folder, self.log_name), 'r')


def get_pdfs():
    '''
        Get a list with all PDF info
    '''
    pdf_list = []
    for file_name in os.listdir(input_folder):                        # List directory files
        pdf = pdf_object()                                              # Create pdf object with all data
        pdf.original_name = file_name
        pdf.log_name = file_name.replace('.pdf', '.txt')
        pdf.path = os.path.join(input_folder, file_name)

        # Get pdf content and store the log
        with pdfplumber.open(pdf.path) as pdf_file:
            page = pdf_file.pages[0]
            text = page.extract_text()
            pdf.save_log(text)

        # Get data from the stored log
        log = pdf.open_log()
        bool_row_before_name_found = False
        print("###### PDF : " + str(pdf.original_name))
        for line in log.readlines():
            if match_due_date in line:
                pdf.due_date = line.split(': 20')[-1].replace('-','').replace('\n','')
                print(pdf.due_date)
            elif match_cost in line:
                pdf.amount = line.split(': ')[-1].split(',')[0].replace(' ','')
                print(pdf.amount)
            elif (match_row_before_name in line) and not bool_row_before_name_found:
                bool_row_before_name_found = True
            elif bool_row_before_name_found:
                pdf.name_person = line.replace('\n','')
                bool_row_before_name_found = None
                print(pdf.name_person)
        
        pdf_list.append(pdf)
    return pdf_list

def copy_pdfs(pdf_list):
    '''
        Copy pdfs to output folder with the new name
    '''
    for pdf in pdf_list:
        input_pdf = os.path.join(input_folder, pdf.original_name)
        output_name = pdf.due_date + '_' + pdf.name_person + '_' + pdf.amount + 'SEK.pdf'
        output_pdf = os.path.join(output_folder, output_name)
        shutil.copy(input_pdf, output_pdf)


def main():
    # Clean up and create new folders + check folder setup
    if not exists(input_folder):
        print("ERROR : No folder called 'in'. Create a folder called in")
        sys.exit(1)
    if len(os.listdir(input_folder)) == 0:
        print("ERROR : In folder is empty. Place files inside the folder")
        sys.exit(1)
    if exists(log_folder):
        shutil.rmtree(log_folder, ignore_errors=True)
    os.makedirs(log_folder)
    if exists(output_folder):
        shutil.rmtree(output_folder, ignore_errors=True)
    os.makedirs(output_folder)
    
    # Get PDF data and store in pdf object list
    pdf_list = get_pdfs()
    # Copy PDFs with new name to out folder
    copy_pdfs(pdf_list)

#################################################################################
# Main function
#################################################################################
main()
