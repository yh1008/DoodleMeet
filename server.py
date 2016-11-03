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

@app.route('/concert', methods = ['post', 'get'])
def getconcert():
	print ("IN HERE----------------------------------------------------------") 
	activitynames = g.conn.execute('select name from activity where aid=1').fetchall()
	print (activitynames)
	print ("JUST PRINT ------------------------------------------------------")
	return render_template('show_list.html', mynames=activitynames)

@app.route('/dancing', methods = ['post', 'get'])
def getdancing():
	print ("IN HERE----------------------------------------------------------") 
	activitynames = g.conn.execute('select name from activity where aid=2').fetchall()
	print (activitynames)
	print ("JUST PRINT ------------------------------------------------------")
	return render_template('show_list.html', mynames=activitynames)

@app.route('/art', methods = ['post', 'get'])
def getart():
	print ("IN HERE----------------------------------------------------------") 
	activitynames = g.conn.execute('select name from activity where aid=3').fetchall()
	print (activitynames)
	print ("JUST PRINT ------------------------------------------------------")
	return render_template('show_list.html', mynames=activitynames)

@app.route('/museum', methods = ['post', 'get'])
def getmuseum():
	print ("IN HERE----------------------------------------------------------") 
	activitynames = g.conn.execute('select name from activity where aid=4').fetchall()
	print (activitynames)
	print ("JUST PRINT ------------------------------------------------------")
	return render_template('show_list.html', mynames=activitynames)

@app.route('/fishing', methods = ['post', 'get'])
def getfishing():
	print ("IN HERE----------------------------------------------------------") 
	activitynames = g.conn.execute('select name from activity where aid=7').fetchall()
	print (activitynames)
	print ("JUST PRINT ------------------------------------------------------")
	return render_template('show_list.html', mynames=activitynames)

@app.route('/kayaking', methods = ['post', 'get'])
def gethayaking():
	print ("IN HERE----------------------------------------------------------") 
	activitynames = g.conn.execute('select name from activity where aid=8').fetchall()
	print (activitynames)
	print ("JUST PRINT ------------------------------------------------------")
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
  @click.option('--debug', is_flag = True)
  @click.option('--threaded', is_flag = True)
  @click.argument('HOST', default = '0.0.0.0')
  @click.argument('PORT', default = 8080, type=int)
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