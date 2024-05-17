import pandas as pd
from datetime import datetime
# import sqlite3

class DataTransformer():
    def __init__(self, filename, filepath, conn):
        self.filename = filename
        self.filepath = filepath
        self.conn = conn
        self.add_query = """
        INSERT INTO crime_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                NIBRSCode,NIBRSCat,NIBRSOffenseType,SRS_UCR,CrimeGrade,
                                PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                NeighborhoodNum,Latitude,Longitude,Supplemented,
                                SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """

    def __str__(self):
        return f"DataTransformer Object: ({self.filename})"

    def clean_data(self):
        filepath = self.filepath
        df = pd.read_csv(filepath)
        df = df.drop('IncidentTopSRS_UCR', axis=1)
        df.rename(columns={'CrimeAgainst': 'NIBRSCat',
                           'NIBRS': 'NIBRSCode',
                           'NIBRSCategory':'NIBRSOffenseType',
                           'OccurredFromTime':'TimeOccurred',
                           'Offense':'SLMPDOffense',
                           'FelMisdCit':'CrimeGrade',
                           'IncidentLocation':'PrimaryLocation',
                           'IntersectionOtherLoc':'SecondaryLocation',
                           'NbhdNum':'NeighborhoodNum',
                           'IncidentSupplemented':'Supplemented',
                           'LastSuppDate':'SupplementDate'}, inplace=True)
        
        ordered_cols = ['IncidentNum', 'IncidentDate', 'TimeOccurred', 'SLMPDOffense',
                        'NIBRSCode', 'NIBRSCat', 'NIBRSOffenseType', 'SRS_UCR', 'CrimeGrade',
                        'PrimaryLocation', 'SecondaryLocation', 'District', 'Neighborhood',
                        'NeighborhoodNum', 'Latitude', 'Longitude', 'Supplemented',
                        'SupplementDate', 'VictimNum', 'FirearmUsed', 'IncidentNature']
        df = df[ordered_cols]

        # remove incidents prior to 2021-01-01
        df['IncidentDate'] = pd.to_datetime(df['IncidentDate'])
        df = df[~(df['IncidentDate'] < '2021-01-01')]
        # revert to string column
        df['IncidentDate'] = df['IncidentDate'].astype('str')

        df = df.reset_index(drop=True)
        self.df = df

    def split_data(self):
        self.supp_df = self.df[self.df['Supplemented'] == 'Yes']
        self.unfound_df = self.df[(self.df['Supplemented'].isna()) & (self.df['SLMPDOffense'] == 'UNFOUNDED INCIDENT')]
        self.new_df = self.df[self.df['Supplemented'] == 'No']

    def check_integrity(self):
        if len(self.df) != len(self.supp_df) + len(self.unfound_df) + len(self.new_df):
            # to-do: automate an error message email.
            raise ValueError("Discrepancy found with `split_data()`: df lengths do not match.")

    def update_db_initial(self):
        supp_df = self.supp_df
        unfound_df = self.unfound_df
        new_df = self.new_df
        conn = self.conn

        add_supp_query = self.add_query
        all_rows = [tuple(x) for x in supp_df.itertuples(index=False)]
        conn.executemany(add_supp_query, all_rows)

        add_unfounded_query = """
        INSERT INTO unfounded_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                    NIBRSCode,NIBRSCat,NIBRSOffenseType,SRS_UCR,CrimeGrade,
                                    PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                    NeighborhoodNum,Latitude,Longitude,Supplemented,
                                    SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        all_rows = [tuple(x) for x in unfound_df.itertuples(index=False)]
        conn.executemany(add_unfounded_query, all_rows)

        add_new_query = self.add_query
        new_rows = [tuple(x) for x in new_df.itertuples(index=False)]
        conn.executemany(add_new_query, new_rows)

    def update_db_from_supp(self):
        supp_df = self.supp_df
        conn = self.conn

        supp_df.to_sql('supp_temp', conn, if_exists='replace', index=False)

        delete_query = """
        DELETE FROM crime_data 
        WHERE IncidentNum IN (SELECT IncidentNum FROM supp_temp)
        """
        conn.execute(delete_query)

        add_supp_query = self.add_query

        # get tuples of each df row for the add query
        new_rows = [tuple(x) for x in supp_df.itertuples(index=False)]
        conn.executemany(add_supp_query, new_rows)

        conn.execute("DROP TABLE IF EXISTS supp_temp")

    def update_db_from_unfound(self):
        unfound_df = self.unfound_df
        conn = self.conn

        unfound_df.to_sql('unfounded_temp', conn, if_exists='replace', index=False)

        delete_query = """
        DELETE FROM crime_data 
        WHERE IncidentNum IN (SELECT IncidentNum FROM unfounded_temp)
        """
        conn.execute(delete_query)

        unfounded_delete_query = """
        DELETE FROM unfounded_data 
        WHERE IncidentNum IN (SELECT IncidentNum FROM unfounded_temp)
        """
        conn.execute(unfounded_delete_query)

        # insert into different table than the self.add_query
        add_unfounded_query = """
        INSERT INTO unfounded_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                    NIBRSCode,NIBRSCat,NIBRSOffenseType,SRS_UCR,CrimeGrade,
                                    PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                    NeighborhoodNum,Latitude,Longitude,Supplemented,
                                    SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """

        # get tuples for the add query
        new_rows = [tuple(x) for x in unfound_df.itertuples(index=False)]
        conn.executemany(add_unfounded_query, new_rows)
        
        conn.execute("DROP TABLE IF EXISTS unfounded_temp")

    def update_db_from_new(self):
        new_df = self.new_df
        conn = self.conn

        new_df.to_sql('new_temp', conn, if_exists='replace', index=False)
    
        delete_query = """
        DELETE FROM crime_data 
        WHERE IncidentNum IN (SELECT IncidentNum FROM new_temp)
        """
        conn.execute(delete_query)
        
        add_new_query = self.add_query

        # get tuples for the add query
        new_rows = [tuple(x) for x in new_df.itertuples(index=False)]
        conn.executemany(add_new_query, new_rows)

        conn.execute("DROP TABLE IF EXISTS new_temp")

    def update_metadata(self):
        conn = self.conn
        filename = self.filename

        if '2021-2023' in filename:
            update_date = 'December2023'
        else:
            date = filename.strip('Crime-').strip('.csv')
            date_obj = datetime.strptime(date, '%m-%Y')
            update_date = date_obj.strftime('%B%Y')

        date_df = pd.DataFrame(data=[[update_date]], columns=['LastUpdated'])

        date_df.to_sql('meta_data', conn, if_exists='replace', index=False)

    def commit_to_db(self):
        self.conn.commit()


    def get_updated_df(self):
        conn=self.conn

        # Return updated table
        updated_df = pd.read_sql_query("""
        SELECT IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
               NIBRSCode,NIBRSCat,NIBRSOffenseType,SRS_UCR,CrimeGrade,
               PrimaryLocation,SecondaryLocation,District,Neighborhood,
               NeighborhoodNum,Latitude,Longitude,Supplemented,
               SupplementDate,VictimNum,FirearmUsed,IncidentNature
        FROM crime_data
        """, conn)
        updated_df = updated_df.sort_values(['IncidentDate', 'IncidentNum']).reset_index(drop=True)
        # updated_df = updated_df.reset_index(drop=True)

        return updated_df

    
    def get_lastupdated(self):
        conn = self.conn
        last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)

        return last_updated

    def get_split_dfs(self):
        supp_df = self.supp_df
        unfound_df = self.unfound_df
        new_df = self.new_df

        return supp_df, unfound_df, new_df
    
    def automated_update(self):  
        self.clean_data()
        self.split_data()
        self.check_integrity()
        self.update_db_from_supp()
        self.update_db_from_unfound()
        self.update_db_from_new()
        self.update_metadata()
        self.commit_to_db()