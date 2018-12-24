from setuptools import find_packages, setup

setup(
    name="donate",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-migrate',
        'flask-sqlalchemy',
        'flask-validator',
        'babel',
        'gitpython',
        'pdoc',
        'pytest',
        'python-dotenv',
        'sadisplay',
        'werkzeug',
    ],
)
