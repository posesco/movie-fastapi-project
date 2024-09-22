from config.database import Base
from sqlalchemy import Column, Integer, String, Float, Date, Enum
import enum

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key = True, autoincrement=True)
    title = Column(String, nullable=False)
    overview = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    director = Column(String, nullable=False)
    studio = Column(String, nullable=False)
    box_office = Column(String, nullable=True)
    
class GenderEnum(enum.Enum):
    male = "Masculino"
    female = "Femenino"
    other = "Otro"

class Actor(Base):
    __tablename__ = "actors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False) 
    birth_date = Column(Date, nullable=False)  
    gender = Column(Enum(GenderEnum), nullable=False)  
    description = Column(String, nullable=True)  


    
