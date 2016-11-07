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


@app.route('/<name>')
def handler(name):
    act_dic = {'concerts':'1', 'dancing' : '2', 'art': '3', 'museums': '4', 'fishing':'7', 'kayaking':'8', 'pets' : '6', "water_sports":'10', "clubing": "11", "sailing" : "12"}
    text_dict = {'museums' : 'Museums provide places of relaxation and inspiration. And most importantly, they are a place of authenticity. We live in a world of reproductions - the objects in museums are real. It\'s a way to get away from the overload of digital technology.',
                 'dancing' : 'The energy you give off is the energy you receive. I really think that, so I\'m always myself - jumping, dancing, singing around, trying to cheer everybody up.',
                 'art' : 'The purpose of art is washing the dust of daily life off our souls.',
                 'concerts' : 'When you go to a great concert, you feel this arc, almost like the music of a well-chosen set takes you on this trip through emotions and through various forms of intellectual engagement.',
                 'fishing' : 'Fishing is much more than fish. It is the great occasion when we may return to the fine simplicity of our forefathers.',
                 'kayaking' : 'Kayaking is the use of a kayak for moving across water. It is distinguished from canoeing by the sitting position of the paddler and the number of blades on the paddle. A kayak is a low-to-the-water, canoe-like boat in which the paddler sits facing forward, legs in front, using a double-bladed paddle to pull front-to-back on one side and then the other in rotation.[1] Most kayaks have closed decks, although sit-on-top and inflatable kayaks are growing in popularity as well',
                 'pets' : 'Until one has loved an animal a part of one\'s soul remains unawakened.',
                 'sailing': 'Channel Bill Murray’s character from What About Bob? by shouting “I’m sailing!” and “Ahoy!” throughout your voyage. You’re guaranteed to make friends.',
                 'clubing' : 'I have Social Disease. I have to go out every night. If I stay home one night I start spreading rumours to my dogs.'}
    quote_dict = {'museums' : "Thomas P. Campbell",
                  'dancing' : 'Cara Delevingne',
                 'art' : 'Pablo Picasso',
                 'concerts' : 'John Green',
                 'fishing' : 'Herbert Hoover',
                 'kayaking' : 'Wikipedia',
                 'pets' : 'Anatole France',
                 'sailing': 'timeout.com',
                 'clubing' : 'Andy Warhol'
                 }
    text = text_dict[name]
    quote = quote_dict[name]
    activity_sub_category = g.conn.execute('select name from activity where aid=' + act_dic[name]).fetchall()
    if (session['logged_in']):
        log_info = " Logout"
    else:
        log_info = " Login"
    return render_template('show_listv1.html',
                            mynames = activity_sub_category, 
                            name = name, 
                            text = text, 
                            quote = quote,
                            log_info = log_info)

@app.route('/getratings/<activity_subcategory>/<pid>/<aid>/<aaid>')
def rating_display(activity_subcategory, pid, aid, aaid):
    username_map = {"emily" : 1, "dhruv" : 8}
    uid = username_map[str(session['username'])]
    print ("user name: ", session['username'])
    print ("******************I am in rating_display *********************************")
    print ("pid,aid, aaid: ", pid, aid, aaid)
    if (str(aid) == 'static'):
        return  ('', 204)
    avg_rating = g.conn.execute('SELECT AVG(score) FROM rate r JOIN friendship f ON r.usr = f.friend WHERE f.usr = %d AND pid = %d AND activity_category = %d AND activity_subcategory = %d;'
                                 %(uid, int(pid), int(aid), int(aaid))).fetchall()
    entry_by_location = g.conn.execute('select * from location where pid = %d and aid = %d and aaid = %d '%(int(pid), int(aid), int(aaid))).fetchall()[0]
    rating_list = g.conn.execute('SELECT * FROM rate r JOIN friendship f ON r.usr = f.friend WHERE f.usr = %d AND pid = %d AND activity_category = %d AND activity_subcategory = %d;'
                                 %(uid, int(pid), int(aid), int(aaid))).fetchall()
    print ("whole list of rating: ", rating_list)
    friends_comment = [] #stores [firstname, lastname, comment, rating]
    for entry in rating_list:
        friend_name = g.conn.execute('SELECT firstname, lastname from users WHERE uid=%d'%int(entry[1])).fetchall()[0]
        friends_comment.append([friend_name[0], friend_name[1], entry[5], entry[6]])
    activity_category = g.conn.execute('select name from activitycategory where aid =%d'% int(aid)).fetchall()[0][0]
    print ("friends_comment: ", friends_comment) 
    print (" entry_by_location: ",  entry_by_location)
    print ("activity_category: ", activity_category)
    print ("avg rating: ", avg_rating)
    #handle no rating yet case
    if (avg_rating[0][0] == None):
        avg_rating = "no rating"
    else:
        avg_rating = int(avg_rating[0][0])
    #get logging info 
    if (session['logged_in']):
        log_info = " Logout"
    else:
        log_info = " Login"
    return render_template('show_ratings.html', 
                            rating = avg_rating, 
                            mynames = entry_by_location, 
                            activity_subcategory = activity_subcategory, 
                            activity_category = activity_category,
                            friends_comment = friends_comment,
                            log_info = log_info)

@app.route('/getloc/<name>')
def loc_display(name):
    print ("******************I am in loc_display *********************************")
    location_table_keys = ["pid", 'aid', 'aaid', 'open_time', 'close_time', 'state', 'city', 'name']
    res = g.conn.execute("select aid, aaid from activity where name='%s'"%name).fetchall()
    aid = res[0][0]
    aaid = res[0][1]
    activity_category =  g.conn.execute("select name from activitycategory where aid='%d'"%aid).fetchall()[0][0]
    print ("activity_category", activity_category)
    entry_by_location = g.conn.execute('select * from location where aid = %d and aaid = %d'%(aid,aaid)).fetchall()
    print (entry_by_location)
    if (session['logged_in']):
        log_info = " Logout"
    else:
        log_info = " Login"
    return render_template('show_locations.html', 
                            name = name, 
                            mynames = entry_by_location, 
                            activity_category = str(activity_category),
                            log_info = log_info)

@app.route('/show_entries')
def show_entries():
    if (session['logged_in']):
        log_info = " Logout"
    else:
        log_info = " Login"
    print ("logged in : ",session['logged_in'])
    return render_template('show_entriesv1.html', log_info = log_info)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entriesv1'))


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
            session['username'] = request.form['username']
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

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host = HOST, port = PORT, debug = debug, threaded = threaded,  use_reloader = False)


  run()