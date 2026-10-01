from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="Processing Course")
    course_url = Column(Text, unique=True, nullable=False)
    provider = Column(String(100), default="Coursera")
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    module_order = Column(Integer)
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String(255), nullable=False)
    lesson_order = Column(Integer)
    module = relationship("Module", back_populates="lessons")
    assets = relationship("Asset", back_populates="lesson", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    asset_type = Column(String(50), nullable=False)  # SRT, TXT, HTML, VIDEO, etc.
    source_url = Column(Text)
    rag_enabled = Column(Boolean, default=False)
    lesson = relationship("Lesson", back_populates="assets")

class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    full_text = Column(Text)
    language = Column(String(20), default="en")

class Segment(Base):
    __tablename__ = "segments"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(String(50))
    end_time = Column(String(50))
    chunk_index = Column(Integer)

class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    html_content = Column(Text)
    clean_text = Column(Text)

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    stage = Column(String(100))
    status = Column(String(50))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class DQIssue(Base):
    __tablename__ = "dq_issues"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    issue_type = Column(String(100))
    description = Column(Text)
    severity = Column(String(50))
