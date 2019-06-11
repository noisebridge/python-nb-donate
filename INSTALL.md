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
FLASK_DEBUG=1  # do not use this in production.  security vulnerability.
FLASK_RUN_PORT=5005

STRIPE_KEY="<get from stripe admin>"
STRIPE_SECRET="<get from stripe admin>"

DONATE_SECRET="<random bits of entropy, available in the woodshop>"
```

# Database installation
`$ flask db init` will complain if the migrations directory exists, which it will since it's included in the package.  It's fine.  When it does complain, make sure the directory migrations/versions exists.  If not, just create the directory.

Note that migrations/env.py contains the configuration for the models used by alembic for migrations.  lines 18-27 are critical for the automigrations to be generated.  Update these imports if any new model is created.

# Application Configuration Data
Configuration is stored in a few places.

## Environment Variables
Environment variables are used to select which environment to run, and perhaps other settings like port, keys, etc.  Some are provided when launching the app.  It's also possible dot-env is used by placing a `.env` file in the application root.  These are loaded into environment variables when the the application is run.

## autoapp.py
Some configuration is handled here when the application is first created and run.  For example, different configuration is loaded based on the environment variable `FLASK_APP`, and based on the loaded configuration, logging configuration is also handled.

## donate/settings.py
This file contains a base configuration class Config and other classes which inheret it.  This is where database, logging, and other config is located.
