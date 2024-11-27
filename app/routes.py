from flask import render_template, Blueprint, request, jsonify
import pandas as pd
import os

main = Blueprint('main', __name__)


@main.route('/')
def home():
    # Load the CSV file for cities
    data_type = 'cities'
    file_path = f'/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_{data_type}.csv'

    # Check if the file exists
    if not os.path.exists(file_path):
        return render_template('home.html', table_data=[], error=f"File not found: {file_path}")

    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Replace NaN with empty strings
        df = df.where(pd.notnull(df), "")

        # Convert to a list of dictionaries for Jinja2
        table_data = df.to_dict(orient='records')
        return render_template('home.html', table_data=table_data, error=None)

    except Exception as e:
        # Handle errors during file reading
        return render_template('home.html', table_data=[], error=f"Error reading file: {str(e)}")

@main.route('/counties')
def counties():
    file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_counties.csv'

    if not os.path.exists(file_path):
        return render_template('counties.html', table_data=[], error=f"File not found: {file_path}")

    try:
        # Load CSV and drop Lat and Long
        df = pd.read_csv(file_path)
        df = df.drop(columns=['Lat', 'Long'], errors='ignore')
        df = df.where(pd.notnull(df), "")  # Replace NaN with empty strings
        table_data = df.to_dict(orient='records')
        return render_template('counties.html', table_data=table_data, error=None)
    except Exception as e:
        return render_template('counties.html', table_data=[], error=f"Error reading file: {str(e)}")


@main.route('/lhd')
def lhd():
    file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_lhd.csv'

    if not os.path.exists(file_path):
        return render_template('lhd.html', table_data=[], error=f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
        df = df.drop(columns=['Lat', 'Long'], errors='ignore')  # Drop unnecessary columns
        df = df.where(pd.notnull(df), "")  # Replace NaN with empty strings
        table_data = df.to_dict(orient='records')
        return render_template('lhd.html', table_data=table_data, error=None)
    except Exception as e:
        return render_template('lhd.html', table_data=[], error=f"Error reading file: {str(e)}")



@main.route('/map')
def map_page():
    return render_template('map.html')

@main.route('/update_map')
def update_map():
    view_type = request.args.get('view_type', 'cities')
    filter_program = request.args.get('filter_program', None)
    keyword = request.args.get('keyword', None)

    map_file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/static/map.html'
    
    if os.path.exists(map_file_path):
        os.remove(map_file_path)
    
    # Use the create_map function to update the map
    create_map(view_type=view_type, filter_program=filter_program, keyword=keyword)
    
    return '', 204

@main.route('/programs')
def get_programs():
    view_type = request.args.get('view_type', 'cities').lower()
    file_path = f'/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_{view_type}.csv'
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if view_type == "cities":
            programs = df['Program Name'].dropna().unique().tolist()
        else:
            programs = df['Document'].dropna().unique().tolist()
        return jsonify({"programs": programs})
    else:
        return jsonify({"error": f"File not found: {file_path}"}), 404
