@echo on
call C:\Users\user\anaconda3\Scripts\activate.bat
call conda activate covid19Env
call python dbConfigReport.py
exit
