from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3
import os
from dateutil import parser
from dateutil.relativedelta import relativedelta
from utils import DataTransformer

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crime_stats.shtml'
DB_LOC = os.environ.get('DB_LOC')
UPLOAD_LOC= os.environ.get('UPLOAD_LOC')

with sqlite3.connect(DB_LOC) as conn:
    last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)

last_updated_string = last_updated.iloc[0,0]
date_object = parser.parse(last_updated_string)
next_month = date_object + relativedelta(months=1)
next_month_string = next_month.strftime("%B%Y")
filename = 'Crime-' + next_month.strftime("%m-%Y") + '.csv'

page = requests.get(page_url)
soup = BeautifulSoup(page.content, "html.parser")
block = soup.find('div', attrs = {'class': 'news_div', 'id': 'news_div'})

entries = block.findAll('a')
recent_entry = entries[-1]
tail_url = recent_entry['href']

if next_month_string in tail_url:
    csv_link = base_url + tail_url
    response = requests.get(csv_link)
    
    filepath = os.path.join(UPLOAD_LOC, filename)
    with open(filepath, 'wb') as f:
        f.write(response.content)

    with sqlite3.connect(DB_LOC) as conn:
        DT = DataTransformer(filename=filename,
                             filepath=filepath,
                             conn=conn)
        DT.automated_update()