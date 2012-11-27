# coding: utf8
#IS_NOT_EMPTY() validator will be added to the fields later!
import datetime


#------------------------------------------------------------------------------------------------------------------------------------
# auth_user db plus added fields


auth = Auth(db)
auth.settings.extra_fields['auth_user']= [
    Field('gender', 'string'),
    Field('dob', 'date', default=datetime.date.today()+datetime.timedelta(days=-3650)),
    Field('phone_number', 'string'),    
    Field('profile_pic', 'upload'),
  ]
auth.define_tables(username=True, signature=False)

db.auth_user.gender.requires = IS_IN_SET(('Male','Female'), zero=T('Select your gender'), error_message='Select your gender')
db.auth_user.dob.requires = IS_DATE_IN_RANGE(format=T('%Y-%m-%d'), minimum=datetime.date.today()+datetime.timedelta(days=-36500), maximum=datetime.date.today()+datetime.timedelta(days=-3650), error_message='You must be at least 10, and younger than 100')
db.auth_user.phone_number.requires =  IS_MATCH('^1?((-)\d{3}-?|\(?\d{3}\)?)\d{3}-?\d{4}$', error_message='Invalid phone number')
db.auth_user.profile_pic.requires = IS_IMAGE(error_message='Invalid file type')


#------------------------------------------------------------------------------------------------------------------------------------
#sportskill table stores a person's skill in a sport  
db.define_table('sportskill',
    Field('sport', 'reference sports_list'), 
    Field('level', 'double'),
    Field('position', 'string', length=64),
    Field('person', 'reference auth_user'),
    )

sports = ['Basketball','Badminton','Soccer','Tennis']
# IS_LIST_OF(IS_IN_SET(....)) if you keep it as list:, but advice is not.
#db.sportskill.sport.requires = IS_IN_DB(db,db.sports_list.sport,'%(name)s')
db.sportskill.level.requires = [IS_FLOAT_IN_RANGE(0, 5), IS_IN_SET([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])]
db.sportskill.person.requires = IS_NOT_EMPTY()

#------------------------------------------------------------------------------------------------------------------------------------
#event table stores the information about each sporting event
db.define_table('event',
    Field('name', 'string', length=128),
    Field('sport', 'reference sports_list'),
    Field('date_time', 'datetime'),
    Field('location', 'string', length=256),
    Field('description', 'text', length=512),
    Field('posting_date', 'datetime', default=datetime.datetime.utcnow(), readable = False, writable = False),
    Field('host', 'reference auth_user', default=auth.user_id, readable = False, writable = False),
    Field('guest_list', 'list:reference auth_user'), # necessary?
    )

db.event.sport.requires = IS_IN_DB(db,'sports_list.id','%(sport)s')
db.event.date_time.requires = IS_DATE_IN_RANGE(format=T('%Y-%m-%d %H:%M:%S'), minimum=datetime.date.today(), maximum=datetime.date.today()+datetime.timedelta(days=365), error_message='Must be a date between now and a year')
#db.event.guest_list.requires = IS_IN_DB(db, 'person.user.first_name', '%(name)s', zero=T('choose one'))
    
#------------------------------------------------------------------------------------------------------------------------------------
#Participation table is for keeping track of the people invited to the event
db.define_table('participation',
    Field('person', 'reference auth_user'),
    Field('status', 'string'),
    Field('event', 'reference event'),
    )

# Invited, Declided, Accepted, Maybe, Owner
db.participation.status.requires = IS_IN_SET(('Invited', 'Declined', 'Accepted', 'Maybe', 'Host'),zero=T('choose one'))
db.participation.event.requires = IS_IN_DB(db, 'event.id', '%(name)s', zero=T('choose an event'))

#------------------------------------------------------------------------------------------------------------------------------------
#Sports_list table keeps the list of sport
db.define_table('sports_list',
    Field('sport', 'string'),
    )
