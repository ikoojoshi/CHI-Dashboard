from flask import render_template, Blueprint, request, jsonify
from .utils import create_map
import pandas as pd
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/map')
def map_page():
    # Render the map.html template which includes the iframe
    return render_template('map.html')

@main.route('/update_map')
def update_map():
    # Get parameters from the request to filter the map data
    view_type = request.args.get('view_type', 'cities')
    filter_program = request.args.get('filter_program', None)
    keyword = request.args.get('keyword', None)

    map_file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/static/map.html'   
    
    # Delete existing map.html if it exists
    if os.path.exists(map_file_path):
        print("deleting file")
        os.remove(map_file_path)
    
    print(view_type)
    # Generate and save the map as HTML
    create_map(view_type=view_type, filter_program=filter_program, keyword=keyword)
    print(view_type)
    
    # Return a 204 No Content response to signify that the map was updated successfully
    return '', 204

@main.route('/programs')
def get_programs():
    # Fetch unique program names based on view type
    view_type = request.args.get('view_type', 'cities')
    file_path = f'app/data/ClimateActionPlan_{view_type.capitalize()}.csv'
    
    # Load data and extract unique program names
    df = pd.read_csv(file_path)
    programs = df['Program Name'].unique().tolist()
    
    return jsonify({"programs": programs})
