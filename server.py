# -*- coding: utf-8 -*-
"""
    Doodle Meet
    ~~~~~~

    An application written with Flask to help users find friends interested in similar leisure actvities

    :copyright: (c) 2016 by Emily Hua and Dhruv Shekhawat.
"""

import os
import json
import flask
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import hashlib
import datetime
from sqlalchemy.exc import IntegrityError
#from sqlalchemy.dialects.postgresql import insert
from flask import Flask, Response, request, session, g, redirect, url_for, abort, \
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


@app.route('/show_activitylist/<name>')
def handler(name):
    act_dic = {'concerts':'1', 'dancing' : '2', 'art': '3', 'museums': '4', 'fishing':'7', 'kayaking':'8', 'pets' : '6', "water_sports":'10', "clubing": "11", "sailing" : "12", "broadwayshow" : "13"}
    text_dict = {'museums' : 'Museums provide places of relaxation and inspiration. And most importantly, they are a place of authenticity. We live in a world of reproductions - the objects in museums are real. It\'s a way to get away from the overload of digital technology.',
                 'dancing' : 'The energy you give off is the energy you receive. I really think that, so I\'m always myself - jumping, dancing, singing around, trying to cheer everybody up.',
                 'art' : 'The purpose of art is washing the dust of daily life off our souls.',
                 'concerts' : 'When you go to a great concert, you feel this arc, almost like the music of a well-chosen set takes you on this trip through emotions and through various forms of intellectual engagement.',
                 'fishing' : 'Fishing is much more than fish. It is the great occasion when we may return to the fine simplicity of our forefathers.',
                 'kayaking' : 'Kayaking is the use of a kayak for moving across water. It is distinguished from canoeing by the sitting position of the paddler and the number of blades on the paddle. A kayak is a low-to-the-water, canoe-like boat in which the paddler sits facing forward, legs in front, using a double-bladed paddle to pull front-to-back on one side and then the other in rotation.[1] Most kayaks have closed decks, although sit-on-top and inflatable kayaks are growing in popularity as well',
                 'pets' : 'Until one has loved an animal a part of one\'s soul remains unawakened.',
                 'sailing': 'Channel Bill Murray’s character from What About Bob? by shouting “I’m sailing!” and “Ahoy!” throughout your voyage. You’re guaranteed to make friends.',
                 'clubing' : 'I have Social Disease. I have to go out every night. If I stay home one night I start spreading rumours to my dogs.',
                 'broadwayshow' : 'Relax, just enjoy the show.'}
    quote_dict = {'museums' : "Thomas P. Campbell",
                  'dancing' : 'Cara Delevingne',
                 'art' : 'Pablo Picasso',
                 'concerts' : 'John Green',
                 'fishing' : 'Herbert Hoover',
                 'kayaking' : 'Wikipedia',
                 'pets' : 'Anatole France',
                 'sailing': 'timeout.com',
                 'clubing' : 'Andy Warhol',
                 'broadwayshow' : 'Ye Hua'
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

@app.route('/rating_display/<activity_subcategory>/<pid>/<aid>/<aaid>', methods = ['GET', 'POST'])
def rating_display(activity_subcategory, pid, aid, aaid):
    uid = session['uid']
    if (str(aid) == 'static'):
        return  ('', 204)
    avg_rating = g.conn.execute(text('SELECT AVG(score) FROM rate r JOIN friendship f ON \
    r.usr = f.friend WHERE f.usr = :uid AND pid = :pid AND activity_category = :aid AND activity_subcategory = :aaid;')
     ,uid = uid, pid = int(pid), aid = int(aid), aaid = int(aaid)).fetchall()
    entry_by_location = g.conn.execute(text('select * from location where pid = :pid and\
     aid = :aid and aaid = :aaid'), pid = int(pid), aid = int(aid), aaid = int(aaid)).fetchall()[0]
    rating_list = g.conn.execute(text('SELECT * FROM rate r JOIN friendship f ON r.usr = f.friend WHERE f.usr = :uid\
                     AND pid = :pid AND activity_category = :aid AND activity_subcategory = :aaid;'),
                                 uid = uid, pid = int(pid), aid = int(aid), aaid = int(aaid)).fetchall()
    friends_comment = [] #stores [firstname, lastname, comment, rating]
    for entry in rating_list:
        friend_name = g.conn.execute(text('SELECT firstname, lastname from users WHERE uid= :uid'), uid = int(entry[1])).fetchall()[0]
        friends_comment.append([friend_name[0], friend_name[1], entry[5], entry[6]])
    activity_category = g.conn.execute(text('select name from activitycategory where aid = :aid'), aid = int(aid)).fetchall()[0][0]
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
    
    #show routes about this place#
    routes = g.conn.execute(text('select route.name from route join modeoftransport on route.rid = modeoftransport.route_number \
                where pid=:pid and aid=:aid and aaid=:aaid;'), pid =int(pid), aid = int(aid), aaid =int(aaid)).fetchall()
    #show most fun routes about his place|activity
    most_fun_routes = g.conn.execute(text('SELECT a.n FROM (SELECT route_number, rt.name n, count(*) counts FROM \
                           ratefunroute r JOIN friendship f ON r.uid = f.friend JOIN route rt ON rt.rid = r.route_number \
                           WHERE f.usr = :uid AND pid = :pid AND aid = :aid AND aaid = :aaid GROUP BY route_number, rt.name ORDER BY counts desc \
                           limit 1)a ;'), uid = uid, pid = int(pid), aid = int(aid), aaid = int(aaid)).fetchall()
    if (len(most_fun_routes) == 0):
        most_fun_routes = "the potential routes to this places are"
    else:
        most_fun_routes = "the majority of your friends think {} is the most fun route, and the potential other routes are".format(most_fun_routes[0][0])
    print ("most_fun_routes: ", most_fun_routes)
    #get all possible routes in route table
    all_routes = g.conn.execute("SELECT rid, name FROM route").fetchall()
    if request.method == 'POST':
        info = None
        if request.method == 'POST':
            uid = session['uid']
            max_rid = g.conn.execute("SELECT max(rid) FROM ratefunroute").fetchall()[0][0]
            rid = max_rid + 1
            pid = request.form['pid']
            aid = request.form['aid']
            aaid = request.form['aaid']
            routeid = request.form['routeid']
            activity_subcategory = g.conn.execute(text('select name from activity where aid = :aid and aaid = :aaid'), aid = aid, aaid = aaid).fetchall()[0][0]
            activity_subcategory = str(activity_subcategory)
            route_exists = g.conn.execute(text("SELECT * FROM modeoftransport WHERE route_number = :routeid AND \
                                     pid = :pid AND aid = :aid AND aaid = :aaid"), routeid = routeid, pid = pid, aid = aid, aaid = aaid).fetchall()
            if len(route_exists) == 0:
                g.conn.execute(text('INSERT INTO modeoftransport (route_number, pid, aid, aaid) VALUES (:routeid, :pid, :aid, :aaid)'),routeid = routeid, pid = pid, aid = aid, aaid = aaid)
            g.conn.execute(text('INSERT INTO ratefunroute (rid, uid, pid, aid, aaid, route_number, score) VALUES (:rid, :uid, :pid, :aid, :aaid, :routeid, 1)'),
                rid = rid, uid = uid, pid = pid, aid = aid, aaid = aaid, routeid = routeid )
            info = "you just selected {} as the most fun route to this place".format(request.form['routename'])
            #get all possible routes in route table
            all_routes = g.conn.execute("SELECT rid, name FROM route").fetchall()
            routes = g.conn.execute(text('select route.name from route join modeoftransport on route.rid = modeoftransport.route_number \
                where pid=:pid and aid=:aid and aaid=:aaid;'), pid =int(pid), aid = int(aid), aaid =int(aaid)).fetchall()
            return render_template('show_ratings.html', 
    						pid = pid,
    						aid = aid,
    						aaid = aaid,
                            rating = avg_rating, 
                            entry_by_location  = entry_by_location, 
                            activity_subcategory = activity_subcategory, 
                            activity_category = activity_category,
                            friends_comment = friends_comment,
                            routes = routes,
                            most_fun_routes = most_fun_routes,
                            log_info = log_info,
                            all_routes = all_routes,
                            info = info)


    return render_template('show_ratings.html', 
    						pid = pid,
    						aid = aid,
    						aaid = aaid,
                            rating = avg_rating, 
                            entry_by_location  = entry_by_location, 
                            activity_subcategory = activity_subcategory, 
                            activity_category = activity_category,
                            friends_comment = friends_comment,
                            routes = routes,
                            most_fun_routes = most_fun_routes,
                            log_info = log_info,
                            all_routes = all_routes)

#, activity_subcategory = activity_subcategory, pid = pid, start_time = mynames[3], end_time = mynames[4], budget = pid)
@app.route('/loc_display/<name>')
def loc_display(name):
    location_table_keys = ["pid", 'aid', 'aaid', 'open_time', 'close_time', 'state', 'city', 'name']
    res = g.conn.execute(text("select aid, aaid from activity where name=:name"),name = name).fetchall()
    aid = res[0][0]
    aaid = res[0][1]
    activity_category =  g.conn.execute(text("select name from activitycategory where aid=:aid"), aid = aid).fetchall()[0][0]
    entry_by_location = g.conn.execute(text('select * from location where aid = :aid and aaid = :aaid'), aid = aid, aaid = aaid).fetchall()
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

@app.route('/added_time/<aid>/<aaid>/<pid>', methods=['POST','GET'])
def added_time(aid, aaid, pid):
    startdatetime = str(request.form['startdatetime'])
    print ("startdatetime: ", startdatetime)
    enddatetime = str(request.form['enddatetime'])
    print ("enddatetime: ", enddatetime)
    startdate_and_time=startdatetime.split('T')
    startdatetime=startdate_and_time[0]+ ' ' + startdate_and_time[1]
    enddate_and_time=enddatetime.split('T')
    enddatetime=enddate_and_time[0] + ' ' + enddate_and_time[1]
    budget=float(request.form['budget'])
    uid = session['uid']
    print "Reaching here!!"
    try:
    	entry_by_location = g.conn.execute(text("insert into interest(usr, activity_category, activity_subcategory, pid, start_time, end_time, budget) values (:uid, :activity_category, :activity_subcategory, :pid, :start_time, :end_time, :budget)"), uid = int(uid), activity_category = int(aid), activity_subcategory = int(aaid), pid = int(pid), start_time = datetime.datetime.strptime(startdatetime,"%Y-%m-%d %H:%M"), end_time = datetime.datetime.strptime(enddatetime,"%Y-%m-%d %H:%M"), budget = budget)
    except IntegrityError as e:
    	print "Oops! Value already in database"
    return redirect(url_for('display_interest_list'))

    
    

@app.route('/interests')
def display_interest_list():
    info = None
    if not session.get('logged_in'):
        abort(401)
    uid = session['uid']
    entry_by_location1 = g.conn.execute(text('select name, state, city, open_time, close_time, start_time, end_time, budget, location.aid, location.aaid, location.pid from location INNER JOIN interest on (location.pid = interest.pid and location.aid = interest.activity_category and location.aaid = interest.activity_subcategory) where usr = :uid'), uid = uid).fetchall()
    entry_by_location = []
    newentry = []
    for entry in entry_by_location1:
        newentry = []
        ticket_info = g.conn.execute(text('SELECT name, price, tid FROM ticketrequired WHERE pid = :pid AND aid = :aid AND aaid = :aaid'), pid = int(entry[10]), aid = int(entry[8]), aaid = int(entry[9])).fetchall()
        if len(ticket_info) == 0:
            ticket_info = []
        else:
            ticket_info = ticket_info
        for i in range (11):
            newentry.append(entry[i])
        newentry.append(ticket_info)
        entry_by_location.append(newentry)
    if len(entry_by_location) == 0:
        info = "you have nothing on your interest list yet!"
    return render_template('show_interest_list.html', 
                            mynames = entry_by_location, 
                            info = info
  )



@app.route('/add_comment/activity', methods=['POST','GET'])
def add_comment():
    error = None
    comment = request.form['comment']
    pid = int(request.form['pid'])
    aid = int(request.form['aid'])
    aaid = int(request.form['aaid'])
    activity_subcategory = g.conn.execute(text('select name from activity where aid = :aid and aaid = :aaid'), aid = aid, aaid = aaid).fetchall()[0][0]
    activity_subcategory = str(activity_subcategory)
    latest_rid = int(g.conn.execute('select max(rid) from rate').fetchall()[0][0])
    rid = latest_rid+1
    print ("comment: %s, pid: %s, aid: %s, aaid: %s"%(comment, pid, aid, aaid))

    uid = session['uid']
    score = request.form['rating']
    if int(score) == -1 and len(comment) != 0:
        query = 'INSERT INTO rate (rid, usr, activity_category,activity_subcategory, pid, comment)\
                VALUES (:rid, :uid, :aid, :aaid, :pid, :comment)'
        g.conn.execute(text(query), rid = rid , uid = uid,  aid = aid, aaid = aaid, pid = pid, comment = comment)
        score = str(score) +'/5'
    elif int(score) == -1 and len(comment) == 0: 
        comment = "Yo, you didn't enter any comment!"
        score = "Yo, you didn't enter any score!"
        error = "needs to enter at least a comment and/or rating in order to submit!"
    elif len(comment) == 0 and int(score) != -1:
        query = 'INSERT INTO rate (rid, usr, activity_category,activity_subcategory, pid, score)\
                VALUES (:rid, :uid, :aid, :aaid, :pid, :score)'
        g.conn.execute(text(query), rid = rid , uid = uid,  aid = aid, aaid = aaid, pid = pid, score = score)
        score = str(score) +'/5'
        comment = "Yo, you didn't enter any comment!"
    elif len(comment) != 0 and int(score) != -1:
         query = 'INSERT INTO rate (rid, usr, activity_category,activity_subcategory, pid, comment, score)\
                VALUES (:rid, :uid, :aid, :aaid, :pid, :comment, :score)'  
         g.conn.execute(text(query), rid = rid , uid = uid,  aid = aid, aaid = aaid, pid = pid, comment = comment, score = score)  
         score = str(score) +'/5'
    entry_by_location = g.conn.execute(text('select * from location where pid = :pid and aid = :aid and aaid = :aaid'), pid = int(pid), aid =int(aid), aaid = int(aaid)).fetchall()[0]
    activity_category =  g.conn.execute(text("select name from activitycategory where aid=:aid"), aid = aid).fetchall()[0][0]
    if (session['logged_in']):
        log_info = " Logout"
    else:
        log_info = " Login"
    return render_template('show_comment.html', 
                            entry_by_location  = entry_by_location, 
                            activity_subcategory = activity_subcategory, 
                            activity_category = activity_category,
                            new_comment = str(comment),
                            score = score,
                            log_info = log_info,
                            error = error)


@app.route("/rate_route", methods = ['GET', 'POST'])
def rate_route():
    info = None
    if request.method == 'POST':
        uid = session['uid']
        max_rid = g.conn.execute("SELECT max(rid) FROM ratefunroute").fetchall()[0][0]
        rid = max_rid + 1
        pid = request.form['pid']
        aid = request.form['aid']
        aaid = request.form['aaid']
        routeid = request.form['routeid']
        activity_subcategory = request.form['activity_subcategory']
        g.conn.execute(text('INSERT INTO ratefunroute (rid, uid, pid, aid, aaid, route_number, score) VALUES (:rid, :uid, :pid, :aid, :aaid, :routeid, 1)'),
                rid = rid, uid = uid, pid = pid, aid = aid, aaid = aaid, routeid = routeid )
        info = "Hey you just selected {} as the most fun route to this place".format(request.form['routename'])
        return redirect(url_for('rating_display(activity_subcategory, pid, aid, aaid)'))


@app.route('/deletefrom_interestlist')
def deletefrom_interestlist():
	uid=session['uid']
	activityID = request.args.get('query')
	activityID = str(activityID)
	words = activityID.split(" ")
	start_time_delete = words[3] + " " + words[4]
	end_time_delete = words[5] + " " + words[6]
	start_time_delete=start_time_delete[:-3]
	end_time_delete=end_time_delete[:-3]
	deleteentry = g.conn.execute(text("delete from interest where usr = :uid AND activity_category = :aid AND activity_subcategory = :aaid AND pid = :pid AND start_time = :start_time AND end_time = :end_time"), uid=int(uid), aid =int(words[0]), aaid= int(words[1]), pid=int(words[2]), start_time = datetime.datetime.strptime(start_time_delete,"%Y-%m-%d %H:%M"), end_time = datetime.datetime.strptime(end_time_delete,"%Y-%m-%d %H:%M"))
	success = ["Successfully deleted this entry"]
	return Response(json.dumps(success), mimetype='application/json')




@app.route('/find_activitygear')
def find_activitygear():
	activityID = request.args.get('query', 0, type = int)
	getgear= g.conn.execute(text('select g.name,s.name,s.city from gears g INNER JOIN gearstocarry gc ON g.gid=gc.gid INNER JOIN travelitemshop ts ON gc.gid=ts.gear INNER JOIN shops s ON s.sid=ts.sid where gc.aid=:activityID'), activityID = activityID).fetchall()
	x=[[] for i in range(len(getgear))]
	for i in getgear:
		for j in x:
			if not j:
				j.append(i[0])
				j.append(i[1] + ", " + i[2])
				break
			elif j[0] == i[0]:
				j.append(i[1] + ", " + i[2])
				break			
	gearData = [ a for a in x if a!=[]]
	return Response(json.dumps(gearData), mimetype='application/json')


@app.route('/find_activityfriends')
def find_activityfriends():
	uid = session['uid']
	activityID = request.args.get('query')
	activityID = str(activityID)
	words = activityID.split(" ")
	getfriends= g.conn.execute(text("select firstname, lastname FROM users u JOIN friendship f \
    on f.friend = u.uid JOIN interest i ON u.uid = i.usr WHERE  f.usr = :uid AND \
    activity_category = :aid AND activity_subcategory = :aaid AND pid = :pid AND \
    start_time::date = :start_time AND budget <= :budget + 10 AND budget >= :budget - 10 AND i.usr <> :uid"), aid = int(words[0]), aaid = int(words[1]), pid = int(words[2]), start_time = words[3], budget = words[5], uid = int(uid)).fetchall()
	l = []
	if len(getfriends)!=0:
		for i in getfriends:
			l.append(str(i[0]) + " " + str(i[1]))
	return Response(json.dumps(l), mimetype='application/json')
   

@app.route('/show_order_history', methods = ['GET', 'POST'])
def show_order_history(price = None):
    info = None
    noorderinfo = None
    uid = session['uid']
    if request.method == 'POST':
        price = request.form['price']
        fund = g.conn.execute(text('SELECT fund from users WHERE uid = :uid'), uid = uid).fetchall()[0][0]
        remain = float(fund) - float(price)
        if (remain > 0 ):
            tid = request.form['tid']
            info = "your successfully purchased the ticket, and your remaining budget is ${}".format(remain)
            g.conn.execute(text('UPDATE users SET fund =:fund WHERE uid = :uid'), fund = remain, uid = uid) 
            #add entry in order history!
            max_oid = g.conn.execute(text('SELECT max(oid) FROM orderhistory')).fetchall()[0][0]
            oid = max_oid + 1 
            cur_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            g.conn.execute(text('INSERT INTO orderhistory (oid, uid, tid, time) VALUES (:oid, :uid , :tid, :time)'), oid=oid, uid=uid, tid=tid, time =cur_time)           
        else: 
            info = "Sorry, you have insuffient budget for this purchase! The budget you have is ${}".format(float(fund))
        orderhistory = g.conn.execute(text('select l.name,  price, t.name, time FROM ticketrequired t JOIN\
                               location l ON t.pid = l.pid and t.aid = l.aid and t.aaid = l.aaid JOIN \
                               orderhistory o on t.tid = o.tid where o.uid= :uid; '), uid = uid).fetchall() 
        if (len(orderhistory) == 0):
            info = info + " you don't have any order history yet"
        return render_template("order_history.html", info = info, orderhistory = orderhistory)
    else: 
        fund = g.conn.execute(text('SELECT fund from users WHERE uid = :uid'), uid = uid).fetchall()[0][0]
        if (fund == None):
            info = "you don't have any fund on this website"
        else: 
            info = "Your remaining budget is ${}\n".format(float(fund))
        orderhistory = g.conn.execute(text('select l.name,  price, t.name, time FROM ticketrequired t JOIN\
                               location l ON t.pid = l.pid and t.aid = l.aid and t.aaid = l.aaid JOIN \
                               orderhistory o on t.tid = o.tid where o.uid= :uid; '), uid = uid).fetchall() 
        if (len(orderhistory) == 0):
            noorderinfo =  " you don't have any order history yet ;)"
        
        return render_template("order_history.html", info = info, noorderinfo = noorderinfo, orderhistory = orderhistory)

@app.route('/add_friends', methods = ['POST', 'GET'])
def add_friends(): 
    error = None
    info = None
    if request.method == 'POST':
        userid = session['uid']
        friendid = int(request.form['uid'])
        #check if they are already friends!
        friendship_exists =  g.conn.execute(text('SELECT * FROM friendship WHERE usr = :uid and friend = :friend'),  uid = userid, friend = friendid).fetchall()
        if len(friendship_exists) != 0:
            error = "Sorry, looks like this person is already your friend"
            print (error)
        else:
            max_fid = g.conn.execute("SELECT max(fid) FROM friendship").fetchall()[0][0]
            fid = max_fid+1
            g.conn.execute(text('INSERT INTO friendship (fid, usr, friend) VALUES (:fid, :uid, :friendid)'), fid = fid, uid = userid, friendid = friendid)
            fullname = g.conn.execute(text("select firstname, lastname from users where uid = :uid"), uid = friendid ).fetchall()[0]
            info = "Successfully added {} {} to your friend list! ".format(fullname[0], fullname[1])
    return render_template('search_friends.html', info = info, error = error)


@app.route('/search_friends', methods=['POST', 'GET'])
def search_friends():
    error = None
    if request.method == 'POST':
        f_firstname = str(request.form['firstname'])
        f_lastname = str(request.form['lastname'])
        if (len(f_firstname) == 0 or len(f_lastname)) == 0:
            error = "Sorry, you have to know the full name of your friends"
            print (error)
        else:
            f_firstname = f_firstname.capitalize()
            f_lastname = f_lastname.capitalize()
            print ("firstname: ", f_firstname)
            print ("lastname: ", f_lastname)
            fullnames = g.conn.execute(text('SELECT firstname, lastname, gender, age, uid FROM users WHERE firstname = :firstname and lastname = :lastname'), firstname = f_firstname, lastname = f_lastname).fetchall()
            print ("in serach friends: ", fullnames)
            if len(fullnames) == 0:
                error = "Sorry, {} {} is not registered on Doodle Meet yet!".format(f_firstname, f_lastname)
                print ("in serach friends: ", fullnames)
            else:
                fullnames = fullnames
                print (fullnames)
                return render_template('add_friends.html', fullnames = fullnames)
    return render_template('search_friends.html', error = error)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username =  g.conn.execute(text("select username from users where username = :username"), username = request.form['username'] ).fetchall()
        password = g.conn.execute(text("select password from users where username = :username"), username = request.form['username'] ).fetchall()
        hashed_password = hashlib.md5(str(request.form['password'])).hexdigest()
        
        if len(username) == 0:
            error = 'Invalid username'
        else:
            #there is this user but the password does not match
            password = password[0][0]
            if hashed_password != password:
                error = 'Invalid password'
            else: #there is a user and matching password
                username = username[0][0]
                session['logged_in'] = True
                #flash('You were logged in')
                uid = g.conn.execute(text("select uid from users where username = :username"), username = username ).fetchall()[0][0]
                session['uid'] = uid
                return redirect(url_for('show_entries'))
    return render_template('login.html', error = error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    #flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/enter_user_info', methods = ['GET', 'POST'])
def enter_user_info(): 
    error = None
    uid = session['uid']
    if request.method == 'POST':
        firstname = str(request.form['firstname']).capitalize()
        lastname = str(request.form['lastname']).capitalize()
        gender = str(request.form['gender'])
        age = str(request.form['age'])
        fund = str(request.form['fund'])
        if len(firstname) == 0:
            error = "please enter firstname"
        elif len(lastname) == 0:
            error = "please enter lastname"
        elif len(age) == 0:
            error = "please enter age"
        elif len(gender) == 0:
            error = "please enter gender"
        elif len(fund) == 0:
            error = "please enter fund"
        else:
            g.conn.execute(text("UPDATE users SET firstname = :firstname, lastname = :lastname, gender = :gender, age = :age, fund = :fund WHERE uid = \
            :uid"), firstname = firstname, lastname = lastname, age = age, gender = gender, fund = fund, uid = uid)
            return redirect(url_for('search_friends'))
    #display the form for users to enter their information
    firstname1 = g.conn.execute(text("SELECT firstname from users WHERE uid = :uid"), uid = uid).fetchall()
    lastname1 = g.conn.execute(text("SELECT lastname from users WHERE uid = :uid"), uid = uid).fetchall()
    age1 = g.conn.execute(text("SELECT age from users WHERE uid = :uid"), uid = uid).fetchall()
    gender1 = g.conn.execute(text("SELECT gender from users WHERE uid = :uid"), uid = uid).fetchall()
    fund1 = g.conn.execute(text("SELECT fund from users WHERE uid = :uid"), uid = uid).fetchall()
    if (firstname1[0][0] == None):
        firstname1 = "Jane"
    else:
        firstname1 = firstname1[0][0]
    if (lastname1[0][0] == None ):
        lastname1 = "Doe"
    else:
        lastname1 = lastname1[0][0]   
    if (age1[0][0] == None):
        age1 = "25" 
    else:
        age1 = age1[0][0]
    if (gender1[0][0] == None):
        gender1 = "female"
    else:
        gender1= gender1[0][0]
    if (fund1[0][0] == None):
        fund1 = "100"
    else:
        fund1= fund1[0][0]    
    return render_template("enter_user_info.html", 
                                error = error,
                                firstname = firstname1,
                                lastname = lastname1,
                                age = age1,
                                gender = gender1,
                                fund = fund1)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        hashed_password = hashlib.md5(str(request.form['password'])).hexdigest()
        #see if the username is already registered 
        username_exists = g.conn.execute(text("select username from users where username = :username"), username = username).fetchall()
        if len(username_exists) != 0:
            error = "username already exists, please be creative and come up with a new one ;)"
        else: #insert username and password into the users table 
            max_uid = g.conn.execute(text("select max(uid) from users")).fetchall()[0][0]
            g.conn.execute(text('INSERT INTO users(uid, username, password)\
                VALUES (:uid, :username, :password)'), uid = max_uid+1, username = username, password = hashed_password)
            session['logged_in'] = True
            session['uid'] = max_uid + 1
            return redirect(url_for('enter_user_info'))
    return render_template('signup.html', error = error)
    
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