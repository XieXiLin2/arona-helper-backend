from sqlalchemy import Column, Integer, String

from .database import Base


class Favor(Base):
    __tablename__ = "favor"

    Id = Column(String, nullable=False)
    favor = Column(Integer, nullable=False)
    stu = Column(String)
    level = Column(Integer)


class FavorGrade(Base):
    __tablename__ = "favor_grade"

    grade = Column(Integer, nullable=False, primary_key=True)
    value = Column(Integer)
