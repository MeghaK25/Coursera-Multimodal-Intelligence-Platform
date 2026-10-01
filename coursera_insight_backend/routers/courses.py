from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Course, ProcessingJob
from schemas import CourseRequest

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/")
def list_courses(db: Session = Depends(get_db)):
    """List all registered courses."""
    courses = db.query(Course).all()
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "course_url": c.course_url,
            "provider": c.provider,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in courses
    ]

@router.post("/analyze")
def analyze_course(request: CourseRequest, db: Session = Depends(get_db)):
    """Register a course and create its first processing job."""
    course_url = str(request.course_url)

    existing = db.query(Course).filter(Course.course_url == course_url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course already exists")

    course = Course(
        title="Processing Course",
        course_url=course_url,
        provider="Coursera",
        status="processing",
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    job = ProcessingJob(
        course_id=course.id,
        stage="ingestion",
        status="started",
        message="Course ingestion has started.",
    )
    db.add(job)
    db.commit()

    return {
        "message": "Course processing started",
        "course_id": course.id,
        "status": course.status,
    }

@router.get("/{course_id}/status")
def course_status(course_id: int, db: Session = Depends(get_db)):
    """Return processing status used by the Processing screen."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.course_id == course_id)
        .order_by(ProcessingJob.id)
        .all()
    )
    return {
        "course_id": course.id,
        "title": course.title,
        "status": course.status,
        "processing_steps": [
            {"stage": j.stage, "status": j.status, "message": j.message} for j in jobs
        ],
    }
