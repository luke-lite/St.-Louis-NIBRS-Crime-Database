from app import app
import os
from flask import render_template, jsonify, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from app.forms import UploadForm
import sqlite3
import pandas as pd
from utils import DataTransformer

appdir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(os.path.join(appdir, os.pardir))
DB_LOC = os.environ.get('DB_LOC')
UPLOAD_LOC = os.environ.get('UPLOAD_LOC')
TEMP_LOC = os.environ.get('TEMP_LOC')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload_page', methods=['GET', 'POST'])
def upload_page():
    form = UploadForm()
    if form.validate_on_submit():
        month = form.month.data
        year = form.year.data
        csv_file = form.csv_file.data
        filename = f"Crime_{month}_{year}"  # Construct the filename
        filesrc = f"Crime_{month}_{year}.csv"
        upload_path = os.path.join(basedir, UPLOAD_LOC, secure_filename(filesrc))
        csv_file.save(upload_path)

        with sqlite3.connect(DB_LOC) as conn:
            DT = DataTransformer(filename=filename,
                                 filepath=upload_path,
                                 conn=conn)
            DT.full_update()
            updated_df = DT.get_updated_df()

        # Save the updated DataFrame to a temporary CSV file
        temp_csv_filename = f"updated_data_{month}_{year}.csv"
        temp_csv_path = os.path.join(basedir, TEMP_LOC, temp_csv_filename)
        updated_df.to_csv(temp_csv_path, index=False)

        # Redirect to a new page after successful upload
        return redirect(url_for('process_completed', filename=temp_csv_filename, filepath=temp_csv_path))

    return render_template('upload_page.html', form=form)



@app.route('/check_file', methods=['GET'])
def check_file():
    filename = request.args.get('filename', None)
    if filename:
        upload_path = os.path.join(basedir, UPLOAD_LOC, filename)
        file_exists = os.path.exists(upload_path)
        return jsonify({'exists': file_exists})
    else:
        return jsonify({'error': 'No filename provided'}), 400
    

@app.route('/process_completed/<filename>', methods=['GET'])
def process_completed(filename):
    filepath = request.args.get('filepath')

    if filepath:
        return send_file(filepath, as_attachment=True)
    else:
        return "Filepath parameter is missing.", 400
    
@app.route('/mock')
def mock():
    return render_template('mock.html')

@app.route('/download_page')
def download_page():
    db_path = os.path.join(basedir, DB_LOC)
    with sqlite3.connect(db_path) as conn:
        last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)
    last_update = last_updated.iloc[0,0]
    formatted_date = f"{last_update[:-4]} {last_update[-4:]}"
    return render_template('download_page.html', last_update=formatted_date)

# Route to handle CSV download
@app.route('/get_csv')
def get_csv():
    db_path = os.path.join(basedir, DB_LOC)
    with sqlite3.connect(db_path) as conn:
        last_updated = pd.read_sql_query("SELECT LastUpdated FROM meta_data", conn)
        updated_df = pd.read_sql_query("""
        SELECT IncidentNum,IncidentDate,TimeOccurred,SLMPDOffense,
                NIBRSCode,NIBRSCat,NIBRSOffenseType,SRS_UCR,CrimeGrade,
                PrimaryLocation,SecondaryLocation,District,Neighborhood,
                NeighborhoodNum,Latitude,Longitude,Supplemented,
                SupplementDate,VictimNum,FirearmUsed,IncidentNature
        FROM crime_data
        """, conn)

    updated_df = updated_df.sort_values(['IncidentDate', 'IncidentNum']).reset_index(drop=True)
    last_update = last_updated.iloc[0,0]
    csv_filename = 'STLCrime_updated' + last_update + '.csv'
    csv_path = os.path.join(basedir, TEMP_LOC, csv_filename)
    updated_df.to_csv(csv_path)

    # Send the file as an attachment
    response = send_file(csv_path, as_attachment=True)
    
    # Delete the CSV file after sending
    os.remove(csv_path)
    
    return response

if __name__ == '__main__':
    app.run(debug=True)