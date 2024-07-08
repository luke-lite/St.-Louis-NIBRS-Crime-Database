import os
from dateutil import parser
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import DataTransformer, validate_csv, download_csv, delete_csv, scrape_csv_elements
from config import DevelopmentConfig, ProductionConfig
from app.models import MetaData

base_url = 'https://www.slmpd.org/'
page_url = 'https://www.slmpd.org/crime_stats.shtml'
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
        recent_entry = entries[-1]
        csv_date = validate_csv(recent_entry)
        csv_date = csv_date.replace(' ', '')

        meta_data = session.query(MetaData).first()
        last_updated = meta_data.LastUpdated
        date_object = parser.parse(last_updated)
        expected_date_obj = date_object + relativedelta(months=1)
        expected_date = expected_date_obj.strftime("%B%Y")

        if csv_date == expected_date:
            url = recent_entry['href']
            csv_date_object = parser.parse(csv_date)
            filename = 'Crime-' + csv_date_object.strftime("%m-%Y") + '.csv'
            filepath = download_csv(url, filename)

            # Initialize DataTransformer and perform automated update
            DT = DataTransformer(filename=filename, filepath=filepath)
            DT.automated_update(session)

            # Delete the CSV file after processing
            delete_csv(filepath)
            session.commit()
            print(f"Committed transaction to the database.")

        elif csv_date == last_updated:
            print('Nothing to see here. No updates yet.')
        else:
            print('CSV date and database date matching error.')

    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")
    finally:
        session.close()




    # app = create_app()
    # with app.app_context():
    #     with db.engine.connect() as conn:
    #         last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)
        
    #         if last_updated.empty:
    #             print("Error: LastUpdated field is empty in meta_data table.")
    #             return

    #         last_updated_string = last_updated.iloc[0, 0]
    #         date_object = parser.parse(last_updated_string)
    #         next_month = date_object + relativedelta(months=1)
    #         next_month_string = next_month.strftime("%B%Y")
    #         filename = 'Crime-' + next_month.strftime("%m-%Y") + '.csv'

    #         page = requests.get(page_url)
    #         soup = BeautifulSoup(page.content, "html.parser")
    #         block = soup.find('div', attrs={'class': 'news_div', 'id': 'news_div'})

    #         # Extract entries for the next month data
    #         entries = block.findAll('a')
    #         recent_entry = None
    #         for entry in entries:
    #             if next_month_string in entry['title']:
    #                 recent_entry = entry
    #                 break

    #         if recent_entry:
    #             tail_url = recent_entry['href']
    #             filepath = download_csv(tail_url, filename)

    #             # Initialize DataTransformer and perform automated update
    #             DT = DataTransformer(filename=filename, filepath=filepath)
    #             DT.automated_update(conn)

    #             # Delete the CSV file after processing
    #             delete_csv(filepath)
    #         else:
    #             print("No new data available for the next month.")

if __name__ == "__main__":
    main()