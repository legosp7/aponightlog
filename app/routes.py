from sqlalchemy.exc import IntegrityError
from app import app, db
from flask import Blueprint,render_template, flash, redirect, url_for, request, jsonify
from app.forms import CurrentLog
import sqlalchemy as sa
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
#remove below
from app.models import Obslog, Proglog, ActivityLog, FailureLog, WeatherLog, TelescopeSoftwareLog, FocusLog
from urllib.parse import urlsplit

def prefill(program):
        '''get the program rules from the database and set the form fields accordingly'''
        today = date.today()
        
        if program == 'Weather':
            latest = db.session.query(WeatherLog).filter(WeatherLog.weatherdate == today).first()
            return {
                'prefill': {
                    "weatherfield": (latest.weatherfield if latest else '') or '',
                    "weathernote": (latest.notes if latest else '') or ''
                },
                "rules": {
                "show": ["weatherfield","weathernote"],              # <-- only this group appears
                "required_fields": ["weatherfield","weathernote"],   # <-- only this is required
            },
        }
            
        if program == 'Activity':
            latest = db.session.query(ActivityLog).filter(ActivityLog.activitydate == today).first()
            return {
                'prefill': {
                    'ObservingSpec': (latest.ObservingSpec if latest else '') or '',
                    'activitynote': (latest.notes if latest else '') or ''
                },
                "rules": {
                    "show": ["ObservingSpec", "activitynote"],
                    "required_fields": ["ObservingSpec", "activitynote"]
                }
            }
        
        if program == 'Focus Log':
            latest = db.session.query(FocusLog).filter(FocusLog.focusdate == today).first()
            return {
                'prefill': {
                    'focuslog': (latest.focustext if latest else '') or ''
                },
                "rules": {
                    "show": ["focuslog"],
                    "required_fields": ["focuslog"]
                }
            }
        
        if program == 'Telescope Software':
            latest = db.session.query(TelescopeSoftwareLog).filter(TelescopeSoftwareLog.telescopemodeldate == today).first()
            return {
                'prefill': {
                    'tccversion': (latest.tccversion if latest else '') or '',
                    'hubversion': (latest.hubversion if latest else '') or '',
                    'tuiversion': (latest.tuiversion if latest else '') or ''
                },
                "rules": {
                    "show": ["tccversion", "hubversion", "tuiversion"],
                    "required_fields": ["tccversion", "hubversion", "tuiversion"]
                }
            }
            
        if program == 'Failure Log':
            latest = db.session.query(FailureLog).filter(FailureLog.progdate == program + today.strftime("%y%m%d")).first()
            return {
                'prefill': {
                    'instrumentfail': (latest.instrument if latest else '') or '',
                    'TI': (latest.TI if latest else '') or '',
                    'SHU': (latest.SHU if latest else '') or '',
                    'failstart': (latest.FAILSTART if latest else None),
                    'failend': (latest.FAILEND if latest else None),
                    'failnote': (latest.FAILDISC if latest else '') or ''
                },
                "rules": {
                    "show": ["progfail", "instrumentfail", "TI", "SHU", "failstart", "failend", "failnote"],
                    "required_fields": ["progfail", "instrumentfail", "TI", "SHU", "failstart", "failend"]
                }
            }
            
        latest = db.session.query(Obslog).filter(Obslog.prog == program,Obslog.obsdate==today).first()
        
        
        
        data = {
            'prog': program,
            'PIAstro': (latest.PIObs if latest else '') or '',
            'Observer': (latest.Obs if latest else '') or '',
            'Instrument': (latest.instrument if latest else '') or '',
            'start_time': None,
            'end_time': None,
        }
        
        #rules
        rules = {"show": ["PIAstro", "Observer", "Instrument", "start_time", "end_time", "progrow",
                          "progdtn","weatherdark","weatherbright","equipmentdark",
                          "equipmentbright","obsdark","obsbright","notuseddark","notusedbright","notes"],
                 "required_fields":[]
                 }
            
        return {"prefill":data,"rules":rules}

@app.route('/') 
@app.route('/home')
def home():
    return render_template('home.html', title='Home')

@app.route('/prevlogs')
def prevlogs():
    return render_template('prevlogs.html', title='Previous Logs')

@app.route('/preview')
def preview():
    #grab the obslogs for today
    today = date.today()
    obslogs = db.session.query(Obslog).filter(Obslog.obsdate == today).all()
    #grab the proglogs for today
    proglogs = db.session.query(Proglog).filter(Proglog.dateprog.like(today.strftime("%y%m%d") + '%')).all()
    #grab the activity log for today
    activity_log = db.session.query(ActivityLog).filter(ActivityLog.activitydate == today).first()
    #grab the failure logs for today
    failure_log = db.session.query(FailureLog).filter(FailureLog.failuredate == today).all()
    #grab the weather log for today
    weather_log = db.session.query(WeatherLog).filter(WeatherLog.weatherdate == today).first()
    #grab the focus log for today
    focus_log = db.session.query(FocusLog).filter(FocusLog.focusdate == today).first()
    #grab the telescope software log for today
    telescope_software_log = db.session.query(TelescopeSoftwareLog).filter(TelescopeSoftwareLog.telescopemodeldate == today).first()
    
    return render_template('preview.html', title='Preview', 
                           date = date.today().strftime("%A, %B %d, %Y"),
                           obslogs=obslogs,
                           proglogs=proglogs,
                           activity_log=activity_log,
                           failure_log=failure_log,
                           weather_log=weather_log,
                           focus_log=focus_log,
                           telescope_software_log=telescope_software_log)


