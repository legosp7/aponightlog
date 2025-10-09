from typing import Optional
from datetime import datetime, timezone, date, time
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Obslog(db.Model):
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
    weatherdate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True)
    weatherfield: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)  # Weather conditions
    notes: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

class ActivityLog(db.Model):
    activitydate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True)
    ObservingSpec: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    notes: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    
class FailureLog(db.Model):
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
    focusdate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True, unique=True)
    focustext: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)  # Focus text
    
class TelescopeSoftwareLog(db.Model):
    telescopemodeldate: so.Mapped[date] = so.mapped_column(sa.Date, primary_key=True, unique=True)
    tccversion: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # TCC version
    hubversion: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # Hub version
    tuiversion: so.Mapped[str] = so.mapped_column(sa.String(20), nullable=True)  # TUI version