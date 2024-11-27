from flask import render_template, Blueprint, request, jsonify, send_file, flash
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




@main.route('/download/cities')
def download_cities():
    file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_cities.csv'

    if not os.path.exists(file_path):
        return "File not found.", 404

    return send_file(file_path, as_attachment=True, download_name="ClimateActionPlan_cities.csv")


@main.route('/download/counties')
def download_counties():
    file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_counties.csv'

    if not os.path.exists(file_path):
        return "File not found.", 404

    return send_file(file_path, as_attachment=True, download_name="ClimateActionPlan_counties.csv")


@main.route('/download/lhd')
def download_lhd():
    file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_lhd.csv'

    if not os.path.exists(file_path):
        return "File not found.", 404

    return send_file(file_path, as_attachment=True, download_name="ClimateActionPlan_lhd.csv")



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



from flask import request, redirect, url_for, flash

# Route to display the management page
# @main.route('/manage/<data_type>', methods=['GET', 'POST'])
# def manage_data(data_type):
#     file_path = f'/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_{data_type}.csv'

#     if not os.path.exists(file_path):
#         return f"File not found: {file_path}", 404

#     if request.method == 'POST':
#         new_row = {key: request.form[key] for key in request.form.keys()}
#         print("NEW ADD HERE THIS SHOULD WORK")
#         print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#         try:
#             df = pd.read_csv(file_path)
#             df = df.append(new_row, ignore_index=True)  # Add new data
#             df.to_csv(file_path, index=False)
#             print("Did it work")
#             flash(f"New entry added successfully to {data_type.capitalize()}!", 'success')
#         except Exception as e:
#             print("Did it not work")
#             print(e)
#             flash(f"Error adding data: {str(e)}", 'danger')

#     # Read current data
#     try:
#         df = pd.read_csv(file_path)
#         table_data = df.to_dict(orient='records')
#         columns = df.columns.tolist()
#         return render_template('manage_data.html', table_data=table_data, columns=columns, data_type=data_type)
#     except Exception as e:
#         return f"Error loading data: {str(e)}", 500

@main.route('/manage/<data_type>', methods=['GET', 'POST'])
def manage_data(data_type):
    file_path = f'/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_{data_type}.csv'

    if not os.path.exists(file_path):
        return f"File not found: {file_path}", 404

    if request.method == 'POST':
        # Handle new data addition
        new_row = {key: request.form[key] for key in request.form.keys()}
        print("Starts lol")
        try:
            print("Are we here")
            df = pd.read_csv(file_path)
            new_row_df = pd.DataFrame([new_row])  # Create a single-row DataFrame
            df = pd.concat([df, new_row_df], ignore_index=True)  # Concatenate the new row
            df.to_csv(file_path, index=False)
            print("Entry added")
            flash(f"New entry added successfully to {data_type.capitalize()}!", 'success')
        except Exception as e:
            print("Not added")
            print(e)
            flash(f"Error adding data: {str(e)}", 'danger')

    # Read current data
    try:
        df = pd.read_csv(file_path)
        df = df.where(pd.notnull(df), "")  # Replace NaN with empty strings
        table_data = df.to_dict(orient='records')
        columns = df.columns.tolist()
        return render_template('manage_data.html', table_data=table_data, columns=columns, data_type=data_type)
    except Exception as e:
        return f"Error loading data: {str(e)}", 500


# Route to handle editing data
@main.route('/edit/<data_type>', methods=['POST'])
def edit_data(data_type):
    file_path = f'/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_{data_type}.csv'

    print("EDIT HERE THIS SHOULD WORK")
    print("0-----0-0--------------0-----------0")
    try:
        print("0-----0-0jethsjkynslkjhnlkjhns0-----------0")
        df = pd.read_csv(file_path)
        row_index = int(request.form['row_index'])
        updated_row = {key: request.form[key] for key in request.form.keys() if key != 'row_index'}
        for key, value in updated_row.items():
            df.at[row_index, key] = value
        df.to_csv(file_path, index=False)
        flash(f"Row {row_index} updated successfully in {data_type.capitalize()}!", 'success')
    except Exception as e:
        flash(f"Error updating data: {str(e)}", 'danger')

    return redirect(url_for('main.manage_data', data_type=data_type))


# Route to handle deleting data
@main.route('/delete/<data_type>/<int:row_index>', methods=['POST'])
def delete_data(data_type, row_index):
    file_path = f'/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_{data_type}.csv'

    try:
        df = pd.read_csv(file_path)
        df.drop(index=row_index, inplace=True)
        df.to_csv(file_path, index=False)
        flash(f"Row {row_index} deleted successfully from {data_type.capitalize()}!", 'success')
    except Exception as e:
        flash(f"Error deleting data: {str(e)}", 'danger')

    return redirect(url_for('main.manage_data', data_type=data_type))

