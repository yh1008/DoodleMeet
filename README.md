# DoodleMeet

Environment set up:

```
$ sudo apt-get install postgresql-9.3 postgresql-server-dev-9.3 python-virtulaenv python-dev python-pip
$ pip install flask psycopg2 sqlalchemy click
```

To run-  
(postgres version) First enter the Doodlemeet directory. The execute-
```
   $ python server.py

```

(sqlite version) First enter the Doodlemeet directory. The execute-
```
   $ export FLASK_APP=doodlemeet.py
   $ flask initdb
   $ export FLASK_DEBUG=1
   $ flask run
```  
   


Project Description

Our aim is to build a web application that allows users to find and meet
friends interested in similar kinds of activities as them. These activities can
include boating, sailing, fishing, eating, shopping, cycling, swimming,
going for a movie etc. The application facilitates the following features -

1. Users can select activities they are interested in from a comprehensive
list of activities. For e.g. she can choose going to GreatCroc Lake in
Bowie, Arizona for boating.  

2. After selecting the activity the users enter the date, time and the amount
they are willing to spend on these activities. This information will be
useful for finding friends who are interested in going to the same place at
the same time with a similar expected expenditure.
 
3. Users can read their friends comments and get ratings for the places they
are interested in based on the average of the scores their friends give to the
place. Furthermore they can also be advised about the 'most fun' route or
mode of transportation to reach their destination based on the data
submitted by their friends. For e.g. the most fun route to reach Yosemite
national park can be renting a car as opposed to taking a train/bus.
Similarly, most fun route to travel Central Park can be cycle. So we output
the max occurence of the fun routes voted by friends.

4. There exists a functionality to buy tickets which is a simple operation in
which the ticket price gets deducted from a users available funds.

5. Finally the user can be informed about the things to carry for his
activity. For e.g if hes interested in going boating then he would need items
such as flashlight, fishing rod, fishing net, bait, life jacket etc. If a user
does not possess any of these items then we also give him information
about shops close to him where he can buy these items from.

6. This is not a dating website!
