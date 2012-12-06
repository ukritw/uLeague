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

def teststar():
    return dict(text="dfgdsfg")
def index():
    text = "index"
    return dict(text=text)

from array import *

@auth.requires_login() 
def home():
    user_participations = db((db.participation.person == auth.user_id) & (db.participation.status != 'Declined')).select(db.participation.ALL)
    #pagination
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=2
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    #events = db(db.event.sport == sports_id ).select(db.event.ALL,orderby = db.event.date_time,limitby=limitby)
    #events = array('I', [])

    #for user_participation in user_participations:
    #    events.append(user_participation.event)
        
    events = db((db.event.id == db.participation.event) & (db.participation.person == auth.user_id)).select(db.event.ALL,orderby = db.event.date_time,limitby=limitby)
    
    search_form = FORM(INPUT(_id='keyword',_name='keyword', _onkeyup="ajax('callback', ['keyword'], 'target');"))
    form=FORM(P('Search by sport:'), 
               INPUT(_id='sports_search', _name='sport'), 
               INPUT(_type='submit'))
    if form.accepts(request,session):
        response.flash = 'form accepted'
        session.sport = request.vars.sport
        redirect(URL('search_result', vars=dict(q=form.vars.sport)))
    return dict(user=auth.user, search_form=search_form, target_div=DIV(_id='target'), form=form, user_participations=user_participations, events=events, page=page, items_per_page=items_per_page)

def sports_complete():
    sports = db(db.sports_list.sport.startswith(request.vars.term)).select(db.sports_list.sport).as_list()
    sport_list = [s['sport'] for s in sports]
    import gluon.contrib.simplejson
    return gluon.contrib.simplejson.dumps(sport_list)

def search_result():
    query_string = request.vars.q or ''
    sports_id = db(db.sports_list.sport == query_string).select().first()
    #events = db(db.event.sport == sports_id ).select(db.event.ALL,orderby = db.event.date_time)
     
    # form=FORM( P('Search for sports:'), 
    #            INPUT(_id='no_table_name', _name='sport'), 
    #            INPUT(_type='submit'))
    form=FORM(P('Search by sport:'), 
               INPUT(_id='sports_search', _name='sport'), 
               INPUT(_type='submit'))
    if form.accepts(request,session):
        response.flash = 'form accepted'
        session.sport = request.vars.sport
        redirect(URL('search_result', vars=dict(q=form.vars.sport)))
    
    #search by event name
    search_form = FORM(INPUT(_id='keyword',_name='keyword', _onkeyup="ajax('callback', ['keyword'], 'target');"))
    
    #need to edit, not working 
    user = db.participation(person=auth.user_id,event=request.args(0))
    participation_form = SQLFORM(db.participation,user)
    if participation_form.process().accepted:
        response.flash = 'Participation changed'
    
    #pagination
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=3
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    events = db(db.event.sport == sports_id ).select(db.event.ALL,orderby = db.event.date_time,limitby=limitby)
    #rows=db().select(db.prime.ALL,limitby=limitby) 
    
    return dict(sports_id=sports_id, events=events, form=form ,participation_form=participation_form, target_div=DIV(_id='target'), page=page, items_per_page=items_per_page)

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
    delete_button = " "
    #if (db.event(request.args(0,cast=int)).host.id) == (auth.user_id):
    delete_button =  A('Delete', _href=URL('delete', args=[event_id]))
     
    #participants = db((db.participation.event==event_id) & (db.participation.person==auth.user_id)).select(db.participation.ALL)
    participants = db(db.participation.event == event_id).select(db.participation.ALL)
    user = db.participation(person=auth.user_id,event=request.args(0))
    
    # form = FORM('Participation:',
    #       SELECT('Accepted','Declined','Maybe',_name="participation"),
    #       INPUT(_type='submit'))
    #form = SQLFORM(db.participation,user)
    form = SQLFORM(db.participation, user)
    if form.process(session=None, formname='participationform').accepted:
        response.flash = 'Participation changed'
        redirect(URL('change_participation'))
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
    return dict(event=this_event, delete_button = delete_button, string = string, stringb=stringb, participants = participants,user=user, participation_form=participation_form )

def change_participation():
    #redirect(URL('home'))
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
     sportskill = db(db.sportskill.person == user).select(db.sportskill.ALL)
     return dict(user=user,sportskill=sportskill)
     
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
     
     if user.username != auth.user.username:
         redirect(URL('home'))
     
     sportskill = db.sportskill(request.args(1))
     
     form = FORM(TABLE(TR("Sure?",SELECT('Yes','No',_name="sure",requires=IS_IN_SET(['Yes','No']))),
                    TR("",INPUT(_type="submit",_value="SUBMIT"))))
                    
     if form.accepts(request,session):
         response.flash="form accepted"
         if form.vars.sure=='Yes':
             db(db.sportskill.id==request.args(1,cast=int)).delete()
             redirect(URL('userinfo',args=user.username))
         if form.vars.sure=='No':
             redirect(URL('userinfo',args=user.username))
     elif form.errors:
         response.flash="form is invalid"
     else:
         response.flash="please fill the form"
     return dict(user=user,sportskill=sportskill,form=form)

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
