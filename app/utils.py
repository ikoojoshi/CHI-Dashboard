import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import requests
from .config import state_geojson_url, counties_geojson_url

def get_coordinates(city, county):
    geolocator = Nominatim(user_agent="flask_folium_app", timeout=10)
    try:
        location = geolocator.geocode(f"{city}, {county}, Illinois")
        if location:
            return [location.latitude, location.longitude]
        return None
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None

def map_county_style(feature):
    return {
        'fillColor': '#FFFAF0',  # FloralWhite
        'color': '#8B0000',      # DarkRed
        'weight': 1.5,
        'fillOpacity': 0.3
    }



def create_cities_map(m, df, illinois_geojson, counties_geojson):
    # Display Illinois boundary with improved styling
    folium.GeoJson(
        illinois_geojson,
        name="Illinois",
        style_function=lambda feature: {
            'fillColor': '#FFFFFF00',
            'color': '#2E8B57',
            'weight': 2
        },
        highlight_function=lambda x: {'weight': 3, 'color': '#FF4500'}
    ).add_to(m)

    # Display county boundaries with tooltips showing county names
    folium.GeoJson(
        counties_geojson,
        name="Counties",
        style_function=map_county_style,
        highlight_function=lambda x: {'weight': 3, 'color': '#FF8C00'},  # DarkOrange highlight
        tooltip=folium.GeoJsonTooltip(
            fields=['name'],
            localize=True
        )
    ).add_to(m)

    # Add markers for cities from df
    for idx, row in df.iterrows():
        city = row['City'] if 'City' in row else None
        county = row['County']
        cap_link = row['Link']
        focus_area = row['Focus Area'] if pd.notnull(row['Focus Area']) else "Unknown"
        outcome_measures = row['Outcome Measures']
        program_name = row['Program Name']
        summary = row['Summary']

        # Get coordinates for marker
        # city_coords = get_coordinates(city, county)
        city_coords = [row['Lat'], row['Long']]
        
        if city_coords:
            popup_html = f"""
                <div style="width: 300px;">
                    <h3 style="margin-top: 0; color: #FF6347;">{city if city else county}</h3>
                    <p><strong>County:</strong> {county}</p>
                    <p><strong>Program:</strong> {program_name}</p>
                    <p><strong>Summary:</strong> {summary}</p>
                    <p><strong>CAP Link:</strong> <a href="{cap_link}" target="_blank" style="color: #1E90FF;">View Plan</a></p>
                    <p><strong>Focus Area:</strong> {focus_area}</p>
                    <p><strong>Outcome Measures:</strong> {outcome_measures}</p>
                </div>
            """

            popup = folium.Popup(popup_html, max_width=300)
            
            # Add a CircleMarker with enhanced visual style
            circle_marker = folium.CircleMarker(
                location=city_coords,
                radius=12,
                color='#FF4500',
                fill=True,
                fill_color='#FF6347',
                fill_opacity=0.7, 
                weight=3,
                tooltip=f"{city}, {county}"
            )

            # Bind popup to CircleMarker
            circle_marker.add_to(m).add_child(popup)

    # Load LHD data and filter to CAP="Yes"
    lhd_file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_lhd.csv'
    lhd_df = pd.read_csv(lhd_file_path)
    lhd_df = lhd_df[lhd_df['CAP'] == "Yes"]

    # Add markers for LHD
    for idx, row in lhd_df.iterrows():
        lhd_name = row['LHD Name']
        area_served = row['Area Served']
        cap_link = row['Link']
        summary = row['Summary'] if pd.notnull(row['Summary']) else "No summary available"
        focus_area = row['Focus Area'] if pd.notnull(row['Focus Area']) else "Unknown"

        # Get coordinates for marker (assumes Area Served provides location)
        lhd_coords = get_coordinates(lhd_name, area_served)
        
        if lhd_coords:
            # Create popup content for LHD
            popup_html = f"""
                <div style="width: 300px;">
                    <h3 style="margin-top: 0; color: #FFD700;">{lhd_name}</h3>
                    <p><strong>Area Served:</strong> {area_served}</p>
                    <p><strong>Focus Area:</strong> {focus_area}</p>
                    <p><strong>Summary:</strong> {summary}</p>
                    <p><strong>CAP Link:</strong> <a href="{cap_link}" target="_blank" style="color: #1E90FF;">View Plan</a></p>
                </div>
            """

            popup = folium.Popup(popup_html, max_width=300)

            # LHD markers
            circle_marker = folium.CircleMarker(
                location=lhd_coords,
                radius=10,
                color='#FFD700',
                fill=True,
                fill_color='#FFFF00',
                fill_opacity=0.7,
                weight=3,
                tooltip=f"{lhd_name}, {area_served}"
            )

            circle_marker.add_to(m).add_child(popup)

    m.save('app/static/map.html')





