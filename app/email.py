from flask_mail import Message
from flask import render_template
from app import mail, app, db
from datetime import time, date, datetime
from app.models import Obslog, Proglog, WeatherLog, ActivityLog, FailureLog, FocusLog, TelescopeSoftwareLog

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    
def send_preview(email):
    
    today = date.today()
    obslogs = db.session.query(Obslog).filter(Obslog.obsdate == today).all()
    proglogs = db.session.query(Proglog).filter(Proglog.dateprog.like('%'+today.strftime("%y%m%d"))).all()
    activity_log = db.session.query(ActivityLog).filter(ActivityLog.activitydate == today).first()
    failure_log = db.session.query(FailureLog).filter(FailureLog.failuredate == today).all()
    weather_log = db.session.query(WeatherLog).filter(WeatherLog.weatherdate == today).first()
    focus_log = db.session.query(FocusLog).filter(FocusLog.focusdate == today).first()
    telescope_software_log = db.session.query(TelescopeSoftwareLog).filter(TelescopeSoftwareLog.telescopemodeldate == today).first()
    send_email('[Nightlog] Preview of your submission',
               sender=app.config['ADMINS'][0],
               recipients=[email],
               text_body=render_template('email/preview.txt',
                                         date = date.today().strftime("%A, %B %d, %Y"),
                                         obslogs=obslogs,
                                         proglogs=proglogs,
                                         activity_log=activity_log,
                                         failure_log=failure_log,
                                         weather_log=weather_log,
                                         focus_log=focus_log,
                                         telescope_software_log=telescope_software_log),
               html_body=render_template('email/preview.html',
                                         date = date.today().strftime("%A, %B %d, %Y"),
                                         obslogs=obslogs,
                                         proglogs=proglogs,
                                         activity_log=activity_log,
                                         failure_log=failure_log,
                                         weather_log=weather_log,
                                         focus_log=focus_log,
                                         telescope_software_log=telescope_software_log),
                )