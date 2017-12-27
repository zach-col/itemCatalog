
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, CatalogItem

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

catalog1 = Catalog(name="Football")

session.add(catalog1)
session.commit()

catalogItem1 = CatalogItem(name="Helmet", description="helmet helps protect the brain", catalog=catalog1 )

session.add(catalogItem1)
session.commit()

print "added catalog and catalog item"
