from flask import Flask
from flask import render_template, url_for
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
    catalogItems = session.query(CatalogItem).order_by("id asc").limit(10)
    return render_template('catalogsOut.html', catalogs = catalogs, catalogItems = catalogItems)

# list all items of certain catalog
@app.route('/catalog/<catalog_name>/')
def catalogItems(catalog_name):
    # list for nav menu
    catalogs = session.query(Catalog).all()
    catalog = session.query(Catalog).filter_by(name = catalog_name).one()
    catalogItems = session.query(CatalogItem).filter_by(catalog_id = catalog.id).all()
    catalogItemsCount = session.query(CatalogItem).filter_by(catalog_id = catalog.id).count()

    return render_template('catalogItemsOut.html',
        catalogs = catalogs,
        catalog = catalog,
        catalogItems = catalogItems,
        catalogItemsCount = catalogItemsCount)

# info about specific item
@app.route('/catalog/<catalog_name>/<catalog_item_name>/')
def catalogItemInfo(catalog_name, catalog_item_name):
    # list for nav menu
    catalogs = session.query(Catalog).all()
    # get catalog name
    catalog = session.query(Catalog).filter_by(name = catalog_name).one()
    # get catalog items
    catalogItems = session.query(CatalogItem).filter_by(catalog_id = catalog.id).all()
    # output = ""
    # output += catalog.name
    # for item in catalogItems:
    #   output += item.name
    #   output += item.description
    # return output
    return render_template('catalogItemOut.html', catalogs = catalogs, catalog = catalog, catalogItems = catalogItems)













if __name__ == '__main__':
     app.debug = True
     app.run(host = '0.0.0.0', port = 5000)
