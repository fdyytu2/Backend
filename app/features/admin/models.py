from sqlalchemy import Column, String, Integer, Text
from app.core.db_base import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)

class Banner(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    image_url = Column(String(255))

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(100))
    status = Column(String(20), default="OPEN")
