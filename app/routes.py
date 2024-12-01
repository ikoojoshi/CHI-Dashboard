from flask import render_template, Blueprint, request, jsonify, send_file, flash, url_for, redirect
import pandas as pd
import os
from app.utils import create_map, get_file_path


main = Blueprint('main', __name__)
cities_file_path = get_file_path("cities")
counties_file_path = get_file_path("counties")
lhd_file_path = get_file_path("lhd")
map_file_path = 'app/static/map.html'


# Cities data
@main.route('/')
def home():
    if not os.path.exists(cities_file_path):
        return render_template('home.html', table_data=[], error=f"File not found: {cities_file_path}")

    try:
        df = pd.read_csv(cities_file_path)
        df = df.where(pd.notnull(df), "")

        table_data = df.to_dict(orient='records')
        return render_template('home.html', table_data=table_data, error=None)

    except Exception as e:
        return render_template('home.html', table_data=[], error=f"Error reading file: {str(e)}")

# Counties data
@main.route('/counties')
def counties():

    if not os.path.exists(counties_file_path):
        return render_template('counties.html', table_data=[], error=f"File not found: {counties_file_path}")

    try:
        # Load CSV and drop Lat and Long
        df = pd.read_csv(counties_file_path)
        df = df.drop(columns=['Lat', 'Long'], errors='ignore')
        df = df.where(pd.notnull(df), "")  # Replace NaN with empty strings
        table_data = df.to_dict(orient='records')
        return render_template('counties.html', table_data=table_data, error=None)
    except Exception as e:
        return render_template('counties.html', table_data=[], error=f"Error reading file: {str(e)}")


@main.route('/lhd')
def lhd():
    
    if not os.path.exists(lhd_file_path):
        return render_template('lhd.html', table_data=[], error=f"File not found: {lhd_file_path}")

    try:
        df = pd.read_csv(lhd_file_path)
        df = df.drop(columns=['Lat', 'Long'], errors='ignore')  # Drop unnecessary columns
        df = df.where(pd.notnull(df), "")  # Replace NaN with empty strings
        table_data = df.to_dict(orient='records')
        return render_template('lhd.html', table_data=table_data, error=None)
    except Exception as e:
        return render_template('lhd.html', table_data=[], error=f"Error reading file: {str(e)}")



# Routes for download cities, counties and lhd sheets
@main.route('/download/cities')
def download_cities():
    if not os.path.exists(cities_file_path): return "File not found.", 404
    return send_file(cities_file_path, as_attachment=True, download_name="ClimateActionPlan_cities.csv")


@main.route('/download/counties')
def download_counties():
    if not os.path.exists(counties_file_path): return "File not found.", 404
    return send_file(counties_file_path, as_attachment=True, download_name="ClimateActionPlan_counties.csv")


@main.route('/download/lhd')
def download_lhd():
    if not os.path.exists(lhd_file_path): return "File not found.", 404
    return send_file(lhd_file_path, as_attachment=True, download_name="ClimateActionPlan_lhd.csv")


# Map routes:
@main.route('/map')
def map_page():
    return render_template('map.html')

@main.route('/update_map')
def update_map():
    view_type = request.args.get('view_type', 'cities')
    filter_program = request.args.get('filter_program', None)
    keyword = request.args.get('keyword', None)

    if os.path.exists(map_file_path):
        os.remove(map_file_path)
    
    create_map(view_type=view_type, filter_program=filter_program, keyword=keyword)
    
    return '', 204

@main.route('/programs')
def get_programs():
    view_type = request.args.get('view_type', 'cities').lower()
    file_path = f'app/data/ClimateActionPlan_{view_type}.csv'
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if view_type == "cities":
            programs = df['Program Name'].dropna().unique().tolist()
        else:
            programs = df['Document Type'].dropna().unique().tolist()
        return jsonify({"programs": programs})
    else:
        return jsonify({"error": f"File not found: {file_path}"}), 404



@main.route('/manage/<data_type>', methods=['GET', 'POST'])
def manage_data(data_type):
    file_path = get_file_path(data_type)

    if not os.path.exists(file_path):
        return f"File not found: {file_path}", 404

    if request.method == 'POST':
        new_row = {key: request.form[key] for key in request.form.keys()}
        print("Starts lol")
        try:
            print("In try block")
            df = pd.read_csv(file_path)
            new_row_df = pd.DataFrame([new_row]) 
            df = pd.concat([df, new_row_df], ignore_index=True) 
            df.to_csv(file_path, index=False)
            print("New entry successfully added")
            flash(f"New entry added successfully to {data_type.capitalize()}!", 'success')
        except Exception as e:
            print("Error adding data:")
            print(e)
            flash(f"Error adding data: {str(e)}", 'danger')

    try:
        df = pd.read_csv(file_path)
        df = df.where(pd.notnull(df), "") 
        table_data = df.to_dict(orient='records')
        columns = df.columns.tolist()
        return render_template('manage_data.html', table_data=table_data, columns=columns, data_type=data_type)
    except Exception as e:
        return f"Error loading data: {str(e)}", 500


# Route to handle editing data
@main.route('/edit/<data_type>', methods=['POST'])
def edit_data(data_type):
    file_path = get_file_path(data_type)

    try:
        df = pd.read_csv(file_path)
        row_index = int(request.form['row_index'])
        updated_row = {key: request.form[key] for key in request.form.keys() if key != 'row_index'}
        for key, value in updated_row.items():
            df.at[row_index, key] = value
        df.to_csv(file_path, index=False)
        print(f"Row {row_index} updated successfully in {data_type.capitalize()}!")
        flash(f"Row {row_index} updated successfully in {data_type.capitalize()}!", 'success')
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        flash(f"Error updating data: {str(e)}", 'danger')

    return redirect(url_for('main.manage_data', data_type=data_type))


# Route to handle deleting data
@main.route('/delete/<data_type>/<int:row_index>', methods=['POST'])
def delete_data(data_type, row_index):
    file_path = get_file_path(data_type)

    try:
        df = pd.read_csv(file_path)
        df.drop(index=row_index, inplace=True)
        df.to_csv(file_path, index=False)
        flash(f"Row {row_index} deleted successfully from {data_type.capitalize()}!", 'success')
    except Exception as e:
        flash(f"Error deleting data: {str(e)}", 'danger')

    return redirect(url_for('main.manage_data', data_type=data_type))

