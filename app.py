import logging
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# import time
# from datetime import date, timedelta, datetime
# from flask_restful import Resource
# import two_factor
# import random

# Local imports
from config import app, db, api
from models import Uploads

# Configure logging to display messages in the console
app.logger.setLevel(logging.DEBUG)  # Set logging level to INFO

# Add a console handler to log messages to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set logging level to INFO
app.logger.addHandler(console_handler)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    month = request.form['month']
    year = request.form['year']
    filename = f"Crime{month}{year}.csv"  # Construct the filename
    csv_file = request.files['file']
    
    # Check if a file with the same month and year exists in the database
    existing_file = Uploads.query.filter_by(month=month, year=year).first()

    if existing_file:
        # File already exists, prompt the user to confirm overwrite or cancel
        app.logger.info(f"File {filename} already exists")
        return jsonify({'status': 'exists', 'filename': filename})

    # Save the file to uploads folder with the provided filename
    csv_file.save(os.path.join('uploads', filename))
    
    # Save file information to the database
    file_record = Uploads(month=month, year=year, filename=filename)
    db.session.add(file_record)
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/checkIfExists', methods=['GET'])
def check_if_exists():
    month = request.args.get('month')
    year = request.args.get('year')

    # Check if a file with the same month and year exists in the database
    existing_file = Uploads.query.filter_by(month=month, year=year).first()
    if existing_file:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

if __name__ == '__main__':
    # db.create_all()
    app.run(port=5555, debug=True)