# Steps to run project 
- First make sure you have python install along with pip and virtualenv. Usually pip is installed along python and to install virtualenv: ```pip install virtualenv```  
- clone the repo 
- create virtualenv: ```virtualenv venv``` or ```virtualenv -p python3 venv```
- activate virtualenv: for linux(```source venv/bin/activate```) and for windows(```source venv/Scripts/activate```)
- install django and necessary libraries in venv: ```pip install -r requirements.txt``` (all necessary libraries for project are in requirements.txt file) 
- make neccessary migrations : ```python manage.py makemigrations```
- migrate the files: ```python manage.py migrate```
- finally run the project: ```python manage.py runserver```
----- 
# Tools & Technologies Used 
----- 
# Features 
----- 
# Demo 
----- 
# Contribution
-----
