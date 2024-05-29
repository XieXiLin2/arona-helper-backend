# ignore: reportAny
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

BaseTable = declarative_base(name="BaseTable")  # type: ignore[reportAny]


class FavorTable(BaseTable):  # type: ignore[reportAny]
    __tablename__ = "favor"

    Id = Column(String, nullable=False)
    favor = Column(Integer, nullable=False)
    stu = Column(String)
    level = Column(Integer)


class FavorGradeTable(BaseTable):  # type: ignore[reportAny]
    __tablename__ = "favor_grade"

    grade = Column(Integer, nullable=False, primary_key=True)
    value = Column(Integer)


class BACardTable(BaseTable):  # type: ignore[reportAny]
    __tablename__ = "ba_card"

    Id = Column(String)
    cardname = Column(String)
    num = Column(Integer)
