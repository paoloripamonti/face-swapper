# Import flask and template operators
from flask import Flask, render_template, session


# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Import a module / component using its blueprint handler variable
from app.controllers.home_controller import mod_home as home_module

# Register blueprint(s)
app.register_blueprint(home_module)




