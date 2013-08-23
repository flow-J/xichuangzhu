#-*- coding: UTF-8 -*-
import sys
sys.path.append('/var/www/flaskconfig/xichuangzhu')
import config
import MySQLdb
import MySQLdb.cursors
from flask import Flask, session, g, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

# convert python's encoding to utf8
reload(sys)
sys.setdefaultencoding('utf8')

# app
app = Flask(__name__)
app.config.update(
    SECRET_KEY=config.SECRET_KEY,
    SESSION_COOKIE_NAME=config.SESSION_COOKIE_NAME,
    PERMANENT_SESSION_LIFETIME=config.PERMANENT_SESSION_LIFETIME,
    DEBUG_TB_INTERCEPT_REDIRECTS=False,
    DEBUG=config.DEBUG
)

# Debug toolbar
if app.debug:
    toolbar = DebugToolbarExtension(app)

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:xiaowangzi@localhost/xcz'
db = SQLAlchemy(app)

# inject vars into template context
@app.context_processor
def inject_vars():
    return dict(
        douban_login_url = config.DOUBAN_LOGIN_URL, # douban oauth url
        admin_id = config.ADMIN_ID, # admin id
    )    

# url generator for pagination
def url_for_other_page(page):
    view_args = request.view_args.copy()
    args = request.args.copy()
    args['page'] = page
    view_args.update(args)
    return url_for(request.endpoint, **view_args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

# before every request
@app.before_request
def before_request():
    g.user_id =  session['user_id'] if 'user_id' in session else None
    g.conn = MySQLdb.connect(host=config.DB_HOST, user=config.DB_USER, passwd=config.DB_PASSWD, db=config.DB_NAME, use_unicode=True, charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
    g.cursor = g.conn.cursor()

# after every request
@app.teardown_request
def teardown_request(exception):
    g.conn.close()

import log
import controllers
import models