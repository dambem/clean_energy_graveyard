import pandas as pd
from pandas import DataFrame
from typing import List, Set
from enum import Enum
import json
import geopandas as gpd

IN_PROGRESS = ['Application submitted', 'Revised', 'Awaiting Construction', 'No Application Required', 'Under Construction', 'Application Submitted']


class RepdProcessor:
    def __init__(self):
        self.location = 'app/data/repd-q1-apr-2025.csv'
        self.encoding = 'cp1252'
        self.df = self.read_csv()
    def read_csv(self) -> DataFrame:
        df = pd.read_csv(self.location, encoding=self.encoding)
        return df
    
    def get_filter_points(self, df=DataFrame) -> Set:
        val = set(df['Development Status (short)'])
        return val
    
    def filter_by_county(self, county:str, df=DataFrame) -> DataFrame:
        df = df[df['County'] == county]
        return df
    
    def filter_by_state(self,  df=DataFrame) -> DataFrame:
        df = df[df['Development Status (short)'].isin(IN_PROGRESS)]
        return(df)
    
    def filter_by_planning_authority(self, authorities:List[str], df=DataFrame | None) -> DataFrame:
        df = df[df['Planning Authority'].isin(authorities)]
        return df   
    
    def en_to_latlon(self, df:DataFrame, east_col='X-coordinate', nor_col='Y-coordinate'):
        from pyproj import Transformer
        transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326")   
        lat,lon = transformer.transform(df[east_col].values, df[nor_col].values)
        df['lat'] = lat.round(5)
        df['lon'] = lon.round(5)
        df.drop(columns=east_col)
        df.drop(columns=nor_col)
        return df
    
    def repd_df_to_geopandas(self, df:DataFrame) -> gpd.GeoDataFrame:
        df_copy = df.copy()
        pp_df = self.en_to_latlon(df_copy, east_col='X-coordinate', nor_col='Y-coordinate')
        gdf = gpd.GeoDataFrame(pp_df,geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
        return gdf
     
    def add_metadata_column(self, df:DataFrame, columns_to_include: List[str], new_column: str = 'metadata') -> DataFrame:
        all_columns = set(df.columns)
        columns_for_json = list(all_columns-set(columns_to_include)) 
        df[new_column] = df.apply(
            lambda row: json.dumps(
                {col: row[col] for col in columns_for_json if pd.notna(row[col])}
            ),
            axis=1
        )
        df_final = df[columns_to_include + [new_column]]
        return df_final

    def drop_columns(self, df:DataFrame, cols_to_drop:List[str]):
        for col in cols_to_drop:
            df.drop(columns=col, inplace=True)
        return df
