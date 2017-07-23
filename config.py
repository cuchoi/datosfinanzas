WTF_CSRF_ENABLED = True
SECRET_KEY = 'juan-se-metio-en-la-baniera'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# GOOGLE_CLIENT_ID = '819755941536-r3eh2mk9p9d9kqepit95nbvdpaa06pd1.apps.googleusercontent.com'
# GOOGLE_CLIENT_SECRET = '5XjAnl9p3kwU6CgD6MUqZrrI'
# REDIRECT_URI = '/oauth2callback'

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['fernando.irarrazaval@gmail.com']
 

