# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
from gluon.contrib.populate import populate
#populate(db.event,20)

def index():
    text = "index"
    return dict(text=text)

#from array import *

@auth.requires_login() 
def home():
    user_participations = db((db.participation.person == auth.user_id) & (db.participation.status != 'Declined')).select(db.participation.ALL)
    
    
    #pagination
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=4
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    events_count = db((db.event.id == db.participation.event) & (db.participation.person == auth.user_id)).count()/items_per_page
    events = db((db.event.id == db.participation.event) & (db.participation.person == auth.user_id)).select(db.event.ALL,orderby = db.event.date_time,limitby=limitby)

    #search_form = FORM(INPUT(_id='keyword',_name='keyword', _onkeyup="ajax('callback', ['keyword'], 'target');"))
    form=FORM(H5('Search for events:'), 
               SPAN(INPUT(_id='sports_search', _name='sport', _placeholder='Search events by sport'), 'or ',
                INPUT(_id='eventname-search', _name='event_name', _placeholder='Search events by name'),
                INPUT(_type='submit')), _class="navbar-form pull-left event-search")
    if form.accepts(request,session):
        response.flash = 'form accepted'
        session.sport = request.vars.sport
        redirect(URL('search_result', vars=dict(q=form.vars.sport, r=form.vars.event_name)))


    sportskills = db(db.sportskill.person == auth.user_id).select(db.sportskill.ALL)

    from array import *
    sportskill_list = array('I', [])
    for skill in sportskills:
        sportskill_list.append(skill.sport)
    #events recommendation
    recommended_events = db().select(db.event.ALL, orderby = db.event.date_time)

    return dict(user=auth.user, form=form, user_participations=user_participations, events=events, page=page, items_per_page=items_per_page, events_count=events_count, recommended_events=recommended_events,sportskill_list=sportskill_list)

def sports_complete():
    sports = db(db.sports_list.sport.startswith(request.vars.term)).select(db.sports_list.sport).as_list()
    sport_list = [s['sport'] for s in sports]
    import gluon.contrib.simplejson
    return gluon.contrib.simplejson.dumps(sport_list)

def eventname_complete():
    events = db(db.event.name.startswith(request.vars.term)).select(db.event.name).as_list()
    event_list = [s['name'] for s in events]
    import gluon.contrib.simplejson
    return gluon.contrib.simplejson.dumps(event_list)

def search_result():
    query_string = request.vars.q or ''
    query_eventname_string = request.vars.r or ''
    sports_id = db(db.sports_list.sport == query_string).select().first()

    form=FORM(H4('Search by sport:'), 
               INPUT(_id='sports_search', _name='sport', _placeholder=query_string), 
               INPUT(_type='submit'))
    if form.accepts(request,session):
        response.flash = 'form accepted'
        session.sport = request.vars.sport
        redirect(URL('search_result', vars=dict(q=form.vars.sport)))
    
    #pagination
    # if len(request.args): page=int(request.args[0])
    # else: page=0
    # items_per_page = 2
    # limitby=(page*items_per_page,(page+1)*items_per_page+1)


    import datetime
    if request.vars.r:
        events = db(db.event.name.contains(query_eventname_string)).select(db.event.ALL,orderby = db.event.date_time)
    else: 
        events = db((db.event.sport == sports_id) & (db.event.date_time >= datetime.datetime.utcnow())).select(db.event.ALL,orderby = db.event.date_time)

    return dict(sports_id=sports_id, events=events, form=form , query_string=query_string)

@auth.requires_login() 
def calendar():
    calendar_events = db((db.event.id == db.participation.event) & (db.participation.person == auth.user_id)).select(db.event.ALL)
    return dict(calendar_events=calendar_events)

def callback():
     "an ajax callback that returns a list of events by name to search_result"
     query = db.event.name.contains(request.vars.keyword)
     events = db(query).select(orderby=db.event.date_time)
     return dict(events=events)
     #links = [P(e.name) for e in events]
     #return UL(*links)
                      
@auth.requires_login() 
def create():
    form = SQLFORM(db.event)
    if form.process().accepted:
       session.event_name = request.vars.name
       event_id = db(db.event.name == request.vars.name).select().first()
       db.participation.insert(person = auth.user_id, status = 'Host', event = event_id)
       db.commit()
       response.flash = "Event Created"
       redirect(URL('home'))
    elif form.errors:
       response.flash = 'form has errors'
   
    return dict(form=form)


