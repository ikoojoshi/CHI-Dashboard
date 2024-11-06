import folium
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from time import sleep
import requests
from .config import *

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
        'fillColor': '#ffeda0',  # light color for counties
        'color': 'blue',  # boundary color
        'weight': 1.5,  # line thickness
        'fillOpacity': 0.5
    }


def create_map():
    # Load data and initialize the map
    # file_path = '../data/ClimateActionPlan.csv'
    file_path = '/Users/ipshitaj/Documents/UIUC/OSI/CHI-Dashboard/app/data/ClimateActionPlan.csv'
    df = pd.read_csv(file_path)
    
    m = folium.Map(location=[40.0, -89.0], zoom_start=6)

    for idx, row in df.iterrows():
        # location = [row['Latitude'], row['Longitude']]
        # popup_content = f"<strong>{row['Location']}</strong><br>{row['Summary']}<br>Type: {row['Document Type']}"
        # folium.Marker(location=location, popup=popup_content).add_to(m)

        city = row['City']
        county = row['County']
        cap_link = row['CAP Link']
        focus_area = row['Focus Area']
        outcome_measures = row['Outcome Measures']

        # Get the coordinates for the city
        city_coords = get_coordinates(city, county)

        if city_coords:
            folium.Marker(
                location=city_coords,
                popup=f"<b>City:</b> {city}<br>"
                      f"<b>County:</b> {county}<br>"
                      f"<b>CAP Link:</b> <a href='{cap_link}' target='_blank'>View Plan</a><br>"
                      f"<b>Focus Area:</b> {focus_area}<br>"
                      f"<b>Outcome Measures:</b> {outcome_measures}",
                tooltip=city
            ).add_to(m)

        # Sleep to avoid hitting the geocoding API rate limit
        # sleep(1)


    # Load and add GeoJSON layers
    # Add your styling functions and markers as in your original code
    # Customize map appearance here as well

    state_geojson = requests.get(state_geojson_url).json()
    counties_geojson = requests.get(counties_geojson_url).json()

    illinois_geojson = next(feature for feature in state_geojson['features'] if feature['properties']['name'] == 'Illinois')

    folium.GeoJson(
        illinois_geojson,
        name="Illinois",
        style_function=lambda feature: {
            'fillColor': '#ffffff00',  # Transparent state color
            'color': 'green',  # Boundary color for the state
            'weight': 2  # Boundary thickness
        },
        highlight_function=lambda x: {'weight': 3, 'color': 'blue'}
    ).add_to(m)

    # Add counties boundaries with colors
    folium.GeoJson(
        counties_geojson,
        name="Counties",
        style_function=map_county_style,
        highlight_function=lambda x: {'weight': 3, 'color': 'orange'}
    ).add_to(m)


    return m._repr_html_()
