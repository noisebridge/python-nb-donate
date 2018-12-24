Donate
======

A rewrite of Noisebridge's donation site in python using Flask.

Quick Start
-----------

Reference: http://flask.pocoo.org/

optional: do it in a virtualenv

``pip install virtualenv; virtualenv venv; source venv/bin/activate``

install requirements

``pip install -r requirements.txt``

run the app

``FLASK_APP=autoapp.py flask run``

Requirements
____________

| Flask
| Flask-Migrate
| Flask-SQLAlchemy
| Flask-Validator
| dot-env

Model Specification
___________________

Financial data is made up of transactions.  A single transaction exchanges and amount of currency.  Transactions occur between two parties: a payer and a receiver.  While the payer and receiver are people or entities, they are modeled as accounts.  The transaction credits one parties account and debits the other simultaneously.  Two accounts are always involved in each transaction.  The collection of transacations builds the structure for double accounting.

Transactions are requested by people and they are approved by others.  In addition to two accounts, each transaction has at least two people associated with it.

Noisebridge is concerned with two top level objects;  Accounts and Projects.

Accounts have some balance of cash which increases with donations and decreases with spending.  An example is the sewing area: People donate money which is then spent on materials.  

Projects have a stated goal.  A project will have at least one account to track donations.  The progress towards the goal is just the sum of the transactions in this account.


.. image:: pics/schema.png
   :width: 60pt

Database Creation / Migration
_____________________________

We use Flask-Migrate to create and run the database.  The workflow is
1) [Once] flask db init to create the migrations folder
2) [Once] edit migrations/env.py to add the model data
3) flask db migrate - creates a migration in the migrations/versions folder which represents the commands to go from teh existing DB state to the new state.  These migration scripts may need to be edited.
4) flask db upgrade - run the migration script.

If having an a issue with a migration, it's important to remore __pycache__ from the migration folder tree to make sure cached versions which may be repeating the same issues.
