from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Crime(Base):
    __tablename__ = "crimes"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    description = Column(String)
    location = Column(String)
    suspect_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    def __repr__(self):
        return "<Crime(id={id}, type={type}, description={description}, location={location}, suspect_name={suspect_name}, latitude={latitude}, longitude={longitude})>".format(
            id=self.id,
            type=self.type,
            description=self.description,
            location=self.location,
            suspect_name=self.suspect_name,
            latitude=self.latitude,
            longitude=self.longitude,
        )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    
    def __repr__(self):
        return "<User(id={id}, username={username}, hashed_password={hashed_password}, is_active={is_active}, is_superuser={is_superuser})>".format(
            id=self.id,
            username=self.username,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
        )




if __name__ == "__main__":
    # Create the database tables
    DATABASE_URL = "sqlite:///./gotham_crime_data.db"

    engine = create_engine(DATABASE_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

