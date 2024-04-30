import sqlite3
import pandas as pd
from utils import transform_data

# Connect to SQLite database
conn = sqlite3.connect('your_database.db')

with conn:
    transform_data(csv_loc, conn)