@app.route('/currentlog', methods=['GET', 'POST'])
def currentlog():
    form = CurrentLog()
    form.prog.choices = form.get_today_progs() + [('Activity','Activity'),
                                                  ('Failure Log','Failure Log'),('Focus Log','Focus Log'),
                                                  ('Weather','Weather'),('Telescope Software','Telescope Software')] # Populate the program choices from the database
    form.progfail.choices = form.get_today_progs()  # Populate the program choices for failure log
    if request.method == "POST" and form.prog.data:
        info = prefill(form.prog.data)  # Get the program info based on the selected program
        if info:
            form._program_rules = info["rules"]
            
    if form.validate_on_submit():
        
        today = date.today().strftime("%y%m%d")  # Get today's date in YYMMDD format
        dateprog = form.prog.data + today
        
        
        # activity log
        if form.prog.data == 'Activity':
            activity_log = db.session.scalar(
                sa.select(ActivityLog).where(ActivityLog.activitydate == date.today())
            )
            if activity_log is None:
                activity_log = ActivityLog(activitydate=date.today())
                db.session.add(activity_log)
            activity_log.ObservingSpec = form.ObservingSpec.data
            activity_log.notes = form.activitynote.data
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            return redirect(url_for('currentlog'))

        #failure log
        if form.prog.data == 'Failure Log':
            failureprogdate = form.progfail.data + today
            failure_log = db.session.scalar(
                sa.select(FailureLog).where(FailureLog.progdate == failureprogdate)
            )
            if failure_log is None:
                failure_log = FailureLog(progdate=failureprogdate, progfail=form.progfail.data, failuredate=date.today())
                db.session.add(failure_log)
            failure_log.instrument = form.instrumentfail.data
            failure_log.TI = form.TI.data
            failure_log.SHU = form.SHU.data
            failure_log.FAILSTART = form.failstart.data
            failure_log.FAILEND = form.failend.data
            failure_log.FAILDISC = form.failnote.data
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            return redirect(url_for('currentlog'))
            
        if form.prog.data == 'Weather':
            weather_log = db.session.scalar(
                sa.select(WeatherLog).where(WeatherLog.weatherdate == date.today())
            )
            if weather_log is None:
                weather_log = WeatherLog(weatherdate=date.today())
                db.session.add(weather_log)
            weather_log.weatherfield = form.weatherfield.data
            weather_log.notes = form.weathernote.data
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            return redirect(url_for('currentlog'))
            
        if form.prog.data == 'Focus Log':
            focus_log = db.session.scalar(
                sa.select(FocusLog).where(FocusLog.focusdate == date.today())
            )
            if focus_log is None:
                focus_log = FocusLog(focusdate=date.today())
                db.session.add(focus_log)
            focus_log.focustext = form.focuslog.data
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            return redirect(url_for('currentlog'))
        
        if form.prog.data == 'Telescope Software':
            telescope_software_log = db.session.scalar(
                sa.select(TelescopeSoftwareLog).where(TelescopeSoftwareLog.telescopemodeldate == date.today()
            ))
            if telescope_software_log is None:
                telescope_software_log = TelescopeSoftwareLog(dateprog=dateprog)
                db.session.add(telescope_software_log)
            telescope_software_log.tccversion = form.tccversion.data
            telescope_software_log.hubversion = form.hubversion.data
            telescope_software_log.tuiversion = form.tuiversion.data
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            return redirect(url_for('currentlog'))
        
        else:
            log = db.session.scalar(
            sa.select(Obslog).where(Obslog.dateprog == dateprog)
            )
            #create a new log if it doesn't exist
            if log is None:
                log = Obslog(dateprog=dateprog,obsdate=date.today(),prog=form.prog.data)
                db.session.add(log)
                
            log.instrument = form.Instrument.data
            log.PIObs = form.PIAstro.data
            log.Obs = form.Observer.data
            log.starttime = form.start_time.data
            log.endtime = form.end_time.data
            
            #do the same for Proglog
            proglog = db.session.scalar(
                sa.select(Proglog).where(Proglog.dateprog == dateprog)
            )
            if proglog is None:
                newproglog = Proglog(
                    dateprog=dateprog,
                    progid =form.prog.data,
                )
                db.session.add(newproglog)
                
            proglog.progloc=form.progrow.data,
            proglog.progdtn=form.progdtn.data,
            proglog.schedstart = None,
            proglog.schedend = None,
            proglog.weatherd=form.weatherdark.data,
            proglog.weatherb=form.weatherbright.data,
            proglog.equipd=form.equipmentdark.data,
            proglog.equipb=form.equipmentbright.data,
            proglog.obsd=form.obsdark.data,
            proglog.obsb=form.obsbright.data,
            proglog.notusedd=form.notuseddark.data,
            proglog.notusedb=form.notusedbright.data,
            proglog.note=form.notes.data
        
        
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            return redirect(url_for('currentlog'))
    return render_template('currentlog.html', title='Current Log', form=form)

@app.get("/obslog/prefill/<string:prog_value>")
def obslog_prefill(prog_value):
    valid_values = [prog for prog, _ in CurrentLog().get_today_progs()]
    if prog_value not in valid_values and prog_value.lower() not in ['activity', 'failure log', 'focus log', 'weather', 'telescope software']:
        return jsonify({"prefill": {}, "rules": {"show": [], "required_fields": []}}), 404
    return jsonify(prefill(prog_value))
    
