from bs4 import BeautifulSoup
import os
import requests
import sqlite3
from dateutil import parser
from utils import DataTransformer

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crime_stats.shtml'
DB_LOC = os.environ.get('DB_LOC')
UPLOAD_LOC = os.environ.get('UPLOAD_LOC')

page = requests.get(page_url)
soup = BeautifulSoup(page.content, "html.parser")
block = soup.find('div', attrs = {'class': 'news_div', 'id': 'news_div'})

entries = block.findAll('a')
past_entry = [entry for entry in entries if '2021-2023' in entry['title']]
monthly_entries = [entry for entry in entries if 'Downloadable Original Crime File' in entry['title']]

if not past_entry:
    raise ValueError("Could not locate `past_entry`: 2021-2023 CSV.")

for entry in past_entry:
    tail_url = entry['href']
    name = tail_url.strip('NIBRSData/')
    filename = 'Crime-' + name

    csv_link = base_url + tail_url
    response = requests.get(csv_link)

    filepath = os.path.join(UPLOAD_LOC, filename)

    with open(filepath, 'wb') as f:
        f.write(response.content)

    with sqlite3.connect(DB_LOC) as conn:
        DT = DataTransformer(filename=filename,
                             filepath=filepath,
                             conn=conn)
        DT.clean_data()
        DT.split_data()
        DT.check_integrity()
        DT.update_db_initial()
        DT.update_metadata()
        DT.commit_to_db()

for entry in monthly_entries:
    tail_url = entry['href']
    name = tail_url.strip('NIBRSData/').strip('.csv')
    date_object = parser.parse(name)
    filename = 'Crime-' + date_object.strftime("%m-%Y") + '.csv'

    csv_link = base_url + tail_url
    response = requests.get(csv_link)
    
    filepath =os.path.join(UPLOAD_LOC, filename)
    
    with open(filepath, 'wb') as f:
        f.write(response.content)

    with sqlite3.connect(DB_LOC) as conn:
        DT = DataTransformer(filename=filename,
                             filepath=filepath,
                             conn=conn)
        DT.automated_update()