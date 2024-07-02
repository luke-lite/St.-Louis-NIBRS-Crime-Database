import pandas as pd
from datetime import datetime
from sqlalchemy import text
from app.models import MetaData

class DataTransformer:
    def __init__(self, filename, filepath):
        self.filename = filename
        self.filepath = filepath
        self.df = None
        self.supp_df = None
        self.unfound_df = None
        self.new_df = None
        self.crime_add_query = self._create_add_query('crime_data')
        self.unfounded_add_query = self._create_add_query('unfounded_data')

    def __str__(self):
        return f"DataTransformer Object: ({self.filename})"
    
    def load_data(self):
        try:
            df = pd.read_csv(self.filepath)
            self.df = df
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            raise

    def clean_data(self):
        df = self.df
        df = df.drop('IncidentTopSRS_UCR', axis=1)
        df.rename(columns={
            'CrimeAgainst': 'NIBRSCat',
            'NIBRS': 'NIBRSCode',
            'NIBRSCategory': 'NIBRSOffenseType',
            'OccurredFromTime': 'TimeOccurred',
            'Offense': 'SLMPDOffense',
            'FelMisdCit': 'CrimeGrade',
            'IncidentLocation': 'PrimaryLocation',
            'IntersectionOtherLoc': 'SecondaryLocation',
            'NbhdNum': 'NeighborhoodNum',
            'IncidentSupplemented': 'Supplemented',
            'LastSuppDate': 'SupplementDate'
        }, inplace=True)

        ordered_cols = [
            'IncidentNum', 'IncidentDate', 'TimeOccurred', 'SLMPDOffense',
            'NIBRSCode', 'NIBRSCat', 'NIBRSOffenseType', 'SRS_UCR', 'CrimeGrade',
            'PrimaryLocation', 'SecondaryLocation', 'District', 'Neighborhood',
            'NeighborhoodNum', 'Latitude', 'Longitude', 'Supplemented',
            'SupplementDate', 'VictimNum', 'FirearmUsed', 'IncidentNature'
        ]
        df = df[ordered_cols]

        df['IncidentDate'] = pd.to_datetime(df['IncidentDate'])
        df = df[~(df['IncidentDate'] < '2021-01-01')]
        df['IncidentDate'] = df['IncidentDate'].astype('str')

        df = df.reset_index(drop=True)
        self.df = df

    def split_data(self):
        self.supp_df = self.df[self.df['Supplemented'] == 'Yes']
        self.unfound_df = self.df[(self.df['Supplemented'].isna()) & (self.df['SLMPDOffense'] == 'UNFOUNDED INCIDENT')]
        self.new_df = self.df[self.df['Supplemented'] == 'No']

    def check_integrity(self):
        if len(self.df) != len(self.supp_df) + len(self.unfound_df) + len(self.new_df):
            raise ValueError("Discrepancy found with `split_data()`: df lengths do not match.")

    def update_db_initial(self, session):
        self._insert_data(self.supp_df, self.crime_add_query, session)
        self._insert_data(self.new_df, self.crime_add_query, session)
        self._insert_data(self.unfound_df, self.unfounded_add_query, session)

    def update_db_from_supp(self, session):
        self._update_db(self.supp_df, 'crime_data', self.crime_add_query, session)

    def update_db_from_new(self, session):
        self._update_db(self.new_df, 'crime_data', self.crime_add_query, session)

    def update_db_from_unfound(self, session):
        self._update_db(self.unfound_df, 'unfounded_data', self.unfounded_add_query, session)

    def update_metadata(self, session):
        filename = self.filename

        if '2021-2023' in filename:
            date = '12-2023'
            date_obj = datetime.strptime(date, '%m-%Y')
            update_date = date_obj.strftime('%B%Y')
        else:
            date = filename.strip('Crime-').strip('.csv')
            date_obj = datetime.strptime(date, '%m-%Y')
            update_date = date_obj.strftime('%B%Y')

        self.update_date = update_date

        # Fetch the existing record
        # with session.no_autoflush:
        meta_data = session.query(MetaData).first()

        try:
            if meta_data:
                # Update the existing record
                meta_data.LastUpdated = update_date
            else:
                # Insert a new record
                meta_data = MetaData(LastUpdated=update_date)
                session.add(meta_data)
        except Exception as e:
            print(f"Error updating metadata: {e}")
            raise

    def update_raw(self, session):
        update_date = self.update_date
        date_obj = datetime.strptime(update_date, '%B%Y')
        update_date = date_obj.strftime('%m-%Y')
        df = self.df
        df['DatePublished'] = update_date
        query_string = """
        INSERT INTO raw_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                              NIBRSCode,NIBRSCat,NIBRSOffenseType,SRS_UCR,CrimeGrade,
                              PrimaryLocation,SecondaryLocation,District,Neighborhood,
                              NeighborhoodNum,Latitude,Longitude,Supplemented,
                              SupplementDate,VictimNum,FirearmUsed,IncidentNature, DatePublished) 
        VALUES (:IncidentNum, :IncidentDate, :TimeOccurred, :SLMPDOffense,
                :NIBRSCode, :NIBRSCat, :NIBRSOffenseType, :SRS_UCR, :CrimeGrade,
                :PrimaryLocation, :SecondaryLocation, :District, :Neighborhood,
                :NeighborhoodNum, :Latitude, :Longitude, :Supplemented,
                :SupplementDate, :VictimNum, :FirearmUsed, :IncidentNature, :DatePublished)
        """
        raw_add_query = text(query_string)
        self._insert_data(self.df, raw_add_query, session)

    # def get_updated_df(self, session):
    #     query = """
    #     SELECT IncidentNum, IncidentDate, TimeOccurred, SLMPDOffense,
    #            NIBRSCode, NIBRSCat, NIBRSOffenseType, SRS_UCR, CrimeGrade,
    #            PrimaryLocation, SecondaryLocation, District, Neighborhood,
    #            NeighborhoodNum, Latitude, Longitude, Supplemented,
    #            SupplementDate, VictimNum, FirearmUsed, IncidentNature
    #     FROM crime_data
    #     """
    #     updated_df = pd.read_sql_query(query, session.bind)
    #     updated_df = updated_df.sort_values(['IncidentDate', 'IncidentNum']).reset_index(drop=True)
    #     return updated_df

    def _create_add_query(self, tablename):
        columns = [
            'IncidentNum', 'IncidentDate', 'TimeOccurred', 'SLMPDOffense', 'NIBRSCode',
            'NIBRSCat', 'NIBRSOffenseType', 'SRS_UCR', 'CrimeGrade', 'PrimaryLocation',
            'SecondaryLocation', 'District', 'Neighborhood', 'NeighborhoodNum', 'Latitude',
            'Longitude', 'Supplemented', 'SupplementDate', 'VictimNum', 'FirearmUsed',
            'IncidentNature'
        ]

        column_str = ','.join(columns)
        placeholder_str = ','.join([':' + col for col in columns])
        query_string = f"INSERT INTO {tablename} ({column_str}) VALUES ({placeholder_str})"
        return text(query_string)

    def _insert_data(self, df, query, session):
        data = df.to_dict(orient='records')
        try:
            session.execute(query, data)
        except Exception as e:
            print(f"Error inserting data: {e}")
            raise

    def _update_db(self, df, table_name, query, session):
        if not df.empty:
            temp_table = 'temp_' + table_name
            data = df.to_dict(orient='records')

            # Create temp table
            create_temp_query = text(f"""
            CREATE TEMPORARY TABLE {temp_table} AS 
            SELECT * FROM {table_name} WHERE 0
            """)
            session.execute(create_temp_query)

            # Insert data into temp table
            try:
                session.execute(query, data)
            except Exception as e:
                print(f"Error inserting data into temp table: {e}")
                raise

            # Delete from main table
            delete_query = text(f"""
            DELETE FROM {table_name} 
            WHERE IncidentNum IN (SELECT IncidentNum FROM {temp_table})
            """)
            session.execute(delete_query)

            # Insert data from temp table to main table
            insert_query = text(f"""
            INSERT INTO {table_name}
            SELECT * FROM {temp_table}
            """)
            session.execute(insert_query)

            # Drop temp table
            drop_temp_query = text(f"DROP TABLE {temp_table}")
            session.execute(drop_temp_query)

    def automated_initialization(self, session):
        self.load_data()
        print(f"Loaded data: {len(self.df)} records")
        self.clean_data()
        print(f"Cleaned data: {len(self.df)} records")
        self.split_data()
        print(f"Split data: {len(self.supp_df)} supplemented, {len(self.unfound_df)} unfounded, {len(self.new_df)} new")
        self.check_integrity()
        print(f"Data integrity check passed.")
        self.update_db_initial(session)
        print(f"Inserted {len(self.supp_df)} records into the database.")
        print(f"Inserted {len(self.new_df)} records into the database.")
        print(f"Inserted {len(self.unfound_df)} records into the database.")
        self.update_metadata(session)
        print(f"Updated metadata with date: {self.update_date}")
        self.update_raw(session)
        print(f"Inserted {len(self.df)} records into the database.")
        print(f"Automated initialization complete.")

    def automated_update(self, session):
        self.load_data()
        print(f"Loaded data: {len(self.df)} records")
        self.clean_data()
        print(f"Cleaned data: {len(self.df)} records")
        self.split_data()
        print(f"Split data: {len(self.supp_df)} supplemented, {len(self.unfound_df)} unfounded, {len(self.new_df)} new")
        self.check_integrity()
        print(f"Data integrity check passed.")
        self.update_db_from_supp(session)
        print(f"Updated database with supplemented records: {len(self.supp_df)}")
        self.update_db_from_unfound(session)
        print(f"Updated database with unfounded records: {len(self.unfound_df)}")
        self.update_db_from_new(session)
        print(f"Updated database with new records: {len(self.new_df)}")
        self.update_metadata(session)
        print(f"Updated metadata with date: {self.update_date}")
        self.update_raw(session)
        print(f"Inserted {len(self.df)} records into the raw data table.")
        print(f"Automated update complete.")