def create_counties_map(m, df, illinois_geojson, counties_geojson):
    def county_color(county_name):
        """Determine the color of a county based on CAP and Document fields."""
        row = df[df['County'] == county_name + " County"]
        if not row.empty:
            cap = row.iloc[0]['CAP']
            document = row.iloc[0]['Document Type']
            if cap == "Yes" and document == "Climate Action Plan":
                return '#1a9850'
            elif cap == "Yes":
                return '#66c2a5'
            else:
                return '#fdae61'
        return '#d9d9d9'


    for feature in counties_geojson['features']:
        county_name = feature['properties']['name']
        color = county_color(county_name)
        
        county_info = df[df['County'] == county_name + " County"]  # Match GeoJSON name with CSV
        
        if not county_info.empty and county_info.iloc[0]['CAP'] == "Yes":
            county_info = county_info.iloc[0]  # Get the first (and only) row
            
            # Add information to GeoJSON properties for the popup
            feature['properties']['document'] = county_info['Document Type']
            feature['properties']['program_name'] = county_info['Program Name']
            feature['properties']['focus_area'] = county_info['Focus Area']
            feature['properties']['outcome_measures'] = county_info['Outcome Measures']
            feature['properties']['link'] = county_info['Link']
        else:
            feature['properties']['document'] = "No data available"
            feature['properties']['program_name'] = "No data available"
            feature['properties']['focus_area'] = "No data available"
            feature['properties']['outcome_measures'] = "No data available"
            feature['properties']['link'] = "#"

    # Add counties with GeoJsonPopup
    folium.GeoJson(
        counties_geojson,
        style_function=lambda feature: {
            'fillColor': county_color(feature['properties']['name']),
            'color': '#555555',  # Border color
            'weight': 1.5,
            'fillOpacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True),
        popup=folium.GeoJsonPopup(
            fields=['document', 'program_name', 'focus_area', 'outcome_measures', 'link'],
            aliases=[
                'Document:', 
                'Program Name:', 
                'Focus Area:', 
                'Outcome Measures:', 
                'Link:'
            ],
            labels=True,
            localize=True,
            style="font-family: Arial; font-size: 12px;"
        )
    ).add_to(m)
    
    # Save the map as HTML
    m.save('app/static/map.html')





def create_map(view_type='cities', filter_program=None, keyword=None):
    # Load the correct CSV file based on the view type

    # Initialize map with zoom restrictions and Illinois bounds
    m = folium.Map(
        location=[40.0, -89.0], 
        zoom_start=7,  
        tiles='cartodbpositron',
        width='100%', 
        height='90%',
        min_zoom=6.5,
        max_bounds=[[36.0, -92.0], [43.5, -87.5]]  # Approximate bounds for Illinois
    )

    # Load GeoJSON data for Illinois and counties
    state_geojson = requests.get(state_geojson_url).json()
    counties_geojson = requests.get(counties_geojson_url).json()

    # Define Illinois boundary
    illinois_geojson = next(
        feature for feature in state_geojson['features']
        if feature['properties']['name'] == 'Illinois'
    )


    # Add a mask to cover areas outside Illinois
    folium.GeoJson(
        data={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-180, 90], [-180, -90], [180, -90], [180, 90], [-180, 90]
                            ]
                        ] + illinois_geojson["geometry"]["coordinates"]
                    }
                }
            ]
        },
        style_function=lambda feature: {
            'fillColor': '#FFFFFF',  # White fill
            'color': '#FFFFFF',  # White border
            'weight': 0,
            'fillOpacity': 1
        }
    ).add_to(m)




    if view_type == 'counties':
        file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_counties.csv'
    else:
        file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan_cities.csv'
        

    df = pd.read_csv(file_path)
    

    # Apply filters for program type and keyword
    if filter_program:
        df = df[df['Program Name'] == filter_program]
    if keyword:
        df = df[df['Summary'].str.contains(keyword, case=False, na=False)]

    if view_type == "counties":
        create_counties_map(m, df, illinois_geojson, counties_geojson)
    else:
        create_cities_map(m, df, illinois_geojson, counties_geojson)

    
