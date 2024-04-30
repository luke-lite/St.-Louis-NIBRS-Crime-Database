import pandas as pd

def transform_data(csv_loc, conn):
    df = pd.read_csv(csv_loc)
    df = df.drop('IncidentTopSRS_UCR', axis=1)
    df.rename(columns={'CrimeAgainst': 'NIBRSCat',
                       'NIBRS': 'NIBRSCode',
                       'NIBRSCategory':'NIBRSOffenseType',
                       'SRS_UCR':'UCR_SRS',
                       'OccurredFromTime':'TimeOccurred',
                       'Offense':'SLMPDOffense',
                       'FelMisdCit':'CrimeGrade',
                       'IncidentLocation':'PrimaryLocation',
                       'IntersectionOtherLoc':'SecondaryLocation',
                       'NbhdNum':'NeighborhoodNum',
                       'IncidentSupplemented':'Supplemented',
                       'LastSuppDate':'SupplementDate'}, inplace=True)
    
    ordered_cols = ['IncidentNum', 'IncidentDate', 'TimeOccurred', 'SLMPDOffense',
                    'NIBRSCode', 'NIBRSCat', 'NIBRSOffenseType', 'UCR_SRS', 'CrimeGrade',
                    'PrimaryLocation', 'SecondaryLocation', 'District', 'Neighborhood',
                    'NeighborhoodNum', 'Latitude', 'Longitude', 'Supplemented',
                    'SupplementDate', 'VictimNum', 'FirearmUsed', 'IncidentNature']
    df = df[ordered_cols]

    # remove incidents prior to 2021-01-01
    df['IncidentDate'] = pd.to_datetime(df['IncidentDate'])
    df = df[~(df['IncidentDate'] < '2021-01-01')]
    # revert to string column
    df['IncidentDate'] = df['IncidentDate'].astype('str')

    df.reset_index(inplace=True, drop=True)
    
    supp_df = df[df['Supplemented'] == 'Yes']
    unfound_df = df[(df['Supplemented'].isna()) & (df['SLMPDOffense'] == 'UNFOUNDED INCIDENT')]
    new_df = df[df['Supplemented'] == 'No']

    if len(df) != len(supp_df) + len(unfound_df) + len(new_df):
        print("Something doesn't add up")


    
    # supp_df transformations:
    
    supp_df.to_sql('supp_temp', conn, if_exists='replace', index=False)
    
    delete_query = """
    DELETE FROM crime_data 
    WHERE IncidentNum IN (SELECT IncidentNum FROM supp_temp)
    """
    conn.execute(delete_query)

    add_supp_query = """INSERT INTO crime_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                               NIBRSCode,NIBRSCat,NIBRSOffenseType,UCR_SRS,CrimeGrade,
                                               PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                               NeighborhoodNum,Latitude,Longitude,Supplemented,
                                               SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

    # get tuples for the add query
    new_rows = [tuple(x) for x in supp_df.itertuples(index=False)]
    
    conn.executemany(add_supp_query, new_rows)

    conn.execute('DROP TABLE IF EXISTS supp_temp')


    # unfound_df transformations:

    
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


    add_unfounded_query = """INSERT INTO unfounded_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                                         NIBRSCode,NIBRSCat,NIBRSOffenseType,UCR_SRS,CrimeGrade,
                                                         PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                                         NeighborhoodNum,Latitude,Longitude,Supplemented,
                                                         SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

    # get tuples for the add query
    new_rows = [tuple(x) for x in unfound_df.itertuples(index=False)]
    
    conn.executemany(add_unfounded_query, new_rows)
    
    
    conn.execute('DROP TABLE IF EXISTS unfounded_temp')


    # new_df transformations:

    
    new_df.to_sql('new_temp', conn, if_exists='replace', index=False)
    
    delete_query = """
    DELETE FROM crime_data 
    WHERE IncidentNum IN (SELECT IncidentNum FROM new_temp)
    """
    conn.execute(delete_query)
    
    add_new_query = """INSERT INTO crime_data (IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                               NIBRSCode,NIBRSCat,NIBRSOffenseType,UCR_SRS,CrimeGrade,
                                               PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                               NeighborhoodNum,Latitude,Longitude,Supplemented,
                                               SupplementDate,VictimNum,FirearmUsed,IncidentNature) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    # get tuples for the add query
    new_rows = [tuple(x) for x in new_df.itertuples(index=False)]
    conn.executemany(add_new_query, new_rows)

    conn.execute('DROP TABLE IF EXISTS new_temp')
    

    
    # Return updated table
    updated_df = pd.read_sql_query("""SELECT IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                                             NIBRSCode,NIBRSCat,NIBRSOffenseType,UCR_SRS,CrimeGrade,
                                             PrimaryLocation,SecondaryLocation,District,Neighborhood,
                                             NeighborhoodNum,Latitude,Longitude,Supplemented,
                                             SupplementDate,VictimNum,FirearmUsed,IncidentNature
                                      FROM crime_data""", conn)
    updated_df = updated_df.sort_values(['IncidentDate', 'IncidentNum'])

    # Commit changes
    conn.commit()

    return [df, supp_df, unfound_df, new_df, updated_df]
