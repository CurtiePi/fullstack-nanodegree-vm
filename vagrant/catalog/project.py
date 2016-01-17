from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# Constants used for uploading an image
IMAGE_FOLDER="static/images/"
DEFAULT_IMAGE="default/NoPicAvailable.png"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Equipment, User

#More imports to help with session handling
from flask import session as login_session
import random, string

# Will allow a flow object from clientsecrets JSON file
# which stores client id, client secret and other oauth2 params

from oauth2client.client import flow_from_clientsecrets

#Used to catch errors when exchanging auth code for access token

from oauth2client.client import FlowExchangeError

import httplib2
import json
import os
import re

#Converts return value from function to response object
from flask import make_response
import requests

CLIENT_ID = json.loads(  \
     open('client_secrets.json', 'r').read())['web']['client_id']

#Connect to Database and create database session
engine = create_engine('sqlite:///sportinggoods.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    print "LET'S GET SOME GRUB!"
    state = ''.join(random.choice(string.ascii_uppercase + string.
        digits) for x in xrange(32))
    login_session['state'] = state
    #RENDER THE LOGIN TEMPLATE
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    print "LET'S GET THIS PARTY STARTED!"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # Exchange the authorization code for a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print "CREDENTIALS RECEIVED!"
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to get the authorization \
                                             code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
 
   # If there was an error in the access token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match \
                                   given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    print "USER VERIFIED!"
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID doesn't match \
                                   application"), 401)
        print "Token's client ID does not match app's!"
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    print "APP VERIFIED!"
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        print "USER ALREADY LOGGED IN!"
        response = make_response(json.dumps("Current user is already \
                                   connected"), 200)
        response.headers['Content-Type'] = 'application/json'
    
    # Store the access token in the session for later use.
    print "STORING SESSION INFO!"
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user information
    print "STORING USER INFO!"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # See if there is an email in the database already
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id
    

    print "SETING OUTPUT!"
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style="width: 300px; height:300px; border-radius: 150px; \
                -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s"%login_session['username'])
    print "RETURNING OUTPUT!"
    return output


# DISCONNECT - Revoke a current user's token and rest thier login_session.
@app.route("/gdisconnect")
def gdisconnect():
    print "TRYING TO DISCONNECT!"
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        print "DAMN, NO ACCESS TOKEN! WHY?"
        response = make_response(json.dumps('Current user not connected.'),\
                                 401)    
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke the current token.
    #access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        print "BOO WE HAVE NOT DISCONNECTED!"
        response = make_response(json.dumps('Failed to revoke token for \
                                                     given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    return "You have successfully signed out!"       


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    print "LET'S GET THIS FACEBOOK PARTY STARTED!"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    #Exchange client token for long-lived server-side token with
    # GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&
    # client_secret={app-secret}&fb_exchange={short-lived-token}
    app_id = \
      json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = \
     json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?' 
    url += 'grant_type=fb_exchange_token&client_id=%s&' % app_id 
    url += 'client_secret=%s&fb_exchange_token=%s' % (app_secret, access_token)
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    #Use token to get user infor from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    #strip expire tage from access token
    token = result.split("&")[0]
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    #print "url sent for API access:%s"% url
    #print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    #Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture'
    url += '?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    #see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    print "SETING OUTPUT!"
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style="width: 300px; height:300px; border-radius: 150px; \
                -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s"%login_session['username'])
    print "RETURNING OUTPUT!"
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out!"

@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        if login_session['provider'] == 'facebook':
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('showCategories'))


# Main Route for the homepage
@app.route('/')
@app.route('/catalog/')
def showCategories():
    current = datetime.utcnow()
    past = current - timedelta(hours=16)

    categories = session.query(Category).all()
    equip = session.query(Equipment).filter(Equipment.entry_time > past).all()
    return render_template('latestequipment.html', equipment = equip, \
                           categories = categories) 

# Route for showing the equipment for a specific category
@app.route('/catalog/<int:cat_id>/')
@app.route('/catalog/<int:cat_id>/equipment/')
def showSportEquipment(cat_id):
    categories = session.query(Category).all()
    equipment = session.query(Equipment).filter_by(category_id = cat_id)
    category = session.query(Category).filter_by(id = cat_id).one()

    output = ""
    return render_template('equipment.html', equipment = list(equipment), \
                           category = category, categories = categories) 
    
# Route for showing the equipment for a specific category
@app.route('/catalog/<int:equip_id>/detail')
@app.route('/catalog/<int:equip_id>/equipment/detail')
def showEquipmentDetail(equip_id):
    equipment = session.query(Equipment).filter_by(id = equip_id).one()
    category = equipment.category

    output = ""
    return render_template('equipmentdetail.html', equip = equipment, \
                           category = category) 
    
# Route for adding equipment to a category
@app.route('/catalog/<int:cat_id>/equipment/create/', methods=['GET', 'POST'])
def newEquipment(cat_id):
    if 'username' not in login_session:
        return redirect('/login')
    # POST or GET, category is used
    category = session.query(Category).filter_by(id = cat_id).one()

    if request.method == 'POST':
        # Handle an image upload 
        # check if the post request has the file part
        catDir = "%s/" % re.sub('[\s+]', '', category.name.lower())
        imageDir = uploadImageFile(request.files, catDir)


        newEquipment = Equipment(name = request.form['ename'], \
                                 price = request.form['price'], \
                                 description =  request.form['description'], \
                                 image = imageDir, \
                                 category_id = category.id)

        session.add(newEquipment)
        session.commit()
        message = "%s has been added" % newEquipment.name
        flash(message)
        return redirect(url_for('showSportEquipment', cat_id = cat_id))
    else:
        return render_template('newequipment.html', cat = category)

