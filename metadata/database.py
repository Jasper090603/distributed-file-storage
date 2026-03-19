from sqlalchemy import create_engine                                                #To connect python to DB
from sqlalchemy.ext.declarative import declarative_base                             #To define talbes as python classes
from sqlalchemy.orm import sessionmaker                                             #Used to create sessions, A session=temporary workspace to talk to DB

DATABASE_URL = "postgresql://postgres:Jasper%4009@localhost:5432/distributed_drive" #connection string

engine = create_engine(DATABASE_URL)                                                #creates the database engine(connection pool) its like manager that knows how to talk to DB

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)         #This creates session factory, autocommit=false we have to call session.commit to save it is not saved automatically, autoflush=false prevents automatic syncing before queries bind=engine links session to the DB engine

Base = declarative_base()                                                           #This is the base class for all models, every table will inherit from this