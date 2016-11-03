# -*- coding: utf-8 -*-
"""
    Doodle Meet
    ~~~~~~

    An application written with Flask to help users find friends interested in similar leisure actvities

    :copyright: (c) 2016 by Emily Hua and Dhruv Shekhawat.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
#from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

#connect to staff managed postgres
DATABASEURL = "postgresql://yh2901:sy38d@104.196.175.120/postgres"
engine = create_engine(DATABASEURL)
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'doodlemeet.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME1='dhruv',
    PASSWORD1='dhruv',
  	USERNAME2='emily',
    PASSWORD2='emily'
      
))
app.config.from_envvar('DOODLEMEET_SETTINGS', silent=True)

'''
def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
'''
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None
@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass   
'''
@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/getactivitylist')
def getactivitylist():
	print ("IN HERE----------------------------------------------------------") 
	db=get_db()
	cur=db.execute('select name from activity where aid=1')
	mynames=cur.fetchall()
	print (mynames)
	print ("JUST PRINT _----------------------------------------------")
	return render_template('show_list.html', mynames=mynames)

'''
@app.route('/getactivitylist', methods = ['post', 'get'])
def getactivitylist():
	print ("IN HERE----------------------------------------------------------") 
	print (g.conn)

	activitynames = g.conn.execute('select name from activity where aid=1').fetchall()
	print (activitynames)
	print ("JUST PRINT _----------------------------------------------")
	return render_template('show_list.html', mynames=activitynames)


@app.route('/show_entries')
def show_entries():
	return render_template('show_entries.html')


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME1'] and request.form['username'] != app.config['USERNAME2']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD1'] and request.form['password'] != app.config['PASSWORD2']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

'''
with app.app_context():
	init_db()
	db=get_db()
	db.execute('insert into activitycategory (aid,name) values (?, ?)', [1,"Hiking"])
	db.execute('insert into activitycategory (aid,name) values (?, ?)', [2,"Sailing"])
	db.execute('insert into activitycategory (aid,name) values (?, ?)', [3,"Fishing"])
	db.execute('insert into activity (aid,aaid,name) values (?, ?, ?)', [1,11,"Old Mountain Smith"])
	db.execute('insert into activity (aid,aaid,name) values (?, ?, ?)', [1,12,"Yosemite Sam Park"])
	db.execute('insert into activity (aid,aaid,name) values (?, ?, ?)', [1,13,"Grand Canyons National Park"])
	db.commit()
'''
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8080, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()