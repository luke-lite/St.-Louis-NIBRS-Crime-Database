from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
from dateutil import parser
from dateutil.relativedelta import relativedelta
from utils import DataTransformer

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crime_stats.shtml'
DB_LOC = 'instance/database.db'

with sqlite3.connect(DB_LOC) as conn:
    last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)

last_updated_string = last_updated.iloc[0,0]
date_object = parser.parse(last_updated_string)
next_month = date_object + relativedelta(months=1)
next_month_string = next_month.strftime("%B%Y")
filename = 'Crime-' + next_month.strftime("%m-%Y")

page = requests.get(page_url)
soup = BeautifulSoup(page.content, "html.parser")
block = soup.find('div', attrs = {'class': 'news_div', 'id': 'news_div'})

entries = block.findAll('a')
recent_entry = entries[-1]
tail_url = recent_entry['href']

if next_month_string in tail_url:
    csv_link = base_url + tail_url
    response = requests.get(csv_link)
    
    loc = 'data/temp/'
    filepath = loc + filename + '.csv'
    
    with open(filepath, 'wb') as f:
        f.write(response.content)
    
    print("CSV file downloaded successfully.")

    # temp_df = pd.read_csv(csv_filename)

    with sqlite3.connect(DB_LOC) as conn:
        DT = DataTransformer(filename=filename,
                             filepath=filepath,
                             conn=conn)
        DT.clean_data()
        DT.split_data()
        DT.integrity_check()
        DT.update_db_from_supp()
        DT.update_db_from_unfound()
        DT.update_db_from_new()
        DT.commit_to_db()