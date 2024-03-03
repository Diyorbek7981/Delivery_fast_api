from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('postgresql://delivery_user:dipper7981@localhost/delivery',
#                        echo=True  # deploy qilayotganda olib tashlanadi
#                        # echo sql stetmentlarni (databaseni holati) konsolda korib turish uchun(devolopment uchun)
#                        )

SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./delivery.db'

engine = create_engine(SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()
# model b-n ishlashda kerak
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# CRUD amallridan foydalanish uchun
