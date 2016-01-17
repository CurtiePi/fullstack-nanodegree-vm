from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Equipment, User
 
engine = create_engine('sqlite:///sportinggoods.db')
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
User1 = User(name="Tiny Tina", email="tinnyTina@bedstuyprod.com",
             picture='http://cdnstatic.visualizeus.com/thumbs/13/90/fuckyou,bad,girl-13907d9a9dba6e37e2906a50347d66f8_h.jpg')
session.add(User1)
session.commit()


#Equipment for Baseball
category1 = Category(name = "Baseball")

session.add(category1)
session.commit()

equipment2 = Equipment(name = "Bat", description = "Juicy grilled veggie patty with tomato mayo and lettuce", price = "$8.99", image="/static/images/default/NoPicAvailable.png", category = category1)

session.add(equipment2)
session.commit()


equipment1 = Equipment(name = "Mitt", description = "with garlic and parmesan", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Batting Helmet", description = "Juicy grilled chicken patty with tomato mayo and lettuce", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category1)

session.add(equipment2)
session.commit()

equipment3 = Equipment(name = "Chest Protector", description = "fresh baked and served with ice cream", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category1)

session.add(equipment3)
session.commit()





#Equipment for Football
category2 = Category(name = "Football")

session.add(category2)
session.commit()


equipment1 = Equipment(name = "Football", description = "With your choice of noodles vegetables and sauces", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category2)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Helmet", description = " A head protector", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category2)

session.add(equipment2)
session.commit()

equipment3 = Equipment(name = "Shoulder pads", description = "Seared rare ahi, avocado, edamame, cucumber with wasabi soy sauce ", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category2)

session.add(equipment3)
session.commit()

equipment4 = Equipment(name = "Thigh pads", description = "Steamed dumplings made with", price = "$8.99", image="/static/images/default/NoPicAvailable.png", category = category2)

session.add(equipment4)
session.commit()


#Equipment for Hockey
category1 = Category(name = "Hockey")

session.add(category1)
session.commit()


equipment1 = Equipment(name = "Puck", description = "a Vietnamese noodle soup consisting of brot.", image="/static/images/default/NoPicAvailable.png", price = "$8.99", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Helmet", description = "a head protector.", image="/static/images/default/NoPicAvailable.png", price = "$6.99", category = category1)

session.add(equipment2)
session.commit()

equipment3 = Equipment(name = "Stick", description = "The most prominent fact is that sticks are much thinner", image="/static/images/default/NoPicAvailable.png", price = "$19.95", category = category1)

session.add(equipment3)
session.commit()


#Equipment for Rugby
category1 = Category(name = "Rugby ")

session.add(category1)
session.commit()


equipment1 = Equipment(name = "Rugby Ball", description = "Odd shaped ball.", image="/static/images/default/NoPicAvailable.png", price = "$25.99", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Mouth guard", description = "Protect your teeth", image="/static/images/default/NoPicAvailable.png", price = "$1.99", category = category1)

session.add(equipment2)
session.commit()

equipment3 = Equipment(name = "Cleats", description = "Milk snow layered with honey boba", image="/static/images/default/NoPicAvailable.png", price = "$49.50", category = category1)

session.add(equipment3)
session.commit()

equipment4 = Equipment(name = "Scrum Cap", description = "A light leathery helmet.", image="/static/images/default/NoPicAvailable.png", price = "$16.95", category = category1)

session.add(equipment4)
session.commit()


#Equipment for Basketball
category1 = Category(name = "Basketball")

session.add(category1)
session.commit()


equipment1 = Equipment(name = "Basketball", description = "Lobster, shrimp ", image="/static/images/default/NoPicAvailable.png", price = "$13.95", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Shorts", description = "Chicken... and rice", image="/static/images/default/NoPicAvailable.png", price = "$4.95", category = category1)

session.add(equipment2)
session.commit()

equipment3 = Equipment(name = "Hoop", description = "Spaghetti made by mom", image="/static/images/default/NoPicAvailable.png", price = "$6.95", category = category1)

session.add(equipment3)
session.commit()



#Equipment for Skating 
category1 = Category(name = "Skating")

session.add(category1)
session.commit()


equipment1 = Equipment(name = "Skates", description = "Slow cook that thang in a pool of tomatoes", image="/static/images/default/NoPicAvailable.png", price = "$59.95", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Knee Gaurds", description = "Chicken", price = "$7.95", image="/static/images/default/NoPicAvailable.png", category = category1)

session.add(equipment2)
session.commit()



#Equipment for Rock Climbing
category1 = Category(name = "Rock Climbing ")

session.add(category1)
session.commit()

equipment9 = Equipment(name = "Rope", description = "Fresh battered sirloin", image="/static/images/default/NoPicAvailable.png", price = "$18.99", category = category1)

session.add(equipment9)
session.commit()



equipment1 = Equipment(name = "Pitons", description = "An unsettlingly huge amount of awesomeness", image="/static/images/default/NoPicAvailable.png", price = "$12.99", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Caribeener", description = "hot & fast", image="/static/images/default/NoPicAvailable.png", price = "$10.95", category = category1)

session.add(equipment2)
session.commit()



#Equipment for Swimming
category1 = Category(name = "Swimming ")

session.add(category1)
session.commit()


equipment1 = Equipment(name = "Swim Cap", description = "Marinated Pork, Rice, Beans, Avocado, Cilantro, Salsa, Tortilla", image="/static/images/default/NoPicAvailable.png", price = "$5.95", category = category1)

session.add(equipment1)
session.commit()

equipment2 = Equipment(name = "Googles", description = "Golden brown. ", image="/static/images/default/NoPicAvailable.png", price = "$7.99", category = category1)

session.add(equipment2)
session.commit()


#Equipment for Weightlifting
category1 = Category(name = "Weightlifting")
session.add(category1)
session.commit()

equipment1 = Equipment(name = "Hand Straps", description = "Crispy Toast with Sesame Seeds ", image="/static/images/default/NoPicAvailable.png", price = "$5.95", category = category1)

session.add(equipment1)
session.commit

equipment1 = Equipment(name = "Belt", description = "Japanese Italian Pork Jowl (guanciale)", image="/static/images/default/NoPicAvailable.png", price = "$6.95", category = category1)

session.add(equipment1)
session.commit()


equipment1 = Equipment(name = "Gloves", description = "Lemon Curd Ice Cream Sandwich", image="/static/images/default/NoPicAvailable.png", price = "$4.25", category = category1)

session.add(equipment1)
session.commit()


print "added menu items!"
