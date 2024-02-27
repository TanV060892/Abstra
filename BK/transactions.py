import os
from abstra.forms import run_steps, Page
from abstra.tables import insert
from abstra.forms import display_progress
from abstra.common import get_persistent_dir
from datetime import datetime

# Page 1: Bio Information
page1 = (
    Page()
    .display("Bio Information")
    .read("Name", key="name")
    .read_email("Email", key="email")
    .read_phone("Mobile", key="mobile")
)

# Page 2: Statement Details
page2 = (
    Page()
    .display("Upload Files")
    .read_file("Bank Statement", accept=".pdf", hint="Bank Statement in .pdf Format Only", required=False, key='statement')
    .display("")
    .read_file("Transactions", accept=".xlsx", hint="Transaction Details in .xlsx Format Only", required=False, key='transactions')
)

def validate_and_upload_form(function_response):
    
    stmt_file_name = txn_file_name = ''

    persistent_dir = get_persistent_dir()
    logs_directory = persistent_dir / datetime.now().strftime("%d-%m-%Y") / function_response['email']
    if not logs_directory.exists():
        logs_directory.mkdir(parents=True, exist_ok=True)

    if function_response['statement'] is not None :
        stmt_file = function_response['statement'].file
        stmt_file_name = os.path.basename(stmt_file.name)
        stmt_file_content = stmt_file.read()
        if os.path.splitext(stmt_file_name)[1] == '.pdf':
            logs = logs_directory / stmt_file_name
            with open(logs, "wb") as destination_file:
                destination_file.write(stmt_file_content)
        else :
           return {'error':"Please provide a valid PDF file."}

    if function_response['transactions'] is not None :
        txn_file = function_response['transactions'].file
        txn_file_name = os.path.basename(txn_file.name)
        txn_file_content = txn_file.read()
        if os.path.splitext(txn_file_name)[1] == '.xlsx':
            logs = logs_directory / txn_file_name
            with open(logs, "wb") as destination_file:
                destination_file.write(txn_file_content)
        else:
            return {'error':"Please provide a valid CSV file."}
        

    # Insert details into table 
    insert("form_details", {
        "name": function_response['name'],
        "email_id":function_response['email'],
        "statement_file":stmt_file_name,
        "transaction_file":txn_file_name
    })

    return {'message':"Details Updated Successfully."}


# Reactive pages will start with previous responses
def render(function_response):
  for i in range(10):
    display_progress(i, 10, text="Computing values")
  if 'message' in function_response :
    return Page().display(function_response['message'])
  else :
    return Page().display(function_response['error'])
 
page3 = Page().reactive(render)

steps_response = run_steps([page1,page2, validate_and_upload_form, page3])

