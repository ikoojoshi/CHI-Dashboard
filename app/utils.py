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
            'fillColor': '#FFFFFF00',  # Transparent fill
            'color': '#2E8B57',        # SeaGreen border
            'weight': 2
        },
        highlight_function=lambda x: {'weight': 3, 'color': '#FF4500'}  # OrangeRed highlight
    ).add_to(m)

    # Display county boundaries with tooltips showing county names
    folium.GeoJson(
        counties_geojson,
        name="Counties",
        style_function=map_county_style,
        highlight_function=lambda x: {'weight': 3, 'color': '#FF8C00'},  # DarkOrange highlight
        tooltip=folium.GeoJsonTooltip(
            fields=['name'],  # Correct field name from your GeoJSON
            # aliases=['County:'],  # Label for the tooltip
            localize=True
        )
    ).add_to(m)

    from folium.plugins import MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers with custom icon
    for idx, row in df.iterrows():
        city = row['City'] if 'City' in row else None
        county = row['County']
        cap_link = row['CAP Link']
        focus_area = row['Focus Area']
        outcome_measures = row['Outcome Measures']
        program_name = row['Program Name']
        summary = row['Summary']

        # Get coordinates for marker
        city_coords = get_coordinates(city, county)
        
        # Custom icon for the marker
        icon_url = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/static/icon.png'
        icon = folium.CustomIcon(icon_url, icon_size=(30, 30))

        if city_coords:
            # Create popup content with better HTML formatting
            popup_html = f"""
                <div style="width: 300px;">
                    <h3 style="margin-top: 0;">{city if city else county}</h3>
                    <p><strong>County:</strong> {county}</p>
                    <p><strong>Program:</strong> {program_name}</p>
                    <p><strong>Summary:</strong> {summary}</p>
                    <p><strong>CAP Link:</strong> <a href="{cap_link}" target="_blank">View Plan</a></p>
                    <p><strong>Focus Area:</strong> {focus_area}</p>
                    <p><strong>Outcome Measures:</strong> {outcome_measures}</p>
                </div>
            """

            popup = folium.Popup(popup_html, max_width=300)
            
            folium.Marker(
                location=city_coords,
                popup=popup,
                tooltip=f"{city}, {county}",
                icon=folium.Icon(color='darkgreen', icon='leaf', prefix='fa')
            ).add_to(marker_cluster)

    # Save the map as HTML
    m.save('app/static/map.html')




def create_counties_map(m, df, illinois_geojson, counties_geojson):
    def county_color(county_name):
        """Determine the color of a county based on CAP and Document fields."""
        row = df[df['County'] == county_name + " County"]
        if not row.empty:
            cap = row.iloc[0]['CAP']
            document = row.iloc[0]['Document']
            if cap == "Yes" and document == "Climate Action Plan":
                return '#1a9850'  # Strong green
            elif cap == "Yes":
                return '#66c2a5'  # Mid green
            else:
                return '#fdae61'  # Light orange
        return '#d9d9d9'  # Gray for missing data

    # Iterate through the counties in the GeoJSON
    for feature in counties_geojson['features']:
        county_name = feature['properties']['name']  # County name from GeoJSON
        print(f"Processing county: {county_name}")  # Debug: check each county
        color = county_color(county_name)  # Get color for this county
        
        # Filter relevant information for the popup
        county_info = df[df['County'] == county_name + " County"]  # Match GeoJSON name with CSV
        
        if not county_info.empty and county_info.iloc[0]['CAP'] == "Yes":
            county_info = county_info.iloc[0]  # Get the first (and only) row
            
            # Add information to GeoJSON properties for the popup
            feature['properties']['document'] = county_info['Document']
            feature['properties']['program_name'] = county_info['Program Name']
            feature['properties']['focus_area'] = county_info['Focus Area']
            feature['properties']['outcome_measures'] = county_info['Outcome Measures']
            feature['properties']['link'] = county_info['Link']
        else:
            # If no data, ensure empty properties for the popup
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
        min_zoom=7,
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

    
