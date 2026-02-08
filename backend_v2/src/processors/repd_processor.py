from enum import Enum
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
from dataclasses import dataclass
from enum import Enum


DEVELOPMENT_TYPES = {'Appeal Refused', 
                     'Appeal Withdrawn', 
                     'Planning Permission Expired',
                     'Revised',
                     'Application Withdrawn', 
                     'Decommissioned', 
                     'Appeal Lodged', 
                     'Under Construction', 
                     'Awaiting Construction', 
                     'Abandoned', 
                     'Application Refused', 
                     'Operational', 
                     'Application Submitted', 
                     'No Application Required'}

CANCELLED_DEVELOPMENT_TYPES = {
                    'Appeal Refused',
                    'Appeal Withdrawn',
                    'Planning Permission Expired',
                    'Application Withdrawn', 
                    'Abandoned', 
                    'Application Refused', 
}

class REPDProcessor:
    """
    REPDProcessor. Creates dataframe based on a REPD CSV

    """
    def __init__(self, src:str='src/data/REPD_Publication_Q3_2025.csv', encoding:str='cp1252'):
        self.src = src
        self._df: pd.DataFrame | None = None
        self.encoding = encoding

    def coordinates_to_lat_lon(self, 
                               df=pd.DataFrame, 
                               easting_col:str='easting', 
                               northing_col:str='northing',
                               from_crs:str='EPSG:27700',
                               to_crs:str='EPSG:4326'
                               ) -> pd.DataFrame:
        transformer = Transformer.from_crs(from_crs, to_crs)
        lat, lon = transformer.transform(df[easting_col].values, df[northing_col].values)
        df['lat'] = lat
        df['lon'] = lon
        pass

    def load(self) -> pd.DataFrame:
        """Load dataframe."""
        return pd.read_csv(self.src, encoding=self.encoding)
    
    def filter_by_cancelled(self, df:pd.DataFrame) -> pd.DataFrame:
        return df[df['Development Status (short)'].isin(CANCELLED_DEVELOPMENT_TYPES)]
    
    def get_unique(self, column:str, df:pd.DataFrame) -> set:
        """Get unique values from pandas dataframe column.

        Args:
            column (str): Column name
            df (pd.DataFrame | None): Dataframe to use by loaded processor.

        Returns:
            set: Set of unique values for the current dataframe
        """
        return set(df[column].unique())