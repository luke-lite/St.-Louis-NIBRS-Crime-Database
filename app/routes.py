from app import app
import os
from flask import render_template, flash, request
from werkzeug.utils import secure_filename
from app.forms import UploadForm

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
        filename = f"Crime_{month}_{year}.csv"  # Construct the filename
        upload_path = os.path.join('uploads', secure_filename(filename))

        # confirmed = request.form.get('confirmed')
        # if confirmed == 'true':
        #     return render_template('index.html')

        # if os.path.exists(upload_path):

        #     # If file with the same name already exists, prompt user for confirmation
        #     return render_template('upload_page.html', form=form, filename=filename, overwrite=True)

        # If file doesn't exist, or user confirms overwrite, save the file
        csv_file.save(upload_path)
        flash('File uploaded successfully!')
        return "File uploaded successfully!"

    return render_template('upload_page.html', form=form)