import time
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./babel.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(8), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    role = Column(String)
    login_token = Column(String(6))

    submissions = relationship("SubmissionDB", back_populates="user", cascade="all, delete-orphan")
    resolves = relationship("ResolveDB", back_populates="user", cascade="all, delete-orphan")


class ProblemDB(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    subject = Column(String, nullable=False)
    difficulty = Column(String(10), nullable=False)
    time_limit = Column(Integer, nullable=False)
    memory_limit = Column(Integer, nullable=False)

    test_cases = relationship("TestCaseDB", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("SubmissionDB", back_populates="problem", cascade="all, delete-orphan")
    resolves = relationship("ResolveDB", back_populates="problem", cascade="all, delete-orphan")


class ResolveDB(Base):
    __tablename__ = "resolve"

    id_problem = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    number_of_tries = Column(Integer, default=0)
    points = Column(Integer, default=0)

    problem = relationship("ProblemDB", back_populates="resolves")
    user = relationship("UserDB", back_populates="resolves")


class TestCaseDB(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stdin = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    id_problem = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))

    problem = relationship("ProblemDB", back_populates="test_cases")


class SubmissionDB(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code_submited = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    time_of_submission = Column(Integer, default=lambda: int(time.time()))
    status = Column(String(25), nullable=False)
    logs = Column(Text)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    id_problem = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"))

    user = relationship("UserDB", back_populates="submissions")
    problem = relationship("ProblemDB", back_populates="submissions")
