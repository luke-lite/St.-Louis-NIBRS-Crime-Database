import sqlite3
import pandas as pd
from utils import clean_data

# Connect to SQLite database
conn = sqlite3.connect('your_database.db')

with conn:
    clean_data()