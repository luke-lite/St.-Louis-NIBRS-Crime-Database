from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(20))
    year = db.Column(db.Integer)
    filename = db.Column(db.String(100))

    def __repr__(self):
        return f"<UploadedFile {self.id}>"

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
    existing_file = UploadedFile.query.filter_by(month=month, year=year).first()

    if existing_file:
        # File already exists, prompt the user to confirm overwrite or cancel
        return jsonify({'status': 'exists', 'filename': filename})

    # Save the file to uploads folder with the provided filename
    csv_file.save(os.path.join('uploads', filename))
    
    # Save file information to the database
    file_record = UploadedFile(month=month, year=year, filename=filename)
    db.session.add(file_record)
    db.session.commit()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
