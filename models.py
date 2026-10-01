from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, JSON
from sqlalchemy.orm import relationship
from database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    course_url = Column(Text, nullable=True)
    provider = Column(String(100), default="Coursera")
    status = Column(String(50), default="In Progress")
    created_at = Column(DateTime, default=datetime.utcnow)

    materials = relationship("CourseMaterial", back_populates="course", cascade="all, delete-orphan")
    videos = relationship("CourseVideo", back_populates="course", cascade="all, delete-orphan")
    audios = relationship("CourseAudio", back_populates="course", cascade="all, delete-orphan")
    images = relationship("CourseImage", back_populates="course", cascade="all, delete-orphan")
    analyses = relationship("CourseAnalysis", back_populates="course", cascade="all, delete-orphan")
    chats = relationship("CourseChatHistory", back_populates="course", cascade="all, delete-orphan")

class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(String(50), default="1.5 MB")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="materials")

class CourseVideo(Base):
    __tablename__ = "course_videos"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    video_url = Column(Text, nullable=False)
    duration = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="videos")
    transcripts = relationship("VideoTranscriptSegment", back_populates="video", cascade="all, delete-orphan")

class VideoTranscriptSegment(Base):
    __tablename__ = "video_transcript_segments"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("course_videos.id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(Text, nullable=False)

    video = relationship("CourseVideo", back_populates="transcripts")

class CourseAudio(Base):
    __tablename__ = "course_audios"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    audio_url = Column(Text, nullable=False)
    duration = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="audios")

class CourseImage(Base):
    __tablename__ = "course_images"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    image_url = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="images")

class CourseAnalysis(Base):
    __tablename__ = "course_analyses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    high_priority = Column(Integer, default=3)
    medium_priority = Column(Integer, default=5)
    low_priority = Column(Integer, default=8)
    main_finding = Column(Text, nullable=False)
    finding_details = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    evidence_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="analyses")

class CourseChatHistory(Base):
    __tablename__ = "course_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="chats")
