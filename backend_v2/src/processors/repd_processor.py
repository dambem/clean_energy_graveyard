from enum import Enum
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
from dataclasses import dataclass
from enum import Enum
from geopandas import gpd
from pydantic import BaseModel
from datetime import datetime


DATETIME_COLS = ['Record Last Updated (dd/mm/yyyy)', 
                    'Planning Application Submitted',
                    'Planning Application Withdrawn',
                    'Planning Permission Refused',
                    'Appeal Lodged',
                    'Appeal Withdrawn',
                    'Appeal Refused',
                    'Appeal Granted',
                    'Planning Permission Granted',
                    'Secretary of State - Intervened',
                    'Secretary of State - Refusal',
                    'Secretary of State - Granted',
                    'Planning Permission Expired',
                    'Under Construction',
                    'Operational']

TECHNOLOGY_TYPES = {
    "Solar Photovoltaics",
    "Compressed Air Energy Storage",
    "Sewage Sludge Digestion",
    "Wind Onshore",
    "Unknown",
    "Wind Offshore",
    "Biomass (dedicated)",
    "Shoreline Wave",
    "Tidal Stream",
    "Battery",
    "Flywheels",
    "Liquid Air Energy Storage",
    "Tidal Lagoon",
    "Fuel Cell (Hydrogen)",
    "Advanced Conversion Technologies",
    "Air Source Heat Pumps",
    "Geothermal",
    "Landfill Gas",
    "Small Hydro",
    "Pumped Storage Hydroelectricity",
    "EfW Incineration",
    "Large Hydro",
    "Biomass (co-firing)",
    "Hot Dry Rocks (HDR)",
    "Hydrogen",
    "Anaerobic Digestion",
}

DEVELOPMENT_TYPES = {
    "Appeal Refused",
    "Appeal Withdrawn",
    "Planning Permission Expired",
    "Revised",
    "Application Withdrawn",
    "Decommissioned",
    "Appeal Lodged",
    "Under Construction",
    "Awaiting Construction",
    "Abandoned",
    "Application Refused",
    "Operational",
    "Application Submitted",
    "No Application Required",
}

CANCELLED_DEVELOPMENT_TYPES = {
    "Appeal Refused",
    "Appeal Withdrawn",
    "Planning Permission Expired",
    "Application Withdrawn",
    "Abandoned",
    "Application Refused",
}

# class REPDRecord(BaseModel):
#     RefID: int
#     RecordUpdated: datetime
#     Operator: str
#     SiteName: str
#     TechnologyType: str


class REPDProcessor:
    """
    REPDProcessor. Creates dataframe based on a REPD CSV

    """

    def __init__(
        self,
        src: str = "src/data/REPD_Publication_Q3_2025.csv",
        encoding: str = "cp1252",
    ):
        self.src = src
        self._df: pd.DataFrame | None = None
        self.encoding = encoding

    def coordinates_to_lat_lon(
        self,
        df: pd.DataFrame,
        drop_na: bool = True,
        easting_col: str = "X-coordinate",
        northing_col: str = "Y-coordinate",
        from_crs: str = "EPSG:27700",
        to_crs: str = "EPSG:4326",
    ) -> pd.DataFrame:
        """Convert coordinates from latlon

        Args:
            df (pd.DataFrame): Dataframe containing coordinates
            drop_na (bool): Drop nan's in specific columns.
            easting_col (str, optional): easting column in csv. Defaults to 'easting'.
            northing_col (str, optional): northing col in csv. Defaults to 'northing'.
            from_crs (_type_, optional): EPSG from. Defaults to 'EPSG:27700'.
            to_crs (_type_, optional): EPSG to. Defaults to 'EPSG:4326'.

        Returns:
            pd.DataFrame: Parsed dataframe.
        """
        df.dropna(subset=[northing_col, easting_col])
        transformer = Transformer.from_crs(from_crs, to_crs)
        lat, lon = transformer.transform(
            df[easting_col].values, df[northing_col].values
        )
        df["lat"] = lat.round(4)
        df["lon"] = lon.round(4)
        df.drop(columns=[easting_col, northing_col])
        return df

    def load(self) -> pd.DataFrame:
        """Load dataframe."""
        return pd.read_csv(self.src, encoding=self.encoding)
    
    def filter_by_planning_authority(self, df: pd.DataFrame, planning_authority:str) -> pd.DataFrame:
        """Filter by local authority.

        Args:
            df (pd.DataFrame): _description_
            local_authority (str): _description_
            date (datetime): _description_

        Returns:
            pd.DataFrame: _description_
        """
        return df[df['Planning Authority'] == planning_authority]
    
    def filter_by_date(self, df: pd.DataFrame, date_col:str, date:datetime) -> pd.DataFrame:
        """Filter by date

        Args:
            df (pd.DataFrame): Dateframe from original filter.
            date_col (str): Date column to filter against.
            date (datetime): Datetime for filter.

        Returns:
            pd.DataFrame: Filtered dataframe with date.
        """
        return df[df[date_col] >= date]

    def filter_by_cancelled(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter only by cancelled development projects

        Args:
            df (pd.DataFrame): Dataframe from load

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        return df[df["Development Status (short)"].isin(CANCELLED_DEVELOPMENT_TYPES)]

    def convert_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert dates to datetime objects

        Args:
            df (pd.DataFrame): Dataframe

        Returns:
            pd.DataFrame: Covnerted dataframe with actual datetime columns.
        """
        for col in DATETIME_COLS:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    def get_unique(self, column: str, df: pd.DataFrame) -> set:
        """Get unique values from pandas dataframe column.

        Args:
            column (str): Column name
            df (pd.DataFrame | None): Dataframe to use by loaded processor.

        Returns:
            set: Set of unique values for the current dataframe
        """
        return set(df[column].unique())

    def df_to_gpd(self, df: pd.DataFrame, col_lon, col_lat) -> pd.DataFrame:
        """Dataframe to Geopandas

        Args:
            df (pd.DataFrame): Dataframe in Pandas.
            col_lon (): Longitude to analyse
            col_lat (): Latitude to analyse

        Returns:
            pd.DataFrame: Geopandas parsed dataframe
        """
        df = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(col_lon, col_lat), crs="EPSG:4326"
        )
        df[df.geometry.notna()]

        return df
    
    def create_geojson(self, df:pd.DataFrame):
        features = []
        for _, row in df.iterrows():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row['lon']), float(row['lat'])]
                },
                "properties": row.drop(['latitude', 'longitude']).to_dict()
            }
            features.append(feature)
        return {
            "type": "FeatureCollection",
            "features": features
        }
    def get_google_query_string(self, row: pd.Series) -> str:
        return f"{row['Site Name'], {row['Country']}, {row['Technology Type']}}, around {row['Record Last Updated (dd/mm/yyyy)']} "

    def process_pipeline(self, 
                         date:datetime | None = None,
                         planning_authority: str | None = None,
                           ) -> pd.DataFrame:
        """Perform necessary pipeline filtering for a cleaned dataset.

        Args:
            date: Datetime to filter and look against for last updated data
            planning_authority: planning authority to filter against

        Returns:
            pd.DataFrame: Processed dataframe for the repd processor.
        """
        df = self.load()
        df = self.convert_datetime(df)
        if date is not None:
            df = self.filter_by_date(df=df, date=date, date_col='Record Last Updated (dd/mm/yyyy)')
        if planning_authority is not None:
            df = self.filter_by_planning_authority(df, planning_authority=planning_authority)
        df = self.coordinates_to_lat_lon(df)
        df = self.df_to_gpd(df, df.lon, df.lat)
       
        return df
