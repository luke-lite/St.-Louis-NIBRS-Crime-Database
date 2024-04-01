from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import SelectField, SubmitField, FileField
from wtforms.validators import InputRequired

class UploadForm(FlaskForm):
    month_choices = [('01', 'January'), ('02', 'February'), ('03', 'March'),
                     ('04', 'April'), ('05', 'May'),('06', 'June'),
                     ('07', 'July'), ('08', 'August'), ('09', 'September'),
                     ('10', 'October'), ('11', 'November'), ('12', 'December')]
    
    year_choices = [(str(year), str(year)) for year in range(2024, 2035)]

    month = SelectField('Month', choices=month_choices, validators=[InputRequired()])
    year = SelectField('Year', choices=year_choices, validators=[InputRequired()])
    csv_file = FileField('CSV File', validators=[InputRequired(), FileAllowed(['csv'], '.csv only')])
    submit = SubmitField('Upload')