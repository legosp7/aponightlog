from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TimeField, SelectField, TextAreaField, RadioField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User, Obslog
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me') 
    submit = SubmitField('Sign In')
    
class CurrentLog(FlaskForm):
    """Form for entering current observation log details."""
    prog = SelectField('Program', coerce=str
    , validators=[DataRequired()])

    PIAstro = StringField('PI Astronomer', validators=[DataRequired()])
    #PIAstro2 = StringField('PI Astro 2', validators=[DataRequired()])
    Observer = StringField('Observer(s)', validators=[DataRequired()])
    #Observer2 = StringField('Observer 2', validators=[DataRequired()])
    Instrument = StringField('Instrument', validators=[DataRequired()])
    #Instrument2 = StringField('Instrument 2', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    progrow = RadioField('Remote/On-site/We Did the Work',choices=[
        ('remote', 'Remote'),
        ('onsite', 'On-site'),
        ('wedidthework', 'We Did the Work')
    ], validators=[DataRequired()])
    progdtn = RadioField('DTN', choices=[
        ('D', 'D'),
        ('T', 'T'),
        ('N', 'N')
    ], validators=[DataRequired()])
    weatherdark = FloatField('Weather Dark Sky Time', validators=[DataRequired()])
    weatherbright = FloatField('Weather Bright Sky Time', validators=[DataRequired()])
    equipmentdark = FloatField('Equipment Dark Sky Time', validators=[DataRequired()])
    equipmentbright = FloatField('Equipment Bright Sky Time', validators=[DataRequired()])
    obsdark = FloatField('Obs Dark Sky Time', validators=[DataRequired()])
    obsbright = FloatField('Obs Bright Sky Time', validators=[DataRequired()])
    notuseddark = FloatField('Not Used Dark Sky Time', validators=[DataRequired()])
    notusedbright = FloatField('Not Used Bright Sky Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=1000)])  # Limit to 1000 characters
    submit = SubmitField('Save Log')
    
    def get_today_progs(self):
        """Fetch programs for today from the database."""
        print("Fetching today's programs from the database...")
        today = date.today()
        # Assuming Proglog has a date field to filter by today's date
        programs = db.session.query(Obslog).filter(Obslog.obsdate == today).all()
        #return a list of programs from the programs query
        return ([(prog.prog, prog.prog) for prog in programs])
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = db.session.scalar(
            sa.select(User).where(User.username == username.data)
        )
        if user is not None:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data)
        )
        if user is not None:
            raise ValidationError('Email already exists. Please choose a different one.')
        
    