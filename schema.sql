drop table if exists users;
create table users(
    userid int primary key,
    firstname text,
    lastname text,
    fund numeric check (fund > 0) ,
    gender text,
    age int
);
drop table if exists friendship;
create table friendship(
    fid int primary key,
    usr int,
    friend int,
    foreign key (usr) references users(userid),
    foreign key (friend) references users(userid)
);
drop table if exists activitycategory;
create table activitycategory(
    aid int,
    name text,
    primary key(aid)
);
drop table if exists activity;
create table activity(
    aid int,
    aaid int,
    name text,
    primary key(aid, aaid),
    foreign key(aid) references activitycategory(aid)
);

drop table if exists interest;
create table interest(
    usr int,
    activity_category int,
    activity_subcategory int, 
    pid int,
    start_time timestamp,
    end_time timestamp,
    budget int check (budget >= 0),
    primary key (usr, activity_category, activity_subcategory, pid, start_time, end_time),
    foreign key (usr) references users(userid),
    foreign key(pid, activity_category, activity_subcategory) references location(pid, aid, aaid)
);

drop table if exists rate;
create table rate(
    rid int,
    usr int not null,
    activity_category int not null,
    activity_subcategory int not null,
    pid int,
    comment1 text,
    score int not null,
    primary key (rid),
    foreign key (usr) references users(userid),
    foreign key (pid, activity_category, activity_subcategory) references location(pid, aid, aaid)
);

drop table if exists location;
create table location(
    pid int, --"think of pid as Arizona State Park"
    aid int, --"climbing"
    aaid int, --"rock climbing"
    open_time timestamp,
    close_time timestamp,
    state text,
    city text,
    name text,
    primary key(pid, aid, aaid),
    foreign key(aid, aaid) references activity(aid, aaid)
    --"pid, aid, aaid uniquely identifies an activity"
);

drop table if exists ticketrequired;
create table ticketrequired(
    tid int,
    pid int,
    aid int,
    aaid int, 
    price numeric check (price >= 0),
    name text,
    primary key (tid),
    foreign key(pid, aid, aaid) references location(pid, aid, aaid) on delete CASCADE
);
drop table if exists modeoftransport;
create table modeoftransport (
    route_number int,
    pid int,
    aid int,
    aaid int,
    primary key(route_number, pid, aid, aaid),
    foreign key(pid, aid, aaid) references location(pid, aid, aaid)
);
drop table if exists ratefunroute;
create table ratefunroute(
    rid int,
    usr int,
    pid int, 
    aid int,
    aaid int,
    route_number int,
    score int check (score = 1), --"constrained on only 1! as the indicator of it being chosen!"
    primary key(rid),
    foreign key(usr) references users(userid),
    foreign key (route_number, pid, aid, aaid) references modeoftransport(route_number, pid, aid, aaid)
);
drop table if exists route;
create table route(
    rid int,
    name text,
    primary key(rid)
);
drop table if exists orderhistory;
create table orderhistory(
    oid int,
    usr int,
    tid int,
    time timestamp, 
    primary key (oid),
    foreign key (usr) references users(userid),
    foreign key(tid) references ticketrequired(tid)
    
);
drop table if exists gearstocarry;
create table gearstocarry(
    gid int,
    aid int,
    primary key(gid, aid),
    foreign key (aid) references activitycategory(aid)
);
drop table if exists gears;
create table gears(
    gid int,
    name text,
    primary key(gid)
);
drop table if exists shops;
create table shops (
    sid int,
    name text not null,
    city text not null,
    primary key(sid)
);
drop table if exists travelitemshop;
create table travelitemshop (
    sid int,
    gear int,
    price numeric check(price >= 0),
    primary key(sid, gear),
    foreign key (sid) references shops(sid),
    foreign key (gear) references gears(gid)
);
