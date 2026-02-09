import pandas as pd 
from pyproj import Transformer
import json
from bs4 import BeautifulSoup
# from newspaper import Article  # For article extraction and summarization
import requests
import time
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326")
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")


def google_search(query, api_key, cse_id, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": min(num_results, 5),  # Limit to 100 results per request
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error during search: {e}")
        return None
    except KeyError:
        print("Error: Invalid API response format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    
def convert_coordinates(df, easting_col='easting', northing_col='northing'):
    lat, lon = transformer.transform(df[easting_col].values, df[northing_col].values)
    df['latitude'] = lat
    df['longitude'] = lon
    return df


def search_news(site_name, cancelled=True):
    """Searches for news articles related to a renewable energy site."""

    query = f"{site_name} renewable energy"  # Basic search query
    if cancelled:
      query += " cancelled"

    # search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx=YOUR_CSE_ID&key={YOUR_API_KEY}" # Replace with your CSE ID and API key
    search_url = f"https://www.google.com/search?q={query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0'
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup)
    links = []
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if href and href.startswith("http"): # Filter out relative links
            links.append(href)
    time.sleep(0.1)
    return links[:5] # Return top 5 links

def get_repd_dataframe(date='2015-01-01'):
    df = pd.read_csv('data/repd-q2-jul-2025.csv', encoding='cp1252')
    
    df = df[df['Development Status (short)'].isin(['Application Refused', 'Abandoned', 'Application Withdrawn', 'Appeal Refused'])]
    
    
    df['Planning Application Submitted'] = pd.to_datetime(df['Planning Application Submitted'], format='%d/%m/%Y', errors='coerce')
    df['Installed Capacity (MWelec)'] = df['Installed Capacity (MWelec)'].apply(get_capacity_value)
    df = convert_coordinates(df, easting_col='X-coordinate', northing_col='Y-coordinate')
    df['Planning Application Submitted'] = pd.to_datetime(df['Planning Application Submitted'], format=('%Y-%m-%d'),  errors='coerce')
    df['Planning Permission Refused'] = pd.to_datetime(df['Planning Permission Refused'], format=('%d/%m/%Y'), errors='coerce')
    df['Planning Application Withdrawn'] = pd.to_datetime(df['Planning Application Withdrawn'], format=('%d/%m/%Y'), errors='coerce')
    df['Record Last Updated (dd/mm/yyyy)'] = pd.to_datetime(df['Record Last Updated (dd/mm/yyyy)'], format=('%d/%m/%Y'), errors='coerce')
    df['Appeal Refused'] = pd.to_datetime(df['Appeal Refused'], format=('%d/%m/%Y'))

    df = df[df['Planning Application Submitted'] >= pd.Timestamp(date)]
    df['Planning Application Submitted String'] = df['Planning Application Submitted'].dt.strftime('%Y-%m-%d')

    df_a_refused = df[df["Development Status (short)"] == "Appeal Refused"]  
    df_a_refused['Processing_Time'] = (df_a_refused['Appeal Refused'] - df_a_refused['Planning Application Submitted']).dt.days
    # print(df_a_refused["Processing_Time"])
    df_a_refused = df_a_refused[["Processing_Time", "Planning Application Submitted"]]


    df_withdrawn = df[df["Development Status (short)"] == "Application Withdrawn"]  
    df_withdrawn['Processing_Time'] = (df_withdrawn['Planning Application Withdrawn'] - df_withdrawn['Planning Application Submitted']).dt.days
    # print(df_withdrawn["Processing_Time"])
    df_withdrawn = df_withdrawn[["Processing_Time", "Planning Application Submitted"]]

        
    df_refused = df[df["Development Status (short)"] == "Application Refused"]  
    df_refused['Processing_Time'] = (df_refused['Planning Permission Refused'] - df_refused['Planning Application Submitted']).dt.days
    # print(df_refused["Processing_Time"])
    df_refused = df_refused[["Processing_Time", "Planning Application Submitted"]]


    all_applications = [df_a_refused,  df_withdrawn, df_refused]
    combined_df = pd.concat(all_applications, ignore_index=True)
    combined_df = combined_df.dropna(subset=['Processing_Time', 'Planning Application Submitted'])
    combined_df['Processing_Time'] = combined_df['Processing_Time'].astype(float)
    combined_df['Year'] = combined_df['Planning Application Submitted'].dt.year

    time_ranges = [
        {"min": 0, "max": 30, "label": "0-90 days"},
        {"min": 90, "max": 180, "label": "90-180 days"},
        {"min": 180, "max": 270, "label": "180-270 days"},
        {"min": 270, "max": 360, "label": "270-360 days"},
        {"min": 360, "max": 450, "label": "360-450 days"},
        {"min": 450, "max": 540, "label": "450-540 days"},
        {"min": 540, "max": 630, "label": "540-630 days"},
        {"min": 630, "max": 720, "label": "630-720 days"},
        {"min": 720, "max": 810, "label": "720-810 days"},
        {"min": 810, "max": 900, "label": "810-900 days"},
        {"min": 900, "max":  float('inf'), "label": "Over 900 days"},

    ]
    result = []
    
    for year, group in combined_df.groupby('Year'):
        avg_time = round(group['Processing_Time'].mean(), 1)
        
        # Calculate distribution
        distribution = []
        for time_range in time_ranges:
            count = len(group[(group['Processing_Time'] >= time_range['min']) & 
                              (group['Processing_Time'] < time_range['max'])])
            distribution.append({
                "range": time_range["label"],
                "count": int(count)
            })
        
        result.append({
            "year": int(year),
            "avgDelay": float(avg_time),
            "distribution": distribution
        })
    result.sort(key=lambda x: x['year'])
    with open('final.json', 'w') as f:
        json.dump(result, f, indent=2)

    df = df.fillna(0)
    return df


def repd_geojson_file():
    df = get_repd_dataframe()
    
    geojson = create_geojson(df)
    print(geojson)
    with open('points.geojson', 'w') as f:
        json.dump(geojson, f, indent=2)

def create_geojson(df):
    features = []
    for _, row in df.iterrows():
        # links = search_news(row['Site Name'])
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['longitude']), float(row['latitude'])]
            },
            "properties": row.drop(['latitude', 'longitude']).to_dict(),
            # "links": links
        }        
        features.append(feature)
    return {
        "type": "FeatureCollection",
        "features": features
    }
def get_capacity_value(value):
    if pd.isna(value) or value == '':
        return 0
    try:
        num_value = float(value)
        return num_value
    except (ValueError, TypeError):
        return 0

def search_query(query):
    try:
        results = google_search(query, API_KEY, CSE_ID, num_results=1)
        return(results)
    except Exception:
        return False

