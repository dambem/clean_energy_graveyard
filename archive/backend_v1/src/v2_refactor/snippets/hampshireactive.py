from app.processor.RepdProcessor import RepdProcessor
from pandas import DataFrame
from tim
def get_hampshire_in_progress() -> DataFrame:
    processor = RepdProcessor()
    df = processor.read_csv()
    
    df = processor.filter_by_county(df=df, county='Hampshire')
    df = processor.filter_by_state(df=df)
    return df

def get_southampton_surrounding() -> DataFrame:
    processor = RepdProcessor()
    useful_cols = ['Operator (or Applicant)', 'Site Name', 'lat','lon', 'Technology Type', 'Installed Capacity (MWelec)', 'Development Status', 'Planning Authority', 'Record Last Updated (dd/mm/yyyy)']
    bad_cols = ['Old Ref ID', 'Ref ID', 'Storage Co-location REPD Ref ID', 'Are they re-applying (New REPD Ref)', 'Are they re-applying (Old REPD Ref) ', 'Appeal Reference']
    local_authorities = ['Southampton', 'Eastleigh', 'Test Valley', 'New Forest', 'Fareham']
    df = processor.read_csv()
    df = processor.filter_by_planning_authority(df=df, authorities=local_authorities)
    df = processor.filter_by_state(df=df)
    df = processor.en_to_latlon(df=df)
    df = processor.drop_columns(df=df, cols_to_drop=bad_cols)
    df = processor.add_metadata_column(df=df, columns_to_include=useful_cols)
    df.sort_values(['Planning Authority','Record Last Updated (dd/mm/yyyy)'])
    final_value = df['Installed Capacity (MWelec)'].astype(float).sum()
    df.to_csv('outputs/')
    return df, final_value