'''
NAME:   email.py - Handles email functionality for the Nightlog application.
PURPOSE: Provides functions to send emails, including asynchronous email sending and a 
function to send a preview of the user's submission.


'''



from flask_mail import Message
from flask import Flask, current_app, render_template
from app import mail, app, db
from datetime import time, date, datetime
from app.models import Obslog, Proglog, WeatherLog, ActivityLog, FailureLog, FocusLog, TelescopeSoftwareLog
from threading import Thread 

def send_email(subject: str, sender: str, recipients: list[str], text_body: str, html_body: str) -> None:
    '''
    Send an email with the given subject, sender, recipients, text body, and HTML body.
    Args:
        subject: The subject of the email.
        sender: The email address of the sender.
        recipients: A list of email addresses of the recipients.
        text_body: The plain text body of the email.
        html_body: The HTML body of the email.
    Returns:
        None
    '''
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_async_email(app:Flask, msg:str) -> None:
    '''
    Send an email asynchronously using the Flask application context.
    Args:
        app: The Flask application instance.
        msg: The email message to be sent.
    Returns:
        None
    '''
    with app.app_context():
        mail.send(msg)
        
def send_preview(email: str) -> None:
    '''
    Send a preview of the user's submission for today's date to the specified email address.
    Args:
        email: The email address to send the preview to.
    Returns:
        None
    '''
    
    #grab all the info from the db
    today = date.today()
    obslogs = db.session.query(Obslog).filter(Obslog.obsdate == today).all()
    proglogs = db.session.query(Proglog).filter(Proglog.dateprog.like('%'+today.strftime("%y%m%d"))).all()
    activity_log = db.session.query(ActivityLog).filter(ActivityLog.activitydate == today).first()
    failure_log = db.session.query(FailureLog).filter(FailureLog.failuredate == today).all()
    weather_log = db.session.query(WeatherLog).filter(WeatherLog.weatherdate == today).first()
    focus_log = db.session.query(FocusLog).filter(FocusLog.focusdate == today).first()
    telescope_software_log = db.session.query(TelescopeSoftwareLog).filter(TelescopeSoftwareLog.telescopemodeldate == today).first()
    send_email('[Nightlog] Preview of your submission',
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               #there are two here, one for the plain text version of the email and one for the HTML version. 
               #they both use the same template but render it differently based on the format
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