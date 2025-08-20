from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TimeField, SelectField, TextAreaField, RadioField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
import sqlalchemy as sa
from app import db
from app.models import Obslog
from datetime import date
    
class CurrentLog(FlaskForm):
    """Form for entering current observation log details."""
    prog = SelectField('Option', coerce=str
    , validators=[DataRequired()]) #actually just the drop down menu, contains more than programs

    #program fields
    PIAstro = StringField('PI Astronomer', validators=[Optional()])
    Observer = StringField('Observer(s)', validators=[Optional()])
    Instrument = StringField('Instrument', validators=[Optional()])
    start_time = TimeField('Start Time', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])
    progrow = RadioField('Remote/On-site/We Did the Work',choices=[
        ('R', 'Remote'),
        ('O', 'On-site'),
        ('W', 'We Did the Work')
    ], validators=[Optional()])
    progdtn = RadioField('DTN', choices=[
        ('D', 'D'),
        ('T', 'T'),
        ('N', 'N')
    ], validators=[Optional()])
    weatherdark = FloatField('Weather Dark Sky Time', validators=[Optional()])
    weatherbright = FloatField('Weather Bright Sky Time', validators=[Optional()])
    equipmentdark = FloatField('Equipment Dark Sky Time', validators=[Optional()])
    equipmentbright = FloatField('Equipment Bright Sky Time', validators=[Optional()])
    obsdark = FloatField('Obs Dark Sky Time', validators=[Optional()])
    obsbright = FloatField('Obs Bright Sky Time', validators=[Optional()])
    notuseddark = FloatField('Not Used Dark Sky Time', validators=[Optional()])
    notusedbright = FloatField('Not Used Bright Sky Time', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Length(max=1000), Optional()])  # Limit to 1000 characters
    
    #text fields for additional information
    weatherfield = TextAreaField('Weather Conditions', validators=[Length(max=500), Optional()])  # Limit to 500 characters
    weathernote = TextAreaField('Weather Notes', validators=[Length(max=500), Optional()])  # Limit to 500 characters
    
    #fields for activity log
    ObservingSpec = StringField('Observing Specialist', validators=[Length(max=1000), Optional()])  # Limit to 1000 characters
    activitynote = TextAreaField('Activity Notes', validators=[Length(max=500), Optional()])  # Limit to 500 characters
    
    #fields for failure log
    progfail = SelectField('Program', coerce=str, validators=[DataRequired()])
    instrumentfail = StringField('Instrument', validators=[Optional()])
    TI = RadioField('Telescope Instrument Failure', choices=[
        ('T', 'T'),
        ('I', 'I')
    ], validators=[Optional()])
    SHU = RadioField('SHU Failure', choices=[
        ('S', 'S'),
        ('H', 'H'),
        ('U', 'U')
    ], validators=[Optional()])
    failstart = TimeField('Failure Start Time', validators=[Optional()])
    failend = TimeField('Failure End Time', validators=[Optional()])
    failnote = TextAreaField('Failure Notes', validators=[Length(max=1000), Optional()])  # Limit to 1000 characters
    
    #fields for focus log
    focuslog = TextAreaField('Focus Log', validators=[Optional()])  # Limit to 1000 characters
    
    #fields for telescope software
    tccversion = StringField('TCC Version', validators=[Optional()])  
    hubversion = StringField('Hub Version', validators=[Optional()])  # Limit to 20 characters
    tuiversion = StringField('TUI Version', validators=[Optional()])  # Limit to 20 characters
    
    submit = SubmitField('Save Log')
    
    def get_today_progs(self):
        """Fetch programs for today from the database."""
        print("Fetching today's programs from the database...")
        today = date.today()
        # Assuming Proglog has a date field to filter by today's date
        programs = db.session.query(Obslog).filter(Obslog.obsdate == today).all()
        #return a list of programs from the programs query
        return ([(prog.prog, prog.prog) for prog in programs])
    
    
    def validate(self, **kwargs):
        ok = super().validate(**kwargs)
        if not ok:
            return False

        # rules injected by the view on POST
        rules = getattr(self, "_program_rules", None) or {}
        required_names = rules.get("required_fields", [])

        def is_blank(val):
            if val is None:
                return True
            if isinstance(val, str):
                return not val.strip()
            return False

        any_missing = False
        for name in required_names:
            fld = getattr(self, name, None)
            if fld is None or is_blank(fld.data):
                any_missing = True
                if fld is not None:
                    fld.errors.append("Required for the selected program.")
        return not any_missing
    
        
    