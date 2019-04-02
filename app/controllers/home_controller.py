# Import flask dependencies
from flask import Blueprint, render_template, request

# Engine
from app.engine.engine import read_and_swap

# Define the blueprint
mod_home = Blueprint('home', __name__)


# Set the route and accepted methods

# GET /
@mod_home.route("/")
def index():
    return render_template('home/index.html')


# POST /swap
@mod_home.route("/swap", methods=["POST"])
def swap():
    img1 = request.form['img1']
    img2 = request.form['img2']

    return read_and_swap(img1, img2)
