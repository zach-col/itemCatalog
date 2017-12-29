from flask import Flask
from flask import render_template, url_for, redirect, request

# sql alchemy database importing database etc...
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItem

# anti forgery state token imports
from flask import session as login_session
import random
import string

# imports for oauth2client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


# google client id
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Menu App"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# create state token to precent requests store it in session
@app.route('/login/')
def showLogin():
    # list for nav menu
    catalogs = session.query(Catalog).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('googleSignIn.html', STATE=state, catalogs = catalogs)

@app.route('/gconnect/', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# home page lists recently created items
@app.route('/')
@app.route('/catalogs')
@app.route('/catalog')
# list all recent catalog items
def catalogs():
    # list for nav menu
    catalogs = session.query(Catalog).all()
    # load items menu when logged out
    if 100 > 20:
        catalogItems = session.query(CatalogItem).order_by("id asc").limit(10)
        return render_template('catalogsOut.html', catalogs = catalogs, catalogItems = catalogItems)
    # load items menu with button when logged in
    else:
        catalogItems = session.query(CatalogItem).order_by("id asc").limit(10)
        return render_template('catalogsIn.html', catalogs = catalogs, catalogItems = catalogItems)

# list all items of certain catalog
@app.route('/catalog/<int:catalog_id>/')
def catalogItems(catalog_id):
    # list for nav menu
    catalogs = session.query(Catalog).all()
    # load logged out menu
    if 100 > 20:
        catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        catalogItems = session.query(CatalogItem).filter_by(catalog_id = catalog_id).all()
        catalogItemsCount = session.query(CatalogItem).filter_by(catalog_id = catalog.id).count()
        return render_template('catalogItemsOut.html', catalogs = catalogs, catalog = catalog, catalogItemsCount = catalogItemsCount, catalogItems = catalogItems)
    else:
        catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        catalogItems = session.query(CatalogItem).filter_by(catalog_id = catalog_id).all()
        catalogItemsCount = session.query(CatalogItem).filter_by(catalog_id = catalog.id).count()
        return render_template('catalogItemsIn.html', catalogs = catalogs, catalog = catalog, catalogItemsCount = catalogItemsCount, catalogItems = catalogItems)

# info about specific item
@app.route('/catalog/<int:catalog_id>/<int:catalog_item_id>/')
def catalogItemInfo(catalog_id, catalog_item_id):
    # list for nav menu
    catalogs = session.query(Catalog).all()
    if 100 > 20:
        # get catalog name
        catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        # get catalog item
        catalogItem = session.query(CatalogItem).filter_by(catalog_id = catalog_id, id = catalog_item_id).one()
        return render_template('catalogItemInfoOut.html', catalogs = catalogs, catalog = catalog, catalogItem = catalogItem)
    else:
        # get catalog name
        catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        # get catalog item
        catalogItem = session.query(CatalogItem).filter_by(catalog_id = catalog_id, id = catalog_item_id).one()
        return render_template('catalogItemInfoIn.html', catalogs = catalogs, catalog = catalog, catalogItem = catalogItem)

# add new catalog item
@app.route('/catalog/newItem', methods=['GET','POST'])
def catalogNewItem():
    # list for nav menu
    catalogs = session.query(Catalog).all()
    if request.method == 'POST':
        newItem = CatalogItem(
            name = request.form['name'],
            description = request.form['description'],
            catalog_id = request.form['catalog_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalogs'))
    else:
        return render_template('catalogNewItem.html', catalogs = catalogs)

# edit catalog item
@app.route('/catalog/<int:catalog_id>/<int:catalog_item_id>/edit/', methods=['GET','POST'])
def catalogEditItem(catalog_id, catalog_item_id):
    # list for nav menu
    catalogs = session.query(Catalog).all()
    # get catalog item to be edited
    editItem = session.query(CatalogItem).filter_by(catalog_id = catalog_id, id = catalog_item_id).one()
    if request.method == 'POST':
        editItem.name = request.form['name']
        editItem.description = request.form['description']
        editItem.catalog_id = request.form['catalog_id']
        editItem.id = catalog_item_id
        session.add(editItem)
        session.commit()
        return redirect(url_for('catalogs'))
    else:
        return render_template('catalogEditItem.html', catalogs = catalogs, editItem = editItem)

# delete catalog item
@app.route('/catalog/<int:catalog_id>/<int:catalog_item_id>/delete/', methods=['GET','POST'])
def catalogDeleteItem(catalog_id, catalog_item_id):
    # list for nav menu
    catalogs = session.query(Catalog).all()
    deleteItem = session.query(CatalogItem).filter_by(catalog_id = catalog_id, id = catalog_item_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('catalogItems', catalog_id = catalog_id))
    return render_template('catalogDeleteItem.html', catalogs = catalogs, deleteItem = deleteItem)









if __name__ == '__main__':
     app.secret_key = 'super_secret_key'
     app.debug = True
     app.run(host = '0.0.0.0', port = 5000)
