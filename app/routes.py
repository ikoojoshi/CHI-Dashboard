from flask import render_template, Blueprint
from .utils import create_map

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/map')
def map_view():
    map_html = create_map()
    return render_template('map.html', map_html=map_html)