def event():
    this_event = db.event(request.args(0,cast=int)) or redirect(URL('home'))
    event_id = db.event(request.args(0,cast=int)).id
    comments = db((db.event.id == db.comments.event)).select(db.comments.ALL)
    delete_button = " "
    #if (db.event(request.args(0,cast=int)).host.id) == (auth.user_id):
    delete_button =  A('Delete', _href=URL('delete', args=[event_id]))
     
    #participants = db((db.participation.event==event_id) & (db.participation.person==auth.user_id)).select(db.participation.ALL)
    participants = db(db.participation.event == event_id).select(db.participation.ALL)
    user = db.participation(person=auth.user_id,event=request.args(0))
    
    #Setting the default value for participation changing form
    if user:
        if user.status == 'Accepted':
            participation_order_xml = '<option value="Accepted">Accepted</option><option value="Declined">Declined</option><option value="Maybe">Maybe</option>'
        elif user.status == 'Declined':
            participation_order_xml = '<option value="Declined">Declined</option><option value="Accepted">Accepted</option><option value="Maybe">Maybe</option>'
        else:
            participation_order_xml = '<option value="Maybe">Maybe</option><option value="Accepted">Accepted</option><option value="Declined">Declined</option>'
    else: 
        participation_order_xml =''
    select_participation_xml ='<select name="status">'+participation_order_xml+'</select>'
    form = FORM(XML(select_participation_xml),
          INPUT(_type='Submit', _class="fix-btn"), _class="event-btn")
    if form.process().accepted:
        response.flash = 'Participation changed'
        redirect(URL('change_participation', args=[event_id,request.vars.status]))
    elif form.errors:
        response.flash = 'form has errors'

    #else:
    # response.flash = 'please fill the form'
    
    participation_form = SQLFORM(db.participation,user, fields=['status'])
    if participation_form.process().accepted:
        response.flash = 'Participation changed'
        redirect(URL('event', args=event_id))
    
    string = db.event(request.args(0,cast=int)).host.id
    stringb = auth.user_id
    
    comment_form = SQLFORM(db.comments, fields=['comment'])
    comment_form.vars.author = auth.user.id
    comment_form.vars.event = event_id
    if comment_form.process().accepted:
        response.flash = 'comment made'
        redirect(URL('event', args=event_id))
        
    return dict(event=this_event, delete_button = delete_button, string = string, stringb=stringb, participants = participants,user=user, participation_form=participation_form, form=form, comments=comments, comment_form=comment_form)

def change_participation():
    db((db.participation.person == auth.user_id) & (db.participation.event == request.args[0])).update(status = request.args[1])
    db.commit()
    redirect(URL('event',args=request.args[0]))
    return ()
    
def delete():
    db(db.event.id == request.args[0]).delete()
    db.commit()
    session.flash = T('The event has been deleted')
    redirect(URL('/home'))
    return ()

@auth.requires_login() 
def join():
    db.participation.insert(person=request.args[1],status='Accepted',event=request.args[0])
    db.commit()
    session.flash = T('You have joined the event ' + db.event(request.args(0,cast=int)).name)
    redirect(URL('event',args=request.args[0]))
    return ()

def event_edit():
    event = db.event(request.args(0))
    form = SQLFORM(db.event,event)
    if form.process().accepted:
       response.flash = 'Event updated'
       redirect(URL('event',args=request.args[0]))
    elif form.errors:
       response.flash = 'Form has errors'
    else:
       response.flash = 'Please fill out the form'
    return dict(form=form)

@auth.requires_login()
def userinfo():
     user = db.auth_user(username=request.args(0))
     sportskill = db(db.sportskill.person == user).select(db.sportskill.ALL, orderby=~db.sportskill.level)
     events = db((db.event.id == db.participation.event) & (db.participation.person == auth.user_id)).select(db.event.ALL, orderby=db.event.date_time, limitby = (0,4))
     return dict(user=user,sportskill=sportskill, events=events)
     
def edit_skills():
     user = db.auth_user(username=request.args(0))
     sportskill = db.sportskill(id=request.args(1))
     
     if user.username != auth.user.username:
         redirect(URL('home'))
     
     sportskill = db.sportskill(request.args(1))
     form = SQLFORM(db.sportskill,sportskill)
                    
     if form.accepts(request,session):
         response.flash="form accepted"
         redirect(URL('userinfo',args=user.username))
     elif form.errors:
         response.flash="form is invalid"
     else:
         response.flash="please fill the form"
     return dict(user=user,sportskill=sportskill,form=form)
     
def delete_skills():
    user = db.auth_user(username=request.args(0))
    sportskill = db.sportskill(id=request.args(1))
     
    response.flash="form accepted"
    db(db.sportskill.id==request.args(1,cast=int)).delete()
    db.commit()
    redirect(URL('userinfo',args=user.username))

    return dict()

def delete_comments():
    event = db.event(id=request.args(0))
    coments = db.comments(id=request.args(1))
     
    response.flash="form accepted"
    db(db.comments.id==request.args(1,cast=int)).delete()
    db.commit()
    redirect(URL('event',args=event.id))

    return dict()

def add_skill():
     user = db.auth_user(username=request.args(0))
     #sportskill = db().select(db.sportskill.ALL)
     
     if user.username != auth.user.username:
         redirect(URL('home'))
         
     form=SQLFORM(db.sportskill)
                    
     if form.accepts(request,session):
         response.flash="form accepted"
         #db.sportskill.insert(person=user.id,sport=form.vars.sport,level=form.vars.level,position=form.vars.position)
         redirect(URL('userinfo',args=user.username))
         
     elif form.errors:
         response.flash="form is invalid"
         
     else:
         response.flash="please fill the form"
         
     return dict(user=user,form=form)
     
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
