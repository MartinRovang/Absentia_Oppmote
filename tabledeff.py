


def reset_dayusers():

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import Column, Integer, Unicode, UnicodeText, Date, Integer, String
    from sqlalchemy import create_engine, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship, backref




    engine = create_engine('sqlite:///temp.db', echo=True)
    Base = declarative_base()

    ########################################################################
    class data(Base):
        """"""
        __tablename__ = "users"

        id = Column(Integer, primary_key=True)
        name = Column(String)
        number = Column(String)

        def __init__(self,name, number):
            """"""
            self.name = name
            self.number = number

    # create tables
    Base.metadata.create_all(engine)


