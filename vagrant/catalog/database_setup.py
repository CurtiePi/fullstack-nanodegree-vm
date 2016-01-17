from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(75), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id'      : self.id,
            'name'    : self.name,
            'email'   : self.email,
            'picture' : self.picture,
        }

class Category(Base):
    __tablename__ = 'categories'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id'           : self.id,
            'name'         : self.name,
        }
 
class Equipment(Base):
    __tablename__ = 'equipment'


    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(8))
    image = Column(String(250))
    entry_time = Column(DateTime, default=func.now()) 
    category_id = Column(Integer,ForeignKey('categories.id'))
    category = relationship(Category)


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id'            : self.id,
            'name'          : self.name,
            'description'   : self.description,
            'price'         : self.price,
            'image'         : self.image,
            'entry_time'    : self.entry_time
        }


engine = create_engine('sqlite:///sportinggoods.db')
 

Base.metadata.create_all(engine)
