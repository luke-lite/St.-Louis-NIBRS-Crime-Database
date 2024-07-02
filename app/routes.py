from app import db
import os
from flask import render_template, send_file, current_app as app
import pandas as pd
import io

TEMP_LOC = os.environ.get('TEMP_LOC')
appdir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(appdir, os.pardir))

@app.route('/')
@app.route('/index')
def index():
    with db.engine.connect() as conn:
        last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)
        sample_data = pd.read_sql_query("SELECT * FROM crime_data LIMIT 10", conn)

    if last_updated.empty:
        raise ValueError("No data found in meta_data table")
    
    last_update = last_updated.iloc[0,0]
    formatted_date = f"{last_update[:-4]} {last_update[-4:]}"
    sample_data_html = sample_data.to_html(classes='table table-striped table-bordered', index=False)
    return render_template('index.html', last_update=formatted_date, sample_data_html=sample_data_html)

@app.route('/preview_data')
def preview_data():
    with db.engine.connect() as conn:
        preview_df = pd.read_sql_query("""
        SELECT IncidentNum, IncidentDate, TimeOccurred, SLMPDOffense,
               NIBRSCode, NIBRSCat, NIBRSOffenseType, SRS_UCR, CrimeGrade,
               PrimaryLocation, SecondaryLocation, District, Neighborhood,
               NeighborhoodNum, Latitude, Longitude, Supplemented,
               SupplementDate, VictimNum, FirearmUsed, IncidentNature
        FROM crime_data
        """, conn)

    if preview_df.empty:
        raise ValueError("No data found in crime_data table")
    
    preview_df = preview_df.sort_values(['IncidentDate', 'IncidentNum']).reset_index(drop=True)
    preview_df_html = preview_df.head().to_html(classes='table table-striped table-bordered')

    buffer = io.StringIO()
    preview_df.info(buf=buffer)
    df_info_str = buffer.getvalue().replace('\n', '<br>')

    return render_template('preview_data.html', table=preview_df_html, df_info=df_info_str)

@app.route('/get_csv')
def get_csv():
    with db.engine.connect() as conn:
        last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)

        if last_updated.empty:
            raise ValueError("No data found in meta_data table")

        updated_df = pd.read_sql_query("""
        SELECT IncidentNum, IncidentDate, TimeOccurred, SLMPDOffense,
               NIBRSCode, NIBRSCat, NIBRSOffenseType, SRS_UCR, CrimeGrade,
               PrimaryLocation, SecondaryLocation, District, Neighborhood,
               NeighborhoodNum, Latitude, Longitude, Supplemented,
               SupplementDate, VictimNum, FirearmUsed, IncidentNature
        FROM crime_data
        """, conn)

        if updated_df.empty:
            raise ValueError("No data found in crime_data table")

    updated_df = updated_df.sort_values(['IncidentDate', 'IncidentNum']).reset_index(drop=True)
    last_update = last_updated.iloc[0,0]
    csv_filename = 'STLCrime_updated_' + last_update + '.csv'
    csv_path = os.path.join(basedir, TEMP_LOC, csv_filename)
    updated_df.to_csv(csv_path, index=False)

    response = send_file(csv_path, as_attachment=True)
    os.remove(csv_path)
    
    return response

@app.errorhandler(ValueError)
def handle_value_error(error):
    return render_template('error.html', error_message=str(error)), 500

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=8080)