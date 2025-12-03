from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from app import app, db
from flask import Blueprint,render_template, flash, redirect, url_for, request, jsonify
from app.forms import CurrentLog, emailForm
import sqlalchemy as sa
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
#remove below
from app.models import Obslog, Proglog, ActivityLog, FailureLog, WeatherLog, TelescopeSoftwareLog, FocusLog
from urllib.parse import urlsplit
from app.email import send_preview
import math

#change the today, otherwise will reset and not work past 12 am every day

def hhmm(t):
    if t is None:
        return ''
    return f"{t.hour:02d}:{t.minute:02d}"
    
def default_times():
    now = datetime.now()
    start = now.replace(second=0, microsecond=0)
    end = (start + timedelta(hours=1))
    return start.strftime("%H:%M"), end.strftime("%H:%M")
    
def prefill_failure(program):
    today = date.today()
    latest = db.session.query(FailureLog).filter(FailureLog.progdate == program + today.strftime("%y%m%d")).first()
    return {
        'prefill': {
            'progfail': program,
            'instrumentfail': (latest.instrument if latest else '') or '',
            'TI': (latest.TI if latest else '') or '',
            'SHU': (latest.SHU if latest else '') or '',
            'failstart': (hhmm(latest.FAILSTART) if latest else default_times()[0]) or '',
            'failend': (hhmm(latest.FAILEND) if latest else default_times()[1]) or '',
            'failnote': (latest.FAILDISC if latest else '') or ''
        },
        "rules": {
            "show": ["progfail", "instrumentfail", "TI", "SHU", "failstart", "failend", "failnote"],
            "required_fields": ["progfail", "instrumentfail", "TI", "SHU", "failstart", "failend"]
        }
    }
    
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
            
        # if program == 'Failure Log':
        #     latest = db.session.query(FailureLog).filter(FailureLog.progdate == program + today.strftime("%y%m%d")).first()
        #     return {
        #         'prefill': {
        #             'instrumentfail': (latest.instrument if latest else '') or '',
        #             'TI': (latest.TI if latest else '') or '',
        #             'SHU': (latest.SHU if latest else '') or '',
        #             'failstart': (hhmm(latest.FAILSTART) if latest else default_times()[0]) or '',
        #             'failend': (hhmm(latest.FAILEND) if latest else default_times()[1]) or '',
        #             'failnote': (latest.FAILDISC if latest else '') or ''
        #         },
        #         "rules": {
        #             "show": ["progfail", "instrumentfail", "TI", "SHU", "failstart", "failend", "failnote"],
        #             "required_fields": ["progfail", "instrumentfail", "TI", "SHU", "failstart", "failend"]
        #         }
        #     }
            
        latest = db.session.query(Obslog).filter(Obslog.prog == program,Obslog.obsdate==today).first()
        latestprog = db.session.query(Proglog).filter(Proglog.progid == program, Proglog.dateprog.like('%'+today.strftime("%y%m%d"))).first()
        
        data = {
            'prog': program,
            'PIAstro': (latest.PIObs if latest else '') or '',
            'Observer': (latest.Obs if latest else '') or '',
            'Instrument': (latest.instrument if latest else '') or '',
            'start_time': (hhmm(latest.starttime) if latest else default_times()[0]) or '',
            'end_time': (hhmm(latest.endtime) if latest else default_times()[1]) or '',
            'progrow': (latestprog.progloc if latest else '') or '',
            'progdtn': (latestprog.progdtn if latest else '') or '',
            'weatherdark': (latestprog.weatherd if latest else '') or '',
            'weatherbright': (latestprog.weatherb if latest else '') or '',
            'equipmentdark': (latestprog.equipd if latest else '') or '',
            'equipmentbright': (latestprog.equipb if latest else '') or '',
            'obsdark': (latestprog.obsd if latest else '') or '',
            'obsbright': (latestprog.obsb if latest else '') or '',
            'notuseddark': (latestprog.notusedd if latest else '') or '',
            'notusedbright': (latestprog.notusedb if latest else '') or '',
            'notes': (latestprog.note if latest else '') or '' 
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

@app.route('/viewlog/<string:date>')
def viewlog(date):
    obslogs = db.session.query(Obslog).filter(Obslog.obsdate == date).all()
    proglogs = db.session.query(Proglog).filter(Proglog.dateprog.like('%'+date)).all()
    activity_log = db.session.query(ActivityLog).filter(ActivityLog.activitydate == date).first()
    failure_log = db.session.query(FailureLog).filter(FailureLog.failuredate == date).all()
    weather_log = db.session.query(WeatherLog).filter(WeatherLog.weatherdate == date).first()
    focus_log = db.session.query(FocusLog).filter(FocusLog.focusdate == date).first()
    telescope_software_log = db.session.query(TelescopeSoftwareLog).filter(TelescopeSoftwareLog.telescopemodeldate == date).first()
    return render_template('viewlog.html', title='View', 
                           date = date,
                           obslogs=obslogs,
                           proglogs=proglogs,
                           activity_log=activity_log,
                           failure_log=failure_log,
                           weather_log=weather_log,
                           focus_log=focus_log,
                           telescope_software_log=telescope_software_log)
    
    
@app.route('/prevlogs')
def prevlogs():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    base_query = db.session.query(Obslog.obsdate).distinct().order_by(Obslog.obsdate.desc())
    
    total_dates = db.session.query(func.count(func.distinct(Obslog.obsdate))).scalar()
    total_pages = math.ceil(total_dates / per_page) if total_dates else 1
    
    dates = (base_query
             .limit(per_page)
             .offset((page - 1) * per_page)
             .all()
            )
    
    return render_template('prevlogs.html', title='Previous Logs',dates=dates,total_pages=total_pages,page=page)

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    '''renders the preview page with today's log'''
    #grab the logs
    today = date.today()
    obslogs = db.session.query(Obslog).filter(Obslog.obsdate == today).all()
    proglogs = db.session.query(Proglog).filter(Proglog.dateprog.like('%'+today.strftime("%y%m%d"))).all()
    activity_log = db.session.query(ActivityLog).filter(ActivityLog.activitydate == today).first()
    failure_log = db.session.query(FailureLog).filter(FailureLog.failuredate == today).all()
    weather_log = db.session.query(WeatherLog).filter(WeatherLog.weatherdate == today).first()
    focus_log = db.session.query(FocusLog).filter(FocusLog.focusdate == today).first()
    telescope_software_log = db.session.query(TelescopeSoftwareLog).filter(TelescopeSoftwareLog.telescopemodeldate == today).first()
    form=emailForm()
    if form.validate_on_submit():
        print("Sending preview to %s" % form.email.data)
        flash('Preview sent to %s' % form.email.data)
        send_preview(form.email.data)
    else:
        print(form.email.data)
    return render_template('preview.html', title='Preview', 
                           date = date.today().strftime("%A, %B %d, %Y"),
                           obslogs=obslogs,
                           proglogs=proglogs,
                           activity_log=activity_log,
                           failure_log=failure_log,
                           weather_log=weather_log,
                           focus_log=focus_log,
                           telescope_software_log=telescope_software_log,
                           form=form)


@app.route('/currentlog', methods=['GET', 'POST'])
def currentlog():
    form = CurrentLog()
    form.prog.choices = form.get_today_progs() + [('Activity','Activity'),
                                                  ('Failure Log','Failure Log'),('Focus Log','Focus Log'),
                                                  ('Weather','Weather'),('Telescope Software','Telescope Software')] # Populate the program choices from the database
    form.progfail.choices = form.get_today_progs()  # Populate the program choices for failure log
    
    
    print(form.prog.data)
    if request.method == "POST" and form.prog.data != "Failure Log":
        info = prefill(form.prog.data)  # Get the program info based on the selected program
        if info:
            form._program_rules = info["rules"]
            
    elif request.method == "POST" and form.prog.data == "Failure Log":
        info = prefill_failure(form.progfail.data)
        if info:
            form._program_rules = info["rules"]
    
            
    if form.validate_on_submit():
        
        today = date.today().strftime("%y%m%d")  # Get today's date in YYMMDD format
        dateprog = form.prog.data + today
        print(form.prog.data)
        
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

        #failure log
        elif form.prog.data == 'Failure Log':
            failureprogdate = form.progfail.data + today
            failure_log = db.session.scalar(
                sa.select(FailureLog).where(FailureLog.progdate == failureprogdate)
            )
            if failure_log is None:
                failure_log = FailureLog(progdate=failureprogdate, prog=form.progfail.data, failuredate=date.today())
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
            
        elif form.prog.data == 'Weather':
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
            
        elif form.prog.data == 'Focus Log':
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
        
        elif form.prog.data == 'Telescope Software':
            telescope_software_log = db.session.scalar(
                sa.select(TelescopeSoftwareLog).where(TelescopeSoftwareLog.telescopemodeldate == date.today()
            ))
            if telescope_software_log is None:
                telescope_software_log = TelescopeSoftwareLog(telescopemodeldate=date.today())
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
            proglog.weatherd=(form.weatherdark.data if form.weatherdark.data != '' else 0) or 0,
            proglog.weatherb=(form.weatherbright.data if form.weatherbright.data != '' else 0) or 0,
            proglog.equipd=(form.equipmentdark.data if form.equipmentdark.data != '' else 0) or 0,
            proglog.equipb=(form.equipmentbright.data if form.equipmentbright.data != '' else 0) or 0,
            proglog.obsd=(form.obsdark.data if form.obsdark.data != '' else 0) or 0,
            proglog.obsb=(form.obsbright.data if form.obsbright.data != '' else 0) or 0,
            proglog.notusedd=(form.notuseddark.data if form.notuseddark.data != '' else 0) or 0,
            proglog.notusedb=(form.notusedbright.data if form.notusedbright.data != '' else 0) or 0,
            proglog.note=form.notes.data
        
        
            try:
                db.session.commit()
                flash(("Updated log for %s" % form.prog.data))
            except IntegrityError:
                db.session.rollback()
                flash('Log for today already exists. Please check the date and program.')
            flash('Log saved successfully!')
            
    return render_template('currentlog.html', title='Current Log', form=form)

@app.get("/obslog/prefill/<string:prog_value>")
def obslog_prefill(prog_value):
    valid_values = [prog for prog, _ in CurrentLog().get_today_progs()]
    if prog_value not in valid_values and prog_value.lower() not in ['activity', 'failure log', 'focus log', 'weather', 'telescope software']:
        return jsonify({"prefill": {}, "rules": {"show": [], "required_fields": []}}), 404
    return jsonify(prefill(prog_value))
    
@app.get("/obslog/prefill_failure/<string:prog_value>")
def obslog_prefill_failure(prog_value):
    valid_values = [prog for prog, _ in CurrentLog().get_today_progs()]
    if prog_value not in valid_values:
        return jsonify({"prefill": {}, "rules": {"show": [], "required_fields": []}}), 404
    data = prefill_failure(prog_value)
    return jsonify(prefill_failure(prog_value))