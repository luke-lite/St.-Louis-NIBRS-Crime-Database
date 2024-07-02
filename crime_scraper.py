from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
from dateutil import parser
from dateutil.relativedelta import relativedelta
from utils import DataTransformer
from app import db, create_app

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crime_stats.shtml'
UPLOAD_LOC = os.environ.get('UPLOAD_LOC')

def download_csv(tail_url, filename):
    csv_link = base_url + tail_url
    response = requests.get(csv_link)
    filepath = os.path.join(UPLOAD_LOC, filename)

    with open(filepath, 'wb') as f:
        f.write(response.content)

    return filepath

def delete_csv(filepath):
    try:
        os.remove(filepath)
        print(f"Deleted CSV file: {filepath}")
    except OSError as e:
        print(f"Error: {filepath} : {e.strerror}")

def main():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)
        
            if last_updated.empty:
                print("Error: LastUpdated field is empty in meta_data table.")
                return

            last_updated_string = last_updated.iloc[0, 0]
            date_object = parser.parse(last_updated_string)
            next_month = date_object + relativedelta(months=1)
            next_month_string = next_month.strftime("%B%Y")
            filename = 'Crime-' + next_month.strftime("%m-%Y") + '.csv'

            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, "html.parser")
            block = soup.find('div', attrs={'class': 'news_div', 'id': 'news_div'})

            # Extract entries for the next month data
            entries = block.findAll('a')
            recent_entry = None
            for entry in entries:
                if next_month_string in entry['title']:
                    recent_entry = entry
                    break

            if recent_entry:
                tail_url = recent_entry['href']
                filepath = download_csv(tail_url, filename)

                # Initialize DataTransformer and perform automated update
                DT = DataTransformer(filename=filename, filepath=filepath)
                DT.automated_update(conn)

                # Delete the CSV file after processing
                delete_csv(filepath)
            else:
                print("No new data available for the next month.")

if __name__ == "__main__":
    main()