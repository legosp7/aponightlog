'''
NAME:  models.py - Defines the database models for the Nightlog application.
PURPOSE: This module contains the SQLAlchemy models that represent the database tables for the Nightlog application.
'''

from typing import Optional
from datetime import datetime, timezone, date, time
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Obslog(db.Model):
    '''
    Obslog model represents the observation log for a specific date and program.
    Attributes:
    - dateprog: A unique identifier for the observation log, combining the date and program.
    - obsdate: The date of the observation.
    - prog: The program associated with the observation.
    - instrument: The instrument used for the observation.
    - PIObs: The Principal Investigator (PI) of the observation.
    - Obs: The observers involved in the observation, can be multiple.
    - starttime: The start time of the observation.
    - endtime: The end time of the observation.
    '''
    
    dateprog: so.Mapped[str] = so.mapped_column(sa.String(12), primary_key=True, unique=True)
    obsdate: so.Mapped[date] = so.mapped_column(sa.Date)
    prog: so.Mapped[str] = so.mapped_column(sa.String(4))
    instrument: so.Mapped[str] = so.mapped_column(sa.String(20))
    PIObs: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=True)  # PI Astronomer
    Obs: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)  # Observers, can be multiple
    starttime: so.Mapped[time] = so.mapped_column(sa.Time, nullable=True)  # Start time of observation
    endtime: so.Mapped[time] = so.mapped_column(sa.Time, nullable=True)  # End time of observation

    def __repr__(self) -> str:
        return f'<Obslog {self.dateprog}>'
    
    def todays_obslog(cls, dateprog: str) -> 'Obslog':
        """Return the Obslog for today's date. to be implemented through webscraping"""
        pass

class Proglog(db.Model):
    '''
    Proglog model represents the program log for a specific date and program.
    Attributes:
    - dateprog: A unique identifier for the program log, combining the date and program.
    - progid: The program ID associated with the program log.
    - progloc: Program loc, so remote, onsite, etc.
    - progdtn: Program dtn.
    - schedstart: The scheduled start time of the program.
    - schedend: The scheduled end time of the program.
    - weatherd: Weather dark
    - weatherb: Weather bright
    - equipd: Equipment dark
    - equipb: Equipment bright
    - obsd: Observing dark
    - obsb: Observing bright
    - notusedd: Not used dark
    - notusedb: Not used bright
    - note: Additional notes for the program log.
    
    '''
    dateprog: so.Mapped[str] = so.mapped_column(sa.ForeignKey(Obslog.dateprog), primary_key=True, index=True, unique=True)
    progid: so.Mapped[str] = so.mapped_column(sa.String(4), index=True)
    progloc: so.Mapped[str] = so.mapped_column(sa.String(1),nullable=True) #actually row
    progdtn: so.Mapped[str] = so.mapped_column(sa.String(1),nullable=True)
    schedstart: so.Mapped[time] = so.mapped_column(sa.Time, nullable=True)
    schedend: so.Mapped[time] = so.mapped_column(sa.Time, nullable=True)
    weatherd: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    weatherb: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    equipd: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    equipb: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    obsd: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    obsb: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    notusedd: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    notusedb: so.Mapped[float] = so.mapped_column(sa.Float,nullable=True)
    note: so.Mapped[str] = so.mapped_column(sa.Text,nullable=True)
    
    def __repr__(self) -> str:
        return f'<Proglog {self.dateprog}>'
    
class WeatherLog(db.Model):
    '''
    WeatherLog model represents the weather log for a specific date.
    Attributes:
    - weatherdate: The date of the weather log, serves as the primary key.
    - weatherfield: The weather conditions for the date.
    - notes: Additional notes for the weather log.
    '''
    weatherdate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True)
    weatherfield: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)  # Weather conditions
    notes: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

class ActivityLog(db.Model):
    '''
    ActivityLog model represents the activity log for a specific date.
    Attributes:
    - activitydate: The date of the activity log, serves as the primary key.
    - ObservingSpec: The observing specifications for the date.
    - notes: Additional notes for the activity log.
    '''
    
    activitydate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True)
    ObservingSpec: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    notes: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    
class FailureLog(db.Model):
    '''
    FailureLog model represents the failure log for a specific date and program.
    Attributes:
    - progdate: A unique identifier for the failure log, combining the date and program.
    - failuredate: The date of the failure log.
    - prog: The program associated with the failure log.
    - instrument: The instrument involved in the failure.
    - TI: T/I.
    - SHU: S/H/U
    - FAILSTART: The start time of the failure.
    - FAILEND: The end time of the failure.
    - FAILDISC: A description of the failure.
    '''
    
    progdate: so.Mapped[str] = so.mapped_column(sa.String(12), primary_key=True, unique=True)
    failuredate: so.Mapped[date] = so.mapped_column(sa.Date, index=True)  # Date of the failure log
    prog: so.Mapped[str] = so.mapped_column(sa.String(4), index=True)
    instrument: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # Instrument involved in the failure
    TI: so.Mapped[str] = so.mapped_column(sa.String(1), nullable=True)  # Telescope Instrument failure
    SHU: so.Mapped[str] = so.mapped_column(sa.String(1), nullable=True)  # SHU failure
    FAILSTART: so.Mapped[time] = so.mapped_column(sa.Time, nullable=True)  # Start time of failure
    FAILEND: so.Mapped[time] = so.mapped_column(sa.Time, nullable=True)  # End time of failure
    FAILDISC: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)  # Failure description
    
class FocusLog(db.Model):
    '''
    FocusLog model represents the focus log for a specific date.
    Attributes:
    - focusdate: The date of the focus log, serves as the primary key.
    - focustext: The focus information for the date.
    '''
    focusdate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True, unique=True)
    focustext: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)  # Focus text
    
class TelescopeSoftwareLog(db.Model):
    '''
    TelescopeSoftwareLog model represents the telescope software log for a specific date.
    Attributes:
    - telescopemodeldate: The date of the telescope software log, serves as the primary key.
    - tccversion: The version of the TCC software.
    - hubversion: The version of the Hub software.
    - tuiversion: The version of the TUI software.
    '''
    
    telescopemodeldate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True, unique=True)
    tccversion: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # TCC version
    hubversion: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # Hub version
    tuiversion: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # TUI version
    
class LogDate(db.Model):
    '''
    LogDate model represents the last known date to work for sure for the autofill
    Attributes:
    - logdate: The date of the log, serves as the primary key.
    '''
    
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True)
    logdate: so.Mapped[date] = so.mapped_column(sa.Date, unique=True)