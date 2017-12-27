from flask import Flask
from flask import render_template, url_for, redirect, request
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalogs')
@app.route('/catalog')
# list all recent catalog items
def catalogs():
    # list for nav menu
    catalogs = session.query(Catalog).all()
    # load items menu when logged out
    if 1 > 20:
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
    if 1 > 20:
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
    if 1 > 20:
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











if __name__ == '__main__':
     app.debug = True
     app.run(host = '0.0.0.0', port = 5000)
