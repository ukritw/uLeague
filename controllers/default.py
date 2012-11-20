# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    text = "index"
    return dict(text=text)
    
@auth.requires_login() 
def home():
    event = db(db.event).select(db.event.ALL)
    search_form = FORM(INPUT(_id='keyword',_name='keyword', _onkeyup="ajax('callback', ['keyword'], 'target');"))
    return dict(event=event, user=auth.user, search_form=search_form, target_div=DIV(_id='target'))

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
     return dict(event=this_event)

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
