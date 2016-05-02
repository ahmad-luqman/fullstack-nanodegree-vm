from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Item, User, Base
engine = create_engine('sqlite:///catalogitemwithuser.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Ahmad Luqman", email="ahmad.luqman@gmail.com",
             picture='https://lh3.googleusercontent.com/-ub-VjKadDJw/AAAAAAAAAAI/AAAAAAAAB3o/F1UDI4dt5V4/photo.jpg')
session.add(User1)
session.commit()

catalog1 = Catalog(user_id=1, name="Soccer")

session.add(catalog1)
session.commit()

catalog2 = Catalog(user_id=1, name="Basketball")

session.add(catalog2)
session.commit()

catalog3 = Catalog(user_id=1, name="Baseball")

session.add(catalog3)
session.commit()

catalog4 = Catalog(user_id=1, name="Frisee")

session.add(catalog4)
session.commit()

catalog5 = Catalog(user_id=1, name="Snowboarding")

session.add(catalog5)
session.commit()

catalog6 = Catalog(user_id=1, name="Rock Climbing")

session.add(catalog6)
session.commit()

catalog7 = Catalog(user_id=1, name="Foosball")

session.add(catalog7)
session.commit()


catalog8 = Catalog(user_id=1, name="Skating")

session.add(catalog8)
session.commit()

catalog9 = Catalog(user_id=1, name="Hockey")

session.add(catalog9)
session.commit()

item1 = Item(user_id=1, title="Soccer Cleats", description="",
             catalog=catalog1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, title="Jersey", description="Jersey Description",
             catalog=catalog1)
session.add(item2)
session.commit()

item3 = Item(user_id=1, title="Bat", description="", catalog=catalog3)
session.add(item3)
session.commit()

item4 = Item(user_id=1, title="Frisbee", description="", catalog=catalog4)
session.add(item4)
session.commit()

item5 = Item(user_id=1, title="Shinguards", description="", catalog=catalog1)
session.add(item5)
session.commit()

item6 = Item(user_id=1, title="Two Shinguards", description="",
             catalog=catalog1)
session.add(item6)
session.commit()

item7 = Item(user_id=1, title="Snowboard", description="", catalog=catalog5)
session.add(item7)
session.commit()

item8 = Item(user_id=1, title="Goggles", description="", catalog=catalog5)
session.add(item8)
session.commit()

item1 = Item(user_id=1, title="Hockey", description="", catalog=catalog9)
session.add(item1)
session.commit()

print "added catalog items!"
