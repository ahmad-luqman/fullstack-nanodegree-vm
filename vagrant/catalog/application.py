from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Item Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitemwithuser.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                    json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    ouptut += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token'] \
        if 'access_token' in login_session \
        else login_session.get('credentials').access_token
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
                     json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        if 'credentials' in login_session:
            del login_session['credentials']
        else:
            del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
                     json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/clearSession')
def clearSession():
    login_session.clear()
    return "Session cleared"


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    items_with_catalog = session.query(Item, Catalog). \
        join(Catalog).order_by(desc(Item.inserted)).limit(9).all()
    return render_template('catalogs.html', catalogs=catalogs,
                           items_with_catalog=items_with_catalog)


@app.route('/catalog/JSON')
def showCatalogsJSON():
    catalogs = session.query(Catalog).order_by(asc(Catalog.name)).all()
    items = session.query(Item).order_by(desc(Item.inserted)).limit(9).all()
    return jsonify(Catalogs=[c.serialize for c in catalogs],
                   Items=[i.serialize for i in items])


# Show a catalog
@app.route('/catalog/<string:cat_name>/items/')
def showCatalog(cat_name):
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    catalog = session.query(Catalog).filter_by(name=cat_name).one()
    items_query = session.query(Item).filter_by(cat_id=catalog.id)
    items = items_query.all()
    count = items_query.count()
    return render_template('items.html', items=items, catalogs=catalogs,
                           catalog=catalog, count=count)


# JSON APIs to view a catalog
@app.route('/catalog/<string:cat_name>/items/JSON')
def showCatalogJSON(cat_name):
    catalog = session.query(Catalog).filter_by(name=cat_name).one()
    items = session.query(Item).filter_by(cat_id=catalog.id).all()
    return jsonify(Catalog=catalog.serialize,
                   Items=[i.serialize for i in items])


# Show a catalog
@app.route('/catalog/<string:cat_name>/<string:item_name>/')
def showItem(cat_name, item_name):
    catalog = session.query(Catalog).filter_by(name=cat_name).one()
    item = session.query(Item).\
        filter_by(cat_id=catalog.id).filter_by(title=item_name).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or \
       creator.id != login_session['user_id']:
        return render_template('publicitemdetails.html', catalog=catalog,
                               item=item, creator=creator)
    else:
        return render_template('itemdetails.html', catalog=catalog,
                               item=item, creator=creator)


# Show a catalog
@app.route('/catalog/<string:cat_name>/<string:item_name>/JSON')
def showItemJSON(cat_name, item_name):
    catalog = session.query(Catalog).filter_by(name=cat_name).one()
    item = session.query(Item).filter_by(cat_id=catalog.id).\
        filter_by(title=item_name).one()
    return jsonify(Item=item.serialize)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form['name'])
        session.add(newCatalog)
        flash('New Catalog %s successfully created!' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newCatalog.html')


@app.route('/catalog/<int:cat_id>/edit', methods=['GET', 'POST'])
def editCatalog(cat_id):
    if request.method == 'POST':
        editedCatalog = session.query(Catalog).filter_by(id=cat_id).one()
        editedCatalog.name = request.form['name']
        session.add(editedCatalog)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('editCatalog.html')


@app.route('/catalog/<int:cat_id>/delete', methods=['GET', 'POST'])
def deleteCatalog(cat_id):
    catalogToDelete = session.query(Catalog).filter_by(id=cat_id).one()
    if request.method == 'POST':
        session.delete(catalogToDelete)
        session.commit()
        return redirect(url_for('showCatalogs', cat_id=cat_id))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)


@app.route('/catalog/<int:cat_id>/item/new', methods=['GET', 'POST'])
def newItem(cat_id):
    if request.method == 'POST':
        catalog = session.query(Catalog).filter_by(id=cat_id).one()
        newItem = Item(title=request.form['name'],
                       description=request.form['description'],
                       cat_id=cat_id, user_id=login_session['user_id'])
        session.add(newItem)
        flash('')
        session.commit()
        return redirect('/catalog/%s/items/' % catalog.name)
    else:
        return render_template('newItem.html')


@app.route('/catalog/<string:cat_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(cat_name, item_name):
    cat_id = session.query(Catalog).filter_by(name=cat_name).one().id
    editedItem = session.query(Item).filter_by(title=item_name).\
        filter_by(cat_id=cat_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
                to edit this item. Please create your own item in order to \
                edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        catalog = session.query(Catalog).filter_by(id=cat_id).one()
        editedItem.title = request.form['name']
        editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect('/catalog/%s/items/' % catalog.name)
    else:
        return render_template('editItem.html', item=editedItem)


@app.route('/catalog/<string:cat_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(cat_name, item_name):
    cat_id = session.query(Catalog).filter_by(name=cat_name).one().id
    itemToDelete = session.query(Item).filter_by(title=item_name).\
        filter_by(cat_id=cat_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
                to delete this item. Please create your own item in order to \
                delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect('/catalog/%s/items/' % cat_name)
    else:
        return render_template('deleteItem.html', item=itemToDelete,
                               cat_name=cat_name)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
