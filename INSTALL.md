# Installation Instructions

1. install python3-pip
2. install python3-virtualenv
3. pip3 install virtualenvwrapper
4. create a virtualenv for donate with python3
5. pip install -r requirements.txt -e . <-- development install
6. run $ pytest
7. retrieve .env file
8. make donate/logs directory (or change log location, this should/can be automated?)
9. flask db init
10. flask db migrate
11. flask db upgrade
12. $ FLASK_ENV=DEVELOPMENT python scripts/initialize_database.py

# .env example

```
FLASK_APP=./autoapp.py
FLASK_ENV=DEVELOPMENT
FLASK_DEBUG=1
FLASK_RUN_PORT=5005

STRIPE_KEY="<get from stripe admin>"
STRIPE_SECRET="<get from stripe admin>"

DONATE_SECRET="<random bits of entropy, available in the woodshop>"
```
