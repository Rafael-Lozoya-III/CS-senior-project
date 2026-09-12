# Group-Match-Senior-Project
Need to create a team for a project but don't know how? Group-Match can help! Its a simpler way to find available teammates with the skills needed to complete the project! 

## Team Members
Rafael Lozoya || Alfredo Zavala || Jordan Saenz

## First-time setup

'''bash
git clone (url of project)
cd CS-senior-project
python -m venv .venv
.venv\Scrips\activate       # Windows
source .venv/bin/activate   # macOS / Linux 
pip install -r requirements.txt
'''

Tip: if python does not work use python3

Build the database and start the server 
'''bash 
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
'''

Open http://127.0.0.1:8000/ you should see the landing page

