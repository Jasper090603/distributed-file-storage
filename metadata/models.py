from sqlalchemy import Column, String, Integer, ForeignKey
from metadata.database import Base

class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    size = Column(Integer)



class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, ForeignKey("files.id"))
    chunk_name = Column(String)
    chunk_order = Column(Integer)
    node = Column(String)