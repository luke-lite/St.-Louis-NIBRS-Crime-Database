import sqlite3
# import pandas as pd
from refactor import DataTransformer

# Connect to SQLite database
conn = sqlite3.connect('your_database.db')

with conn:
    DT = DataTransformer(filename='Crime_01_2024',
                         upload_path='uploads/Crime_01_2024.csv',
                         conn=conn)
    
    DT.clean_data()
    DT.split_data()
    DT.integrity_check()
    DT.update_db_from_supp()
    DT.update_db_from_unfound()
    DT.update_db_from_new()
    DT.commit_to_db()
    updated_df = DT.get_updated_df()
    supp_df, unfound_df, new_df = DT.get_split_dfs()