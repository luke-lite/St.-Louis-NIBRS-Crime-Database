# from sqlalchemy import create_engine
import sqlite3
import pandas as pd

conn=sqlite3.connect('database.db')
# engine = create_engine('sqlite:///database.db', echo=False)
df = pd.read_csv('uploads/Crime2021-2023.csv')

# df.to_sql('crime_data', con=engine, if_exists='append', index=True, index_label='Id')

add_df_query = """INSERT INTO crime_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                            NIBRSCode,NIBRSCat,NIBRSOffenseType,UCR_SRS,CrimeGrade,
                                            PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                            NeighborhoodNum,Latitude,Longitude,Supplemented,
                                            SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

# get tuples for the add query
df_rows = [tuple(x) for x in df.itertuples(index=False)]

with conn:
    conn.executemany(add_df_query, df_rows)