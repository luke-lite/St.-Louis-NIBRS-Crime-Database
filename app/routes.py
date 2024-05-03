from app import app
import os
from flask import render_template, flash, jsonify, request, redirect, url_for, Response, send_file
from werkzeug.utils import secure_filename
from app.forms import UploadForm
import sqlite3
import pandas as pd
from utils import DataTransformer

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
        upload_path = os.path.join('uploads', secure_filename(filesrc))
        csv_file.save(upload_path)

        with sqlite3.connect('database.db') as conn:
            DT = DataTransformer(filename=filename,
                                 upload_path=upload_path,
                                 conn=conn)
            DT.full_update()
            updated_df = DT.get_updated_df()

        # Save the updated DataFrame to a temporary CSV file
        temp_csv_filename = f"updated_data_{month}_{year}.csv"
        temp_csv_path = os.path.join('temp', temp_csv_filename)
        updated_df.to_csv(temp_csv_path, index=False)

        # Redirect to a new page after successful upload
        return redirect(url_for('process_completed', filename=temp_csv_filename))

    return render_template('upload_page.html', form=form)



@app.route('/check_file', methods=['GET'])
def check_file():
    filename = request.args.get('filename', None)
    if filename:
        upload_path = os.path.join('uploads', filename)
        file_exists = os.path.exists(upload_path)
        return jsonify({'exists': file_exists})
    else:
        return jsonify({'error': 'No filename provided'}), 400
    

@app.route('/process_completed/<filename>', methods=['GET'])
def process_completed(filename):
    # # Retrieve the DataFrame from the query string
    # df = request.args.get('df')
    # df = pd.read_json(request.args.get('df'))

    # # Here you can generate a new CSV file or do any other processing
    # # For demonstration, let's just create a simple CSV file
    # csv_data = df.to_csv(index=False)
    
    # # Serve the CSV file to the user for download
    # return Response(
    #     csv_data,
    #     mimetype="text/csv",
    #     headers={"Content-disposition":
    #              f"attachment; filename=SLMPD_NIBRS_crime_updated_{month}_{year}.csv"})

    # Serve the temporary CSV file to the user for download
    return send_file(f'temp/{filename}', as_attachment=True)