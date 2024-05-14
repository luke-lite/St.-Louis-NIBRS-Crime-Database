# from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import os

DB_LOC = 'instance/database.db'

df = pd.read_csv('data/uploads/Crime2021-2023.csv')

add_df_query = """
INSERT INTO crime_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                        NIBRSCode,NIBRSCat,NIBRSOffenseType,UCR_SRS,CrimeGrade,
                        PrimaryLocation,SecondaryLocation,District,Neighborhood,
                        NeighborhoodNum,Latitude,Longitude,Supplemented,
                        SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

meta_query = """
INSERT INTO meta_data (LastUpdated) VALUES ('December2023')"""

# get tuples for the add query
df_rows = [tuple(x) for x in df.itertuples(index=False)]

with sqlite3.connect(DB_LOC) as conn:
    conn.executemany(add_df_query, df_rows)
    conn.execute(meta_query)