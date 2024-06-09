from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String

from .database import Base


class Favor(Base):
    __tablename__ = "favor"
    __table_args__ = (
        PrimaryKeyConstraint("Id", "favor", "stu", "level", name="favor"),
        {},
    )

    Id = Column(String, nullable=False)
    favor = Column(Integer, nullable=False)
    stu = Column(String)
    level = Column(Integer)

    def __repr__(self) -> str:
        return f"<Favor(Id={self.Id!r}, favor={self.favor!r}, stu={self.stu!r}, level={self.level!r})>"


class FavorGrade(Base):
    __tablename__ = "favor_grade"

    grade = Column(Integer, nullable=False, primary_key=True)
    value = Column(Integer)

    def __repr__(self) -> str:
        return f"<FavorGrade(grade={self.grade!r}, value={self.value!r})>"
