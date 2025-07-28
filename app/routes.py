from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, CurrentLog, RegistrationForm
import sqlalchemy as sa
#remove below
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from urllib.parse import urlsplit


@app.route('/') 
@app.route('/home')
@login_required #remove if login not needed
def home():
    return render_template('home.html', title='Home')

@app.route('/prevlogs')
def prevlogs():
    user = {'username': 'span'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('prevlogs.html', title='Previous Logs', posts=posts)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: #checks if the user is already logged in
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar( #checks the db for a user with the given username, if found, returns the user object else none
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) #logs the user in, sets current_user to the logged-in user
        next_page = request.args.get('next') #gets the next page to redirect to after login
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/currentlog', methods=['GET', 'POST'])
@login_required #remove if login not needed
def currentlog():
    form = CurrentLog()
    return render_template('currentlog.html', title='Current Log', form=form)


