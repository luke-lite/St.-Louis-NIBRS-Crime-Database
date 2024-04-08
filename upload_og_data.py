from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('sqlite:///server.db', echo=False)
df = pd.read_csv('uploads/Crime2021-2023.csv')

df.to_sql('crime_data', con=engine, if_exists='append')