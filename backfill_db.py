import os
import calendar
from dateutil import parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import DataTransformer
from config import DevelopmentConfig, ProductionConfig
from utils import validate_csv, download_csv, delete_csv, scrape_csv_elements

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crimestats/'
months = list(calendar.month_name)[1:]  # Skip the first empty string
UPLOAD_LOC = os.environ.get('UPLOAD_LOC')

def main():
    if os.environ.get('APP_MODE') == 'production':
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()

    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        entries = scrape_csv_elements(page_url)

        past_entry = [entry for entry in entries if '2021-2023' in entry.text]
        monthly_entries = [entry for entry in entries if not '2021-2023' in entry.text]

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

    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
