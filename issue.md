
      7 # Activate virtual environment
      8 source venv/bin/activate
      9 
     10 # Install NEW Python packages for HR automation (OCR 
        support)
     11 pip install pytesseract pdf2image pillow
     12 
     13 # Install Poppler for PDF OCR (Ubuntu/Debian)        
     14 apt-get install -y poppler-utils
     15 
     16 # Install Tesseract OCR (Ubuntu/Debian)
     17 apt-get install -y tesseract-ocr
     18 
     19 # Install English language pack for Tesseract        
     20 apt-get install -y tesseract-ocr-eng
     21 
     22 # Verify installations
     23 tesseract --version
     24 pdfinfo -v





scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" D:\DATA\HACKATHON_0\AI_Employee_Vault/execute_approved.py  root@167.71.237.77:/home/AI_Employee/

scp -i "$KEY" -r "$LOCAL/services/*" D:\DATA\HACKATHON_0\AI_Employee_Vault/services/

scp -i "$KEY" "$LOCAL/services/google/docs_service.py" root@167.71.237.77:/home/AI_Employee/services

scp -i "$KEY" "$LOCAL/services/google/calendar_service.py" root@167.71.237.77:/home/AI_Employee/services

scp -i "$KEY" "$LOCAL/services/__init__.py" root@167.71.237.77:/home/AI_Employee/services
nan
scp -i "$KEY" "$LOCAL/services/hr_candidate_tracker.py" root@167.71.237.77:/home/AI_Employee/services

Move-Item calendar_service.py, docs_service.py, drive_service.py, sheets_service.py -Destination .\google\

mv calendar_service.py docs_service.py drive_service.py sheets_service.py google/

"$LOCAL/services/hr_ocr_parser.py"

scp -i "$KEY" "$LOCAL/services/hr_resume_doc_creator.py", "$LOCAL/services/hr_ocr_parser.py" root@167.71.237.77:/home/AI_Employee/services

source /home/venv/bin/activate

Knowledge_Base
Post_Images
Resumes
Support_Tickets
Uploads