# Route for editing the information for a piece of equipment
@app.route('/catalog/<int:cat_id>/equipment/<int:equip_id>/edit/', \
           methods=['GET', 'POST'])
def editEquipment(cat_id, equip_id):

    if 'username' not in login_session:
        return redirect('/login')

    equipment = session.query(Equipment).filter_by(id = equip_id).one()
    category = equipment.category

    if request.method == 'POST':
        # Handle an image upload 
        # check if the post request has the file part
        catDir = "%s/" % re.sub('[\s+]', '', category.name.lower())
        imageDir = uploadImageFile(request.files, catDir)


        if request.form['ename']:
            equipment.name = request.form['ename']
        if request.form['price']:
            equipment.price = request.form['price']
        if request.form['description']:
            equipment.description = request.form['description']
        if not (equipment.image and  \
                re.search(app.config['DEFAULT_IMAGE'], imageDir)):
            removeImage(equipment.image)
            equipment.image = imageDir

        session.add(equipment)
        session.commit()
        message = "%s has been edited" % equipment.name
        flash(message)

        return redirect(url_for('showSportEquipment', cat_id = cat_id))
        
    else:

        return render_template('editequipment.html', cat = category, \
                                equip = equipment)


# Route for deleting a piece of equipment
@app.route('/catalog/<int:cat_id>/equipment/<int:equip_id>/delete/', \
           methods=['GET', 'POST'])
def deleteEquipment(cat_id, equip_id):

    if 'username' not in login_session:
        return redirect('/login')

    equipment = session.query(Equipment).filter_by(id = equip_id).one()
    if request.method == 'POST':

        removeImage(equipment.image)

        session.delete(equipment)
        session.commit

        message = "%s has been deleted" % equipment.name
        flash(message)

        return redirect(url_for('showSportEquipment', cat_id = cat_id))
    else:
        category = equipment.category

        return render_template('deleteequipment.html', category = category, \
                                equipment = equipment)


#JSON APIs to view Catalog Information
@app.route('/catalog/<int:cat_id>/equipment/JSON')
def categoryEquipmentJSON(cat_id):
    print "CATEGORY ITEMS JSON!"
    category = session.query(Category).filter_by(id = cat_id).one()
    equipment = session.query(Equipment).filter_by(category_id = cat_id).all()
    return jsonify(Equipment=[e.serialize for e in equipment])

@app.route('/catalog/equipment/JSON')
def catalogJSON():
    print "CATALOG JSON!"
    categories = session.query(Category).all()
    equipment = session.query(Equipment).all()
    
    catalog = [ ]
    for c in categories:
        equip = [e.serialize for e in equipment if e.category_id == c.id]
        cat = c.serialize
        cat['Equipment'] = equip
        catalog.append([cat])
     
    return jsonify(Catagories=catalog)


@app.route('/catalog/<int:cat_id>/equipment/<int:equip_id>/JSON')
def equipmentJSON(cat_id, equip_id):
    print "EQUIPMENT JSON!"
    equipment = session.query(Equipment).filter_by(id = equip_id).one()
    return jsonify(Equipment = equipment.serialize)

@app.route('/catalog/JSON')
def categoriesJSON():
    print "CATEGORIES JSON!"
    categories = session.query(Category).all()
    return jsonify(categories= [c.serialize for c in categories])


#Handle the file upload here
def uploadImageFile(requestFiles, imgdir):
    defaultImagePath = os.path.join(app.config['IMAGE_FOLDER'], \
                               app.config['DEFAULT_IMAGE']) 
    defaultImageLocale = "/%s" % defaultImagePath

    if 'imagefile' not in requestFiles:
        return defaultImageLocale

    print "Image file was in the requestFiles"
    file = requestFiles['imagefile']
    # if user does not select file, browser also 
    # submit a empty part without filename
    if file.filename == '':
        return defaultImageLocale

    if file and allowed_file(file.filename.lower()):
        filename = secure_filename(file.filename)
    
        # Change the file name and store in static directory
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        ext = filename.lower().rsplit('.', 1)[1]
    
        new_file = "%s_%s.%s" % (filename.rsplit('.', 1)[0], timestamp, ext)
        img_dir = os.path.join(app.config['IMAGE_FOLDER'], imgdir) 
    
        try:
            os.makedirs(img_dir)
        except OSError:
            if not os.path.isdir(img_dir):
                raise

        img_path = os.path.join(img_dir, new_file) 
        file.save(img_path)
        #Flask requires the slash in front of the path
        imgage_locale = "/%s" % img_path

        return imgage_locale
    else:
        return defaultImageLocale

#Remove an image via an input path
def removeImage(pathToFile):
    if pathToFile:
        if not re.search(app.config['DEFAULT_IMAGE'], pathToFile):
            if os.path.isfile(pathToFile[1:]):
                os.remove(pathToFile[1:])
    return


# Check that an uploaded filetype is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def createUser(login_session):
    newUser = User(name = login_session['username'],  \
                    email = login_session['email'],   \
                    picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.debug = True
    app.secret_key='TheQuickBrownFoxJumpsOverTheLazyDog!'
    app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
    app.config['DEFAULT_IMAGE'] = DEFAULT_IMAGE
    app.run(host = '0.0.0.0', port = 5000)
