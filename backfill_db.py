from bs4 import BeautifulSoup
import os
import requests
import calendar
from dateutil import parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import DataTransformer
from config import DevelopmentConfig, ProductionConfig
import re

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crimestats/'

months = list(calendar.month_name)[1:]  # Skip the first empty string

UPLOAD_LOC = os.environ.get('UPLOAD_LOC')

def validate_csv(html_element):
    regex_pattern = r'\b(' + '|'.join(months) + r')\s(\d{4})\b'
    match = re.search(regex_pattern, html_element.text)
    if match:
        month = match.group(1)
        year = match.group(2)
        return month + ' ' + year
    else:
        raise ValueError("No valid 'Month Year' format found in the given HTML element.")

def download_csv(url, filename):
    response = requests.get(url)
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
    if os.environ.get('APP_MODE') == 'production':
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, "html.parser")

        block = soup.find('div', attrs={'class': 'uagb-tabs__body-wrap'})
        tabs = block.findAll('div')

        crime_tab = tabs[-1]
        entries = crime_tab.findAll('a')

        past_entry = [entry for entry in entries if '2021-2023' in entry.text]
        monthly_entries = [entry for entry in entries if not '2021-2023' in entry.text]

        if not past_entry:
            raise ValueError("Could not locate `past_entry`: 2021-2023 CSV.")

        # Process past_entry
        for entry in past_entry:
            url = entry['href']
            time_frame = '2021-2023'
            filename = 'Crime-' + time_frame
            filepath = download_csv(url, filename)
            print(filename, filepath)

            DT = DataTransformer(filename=filename, filepath=filepath)
            DT.automated_initialization(session)

            # Delete the CSV file after processing
            delete_csv(filepath)
            session.commit()
            print(f"Committed transaction to the database.")

        # Process monthly_entries
        for entry in monthly_entries:
            url = entry['href']
            date = validate_csv(entry)
            date_object = parser.parse(date)
            filename = 'Crime-' + date_object.strftime("%m-%Y") + '.csv'
            filepath = download_csv(url, filename)

            # Initialize DataTransformer and perform automated update
            DT = DataTransformer(filename=filename, filepath=filepath)
            DT.automated_update(session)

            # Delete the CSV file after processing
            delete_csv(filepath)
            session.commit()
            print(f"Committed transaction to the database.")
        
        # session.commit()
        # print(f"Committed transaction to the database.")
    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
