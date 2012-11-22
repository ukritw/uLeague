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
   
@auth.requires_login() 
def home():
    event = db(db.event).select(db.event.ALL)
    search_form = FORM(INPUT(_id='keyword',_name='keyword', _onkeyup="ajax('callback', ['keyword'], 'target');"))
    form=FORM('Search for sports:', 
               INPUT(_name='sport'), 
               INPUT(_type='submit'))
    if form.accepts(request,session):
        response.flash = 'form accepted'
        session.sport = request.vars.sport
        redirect(URL('search_result'))
    return dict(event=event, user=auth.user, search_form=search_form, target_div=DIV(_id='target'), form=form)

def list_states():
    states = db(db.sports_list.sport.startswith(request.vars.name)).select().as_list()
    return dict(states=states)

def states_complete():
    states = db(db.sports_list.sport.startswith(request.vars.term)).select(db.sports_list.sport).as_list()
    logger.info("The list is: " + str(states))
    state_list = [s['name'] for s in states]
    import gluon.contrib.simplejson
    return gluon.contrib.simplejson.dumps(state_list)

def month_selector():
    if not request.vars.month:
        return ''
    pattern = request.vars.month.capitalize() + '%'
    selected = [row.sport for row in db(db.sports_list.sport.like(pattern)).select()]
    return ''.join([DIV(k,
                 _onclick="jQuery('#month').val('%s')" % k,
                 _onmouseover="this.style.backgroundColor='yellow'",
                 _onmouseout="this.style.backgroundColor='white'"
                 ).xml() for k in selected])
                     
def search_result():
    sports_id = db(db.sports_list.sport == session.sport).select().first()
    events = db(db.event.sport == sports_id ).select(db.event.ALL,orderby = db.event.date_time)
 
    #needs to be implement with ajax w/o page refresh and autocomplete
    form=FORM('Search for sports:', 
               INPUT(_name='sport'), 
               INPUT(_type='submit'))
    if form.accepts(request,session):
        response.flash = 'form accepted'
        session.sport = request.vars.sport
        redirect(URL('search_result'))
    
     #need to edit, not working 
    user = db.participation(person=auth.user_id,event=request.args(0))
    participation_form = SQLFORM(db.participation,user)
    if participation_form.process().accepted:
        response.flash = 'Participation changed'
    return dict(sports_id=sports_id, events=events, form=form, participation_form=participation_form)
                     
@auth.requires_login() 
def create():
    form = SQLFORM(db.event)
    if form.process().accepted:
       response.flash = 'form accepted'
       redirect(URL('home'))
    elif form.errors:
       response.flash = 'form has errors'
    else:
       response.flash = 'please fill out the form'
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
     form = SQLFORM(db.participation,user)
     if form.process().accepted:
       response.flash = 'Participation changed'
       
     string = db.event(request.args(0,cast=int)).host.id
     stringb = auth.user_id
     return dict(event=this_event, delete_button = delete_button, string = string, stringb=stringb, participants = participants,user=user, form=form)


def delete():
    db(db.event.id == request.args[0]).delete()
    db.commit()
    session.flash = T('The event has been deleted')
    redirect(URL('home'))
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
    
def userinfo():
     user = db.auth_user(username=request.args(0)) or redirect(URL('error'))
     return dict(user=user)
     
def callback():
     "an ajax callback that returns a <ul> of links to wiki pages"
     query = db.event.name.contains(request.vars.keyword)
     events = db(query).select(orderby=db.event.name)
     links = [A(e.name, _href=URL('event',args=e.id)) for e in events]
     return UL(*links)

     
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
