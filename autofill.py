from urllib.request import urlopen
from lxml import html
import schedule
from datetime import datetime, date
import sqlalchemy as sa
import pandas
from app import app,db
from app.models import Obslog, Proglog
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

INSTRUMENTS = {'A': 'APOLLO', 'E': 'Echelle', 'EK': 'EK', 'EKR': 'EKR', 'K':'KOSMOS',
               'K(D)':'K(D)', 'K(R)':'K(R)', 'N':'NIC-FPS','R':'ARCTIC','R(K)':'R(K)',
               'T':'TripleSpec', 'V':'VS', 'X':'X',}


def web_crawl_and_fill():
    #first, get the current date
    today = datetime.now()
    #format the date to match the URL format
    date_str = today.strftime('%Y-%m-%d')
    #date_str = '2025-08-01'
    #construct the URL
    url = f'http://35m-schedule.apo.nmsu.edu/2025-08-01.1/html/days/{date_str}.html'
    page = urlopen(url)
    htmlbites = page.read().decode('utf-8')
    tree = html.fromstring(htmlbites)
    link_trees = tree.xpath('//a/text()')
    other_tree = tree.xpath('//td/text()')

    #get the index of A\n
    index_a = other_tree.index("A\n ")
    other_tree = other_tree[index_a:]
    #split it into chunks of 11
    other_tree = [other_tree[i:i + 12] for i in range(0, len(other_tree), 12)]
    link_trees = link_trees[3:]

    #convert to a pandas dataframe, with the columns being link tree
    df = pandas.DataFrame(other_tree)
    #strip all the whitespace from the dataframe
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    #add link_tree's elements into column 1 
    df[1] = link_trees
    #if there are two elements with the same program, remove the second one, and make it's end time the end time of the next program
    df = df.groupby(1, as_index=False).agg({0:'first',2:'max',3:'max',4:'first',5:'first',6:'first',
                                            7:'first',8:'first',9:'first',10:'first',11:'first'}) #both set to max due to 24 hr time
    #rename the columns
    return (df)


def fill_db():
    print('Running!')
    with app.app_context():
        df = web_crawl_and_fill()
        #get the current date
        today = date.today().strftime("%y%m%d")  # Get today's date in YYMMDD format
        #iterate through the dataframe and fill the db
        for index, row in df.iterrows():
            if row[1] not in [None, ''] and row[1].lower() != 'open':
                #create a dateprog string
                dateprog = row[1] + today
                #check if the log already exists
                log = db.session.scalar(
                    sa.select(Obslog).where(Obslog.dateprog == dateprog)
                )
                if row[5] in INSTRUMENTS:
                    instrument_mapping = INSTRUMENTS[row[5]]
                else:
                    instrument_mapping = None
                if log is None:
                    #create a new log
                    newlog = Obslog(
                        dateprog=dateprog,
                        obsdate=date.today(),
                        prog=row[1],
                        instrument=instrument_mapping,  # Use the instrument mapping
                        PIObs=None,
                        Obs=None,
                        starttime=row[2],
                        endtime=row[3]
                    )
                    db.session.add(newlog)

                #do the same for Proglog
                proglog = db.session.scalar(
                    sa.select(Proglog).where(Proglog.dateprog == dateprog)
                )
                if proglog is None:
                    new_proglog = Proglog(
                        dateprog=dateprog,
                        progid = row[1],
                        progloc=None,
                        progdtn=None,
                        schedstart = datetime.strptime(row[2], "%H:%M").time(),
                        schedend = datetime.strptime(row[3], "%H:%M").time(),
                        weatherd=None,
                        weatherb=None,
                        equipd=None,
                        equipb=None,
                        obsd=None,
                        obsb=None,
                        notusedd=None,
                        notusedb=None,
                        note=None
                    )
                    db.session.add(new_proglog)
        db.session.commit()
            

def sensor():
    """Function to run the sensor."""
    print("Sensor is running...")

# sched = BackgroundScheduler(daemon=True)
# sched.add_job(id='autofill',func=fill_db, trigger=CronTrigger(hour=16, minute=0, second=0, timezone='America/Denver'), replace_existing=True)
# sched.start()

