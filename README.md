# Steps to run project 
- First make sure you have python install along with pip and virtualenv. Usually pip is installed along python and to install virtualenv: ```pip install virtualenv```  
- clone the repo 
- create virtualenv: ```virtualenv venv``` or ```virtualenv -p python3 venv```
- activate virtualenv: for linux(```source venv/bin/activate```) and for windows(```source venv/Scripts/activate```)
- install django and necessary libraries in venv: ```pip install -r requirements.txt``` (all necessary libraries for project are in requirements.txt file) 
- make neccessary migrations : ```python manage.py makemigrations```
- migrate the files: ```python manage.py migrate```
- create one superuser to access the admin panel: ```python manage.py createsuperuser```
- finally run the project: ```python manage.py runserver```
----- 
# Tools & Technologies Used 
- Django==2.1.5
- django-cors-headers==2.4.0
- pytz==2018.7
- PyYAML==3.13
- Pusher
- djangorestframework==3.9.4
- django-rest-auth==0.9.5
- firebase-admin
- pyjwt==1.7.1
----- 
# Features 
- Basically this project is all about leave management system so some features are as follows
  - Users can login and users can be head of department(H.O.D) or employees
  - Users can apply for leave and leave request is sent to H.O.D for approval/rejection
  - Users can check their leave history
  - Users can check for holidays and birthday notification
  - Users can change their password
  - Admin/H.O.D can check leave request and approve/reject the request
  - Admin/H.O.D can register new employees
  - Admin/H.O.D can generate leave report
  - Forget password feature is also available
----- 
# Demo 
- The landing page when run server:
![landing page](https://github.com/incwell-technology/lms/blob/mobile_api/demo%20images/landing.png)
----- 
# Contribution
-----
