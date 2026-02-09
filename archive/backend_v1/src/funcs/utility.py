import pandas as pd
from pyproj import Transformer
from bs4 import BeautifulSoup
import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Constants
API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")
DATA_PATH = Path("data/repd-q4-jan-2025.csv")
OUTPUT_JSON = Path("final.json")
GEOJSON_FILE = Path("points.geojson")

# Coordinate Transformer
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326")

# Utility Functions
def convert_coordinates(df, easting_col='easting', northing_col='northing'):
    lat, lon = transformer.transform(df[easting_col].values, df[northing_col].values)
    df['latitude'] = lat
    df['longitude'] = lon
    return df

def get_capacity_value(value):
    if pd.isna(value) or value == '':
        return 0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

def google_search(query, api_key, cse_id, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": min(num_results, 5),
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        print(f"Search error: {e}")
        return []

def search_news(site_name, cancelled=True):
    query = f"{site_name} renewable energy{' cancelled' if cancelled else ''}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    links = [a.get('href') for a in soup.find_all('a') if a.get('href', '').startswith("http")]
    return links[:5]

# Main Data Processor Class
class REPDProcessor:
    def __init__(self, file_path=DATA_PATH):
        self.df = pd.read_csv(file_path, encoding='cp1252')
        self.clean_and_process()

    def clean_and_process(self):
        df = self.df
        df = df[df['Development Status (short)'].isin([
            'Application Refused', 'Abandoned', 'Application Withdrawn', 'Appeal Refused'
        ])]
        df['Planning Application Submitted'] = pd.to_datetime(df['Planning Application Submitted'], dayfirst=True)
        df['Installed Capacity (MWelec)'] = df['Installed Capacity (MWelec)'].apply(get_capacity_value)
        df = convert_coordinates(df, easting_col='X-coordinate', northing_col='Y-coordinate')

        date_fields = [
            'Planning Application Submitted', 'Planning Permission Refused',
            'Planning Application Withdrawn', 'Record Last Updated (dd/mm/yyyy)',
            'Appeal Refused'
        ]
        for field in date_fields:
            df[field] = pd.to_datetime(df[field], dayfirst=True, errors='coerce')

        df['Planning Application Submitted String'] = df['Planning Application Submitted'].dt.strftime('%Y-%m-%d')
        self.df = df.fillna(0)

    def filter_by_date(self, date_str='2015-01-01'):
        return self.df[self.df['Planning Application Submitted'] >= pd.Timestamp(date_str)]

    def calculate_processing_stats(self):
        df = self.filter_by_date()
        status_mapping = {
            "Appeal Refused": "Appeal Refused",
            "Application Withdrawn": "Planning Application Withdrawn",
            "Application Refused": "Planning Permission Refused"
        }

        all_applications = []
        for status, date_col in status_mapping.items():
            subset = df[df["Development Status (short)"] == status]
            subset['Processing_Time'] = (subset[date_col] - subset['Planning Application Submitted']).dt.days
            all_applications.append(subset[['Processing_Time', 'Planning Application Submitted']])

        combined_df = pd.concat(all_applications).dropna()
        combined_df['Processing_Time'] = combined_df['Processing_Time'].astype(float)
        combined_df['Year'] = combined_df['Planning Application Submitted'].dt.year

        ranges = [
            {"min": 0, "max": 90, "label": "0-90 days"},
            {"min": 90, "max": 180, "label": "90-180 days"},
            {"min": 180, "max": 365, "label": "180-365 days"},
            {"min": 365, "max": 730, "label": "1 Year - 2 Years"},
            {"min": 730, "max": float('inf'), "label": "Over 2 Years"},
        ]

        result = []
        for year, group in combined_df.groupby('Year'):
            avg_time = round(group['Processing_Time'].mean(), 1)
            distribution = [
                {
                    "range": r["label"],
                    "count": int(len(group[(group['Processing_Time'] >= r["min"]) & (group['Processing_Time'] < r["max"])]))
                }
                for r in ranges
            ]
            result.append({"year": int(year), "avgDelay": avg_time, "distribution": distribution})

        result.sort(key=lambda x: x['year'])
        with open(OUTPUT_JSON, 'w') as f:
            json.dump(result, f, indent=2)

        return result

    def generate_geojson(self):
        df = self.df
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row['longitude']), float(row['latitude'])]
                },
                "properties": row.drop(['latitude', 'longitude']).to_dict()
            }
            for _, row in df.iterrows()
        ]
        geojson = {"type": "FeatureCollection", "features": features}
        with open(GEOJSON_FILE, 'w') as f:
            json.dump(geojson, f, indent=2)

        return geojson
